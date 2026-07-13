// ============================================================
// 主题管理 Composable v3.0
// 支持亮色/暗黑主题切换，持久化到 localStorage
// ============================================================

import { ref, watch, onMounted } from 'vue'

type Theme = 'light' | 'dark'

const theme = ref<Theme>('light')

// 检测系统主题偏好
const getSystemTheme = (): Theme => {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

// 从 localStorage 读取主题
const getStoredTheme = (): Theme => {
  if (typeof window === 'undefined') return 'light'
  const stored = localStorage.getItem('theme') as Theme | null
  return stored || getSystemTheme()
}

// 应用主题到 DOM
const applyTheme = (newTheme: Theme) => {
  if (typeof document === 'undefined') return

  const root = document.documentElement

  if (newTheme === 'dark') {
    root.setAttribute('data-theme', 'dark')
  } else {
    root.removeAttribute('data-theme')
  }

  // 更新 meta 标签（用于移动端浏览器UI）
  const metaThemeColor = document.querySelector('meta[name="theme-color"]')
  if (metaThemeColor) {
    metaThemeColor.setAttribute('content', newTheme === 'dark' ? '#1A1A2E' : '#FFFFFF')
  }
}

// 切换主题
const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

// 设置主题
const setTheme = (newTheme: Theme) => {
  theme.value = newTheme
}

// 监听系统主题变化
if (typeof window !== 'undefined') {
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    // 如果用户没有手动设置过主题，则跟随系统
    if (!localStorage.getItem('theme')) {
      theme.value = e.matches ? 'dark' : 'light'
    }
  })
}

// 监听主题变化并持久化
watch(theme, (newTheme) => {
  applyTheme(newTheme)
  localStorage.setItem('theme', newTheme)
}, { immediate: true })

// 初始化
onMounted(() => {
  const storedTheme = getStoredTheme()
  theme.value = storedTheme
  applyTheme(storedTheme)
})

export function useTheme() {
  return {
    theme,
    toggleTheme,
    setTheme,
    isDark: theme.value === 'dark'
  }
}
