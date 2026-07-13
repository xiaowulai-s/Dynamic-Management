<template>
  <div class="notification-list" v-loading="loading">
    <div v-if="notifications.length === 0" class="empty-state">
      <el-empty description="暂无通知" />
    </div>

    <div
      v-for="notification in notifications"
      :key="notification.id"
      class="notification-item"
      :class="{ unread: !notification.is_read }"
      @click="handleClick(notification)"
    >
      <div class="notification-icon">
        <el-icon :color="getTypeColor(notification.type)">
          <component :is="getTypeIcon(notification.type)" />
        </el-icon>
      </div>

      <div class="notification-content">
        <div class="notification-header">
          <span class="notification-title">{{ notification.title }}</span>
          <el-tag
            v-if="notification.type"
            :type="getTypeTagType(notification.type)"
            size="small"
          >
            {{ getTypeLabel(notification.type) }}
          </el-tag>
        </div>

        <div class="notification-text">{{ notification.content }}</div>

        <div class="notification-meta">
          <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
          <span v-if="notification.equipment" class="notification-equipment">
            {{ notification.equipment.name }}
          </span>
        </div>
      </div>

      <div class="notification-actions">
        <el-button
          v-if="!notification.is_read"
          type="primary"
          text
          size="small"
          @click.stop="handleMarkRead(notification.id)"
        >
          标为已读
        </el-button>
        <el-button
          type="danger"
          text
          size="small"
          @click.stop="handleDelete(notification.id)"
        >
          删除
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { Bell, Tools, Warning, Calender, Reading, Document } from '@element-plus/icons-vue'

interface Notification {
  id: number
  title: string
  content: string
  type?: string
  is_read: boolean
  equipment?: {
    name: string
  }
  created_at: string
}

interface Props {
  notifications: Notification[]
  loading: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  read: [id: number]
  delete: [id: number]
  refresh: []
}>()

const getTypeIcon = (type?: string) => {
  const icons: Record<string, any> = {
    maintenance: Tools,
    lifecycle: Warning,
    calibration: Calender,
    system: Reading
  }
  return icons[type || ''] || Bell
}

const getTypeColor = (type?: string) => {
  const colors: Record<string, string> = {
    maintenance: '#F59E0B',
    lifecycle: '#EF4444',
    calibration: '#3B82F6',
    system: '#64748B'
  }
  return colors[type || ''] || '#64748B'
}

const getTypeTagType = (type?: string) => {
  const types: Record<string, string> = {
    maintenance: 'warning',
    lifecycle: 'danger',
    calibration: 'primary',
    system: 'info'
  }
  return types[type || ''] || 'info'
}

const getTypeLabel = (type?: string) => {
  const labels: Record<string, string> = {
    maintenance: '保养提醒',
    lifecycle: '寿命预警',
    calibration: '校准提醒',
    system: '系统通知'
  }
  return labels[type || ''] || '其他'
}

const formatTime = (dateStr: string): string => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)} 分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)} 小时前`
  } else {
    return date.toLocaleString('zh-CN')
  }
}

const handleClick = (notification: any) => {
  // 点击通知跳转到相关设备或日志
  if (notification.equipment_id) {
    window.location.href = `/equipment?id=${notification.equipment_id}`
  }
}

const handleMarkRead = async (id: number) => {
  emit('read', id)
}

const handleDelete = (id: number) => {
  emit('delete', id)
}
</script>

<style scoped>
.notification-list {
  min-height: 200px;
}

.empty-state {
  padding: var(--space-8) 0;
}

.notification-item {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-5);
  border-bottom: 1px solid var(--color-neutral-100);
  cursor: pointer;
  transition: background-color var(--transition-fast);
}

.notification-item:hover {
  background-color: var(--color-neutral-50);
}

.notification-item.unread {
  background-color: var(--color-primary-50);
}

.notification-item.unread:hover {
  background-color: var(--color-primary-100);
}

.notification-icon {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-neutral-100);
  border-radius: var(--radius-full);
}

.notification-icon .el-icon {
  font-size: 1.25rem;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}

.notification-title {
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  font-size: var(--text-base);
}

.notification-text {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-2);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-meta {
  display: flex;
  gap: var(--space-4);
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.notification-time {
  flex-shrink: 0;
}

.notification-equipment {
  flex-shrink: 0;
}

.notification-actions {
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  opacity: 0;
  transition: opacity var(--transition-fast);
}

.notification-item:hover .notification-actions {
  opacity: 1;
}
</style>
