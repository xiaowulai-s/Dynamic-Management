<template>
  <div class="notifications-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">通知中心</span>
          <el-button
            v-if="unreadCount > 0"
            type="primary"
            text
            @click="handleMarkAllRead"
          >
            全部标为已读
          </el-button>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="全部通知" name="all">
          <NotificationList
            :notifications="notifications"
            :loading="loading"
            @read="handleMarkRead"
            @delete="handleDelete"
            @refresh="loadNotifications"
          />
        </el-tab-pane>

        <el-tab-pane label="未读通知" name="unread">
          <NotificationList
            :notifications="unreadNotifications"
            :loading="loading"
            @read="handleMarkRead"
            @delete="handleDelete"
            @refresh="loadNotifications"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getNotifications, markNotificationRead, markAllNotificationsRead, deleteNotification } from '@/api'
import NotificationList from '@/components/NotificationList.vue'

const userStore = useUserStore()
const loading = ref(false)
const notifications = ref<any[]>([])
const activeTab = ref('all')

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.is_read).length
})

const unreadNotifications = computed(() => {
  return notifications.value.filter(n => !n.is_read)
})

const loadNotifications = async () => {
  try {
    loading.value = true
    const res = await getNotifications()
    notifications.value = res.data
  } catch (error) {
    ElMessage.error('加载通知失败')
  } finally {
    loading.value = false
  }
}

const handleMarkRead = async (id: number) => {
  try {
    await markNotificationRead(id)
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.is_read = true
    }
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleMarkAllRead = async () => {
  try {
    await markAllNotificationsRead()
    notifications.value.forEach(n => n.is_read = true)
    ElMessage.success('已全部标为已读')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (id: number) => {
  try {
    await ElMessageBox.confirm('确认删除此通知？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteNotification(id)
    notifications.value = notifications.value.filter(n => n.id !== id)
    ElMessage.success('删除成功')
  } catch (error) {
    // 用户取消
  }
}

onMounted(() => {
  loadNotifications()
})
</script>

<style scoped>
.notifications-container {
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
</style>
