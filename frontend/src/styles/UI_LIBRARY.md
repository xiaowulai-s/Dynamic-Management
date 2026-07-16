# UI 组件库 v4.0 — Industrial Precision

> **设计哲学**: Industrial Precision (工业精密感)
> **核心色**: Deep Navy (#6366F1) + Amber Gold (#F59E0B)
> **字体**: 系统字体 + 数据用等宽字体

---

## 1. 快速开始

### 1.1 引入样式

`frontend/src/main.ts` 已自动引入：

```ts
import './styles/index.css'
```

### 1.2 主题切换

```ts
// 设置主题
document.documentElement.setAttribute('data-theme', 'dark')  // 暗色
document.documentElement.setAttribute('data-theme', 'light') // 亮色
```

---

## 2. Design Tokens

### 2.1 颜色系统

| 语义 | 亮色值 | 暗色值 | 用途 |
|------|--------|--------|------|
| `--navy-500` | `#6366F1` | `#6366F1` | 主色 |
| `--navy-600` | `#4F46E5` | `#4F46E5` | 主色深 |
| `--amber-500` | `#F59E0B` | `#F59E0B` | 强调色 |
| `--status-success` | `#10B981` | `#10B981` | 成功/运行 |
| `--status-warning` | `#F59E0B` | `#F59E0B` | 警告/维修 |
| `--status-danger` | `#EF4444` | `#EF4444` | 危险/停机 |
| `--status-info` | `#6366F1` | `#6366F1` | 信息 |

### 2.2 字体系统

| Token | 值 | 用途 |
|-------|-----|------|
| `--text-xs` | 12px | 辅助文字 |
| `--text-sm` | 13px | 次要信息 |
| `--text-base` | 15px | 正文 |
| `--text-lg` | 20px | 小标题 |
| `--text-xl` | 24px | 卡片标题 |
| `--text-2xl` | 30px | 区块标题 |
| `--text-3xl` | 36px | 页面标题 |

### 2.3 间距系统

| Token | 值 | 用途 |
|-------|-----|------|
| `--space-2` | 8px | 紧凑间距 |
| `--space-4` | 16px | 标准间距 |
| `--space-6` | 24px | 宽松间距 |
| `--space-8` | 32px | 区块间距 |

### 2.4 阴影系统

| Token | 用途 |
|-------|------|
| `--shadow-card` | 卡片基础 |
| `--shadow-md` | 悬浮卡片 |
| `--shadow-lg` | 弹窗浮层 |
| `--shadow-glow` | 主色发光 |

---

## 3. 组件库

### 3.1 Buttons

```vue
<!-- 主要按钮 -->
<el-button type="primary">主要按钮</el-button>

<!-- 次要按钮 -->
<el-button>次要按钮</el-button>

<!-- 危险按钮 -->
<el-button type="danger">删除</el-button>
```

| 类名 | 效果 |
|------|------|
| `.dm-btn` | 基础按钮 |
| `.dm-btn--primary` | 主色渐变 + 发光阴影 |
| `.dm-btn--secondary` | 次要按钮 |
| `.dm-btn--ghost` | 透明按钮 |
| `.dm-btn--danger` | 危险按钮 |
| `.dm-btn--sm` | 小号 (32px) |
| `.dm-btn--lg` | 大号 (48px) |
| `.dm-btn--icon` | 图标按钮 |

### 3.2 Cards

```vue
<div class="dm-card">
  <div class="dm-card__header">标题</div>
  <div class="dm-card__body">内容</div>
</div>
```

| 类名 | 效果 |
|------|------|
| `.dm-card` | 基础卡片 |
| `.dm-card--interactive` | 悬浮上移动效 |

### 3.3 Stat Cards (数据卡片)

```vue
<div class="dm-stat-card">
  <div class="dm-stat-card__icon dm-stat-card__icon--navy">📊</div>
  <div class="dm-stat-card__value">128</div>
  <div class="dm-stat-card__label">设备总数</div>
</div>
```

| 图标变体 | 颜色 |
|---------|------|
| `dm-stat-card__icon--navy` | 海军蓝 |
| `dm-stat-card__icon--amber` | 琥珀金 |
| `dm-stat-card__icon--green` | 绿色 |
| `dm-stat-card__icon--red` | 红色 |

### 3.4 Badges (状态徽章)

```vue
<span class="dm-badge dm-badge--success">
  <span class="dm-badge__dot"></span>
  运行中
</span>
```

| 变体 | 用途 |
|------|------|
| `dm-badge--success` | 成功/运行 |
| `dm-badge--warning` | 警告/维修 |
| `dm-badge--danger` | 危险/停机 |
| `dm-badge--info` | 信息 |
| `dm-badge--neutral` | 中性 |

### 3.5 Data Table

```vue
<table class="dm-table dm-table--striped">
  <thead>
    <tr>
      <th>设备编号</th>
      <th>设备名称</th>
      <th>状态</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>EQ-001</td>
      <td>CNC 机床 #1</td>
      <td><span class="dm-badge dm-badge--success">运行中</span></td>
    </tr>
  </tbody>
</table>
```

### 3.6 Form Elements

```vue
<!-- 输入框 -->
<input class="dm-input" placeholder="请输入" />

<!-- 选择框 -->
<select class="dm-select">
  <option>选项一</option>
</select>
```

### 3.7 Page Header

```vue
<div class="dm-page-header">
  <div>
    <h2 class="dm-page-header__title">设备管理</h2>
    <p class="dm-page-header__subtitle">管理所有工业设备信息</p>
  </div>
  <el-button type="primary">新增设备</el-button>
</div>
```

### 3.8 Progress Bar

```vue
<div class="dm-progress">
  <div class="dm-progress__bar" style="width: 60%"></div>
</div>

<!-- 带颜色 -->
<div class="dm-progress">
  <div class="dm-progress__bar dm-progress__bar--success" style="width: 80%"></div>
</div>
```

### 3.9 Status Badge (状态标记)

```vue
<span class="dm-badge dm-badge--success">
  <span class="dm-badge__dot"></span>运行中
</span>

<span class="dm-badge dm-badge--warning">
  <span class="dm-badge__dot"></span>维修中
</span>
```

### 3.10 Empty State

```vue
<div class="dm-empty">
  <div class="dm-empty__icon">📭</div>
  <p class="dm-empty__text">暂无数据</p>
</div>
```

---

## 4. 页面模板

### 4.1 登录页

```vue
<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-card__logo">
        <div class="login-card__logo-icon">&#x2699;</div>
        <div class="login-card__logo-text">设备管理系统</div>
      </div>
      <h2 class="login-card__title">欢迎回来</h2>
      <p class="login-card__subtitle">登录以继续管理系统</p>
      <!-- 表单内容 -->
    </div>
  </div>
</template>
```

### 4.2 布局页

```vue
<template>
  <div class="dm-layout">
    <aside class="dm-sidebar">
      <div class="dm-sidebar__logo">...</div>
      <nav class="dm-sidebar__nav">
        <router-link class="dm-sidebar__item" to="/dashboard">
          <span class="dm-sidebar__item-icon"><el-icon><Odometer /></el-icon></span>
          <span class="dm-sidebar__item-label">仪表盘</span>
        </router-link>
      </nav>
    </aside>
    <div class="main-content">
      <header class="dm-header">...</header>
      <main class="dm-content"><router-view /></main>
    </div>
  </div>
</template>
```

---

## 5. 动画系统

### 5.1 页面过渡

```vue
<router-view v-slot="{ Component }">
  <transition name="page" mode="out-in">
    <component :is="Component" />
  </transition>
</router-view>
```

### 5.2 列表动画

```vue
<TransitionGroup name="list" tag="div">
  <div v-for="item in items" :key="item.id" class="list-item">
    {{ item.name }}
  </div>
</TransitionGroup>
```

### 5.3 实用动画类

| 类名 | 效果 |
|------|------|
| `.dm-animate-fade-in` | 淡入 |
| `.dm-animate-slide-in` | 滑入 |
| `.dm-animate-scale-in` | 缩放进入 |
| `.dm-skeleton` | 骨架屏闪烁 |

---

## 6. 文件清单

```
frontend/src/styles/
├── index.css              # 全局样式入口 (导入所有模块)
├── design-tokens.css      # Design Tokens v4.0 (颜色/字体/间距)
├── components/
│   └── index.css          # 组件库样式 (按钮/卡片/表格/表单)
├── pages.css              # 页面样式 (登录/布局)
└── animations.css         # 动画系统
```

---

## 7. 色彩对比

| 元素 | 亮色 | 暗色 |
|------|------|------|
| 背景 | `#FFFFFF` | `#0F172A` |
| 卡片 | `#FFFFFF` | `#1E293B` |
| 侧边栏 | `#1E1B4B` | `#0A0F1E` |
| 文字 | `#0F172A` | `#F1F5F9` |
| 边框 | `#E2E8F0` | `#334155` |

---

## 8. 设计规范

### 8.1 圆角

| 尺寸 | 值 | 用途 |
|------|-----|------|
| xs | 4px | 小标签 |
| sm | 8px | 按钮、输入框 |
| md | 12px | 卡片、面板 |
| lg | 16px | 对话框 |
| xl | 20px | 大型浮层 |
| 2xl | 24px | 特殊容器 |

### 8.2 阴影层次

| 层级 | 用途 |
|------|------|
| `--shadow-card` | 卡片基础 |
| `--shadow-md` | 悬浮效果 |
| `--shadow-lg` | 弹窗浮层 |
| `--shadow-glow` | 主色发光 |

### 8.3 交互状态

| 状态 | 效果 |
|------|------|
| Hover | `translateY(-1px)` + 阴影加深 |
| Active | `scale(0.98)` + 阴影收缩 |
| Focus | 3px 主色光环 |
| Disabled | 降低透明度 |

---

## 9. 迁移指南

从 v3.0 → v4.0：

| v3.0 | v4.0 | 说明 |
|------|------|------|
| `--color-primary-500` | `--navy-500` | 主色重命名 |
| `--surface-sidebar` | `--surface-sidebar` | 值变更 (深海军蓝) |
| `.sidebar-logo` | `.dm-sidebar__logo` | BEM 命名 |
| `.login-container` | `.login-container` | 样式重写 |
| `.stat-grid` | `.dm-stat-card` | 独立卡片组件 |
| `.el-card` | `.dm-card` | 新增基础卡片 |

---

## 10. 预览

**登录页**:
- 深海军蓝渐变背景 + 径向光晕
- 毛玻璃卡片 + 琥珀色图标
- 动画缩放进入

**侧边栏**:
- 深色背景 + 高亮激活项
- 平滑折叠动画
- 图标 + 文字布局

**数据卡片**:
- 顶部彩色图标区
- 大号等宽数值
- 悬浮上移 + 顶部渐变线
