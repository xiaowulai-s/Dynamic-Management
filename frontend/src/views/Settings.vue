<template>
  <div class="settings-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">系统设置</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <!-- 审批配置 -->
        <el-tab-pane label="审批配置" name="approval">
          <div class="tab-content">
            <div class="section-header">
              <h3>审批规则配置</h3>
              <p class="description">配置哪些日志类型需要管理员审批后才能生效</p>
            </div>

            <el-table :data="approvalConfigs" v-loading="loading">
              <el-table-column prop="log_type" label="日志类型" min-width="150">
                <template #default="{ row }">
                  {{ getLogTypeLabel(row.log_type) }}
                </template>
              </el-table-column>
              <el-table-column prop="require_approval" label="需要审批" width="120">
                <template #default="{ row }">
                  <el-switch
                    v-model="row.require_approval"
                    @change="handleApprovalConfigChange(row)"
                    :loading="row.updating"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="更新时间" width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.updated_at || row.created_at) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 系统配置 -->
        <el-tab-pane label="系统配置" name="system">
          <div class="tab-content">
            <div class="section-header">
              <h3>系统参数配置</h3>
              <p class="description">配置系统运行参数，如保养周期、设备寿命等</p>
            </div>

            <el-table :data="systemConfigs" v-loading="loading">
              <el-table-column prop="config_key" label="配置项" min-width="180">
                <template #default="{ row }">
                  {{ getConfigKeyLabel(row.config_key) }}
                </template>
              </el-table-column>
              <el-table-column prop="config_value" label="配置值" min-width="200">
                <template #default="{ row }">
                  <el-input
                    v-model="row.config_value"
                    type="textarea"
                    :rows="2"
                    placeholder="请输入配置值"
                    @blur="handleSystemConfigChange(row)"
                  />
                </template>
              </el-table-column>
              <el-table-column prop="description" label="说明" min-width="200" />
              <el-table-column prop="updated_at" label="更新时间" width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.updated_at) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getApprovalConfigs, updateApprovalConfig, getSystemConfigs, updateSystemConfig } from '@/api'
import { useSiteTitle } from '@/composables/useSiteTitle'

const { setSiteTitle } = useSiteTitle()

interface ApprovalConfig {
  id: number
  log_type: string
  require_approval: boolean
  created_at: string
  updated_at?: string
  updating?: boolean
}

interface SystemConfig {
  id: number
  config_key: string
  config_value: any
  description: string
  updated_at: string
}

const activeTab = ref('approval')
const loading = ref(false)
const approvalConfigs = ref<ApprovalConfig[]>([])
const systemConfigs = ref<SystemConfig[]>([])

const logTypeLabels: Record<string, string> = {
  installation: '设备安装',
  repair: '设备维修',
  scrap: '设备报废',
  inspection: '日常巡检',
  maintenance: '保养记录',
  fault: '故障报修',
  parts: '配件更换',
  calibration: '校准记录'
}

const configKeyLabels: Record<string, string> = {
  maintenance_cycle: '保养周期（天）',
  equipment_life: '设备寿命（年）',
  calibration_cycle: '校准周期（天）',
  warning_days: '预警提醒天数',
  site_title_zh: '系统中文名称（侧边栏主标题）',
  site_title_en: '系统英文名称（侧边栏副标题）'
}

const getLogTypeLabel = (key: string): string => {
  return logTypeLabels[key] || key
}

const getConfigKeyLabel = (key: string): string => {
  return configKeyLabels[key] || key
}

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadApprovalConfigs = async () => {
  try {
    loading.value = true
    const res = await getApprovalConfigs()
    approvalConfigs.value = res.data
  } catch (error) {
    ElMessage.error('加载审批配置失败')
  } finally {
    loading.value = false
  }
}

const loadSystemConfigs = async () => {
  try {
    loading.value = true
    const res = await getSystemConfigs()
    // 字符串类型的配置项，后端以 JSON 字符串存储（带引号），显示时去掉首尾引号
    systemConfigs.value = (res.data || []).map((c: SystemConfig) => {
      const val = c.config_value
      if (typeof val === 'string' && val.startsWith('"') && val.endsWith('"')) {
        return { ...c, config_value: val.slice(1, -1) }
      }
      return c
    })
  } catch (error) {
    ElMessage.error('加载系统配置失败')
  } finally {
    loading.value = false
  }
}

