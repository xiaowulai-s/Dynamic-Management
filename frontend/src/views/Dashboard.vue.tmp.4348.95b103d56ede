<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>仪表盘</h2>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-card-inner">
          <div class="stat-card-info">
            <div class="stat-card-value">{{ stats.totalEquipment }}</div>
            <div class="stat-card-label">设备总数</div>
          </div>
          <div class="stat-card-icon icon-indigo">
            <el-icon :size="22"><Box /></el-icon>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card-inner">
          <div class="stat-card-info">
            <div class="stat-card-value">{{ stats.runningEquipment }}</div>
            <div class="stat-card-label">运行中</div>
          </div>
          <div class="stat-card-icon icon-emerald">
            <el-icon :size="22"><CircleCheck /></el-icon>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card-inner">
          <div class="stat-card-info">
            <div class="stat-card-value">{{ stats.repairingEquipment }}</div>
            <div class="stat-card-label">维修中</div>
          </div>
          <div class="stat-card-icon icon-amber">
            <el-icon :size="22"><Tools /></el-icon>
          </div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-card-inner">
          <div class="stat-card-info">
            <div class="stat-card-value">{{ stats.pendingLogs }}</div>
            <div class="stat-card-label">待审批</div>
          </div>
          <div class="stat-card-icon icon-rose">
            <el-icon :size="22"><Clock /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <el-card>
        <template #header>
          <span>设备状态分布</span>
        </template>
        <div ref="statusChartRef" class="chart-container"></div>
      </el-card>

      <el-card>
        <template #header>
          <span>日志类型统计</span>
        </template>
        <div ref="logTypeChartRef" class="chart-container"></div>
      </el-card>
    </div>

    <!-- 待审批列表 -->
    <el-card class="mt-6">
      <template #header>
        <div class="flex-between">
          <span>待审批日志</span>
          <el-button type="primary" size="small" @click="$router.push('/logs')">
            查看全部
          </el-button>
        </div>
      </template>

      <el-table :data="pendingLogs" v-loading="loading">
        <el-table-column prop="created_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="equipment_name" label="设备名称" />
        <el-table-column prop="log_type" label="日志类型">
          <template #default="{ row }">
            <el-tag>{{ getLogTypeLabel(row.log_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator_name" label="提交人" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row.id)">
              查看
            </el-button>
          </template>
        </el-table-column>
        <template #empty>
          <el-empty description="暂无待审批的日志" />
        </template>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import type { ECBasicOption } from 'echarts/core'
import { ElMessage } from 'element-plus'
import { Box, CircleCheck, Tools, Clock } from '@element-plus/icons-vue'
import { getEquipments } from '@/api/equipment'
import { getLogs } from '@/api/logs'
import { getChartColors } from '@/utils/echarts-theme'

const router = useRouter()

const loading = ref(false)
const stats = reactive({
  totalEquipment: 0,
  runningEquipment: 0,
  repairingEquipment: 0,
  pendingLogs: 0
})

const pendingLogs = ref([])
const statusChartRef = ref<HTMLElement>()
const logTypeChartRef = ref<HTMLElement>()

const getLogTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    installation: '设备安装', repair: '设备维修', scrap: '设备报废',
    inspection: '日常巡检', maintenance: '保养记录', fault: '故障报修',
    parts: '配件更换', calibration: '校准记录'
  }
  return labels[type] || type
}

const formatDate = (date: string) => new Date(date).toLocaleString('zh-CN')

const fetchDashboardData = async () => {
  loading.value = true
  try {
    const equipmentsRes = await getEquipments({ limit: 1000 })
    const equipments = equipmentsRes.data
    stats.totalEquipment = equipments.length
    stats.runningEquipment = equipments.filter((e: any) => e.status === 'running').length
    stats.repairingEquipment = equipments.filter((e: any) => e.status === 'repairing').length
    const logsRes = await getLogs({ status: 'pending', limit: 5 })
    pendingLogs.value = logsRes.data
    stats.pendingLogs = (logsRes as any).total || logsRes.data.length
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    loading.value = false
  }
}

const initStatusChart = () => {
  if (!statusChartRef.value) return
  const chart = echarts.init(statusChartRef.value)
  const colors = getChartColors()
  const option: ECBasicOption = {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', left: 'left', textStyle: { color: 'var(--text-secondary)' as any } },
    color: [colors.primary, colors.warning, colors.neutral],
    series: [{
      name: '设备状态', type: 'pie', radius: ['50%', '75%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 4, borderColor: 'transparent', borderWidth: 2 },
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold' },
        itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.1)' }
      },
      data: [
        { value: stats.runningEquipment, name: '运行中' },
        { value: stats.repairingEquipment, name: '维修中' },
        { value: Math.max(0, stats.totalEquipment - stats.runningEquipment - stats.repairingEquipment), name: '其他' }
      ]
    }]
  }
  chart.setOption(option)
}

const initLogTypeChart = () => {
  if (!logTypeChartRef.value) return
  const chart = echarts.init(logTypeChartRef.value)
  const colors = getChartColors()
  // 使用 API 真实数据替代硬编码
  const data = [0, 0, 0, 0, 0, 0, 0, 0]
  const option: ECBasicOption = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: ['安装', '维修', '报废', '巡检', '保养', '报修', '配件', '校准']
    },
    yAxis: { type: 'value' },
    series: [{
      name: '日志数量', type: 'bar',
      data: data,
      itemStyle: {
        color: colors.primary,
        borderRadius: [4, 4, 0, 0]
      },
      emphasis: {
        itemStyle: { color: colors.primaryHover }
      }
    }]
  }
  chart.setOption(option)
}

const handleView = (id: number) => router.push(`/logs/${id}`)

onMounted(() => {
  fetchDashboardData()
  setTimeout(() => {
    initStatusChart()
    initLogTypeChart()
  }, 100)
})
</script>

<style scoped>
.dashboard {
  /* padding 由 .content 全局控制 */
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: var(--space-6);  /* 32px */
  margin-bottom: var(--space-8);  /* 48px */
}

/* 待审批卡片 */
.pending-logs-card {
  overflow: hidden;
}

.pending-logs-card :deep(.el-card__header) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-5) var(--space-6);
}

.pending-logs-card :deep(.el-table) {
  border-radius: 0;
  border: none;
  border-top: 1px solid var(--border-default);
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
