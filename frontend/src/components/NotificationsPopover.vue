<template>
  <el-popover
    :width="400"
    trigger="click"
    :show-after="200"
    popper-class="notification-popover"
  >
    <template #reference>
      <div class="notification-icon">
        <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99">
          <el-button :icon="Bell" circle />
        </el-badge>
      </div>
    </template>

    <template #default>
      <div class="notification-container">
        <div class="notification-header">
          <span class="title">通知中心</span>
          <el-button
            v-if="unreadCount > 0"
            type="primary"
            link
            size="small"
            @click="handleMarkAllRead"
          >
            全部已读
          </el-button>
        </div>

        <div v-loading="loading" class="notification-list">
          <el-empty v-if="notifications.length === 0" description="暂无通知" :image-size="80" />

          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="notification-item"
            :class="{ unread: !notification.is_read }"
            @click="handleNotificationClick(notification)"
          >
            <div class="notification-icon-wrapper">
              <el-icon :class="getNotificationIcon(notification.type)">
                <component :is="getNotificationIcon(notification.type)" />
              </el-icon>
            </div>
            <div class="notification-content">
              <div class="notification-title">{{ notification.title }}</div>
              <div class="notification-text">{{ notification.content }}</div>
              <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
            </div>
            <el-button
              v-if="!notification.is_read"
              type="primary"
              link
              size="small"
              class="mark-read-btn"
              @click.stop="handleMarkRead(notification.id)"
            >
              标为已读
            </el-button>
          </div>
        </div>

        <div class="notification-footer">
          <el-button type="primary" link @click="$router.push('/notifications')">
            查看全部通知
          </el-button>
        </div>
      </div>
    </template>
  </el-popover>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Bell, BellFilled, Warning, Calendar, Tools } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import {
  getNotifications,
  getUnreadCount,
  markNotificationRead,
  markAllRead
} from '@/api'

const router = useRouter()
const notifications = ref<any[]>([])
const unreadCount = ref(0)
const loading = ref(false)
let refreshInterval: any = null

const fetchNotifications = async () => {
  try {
    const res = await getNotifications({ limit: 10 })
    notifications.value = res.data
  } catch (error) {
    console.error('获取通知失败:', error)
  }
}

const fetchUnreadCount = async () => {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.data.count
  } catch (error) {
    console.error('获取未读数量失败:', error)
  }
}

const loadNotifications = async () => {
  loading.value = true
  try {
    await Promise.all([fetchNotifications(), fetchUnreadCount()])
  } finally {
    loading.value = false
  }
}

const handleMarkRead = async (id: number) => {
  try {
    await markNotificationRead(id)
    ElMessage.success('已标为已读')
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.is_read = true
    }
    await fetchUnreadCount()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleMarkAllRead = async () => {
  try {
    await markAllRead()
    ElMessage.success('已全部标为已读')
    notifications.value.forEach(n => n.is_read = true)
    unreadCount.value = 0
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const handleNotificationClick = (notification: any) => {
  if (!notification.is_read) {
    handleMarkRead(notification.id)
  }
  if (notification.equipment_id) {
    router.push(`/equipment/${notification.equipment_id}`)
  }
}

const getNotificationIcon = (type: string) => {
  const iconMap: Record<string, string> = {
    maintenance: 'Tools',
    lifecycle: 'Warning',
    calibration: 'Calendar'
  }
  return iconMap[type] || 'BellFilled'
}

const formatTime = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`

  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadNotifications()
  // 每30秒刷新一次
  refreshInterval = setInterval(loadNotifications, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.notification-container {
  max-height: 500px;
  display: flex;
  flex-direction: column;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 8px;
}

.notification-header .title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s;
  border-bottom: 1px solid #f5f7fa;
  position: relative;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.unread {
  background-color: #f0f9ff;
}

.notification-item.unread::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background-color: #409eff;
}

.notification-icon-wrapper {
  margin-right: 12px;
  font-size: 20px;
  color: #409eff;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
}

.notification-text {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

.mark-read-btn {
  margin-left: 8px;
  flex-shrink: 0;
}

.notification-footer {
  padding: 12px 16px;
  border-top: 1px solid #e4e7ed;
  text-align: center;
}
</style>
