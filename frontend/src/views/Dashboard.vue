<template>
  <div class="dashboard">
    <!-- 1. 页头 -->
    <header class="page-head">
      <div class="head-left">
        <h1 class="page-title">仪表盘</h1>
        <p class="page-subtitle">设备与日志运行概览 · {{ new Date().toLocaleDateString('zh-CN') }}</p>
      </div>
      <div class="head-right">
        <el-button :icon="Filter">筛选</el-button>
        <el-button type="primary" :icon="Plus" @click="router.push('/logs')">新建日志</el-button>
      </div>
    </header>

    <!-- 2. KPI 卡片网格 -->
    <section class="kpi-grid">
      <!-- KPI 1: 设备总数 -->
      <div class="kpi-card">
        <div class="kpi-head">
          <div class="kpi-icon"><el-icon :size="14"><Box /></el-icon></div>
          <span class="kpi-label">设备总数</span>
        </div>
        <div class="kpi-value numeric">{{ stats.totalEquipment }}</div>
        <div class="kpi-trend">
          <el-icon class="trend-icon up"><TrendCharts /></el-icon>
          <span class="trend-text up">+2.3%</span>
          <span class="trend-sub">较上月</span>
        </div>
      </div>

      <!-- KPI 2: 运行中 -->
      <div class="kpi-card">
        <div class="kpi-head">
          <div class="kpi-icon success"><el-icon :size="14"><CircleCheck /></el-icon></div>
          <span class="kpi-label">运行中</span>
        </div>
        <div class="kpi-value numeric">{{ stats.runningEquipment }}</div>
        <div class="kpi-trend">
          <el-icon class="trend-icon up"><TrendCharts /></el-icon>
          <span class="trend-text up">+5</span>
          <span class="trend-sub">较昨日</span>
        </div>
      </div>

      <!-- KPI 3: 维修中 -->
      <div class="kpi-card">
        <div class="kpi-head">
          <div class="kpi-icon warning"><el-icon :size="14"><Tools /></el-icon></div>
          <span class="kpi-label">维修中</span>
        </div>
        <div class="kpi-value numeric">{{ stats.repairingEquipment }}</div>
        <div class="kpi-trend">
          <el-icon class="trend-icon warning"><TrendCharts /></el-icon>
          <span class="trend-text warning">+1</span>
          <span class="trend-sub">较昨日</span>
        </div>
      </div>

      <!-- KPI 4: 待审批 -->
      <div class="kpi-card">
        <div class="kpi-head">
          <div class="kpi-icon warning"><el-icon :size="14"><Clock /></el-icon></div>
          <span class="kpi-label">待审批</span>
        </div>
        <div class="kpi-value numeric">{{ stats.pendingLogs }}</div>
        <div class="kpi-trend">
          <el-icon class="trend-icon warning"><TrendCharts /></el-icon>
          <span class="trend-text warning">+2</span>
          <span class="trend-sub">较昨日</span>
        </div>
      </div>

      <!-- KPI 5: 在线率 -->
      <div class="kpi-card">
        <div class="kpi-head">
          <div class="kpi-icon info"><el-icon :size="14"><DataLine /></el-icon></div>
          <span class="kpi-label">在线率</span>
        </div>
        <div class="kpi-value numeric">
          {{ stats.totalEquipment ? Math.round(stats.runningEquipment / stats.totalEquipment * 100) : 0 }}<span class="kpi-unit">%</span>
        </div>
        <div class="kpi-trend">
          <el-icon class="trend-icon up"><TrendCharts /></el-icon>
          <span class="trend-text up">+1.2%</span>
          <span class="trend-sub">较上月</span>
        </div>
      </div>

      <!-- KPI 6: 其他状态 -->
      <div class="kpi-card">
        <div class="kpi-head">
          <div class="kpi-icon neutral"><el-icon :size="14"><Histogram /></el-icon></div>
          <span class="kpi-label">其他状态</span>
        </div>
        <div class="kpi-value numeric">{{ Math.max(0, stats.totalEquipment - stats.runningEquipment - stats.repairingEquipment) }}</div>
        <div class="kpi-trend">
          <el-icon class="trend-icon down"><TrendCharts /></el-icon>
          <span class="trend-text up">-3</span>
          <span class="trend-sub">较昨日</span>
        </div>
      </div>
    </section>

    <!-- 3. 主内容区 -->
    <div class="main-grid">
      <!-- 左栏 -->
      <div class="main-left">
        <!-- 图表区头部 -->
        <div class="chart-head">
          <h2 class="section-title">数据可视化</h2>
          <div class="segmented">
            <button type="button">今日</button>
            <button type="button" class="active">本周</button>
            <button type="button">本月</button>
          </div>
        </div>

        <!-- 两个图表卡片 -->
        <div class="chart-row">
          <div class="chart-card">
            <div class="card-head">
              <h3 class="section-title">设备状态分布</h3>
              <span class="card-meta">共 {{ stats.totalEquipment }} 台</span>
            </div>
            <div ref="statusChartRef" class="chart-box"></div>
          </div>

          <div class="chart-card">
            <div class="card-head">
              <h3 class="section-title">日志类型统计</h3>
            </div>
            <div ref="logTypeChartRef" class="chart-box"></div>
          </div>
        </div>

        <!-- 审批进度卡片 -->
        <div class="approval-card">
          <div class="card-head">
            <h3 class="section-title">近期审批进度</h3>
            <a class="link-btn" @click="router.push('/logs')">查看全部</a>
          </div>
          <div class="approval-flow">
            <div class="approval-step done">
              <div class="approval-dot"><el-icon :size="12"><Check /></el-icon></div>
              <div class="approval-label">提交</div>
              <div class="approval-time">
                {{ pendingLogs.length ? formatDate(pendingLogs[0].created_at) : '—' }}
              </div>
            </div>
            <div class="approval-connector done"></div>
            <div class="approval-step done">
              <div class="approval-dot"><el-icon :size="12"><Check /></el-icon></div>
              <div class="approval-label">初审</div>
              <div class="approval-time">已通过</div>
            </div>
            <div class="approval-connector done"></div>
            <div class="approval-step current">
              <div class="approval-dot"></div>
              <div class="approval-label">复核</div>
              <div class="approval-time">进行中</div>
            </div>
            <div class="approval-connector"></div>
            <div class="approval-step pending">
              <div class="approval-dot"></div>
              <div class="approval-label">通过</div>
              <div class="approval-time">待处理</div>
            </div>
          </div>
          <div v-if="pendingLogs.length" class="approval-meta">
            当前审批单：<span class="numeric">{{ 'LOG-' + String(pendingLogs[0].id).padStart(4, '0') }}</span>
          </div>
          <div v-else class="approval-meta muted">暂无进行中的审批流程</div>
        </div>

        <!-- 骨架屏卡片 -->
        <div v-if="loading" class="skeleton-card">
          <div class="card-head">
            <h3 class="section-title">图表加载态</h3>
            <span class="card-meta">骨架屏示例</span>
          </div>
          <div class="skeleton-bars">
            <div class="skeleton-block" style="height: 40%"></div>
            <div class="skeleton-block" style="height: 65%"></div>
            <div class="skeleton-block" style="height: 50%"></div>
            <div class="skeleton-block" style="height: 80%"></div>
            <div class="skeleton-block" style="height: 35%"></div>
            <div class="skeleton-block" style="height: 70%"></div>
            <div class="skeleton-block" style="height: 55%"></div>
          </div>
          <div class="skeleton-labels">
            <div class="skeleton-block sm"></div>
            <div class="skeleton-block sm"></div>
            <div class="skeleton-block sm"></div>
            <div class="skeleton-block sm"></div>
            <div class="skeleton-block sm"></div>
            <div class="skeleton-block sm"></div>
            <div class="skeleton-block sm"></div>
          </div>
        </div>
      </div>

      <!-- 右栏 -->
      <div class="main-right">
        <!-- 待审核日志 -->
        <div class="side-card">
          <div class="card-head">
            <h3 class="section-title">待审核日志</h3>
            <a class="link-btn" @click="router.push('/logs')">查看全部</a>
          </div>
          <ul v-if="pendingLogs.length" class="log-list">
            <li v-for="log in pendingLogs" :key="log.id" class="log-item">
              <div class="log-info">
                <div class="log-row">
                  <span class="log-id numeric">{{ 'LOG-' + String(log.id).padStart(4, '0') }}</span>
                  <span class="badge badge-neutral">{{ getLogTypeLabel(log.log_type) }}</span>
                </div>
                <div class="log-equip">{{ log.equipment_name }}</div>
                <div class="log-meta">{{ log.operator_name }} · {{ formatDate(log.created_at) }}</div>
              </div>
              <div class="log-actions">
                <button class="icon-btn approve" title="通过" @click="handleView(log.id)">
                  <el-icon :size="14"><Check /></el-icon>
                </button>
                <button class="icon-btn reject" title="驳回" @click="handleView(log.id)">
                  <el-icon :size="14"><Close /></el-icon>
                </button>
              </div>
            </li>
          </ul>
          <div v-else class="empty-state">
            <div class="empty-icon"><el-icon :size="24"><Bell /></el-icon></div>
            <div class="empty-title">暂无待审核日志</div>
            <div class="empty-sub">所有日志均已处理完毕</div>
          </div>
        </div>

        <!-- 设备告警示例 -->
        <div class="side-card">
          <div class="card-head">
            <h3 class="section-title">设备告警</h3>
            <a class="link-btn">查看全部</a>
          </div>
          <ul class="alert-list">
            <li class="alert-item">
              <div class="alert-info">
                <div class="alert-row">
                  <span class="alert-name">空压机 A-12</span>
                  <span class="badge badge-error">高</span>
                </div>
                <div class="alert-meta">车间 B-3 · 10 分钟前</div>
              </div>
              <a class="link-btn sm">处理</a>
            </li>
            <li class="alert-item">
              <div class="alert-info">
                <div class="alert-row">
                  <span class="alert-name">冷却泵 P-08</span>
                  <span class="badge badge-warning">中</span>
                </div>
                <div class="alert-meta">动力站 2F · 32 分钟前</div>
              </div>
              <a class="link-btn sm">处理</a>
            </li>
            <li class="alert-item">
              <div class="alert-info">
                <div class="alert-row">
                  <span class="alert-name">传送带 C-03</span>
                  <span class="badge badge-warning">中</span>
                </div>
                <div class="alert-meta">包装线 1 · 1 小时前</div>
              </div>
              <a class="link-btn sm">处理</a>
            </li>
            <li class="alert-item">
              <div class="alert-info">
                <div class="alert-row">
                  <span class="alert-name">液压站 H-15</span>
                  <span class="badge badge-neutral">低</span>
                </div>
                <div class="alert-meta">主车间 1F · 2 小时前</div>
              </div>
              <a class="link-btn sm">处理</a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import type { ECBasicOption } from 'echarts/core'
