<template>
  <div class="el-page">
    <div class="page-header">
      <h2>{{ equipName }} — 日志时间线</h2>
      <n-space>
        <n-date-picker v-model:formatted-value="dateRange[0]" type="date" value-format="yyyy-MM-dd" placeholder="开始日期" style="width:140px" @update:value="fetchLogs" />
        <span style="color:var(--text-muted)">至</span>
        <n-date-picker v-model:formatted-value="dateRange[1]" type="date" value-format="yyyy-MM-dd" placeholder="结束日期" style="width:140px" @update:value="fetchLogs" />
        <n-button text @click="$router.back()">返回设备列表</n-button>
      </n-space>
    </div>

    <n-spin :show="loading">
      <n-empty v-if="!logs.length" description="该设备暂无日志记录" />
      <div v-else class="timeline">
        <div v-for="log in logs" :key="log.id" class="tl-item">
          <div class="tl-dot" :class="dotClass(log.log_type)"></div>
          <div class="tl-card">
            <div class="tl-card-header">
              <n-tag :type="tagType(log.log_type)" size="small">{{ typeLabels[log.log_type] || log.log_type }}</n-tag>
              <n-tag :type="log.status==='approved'?'success':log.status==='rejected'?'error':'warning'" size="small">{{ statusLabels[log.status] || log.status }}</n-tag>
              <span class="tl-time">{{ formatTime(log.created_at) }}</span>
            </div>
            <div class="tl-card-body">
              <!-- 基本信息 -->
              <div class="tl-row"><span class="tl-label">设备编号</span>{{ log.equipment_code || '-' }}</div>
              <div class="tl-row"><span class="tl-label">操作人</span>{{ log.operator_name || '-' }}</div>
              <!-- 动态字段 -->
              <template v-for="field in getDynamicFields(log)" :key="field.key">
                <div class="tl-row"><span class="tl-label">{{ field.label }}</span>{{ field.value }}</div>
              </template>
              <div class="tl-row" style="margin-top:4px"><span class="tl-label">描述</span>{{ log.description || '-' }}</div>

              <!-- 审批信息 -->
              <div v-if="log.status==='approved'||log.status==='rejected'" class="tl-approval">
                <div style="font-weight:600;margin-bottom:4px">审批记录</div>
                <div class="tl-row"><span class="tl-label">审批人</span>{{ log.approved_by_name || '-' }}</div>
                <div class="tl-row"><span class="tl-label">审批时间</span>{{ formatTime(log.approved_at) }}</div>
                <div class="tl-row"><span class="tl-label">审批结果</span>
                  <n-tag :type="log.status==='approved'?'success':'error'" size="tiny">{{ log.status==='approved'?'通过':'驳回' }}</n-tag>
                </div>
                <div v-if="log.rejection_reason" class="tl-row">
                  <span class="tl-label">驳回原因</span>
                  <span style="color:var(--color-error)">{{ log.rejection_reason }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { NTag, NButton, NSpin, NEmpty, NDatePicker, NSpace } from 'naive-ui'
import { getLogs } from '@/api/logs'

const route = useRoute()
const equipId = Number(route.params.id)
const equipName = ref('')
const logs = ref<any[]>([])
const loading = ref(true)
const dateRange = ref<[string|null,string|null]>([null,null])

const typeLabels: Record<string,string> = { installation:'设备安装', repair:'设备维修', scrap:'设备报废', inspection:'日常巡检', maintenance:'保养记录', fault:'故障报修', parts:'配件更换', calibration:'校准记录' }
const statusLabels: Record<string,string> = { pending:'待审批', approved:'已通过', rejected:'已驳回' }
const tagType = (t:string) => ({installation:'info',repair:'warning',scrap:'error',inspection:'success',maintenance:'success',fault:'error',parts:'warning',calibration:'info'} as any)[t]||'default'
const dotClass = (t:string) => 'dot-' + (t||'default')
const formatTime = (t:string) => t ? new Date(t).toLocaleString('zh-CN') : '-'

// 动态字段定义
const fieldDefs: Record<string, {key:string;label:string}[]> = {
  installation: [{key:'installation_date',label:'安装日期'},{key:'installer',label:'安装人员'},{key:'location',label:'安装位置'},{key:'acceptance_status',label:'验收状态'}],
  repair: [{key:'repair_date',label:'维修日期'},{key:'fault_description',label:'故障描述'},{key:'solution',label:'解决方案'},{key:'cost',label:'费用(元)'},{key:'repair_time',label:'工时(小时)'}],
  scrap: [{key:'scrap_date',label:'报废日期'},{key:'scrap_reason',label:'报废原因'},{key:'residual_value',label:'残值'}],
  inspection: [{key:'inspection_date',label:'巡检日期'},{key:'inspector',label:'巡检人员'},{key:'result',label:'结果'}],
  maintenance: [{key:'maintenance_date',label:'保养日期'},{key:'next_maintenance_date',label:'下次保养'}],
  fault: [{key:'fault_date',label:'故障日期'},{key:'fault_level',label:'故障等级'},{key:'reporter',label:'报告人'},{key:'fault_description',label:'故障描述'},{key:'handle_status',label:'处理状态'}],
  parts: [{key:'replacement_date',label:'更换日期'},{key:'parts_name',label:'配件名称'},{key:'parts_code',label:'配件编号'},{key:'quantity',label:'数量'},{key:'cost',label:'费用(元)'}],
  calibration: [{key:'calibration_date',label:'校准日期'},{key:'calibration_org',label:'校准机构'},{key:'calibration_result',label:'结果'},{key:'next_calibration_date',label:'下次校准'}]
}

const getDynamicFields = (log: any) => {
  const defs = fieldDefs[log.log_type] || []
  return defs.filter(f => log[f.key] != null && log[f.key] !== '').map(f => ({
    key: f.key,
    label: f.label,
    value: typeof log[f.key] === 'number' ? String(log[f.key]) : (log[f.key] || '-')
  }))
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const params: any = { equipment_id: equipId, limit: 500 }
    if (dateRange.value[0]) params.start_date = dateRange.value[0]
    if (dateRange.value[1]) params.end_date = dateRange.value[1]
    const r = await getLogs(params)
    const raw = r.data || {}
    const list = Array.isArray(raw) ? raw : (raw.data || [])
    logs.value = list.sort((a:any,b:any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    if (list.length) equipName.value = list[0].equipment_name || `设备 #${equipId}`
  } catch(e) { /* empty */ }
  finally { loading.value = false }
}

onMounted(() => fetchLogs())
</script>

<style scoped>
.el-page { /* padding from dm-content */ }
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; }
.page-header h2 { margin:0; font-size:22px; }
.timeline { position:relative; padding-left:28px; }
.timeline::before { content:''; position:absolute; left:8px; top:4px; bottom:0; width:2px; background:var(--border-default); }
.tl-item { position:relative; margin-bottom:20px; }
.tl-dot { position:absolute; left:-24px; top:14px; width:14px; height:14px; border-radius:50%; border:2px solid var(--surface-card); z-index:1; }
.dot-installation,.dot-calibration { background:#6366F1; }
.dot-repair,.dot-parts { background:#F59E0B; }
.dot-scrap,.dot-fault { background:#EF4444; }
.dot-inspection,.dot-maintenance { background:#10B981; }
.dot-default { background:#94A3B8; }
.tl-card { background:var(--surface-card); border:1px solid var(--border-default); border-radius:10px; overflow:hidden; }
.tl-card-header { display:flex; align-items:center; gap:8px; padding:10px 14px; background:var(--surface-subtle); border-bottom:1px solid var(--border-default); }
.tl-time { margin-left:auto; font-size:12px; color:var(--text-muted); }
.tl-card-body { padding:12px 14px; }
.tl-row { font-size:13px; line-height:1.7; }
.tl-label { font-weight:600; margin-right:8px; color:var(--text-tertiary); min-width:60px; display:inline-block; }
.tl-approval { margin-top:8px; padding-top:8px; border-top:1px solid var(--border-default); }
</style>