const handleApprovalConfigChange = async (config: ApprovalConfig) => {
  try {
    config.updating = true
    await updateApprovalConfig(config.id, {
      log_type: config.log_type,
      require_approval: config.require_approval
    })
    ElMessage.success('更新成功')
  } catch (error) {
    ElMessage.error('更新失败')
    // 恢复原值
    const original = approvalConfigs.value.find(c => c.id === config.id)
    if (original) {
      config.require_approval = !config.require_approval
    }
  } finally {
    config.updating = false
  }
}

const handleSystemConfigChange = async (config: SystemConfig) => {
  try {
    // 字符串类型配置项（site_title_*）保存时加引号，与后端 JSON 字符串格式一致
    const isStringType = config.config_key === 'site_title_zh' || config.config_key === 'site_title_en'
    const payload = isStringType
      ? { ...config, config_value: `"${config.config_value}"` }
      : config
    await updateSystemConfig(config.config_key, { config_value: payload.config_value })
    ElMessage.success('更新成功')
    // 保存站点标题后实时更新侧边栏
    if (isStringType) {
      const zh = systemConfigs.value.find(c => c.config_key === 'site_title_zh')
      const en = systemConfigs.value.find(c => c.config_key === 'site_title_en')
      const zhVal = zh ? String(zh.config_value) : ''
      const enVal = en ? String(en.config_value) : ''
      setSiteTitle(zhVal, enVal)
    }
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

onMounted(() => {
  loadApprovalConfigs()
  loadSystemConfigs()
})
</script>

<style scoped>
.settings-container {
  /* padding 由 .content 全局控制 */
}

.settings-container :deep(.el-card) {
  border-radius: var(--radius-md);
  overflow: hidden;
}

.settings-container :deep(.el-card__header) {
  padding: var(--space-5) var(--space-6);
  border-bottom: 2px solid var(--border-default);
  background-color: var(--surface-elevated);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .title {
  font-size: var(--text-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

/* Tab 内容区域 */
.tab-content {
  padding: var(--space-6) 0;
}

.tab-content .section-header {
  margin-bottom: var(--space-6);
}

.tab-content .section-header h3 {
  margin: 0 0 var(--space-3) 0;
  font-size: var(--text-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.tab-content .section-header .description {
  margin: 0;
  color: var(--text-tertiary);
  font-size: var(--text-base);
  line-height: var(--leading-relaxed);
}

/* 表格优化 */
.settings-container :deep(.el-table) {
  border-radius: var(--radius-md);
}

.settings-container :deep(.el-table__cell) {
  padding: var(--space-4) var(--space-5);
}

/* Switch 开关优化 */
.settings-container :deep(.el-switch) {
  --el-switch-on-color: var(--color-primary-600);
  --el-switch-off-color: var(--color-neutral-300);
}

/* Input 文本域优化 */
.settings-container :deep(.el-textarea__inner) {
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

/* Tabs 优化 */
:deep(.el-tabs--border-card) {
  border-radius: var(--radius-md);
  border: 1px solid var(--border-default);
  box-shadow: var(--shadow-card);
}

:deep(.el-tabs--border-card>.el-tabs__header) {
  background-color: var(--surface-elevated);
  border-bottom: 1px solid var(--border-default);
}

:deep(.el-tabs__item) {
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
}

:deep(.el-tabs__item:hover) {
  color: var(--color-primary-600);
}

:deep(.el-tabs__item.is-active) {
  color: var(--color-primary-600);
  background-color: var(--surface-card);
}

:deep(.el-tabs--border-card>.el-tabs__header .el-tabs__item.is-active) {
  border-right-color: var(--border-default);
  border-left-color: var(--border-default);
}

:deep(.el-tabs__content) {
  padding: var(--space-6);
}
</style>
