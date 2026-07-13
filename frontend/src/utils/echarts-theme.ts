/**
 * ECharts 动态主题工具
 * 从 CSS 变量读取颜色，支持亮色/暗黑模式自动跟随
 */
export function getChartColors() {
  const cssVar = (name: string) =>
    getComputedStyle(document.documentElement).getPropertyValue(name).trim() || undefined

  return {
    primary: cssVar('--color-primary-500'),
    primaryHover: cssVar('--color-primary-400'),
    success: cssVar('--color-success-500'),
    warning: cssVar('--color-warning-500'),
    danger: cssVar('--color-danger-500'),
    accent: cssVar('--color-accent-500'),
    info: cssVar('--color-info-500'),
    neutral: cssVar('--color-neutral-400'),
    textPrimary: cssVar('--text-primary'),
    textSecondary: cssVar('--text-secondary'),
    surfaceCard: cssVar('--surface-card'),
    surfaceElevated: cssVar('--surface-elevated'),
    borderDefault: cssVar('--border-default'),
  }
}

/**
 * 获取 ECharts 完整主题配置
 */
export function getEChartsTheme() {
  const colors = getChartColors()

  return {
    color: [
      colors.primary,
      colors.success,
      colors.warning,
      colors.danger,
      colors.accent,
      colors.info,
    ],
    backgroundColor: 'transparent',
    textStyle: { color: colors.textSecondary },
    title: { textStyle: { color: colors.textPrimary } },
    legend: { textStyle: { color: colors.textSecondary } },
    tooltip: {
      backgroundColor: colors.surfaceElevated,
      borderColor: colors.borderDefault,
      textStyle: { color: colors.textPrimary },
      axisPointer: {
        lineStyle: { color: colors.borderDefault },
        crossStyle: { color: colors.borderDefault },
      },
    },
    categoryAxis: {
      axisLine: { lineStyle: { color: colors.borderDefault } },
      axisTick: { lineStyle: { color: colors.borderDefault } },
      axisLabel: { color: colors.textSecondary },
      splitLine: { show: false },
    },
    valueAxis: {
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: colors.textSecondary },
      splitLine: { lineStyle: { color: colors.borderDefault, type: 'dashed' as const } },
    },
  }
}