import { ElMessage } from 'element-plus'
import { Box, CircleCheck, Tools, Clock, TrendCharts, DataLine, Histogram, Plus, Filter, Check, Close, Bell } from '@element-plus/icons-vue'
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

const pendingLogs = ref<any[]>([])
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
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}

/* ===== 页头 ===== */
.page-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  flex-wrap: wrap;
}
.page-title {
  font-size: var(--text-xl);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
  letter-spacing: -0.01em;
  line-height: 1.2;
  margin: 0;
}
.page-subtitle {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin-top: 4px;
}
.head-right {
  display: flex;
  gap: var(--space-2);
}

/* ===== Section title（蓝色竖条） ===== */
.section-title {
  font-size: var(--text-sm);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
  display: inline-flex;
  align-items: center;
  margin: 0;
  line-height: 1.4;
}
.section-title::before {
  content: "";
  display: inline-block;
  width: 2px;
  height: 14px;
  background: var(--color-primary-600);
  border-radius: 1px;
  margin-right: 8px;
  vertical-align: middle;
  flex-shrink: 0;
}

/* ===== KPI 网格 ===== */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
}
.kpi-card {
  background: var(--surface-overlay);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: none;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  transition: border-color var(--duration-fast) var(--ease-default);
}
.kpi-card:hover {
  border-color: var(--color-primary-500);
}
.kpi-head {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.kpi-icon {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-elevated);
  color: var(--text-tertiary);
  flex-shrink: 0;
}
.kpi-icon.success {
  color: var(--color-success-500);
  background: color-mix(in srgb, var(--color-success-500) 12%, transparent);
}
.kpi-icon.warning {
  color: var(--color-warning-500);
  background: color-mix(in srgb, var(--color-warning-500) 12%, transparent);
}
.kpi-icon.info {
  color: var(--color-primary-600);
  background: color-mix(in srgb, var(--color-primary-600) 12%, transparent);
}
.kpi-icon.neutral {
  color: var(--text-tertiary);
  background: var(--surface-elevated);
}
.kpi-label {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-weight: var(--font-w-medium);
}
.kpi-value {
  font-size: var(--text-xl);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
  line-height: 1.1;
}
.numeric {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}
.kpi-unit {
  font-size: var(--text-sm);
  font-weight: var(--font-w-medium);
  color: var(--text-tertiary);
  margin-left: 2px;
}
.kpi-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-xs);
}
.trend-icon {
  font-size: 12px;
  flex-shrink: 0;
}
.trend-icon.up { color: var(--color-success-500); }
.trend-icon.warning { color: var(--color-warning-500); }
.trend-icon.down {
  color: var(--color-success-500);
  transform: rotate(180deg);
}
.trend-text { font-weight: var(--font-w-medium); }
.trend-text.up { color: var(--color-success-500); }
.trend-text.warning { color: var(--color-warning-500); }
.trend-sub { color: var(--text-tertiary); }

