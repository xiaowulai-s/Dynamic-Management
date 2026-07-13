<template>
  <div class="log-detail-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="title">日志详情</span>
          <div>
            <el-button @click="$router.back()">返回</el-button>
            <el-button
              v-if="logDetail?.status === 'pending'"
              type="danger"
              @click="handleReject"
            >
              驳回
            </el-button>
            <el-button
              v-if="logDetail?.status === 'pending'"
              type="primary"
              @click="handleApprove"
            >
              通过
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="logDetail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="日志类型">
            {{ getLogTypeLabel(logDetail.log_type) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(logDetail.status)">
              {{ getStatusLabel(logDetail.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="设备">
            {{ logDetail.equipment?.name }} ({{ logDetail.equipment?.code }})
          </el-descriptions-item>
          <el-descriptions-item label="操作人">
            {{ logDetail.operator?.username }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(logDetail.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="审批时间" v-if="logDetail.approved_at">
            {{ formatDateTime(logDetail.approved_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="审批人" v-if="logDetail.approver">
            {{ logDetail.approver.username }}
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ logDetail.description || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="驳回原因" :span="2" v-if="logDetail.rejection_reason">
            <el-text type="danger">{{ logDetail.rejection_reason }}</el-text>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 详细信息 -->
        <el-divider />

        <div v-if="logDetail.detail">
          <h3>详细信息</h3>

          <!-- 安装日志 -->
          <div v-if="logDetail.log_type === 'installation' && logDetail.detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="安装日期">
                {{ logDetail.detail.installation_date }}
              </el-descriptions-item>
              <el-descriptions-item label="安装人员">
                {{ logDetail.detail.installer }}
              </el-descriptions-item>
              <el-descriptions-item label="安装位置">
                {{ logDetail.detail.location }}
              </el-descriptions-item>
              <el-descriptions-item label="验收状态">
                <el-tag>{{ logDetail.detail.acceptance_status }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 维修日志 -->
          <div v-else-if="logDetail.log_type === 'repair' && logDetail.detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="维修日期">
                {{ logDetail.detail.repair_date }}
              </el-descriptions-item>
              <el-descriptions-item label="维修费用">
                ¥{{ logDetail.detail.cost }}
              </el-descriptions-item>
              <el-descriptions-item label="维修时长(小时)">
                {{ logDetail.detail.repair_time }}
              </el-descriptions-item>
              <el-descriptions-item label="故障描述" :span="2">
                {{ logDetail.detail.fault_description }}
              </el-descriptions-item>
              <el-descriptions-item label="解决方案" :span="2">
                {{ logDetail.detail.solution }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 报废日志 -->
          <div v-else-if="logDetail.log_type === 'scrap' && logDetail.detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="报废日期">
                {{ logDetail.detail.scrap_date }}
              </el-descriptions-item>
              <el-descriptions-item label="残值">
                ¥{{ logDetail.detail.residual_value }}
              </el-descriptions-item>
              <el-descriptions-item label="报废原因" :span="2">
                {{ logDetail.detail.scrap_reason }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 巡检日志 -->
          <div v-else-if="logDetail.log_type === 'inspection' && logDetail.detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="巡检日期">
                {{ logDetail.detail.inspection_date }}
              </el-descriptions-item>
              <el-descriptions-item label="巡检人员">
                {{ logDetail.detail.inspector }}
              </el-descriptions-item>
              <el-descriptions-item label="巡检结果" :span="2">
                <el-tag :type="logDetail.detail.result === 'normal' ? 'success' : 'danger'">
                  {{ logDetail.detail.result === 'normal' ? '正常' : '异常' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 保养记录 -->
          <div v-else-if="logDetail.log_type === 'maintenance' && logDetail.detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="保养日期">
                {{ logDetail.detail.maintenance_date }}
              </el-descriptions-item>
              <el-descriptions-item label="下次保养日期">
                {{ logDetail.detail.next_maintenance_date }}
              </el-descriptions-item>
              <el-descriptions-item label="保养项目" :span="2">
                <el-tag
                  v-for="item in logDetail.detail.maintenance_items"
                  :key="item"
                  style="margin: 2px"
                >
                  {{ item }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 故障报修 -->
          <div v-else-if="logDetail.log_type === 'fault' && logDetail.detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="故障日期">
                {{ logDetail.detail.fault_date }}
              </el-descriptions-item>
              <el-descriptions-item label="故障等级">
                <el-tag :type="getFaultLevelType(logDetail.detail.fault_level)">
                  {{ getFaultLevelLabel(logDetail.detail.fault_level) }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="报告人">
                {{ logDetail.detail.reporter }}
              </el-descriptions-item>
              <el-descriptions-item label="处理状态">
                <el-tag>{{ logDetail.detail.handle_status }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="故障描述" :span="2">
                {{ logDetail.detail.fault_description }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 配件更换 -->
          <div v-else-if="logDetail.log_type === 'parts' && logDetail.detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="更换日期">
                {{ logDetail.detail.replacement_date }}
              </el-descriptions-item>
              <el-descriptions-item label="配件编号">
                {{ logDetail.detail.parts_code }}
              </el-descriptions-item>
              <el-descriptions-item label="配件名称">
                {{ logDetail.detail.parts_name }}
              </el-descriptions-item>
              <el-descriptions-item label="数量">
                {{ logDetail.detail.quantity }}
              </el-descriptions-item>
              <el-descriptions-item label="费用">
                ¥{{ logDetail.detail.cost }}
              </el-descriptions-item>
            </el-descriptions>
          </div>

          <!-- 校准记录 -->
          <div v-else-if="logDetail.log_type === 'calibration' && logDetail.detail">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="校准日期">
                {{ logDetail.detail.calibration_date }}
              </el-descriptions-item>
              <el-descriptions-item label="校准机构">
                {{ logDetail.detail.calibration_org }}
              </el-descriptions-item>
              <el-descriptions-item label="校准结果">
                <el-tag :type="logDetail.detail.calibration_result === 'qualified' ? 'success' : 'danger'">
                  {{ logDetail.detail.calibration_result === 'qualified' ? '合格' : '不合格' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="下次校准日期">
                {{ logDetail.detail.next_calibration_date }}
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </div>

        <!-- 附件 -->
        <el-divider v-if="logDetail.attachments && logDetail.attachments.length > 0" />
        <div v-if="logDetail.attachments && logDetail.attachments.length > 0">
          <h3>附件</h3>
          <el-space wrap>
            <el-button
              v-for="(file, index) in logDetail.attachments"
              :key="index"
              @click="handleDownload(file)"
            >
              下载附件 {{ index + 1 }}
            </el-button>
          </el-space>
        </div>
      </div>

      <el-empty v-else description="日志不存在" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLogDetail, approveLog, rejectLog } from '@/api'

const route = useRoute()
const loading = ref(false)
const logDetail = ref<any>(null)

const getLogTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    installation: '设备安装',
    repair: '设备维修',
    scrap: '设备报废',
    inspection: '日常巡检',
    maintenance: '保养记录',
    fault: '故障报修',
    parts: '配件更换',
    calibration: '校准记录'
  }
  return labels[type] || type
}

const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    pending: '待审批',
    approved: '已通过',
    rejected: '已驳回'
  }
  return labels[status] || status
}

const getStatusType = (status: string): string => {
  const types: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return types[status] || 'info'
}

const getFaultLevelLabel = (level: string): string => {
  const labels: Record<string, string> = {
    minor: '轻微',
    major: '严重',
    critical: '紧急'
  }
  return labels[level] || level
}

const getFaultLevelType = (level: string): string => {
  const types: Record<string, string> = {
    minor: 'info',
    major: 'warning',
    critical: 'danger'
  }
  return types[level] || 'info'
}

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadLogDetail = async () => {
  try {
    loading.value = true
    const id = route.params.id
    const res = await getLogDetail(Number(id))
    logDetail.value = res.data
  } catch (error) {
    ElMessage.error('加载日志详情失败')
  } finally {
    loading.value = false
  }
}

const handleApprove = async () => {
  try {
    await ElMessageBox.confirm('确认通过此日志？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await approveLog(logDetail.value.id)
    ElMessage.success('审批通过')
    loadLogDetail()
  } catch (error) {
    // 用户取消
  }
}

const handleReject = async () => {
  try {
    const { value } = await ElMessageBox.prompt('请输入驳回原因', '驳回', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputType: 'textarea'
    })
    await rejectLog(logDetail.value.id, { rejection_reason: value })
    ElMessage.success('已驳回')
    loadLogDetail()
  } catch (error) {
    // 用户取消
  }
}

const handleDownload = (filePath: string) => {
  window.open(filePath, '_blank')
}

onMounted(() => {
  loadLogDetail()
})
</script>

<style scoped>
.log-detail-container {
  /* padding 由 .content 全局控制 */
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

h3 {
  font-size: var(--text-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  margin: 0 0 var(--space-4) 0;
}
</style>
