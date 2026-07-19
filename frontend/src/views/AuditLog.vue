<template>
  <div class="al-page">
    <div class="page-header"><h2>操作审计</h2></div>
    <el-card shadow="never">
      <el-table :data="items" v-loading="loading" stripe size="small">
        <el-table-column label="时间" width="170" align="center">
          <template #default="{row}">{{ new Date(row.created_at).toLocaleString('zh-CN') }}</template>
        </el-table-column>
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column label="操作" width="100" align="center">
          <template #default="{row}">{{ actionLabels[row.action] || row.action }}</template>
        </el-table-column>
        <el-table-column prop="target" label="目标" width="120" />
        <el-table-column prop="details" label="详情" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getAuditLogs } from '@/api'

const userStore = useUserStore()
const loading = ref(false)
const items = ref<any[]>([])

const actionLabels: Record<string, string> = {
  create: '创建', update: '修改', delete: '删除',
  login: '登录', logout: '退出', approve: '审批', reject: '驳回'
}

onMounted(async () => {
  loading.value = true
  try {
    const res = await getAuditLogs({ limit: 200 })
    items.value = res.data
  } catch (error) {
    console.error('获取审计日志失败:', error)
    ElMessage.error('获取审计日志失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.al-page { /* padding */ }
.page-header { margin-bottom: 24px }
.page-header h2 { margin: 0; font-size: 24px; font-weight: 600 }
</style>