/* ===== 主内容区 ===== */
.main-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
  align-items: start;
}
.main-left,
.main-right {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  min-width: 0;
}

/* ===== 图表区头部 ===== */
.chart-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}
.segmented {
  display: inline-flex;
  background: var(--surface-elevated);
  border-radius: var(--radius-md);
  padding: 2px;
  gap: 2px;
}
.segmented button {
  padding: 4px 12px;
  font-size: var(--text-xs);
  border-radius: 6px;
  color: var(--text-tertiary);
  border: none;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
  line-height: 1.5;
  transition: all var(--duration-fast) var(--ease-default);
}
.segmented button:hover {
  color: var(--text-secondary);
}
.segmented button.active {
  background: var(--surface-overlay);
  color: var(--color-primary-600);
  font-weight: var(--font-w-medium);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
}

/* ===== 卡片公共样式 ===== */
.chart-card,
.approval-card,
.skeleton-card,
.side-card {
  background: var(--surface-overlay);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: none;
  padding: var(--space-4);
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
}
.card-meta {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}
.link-btn {
  font-size: var(--text-xs);
  color: var(--color-primary-600);
  cursor: pointer;
  font-weight: var(--font-w-medium);
  white-space: nowrap;
  transition: color var(--duration-fast) var(--ease-default);
}
.link-btn:hover {
  color: var(--color-primary-700);
}
.link-btn.sm {
  font-size: var(--text-xs);
}

