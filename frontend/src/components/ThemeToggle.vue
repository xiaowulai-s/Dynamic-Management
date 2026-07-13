<!-- ============================================================
     主题切换按钮组件 v3.0
     支持亮色/暗黑主题切换，带动画效果
     ============================================================ -->

<template>
  <el-tooltip
    :content="isDark ? '切换到亮色模式' : '切换到暗黑模式'"
    placement="bottom"
  >
    <el-button
      class="theme-toggle-btn"
      :icon="isDark ? 'Sunny' : 'Moon'"
      circle
      @click="handleToggle"
    />
  </el-tooltip>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTheme } from '@/composables/useTheme'
import { Sunny, Moon } from '@element-plus/icons-vue'

const { theme, toggleTheme, isDark } = useTheme()

const handleToggle = () => {
  toggleTheme()
}
</script>

<style scoped>
.theme-toggle-btn {
  border: none;
  background: transparent;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  border-radius: var(--radius-full);
}

.theme-toggle-btn:hover {
  color: var(--color-primary-600);
  background: var(--color-primary-50);
  transform: rotate(180deg) scale(1.1);
}

.theme-toggle-btn:active {
  transform: rotate(180deg) scale(0.95);
}

/* 图标动画 */
.theme-toggle-btn :deep(.el-icon) {
  transition: transform var(--duration-normal) var(--ease-bounce);
}

.theme-toggle-btn:hover :deep(.el-icon) {
  transform: rotate(360deg);
}
</style>
