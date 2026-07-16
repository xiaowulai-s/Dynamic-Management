<template>
  <div class="al-page">
    <div class="page-header"><h2>操作审计</h2></div>
    <n-data-table :columns="cols" :data="items" :loading="loading" striped size="small" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { NDataTable } from 'naive-ui'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const userStore = useUserStore()
const loading = ref(false)
const items = ref<any[]>([])
const base = import.meta.env.VITE_API_URL || '/api'

const actionLabels: Record<string, string> = {
  create: '创建', update: '修改', delete: '删除',
  login: '登录', logout: '退出', approve: '审批', reject: '驳回'
}

const cols = [
  { title: '时间', key: 'created_at', width: 170, render: (r: any) => new Date(r.created_at).toLocaleString('zh-CN') },
  { title: '用户', key: 'username', width: 120 },
  { title: '操作', key: 'action', width: 100, render: (r: any) => actionLabels[r.action] || r.action },
  { title: '目标', key: 'target', width: 120 },
  { title: '详情', key: 'details', ellipsis: { tooltip: true } }
]

onMounted(async () => {
  loading.value = true
  try {
    const r = await axios.get(base + '/audit/?limit=200', {
      headers: { Authorization: 'Bearer ' + userStore.token }
    })
    items.value = r.data
  } catch { /* empty */ }
  finally { loading.value = false }
})
</script>

<style scoped>
.al-page { /* padding */ }
.page-header { margin-bottom: 24px }
.page-header h2 { margin: 0; font-size: 24px; font-weight: 600 }
</style>