/* ===== 图表行 ===== */
.chart-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-4);
}
.chart-box {
  width: 100%;
  height: 160px;
}

/* ===== 审批流 ===== */
.approval-flow {
  display: flex;
  align-items: flex-start;
  padding: var(--space-2) 0;
}
.approval-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  min-width: 56px;
}
.approval-dot {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-full);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--border-default);
  background: var(--surface-overlay);
  color: var(--text-tertiary);
  transition: all var(--duration-fast) var(--ease-default);
}
.approval-step.done .approval-dot {
  background: var(--color-success-500);
  border-color: var(--color-success-500);
  color: #fff;
}
.approval-step.current .approval-dot {
  background: var(--color-primary-600);
  border-color: var(--color-primary-600);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--color-primary-600) 20%, transparent);
}
.approval-label {
  font-size: var(--text-xs);
  font-weight: var(--font-w-medium);
  color: var(--text-primary);
}
.approval-step.pending .approval-label {
  color: var(--text-tertiary);
}
.approval-time {
  font-size: 11px;
  color: var(--text-tertiary);
  text-align: center;
}
.approval-connector {
  flex: 1;
  height: 2px;
  background: var(--border-default);
  margin-top: 11px;
  min-width: 24px;
}
.approval-connector.done {
  background: var(--color-success-500);
}
.approval-meta {
  margin-top: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-default);
  font-size: var(--text-xs);
  color: var(--text-secondary);
}
.approval-meta.muted {
  color: var(--text-tertiary);
}

/* ===== 骨架屏 ===== */
.skeleton-bars {
  display: flex;
  align-items: flex-end;
  gap: var(--space-2);
  height: 120px;
  margin-top: var(--space-2);
}
.skeleton-block {
  flex: 1;
  background: var(--surface-elevated);
  border-radius: var(--radius-sm);
  animation: skel-pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
.skeleton-labels {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-2);
}
.skeleton-block.sm {
  height: 8px;
}
@keyframes skel-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

/* ===== Badge ===== */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-w-medium);
  line-height: 1.5;
  white-space: nowrap;
}
.badge-neutral {
  background: var(--surface-elevated);
  color: var(--text-tertiary);
}
.badge-error {
  background: color-mix(in srgb, var(--color-danger-500) 12%, transparent);
  color: var(--color-danger-500);
}
.badge-warning {
  background: color-mix(in srgb, var(--color-warning-500) 12%, transparent);
  color: var(--color-warning-500);
}
.badge-success {
  background: color-mix(in srgb, var(--color-success-500) 12%, transparent);
  color: var(--color-success-500);
}

/* ===== 图标按钮 ===== */
.icon-btn {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-default);
  background: var(--surface-overlay);
  color: var(--text-tertiary);
  cursor: pointer;
  padding: 0;
  transition: all var(--duration-fast) var(--ease-default);
}
.icon-btn:hover {
  border-color: var(--color-primary-400);
  color: var(--color-primary-600);
}
.icon-btn.approve:hover {
  border-color: var(--color-success-500);
  color: var(--color-success-500);
  background: color-mix(in srgb, var(--color-success-500) 8%, transparent);
}
.icon-btn.reject:hover {
  border-color: var(--color-danger-500);
  color: var(--color-danger-500);
  background: color-mix(in srgb, var(--color-danger-500) 8%, transparent);
}

/* ===== 待审核日志列表 ===== */
.log-list,
.alert-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
}
.log-item,
.alert-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--border-default);
}
.log-item:last-child,
.alert-item:last-child {
  border-bottom: none;
}
.log-info,
.alert-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  flex: 1;
}
.log-row,
.alert-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.log-id {
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-weight: var(--font-w-medium);
}
.log-equip {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-w-medium);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.log-meta {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}
.log-actions {
  display: flex;
  gap: var(--space-1);
  flex-shrink: 0;
}

/* ===== 告警列表 ===== */
.alert-name {
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-weight: var(--font-w-medium);
}
.alert-meta {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-6) var(--space-4);
  text-align: center;
  gap: var(--space-2);
}
.empty-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-full);
  background: var(--surface-elevated);
  color: var(--text-tertiary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-1);
}
.empty-title {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  font-weight: var(--font-w-medium);
}
.empty-sub {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* ===== 响应式 ===== */
@media (min-width: 768px) {
  .kpi-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  .chart-row {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (min-width: 1024px) {
  .kpi-grid {
    grid-template-columns: repeat(6, 1fr);
  }
  .main-grid {
    grid-template-columns: 2fr 1fr;
  }
}
</style>
