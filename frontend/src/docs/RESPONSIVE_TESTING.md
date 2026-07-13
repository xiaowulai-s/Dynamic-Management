# 响应式设计测试指南

**版本**: v3.0
**更新日期**: 2026-07-13
**测试范围**: 5个断点 × 10个页面

---

## 📱 断点定义

| 断点 | 屏幕宽度 | 设备类型 | 布局模式 |
|------|---------|---------|---------|
| **2XL** | ≥1536px | 大屏桌面 | 完整布局 |
| **XL** | 1280px-1535px | 标准桌面 | 完整布局 |
| **LG** | 1024px-1279px | 小屏桌面/平板横屏 | 完整布局 |
| **MD** | 768px-1023px | 平板竖屏 | 收缩侧边栏 |
| **SM** | 640px-767px | 大屏手机 | 移动端布局 |
| **XS** | <640px | 手机 | 移动端布局 |

---

## 🎯 响应式策略

### 1. 侧边栏 (Sidebar)

| 断点 | 宽度 | 行为 |
|------|------|------|
| ≥1024px | 240px | 完整显示，可折叠至64px |
| 768px-1023px | 64px | 默认收缩，hover展开 |
| <768px | 0px | 隐藏，通过汉堡菜单唤出 |

**实现**:
```css
/* 桌面端 */
@media (min-width: 1024px) {
  .sidebar { width: 240px; }
}

/* 平板端 */
@media (min-width: 768px) and (max-width: 1023px) {
  .sidebar { width: 64px; }
}

/* 移动端 */
@media (max-width: 767px) {
  .sidebar {
    position: fixed;
    transform: translateX(-100%);
  }
  .sidebar.mobile-open {
    transform: translateX(0);
  }
}
```

### 2. 内容区域 (Content)

| 断点 | 内边距 | 说明 |
|------|-------|------|
| ≥1024px | 48px (--space-8) | 桌面舒适间距 |
| 768px-1023px | 32px (--space-6) | 平板标准间距 |
| 640px-767px | 24px (--space-4) | 大屏手机 |
| <640px | 16px (--space-3) | 小屏手机 |

### 3. 统计卡片网格 (Stat Grid)

| 断点 | 列数 | 最小宽度 |
|------|------|---------|
| ≥1400px | 4列 | 240px |
| 1024px-1399px | 3列 | 240px |
| 768px-1023px | 2列 | 240px |
| <768px | 1列 | 100% |

**实现**:
```css
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--space-6);
}

@media (max-width: 1024px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
```

### 4. 图表网格 (Charts Grid)

| 断点 | 列数 | 说明 |
|------|------|------|
| ≥1024px | 2列 | 并排显示 |
| <1024px | 1列 | 垂直堆叠 |

### 5. 表格 (Table)

| 断点 | 行为 |
|------|------|
| ≥768px | 正常显示所有列 |
| <768px | 横向滚动，隐藏次要列 |

**实现**:
```css
@media (max-width: 768px) {
  .table-container {
    overflow-x: auto;
  }
}
```

### 6. 表单 (Form)

| 断点 | 布局 |
|------|------|
| ≥768px | 水平排列 (inline) |
| <768px | 垂直堆叠 |

**实现**:
```css
@media (max-width: 768px) {
  .search-card :deep(.el-form) {
    flex-direction: column;
  }
}
```

### 7. 对话框 (Dialog)

| 断点 | 宽度 |
|------|------|
| ≥768px | 50%-70% |
| <768px | 95% |

**实现**:
```css
@media (max-width: 480px) {
  .el-dialog {
    width: 95% !important;
  }
}
```

### 8. 页面标题 (Page Header)

| 断点 | 字体大小 | 布局 |
|------|---------|------|
| ≥1024px | 40px (--text-3xl) | 水平排列 |
| <1024px | 32px (--text-2xl) | 垂直堆叠 |

---

## 📋 测试检查清单

### Dashboard 页面

- [ ] **桌面 (1920x1080)**
  - [ ] 4个统计卡片并排显示
  - [ ] 2个图表并排显示
  - [ ] 待审批列表正常显示
  - [ ] 所有间距符合设计规范

- [ ] **笔记本 (1280x720)**
  - [ ] 统计卡片自适应宽度
  - [ ] 图表可能换行
  - [ ] 内容无溢出

- [ ] **平板横屏 (1024x768)**
  - [ ] 统计卡片2-3列
  - [ ] 图表可能垂直堆叠

- [ ] **平板竖屏 (768x1024)**
  - [ ] 统计卡片2列
  - [ ] 图表1列
  - [ ] 表格横向滚动

- [ ] **手机 (375x667)**
  - [ ] 统计卡片1列
  - [ ] 图表1列
  - [ ] 无横向溢出

### Equipment 页面

- [ ] **桌面**
  - [ ] 表格所有列正常显示
  - [ ] 搜索栏水平排列
  - [ ] 分页在右侧

- [ ] **平板**
  - [ ] 表格部分列可能需要横向滚动

- [ ] **手机**
  - [ ] 表格横向滚动
  - [ ] 搜索栏垂直堆叠
  - [ ] 按钮全宽

### Logs 页面

- [ ] **桌面**
  - [ ] 搜索栏所有筛选器可见
  - [ ] 表格操作列完整显示
  - [ ] 表单多列布局

- [ ] **平板**
  - [ ] 部分筛选器换行
  - [ ] 表格可能需要横向滚动

- [ ] **手机**
  - [ ] 搜索栏垂直堆叠
  - [ ] 表格关键列显示
  - [ ] 表单单列布局

### Analytics 页面

- [ ] **桌面**
  - [ ] 4个图表2x2网格
  - [ ] 统计卡片4列
  - [ ] 表格完整显示

- [ ] **平板**
  - [ ] 图表1列垂直堆叠
  - [ ] 统计卡片2-3列

- [ ] **手机**
  - [ ] 图表1列
  - [ ] 统计卡片1列
  - [ ] 表格横向滚动

### Settings 页面

- [ ] **桌面**
  - [ ] Tabs标签页正常
  - [ ] 表格完整显示
  - [ ] 配置表单正常

- [ ] **平板**
  - [ ] 表格可能需要横向滚动

- [ ] **手机**
  - [ ] Tabs垂直堆叠
  - [ ] 表格横向滚动
  - [ ] 表单全宽

---

## 🔧 常见响应式问题修复

### 问题1: 表格横向溢出

**症状**: 表格在小屏幕出现横向滚动条

**解决**:
```css
.table-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
```

### 问题2: 图片/图表过大

**症状**: 图片或图表超出容器

**解决**:
```css
.chart-container,
img {
  max-width: 100%;
  height: auto;
}
```

### 问题3: 文字换行不当

**症状**: 文字在错误位置换行

**解决**:
```css
.text-nowrap {
  white-space: nowrap;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

### 问题4: 按钮间距太小

**症状**: 移动端按钮挤在一起

**解决**:
```css
@media (max-width: 768px) {
  .button-group {
    flex-direction: column;
    gap: var(--space-3);
  }
}
```

### 问题5: 表单输入框太小

**症状**: 移动端输入框难以点击

**解决**:
```css
@media (max-width: 768px) {
  .el-input__inner {
    font-size: 16px; /* 防止iOS缩放 */
  }
}
```

---

## 🎨 移动端优化建议

### 1. 触摸目标

**最小尺寸**: 44x44px (WCAG 2.1)

```css
.el-button {
  min-height: 44px;
  min-width: 44px;
}

.el-menu-item {
  height: 44px;
  line-height: 44px;
}
```

### 2. 间距

**建议**:
- 按钮间距: ≥16px
- 表单字段间距: ≥24px
- 区块间距: ≥32px

### 3. 字体大小

**移动端最小**: 14px (防止iOS自动缩放)

```css
@media (max-width: 768px) {
  body {
    font-size: 16px;
  }

  .el-button {
    font-size: var(--text-base);
  }
}
```

### 4. 汉堡菜单

**移动端侧边栏动画**:
```css
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform var(--duration-normal) var(--ease-default);
  }

  .sidebar.mobile-open {
    transform: translateX(0);
  }

  .mobile-overlay {
    display: block;
    animation: fadeIn var(--duration-fast);
  }
}
```

### 5. 横向滚动优化

**触摸滚动**:
```css
.overflow-x-auto {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scroll-behavior: smooth;
}

/* 滚动条美化 */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background-color: var(--color-neutral-300);
  border-radius: var(--radius-full);
}
```

---

## 📊 性能优化

### 1. 图片懒加载

```vue
<el-image
  :src="imageUrl"
  loading="lazy"
/>
```

### 2. 组件懒加载

```typescript
// router/index.ts
{
  path: '/analytics',
  component: () => import('@/views/Analytics.vue')
}
```

### 3. 虚拟滚动 (长列表)

```vue
<el-table-v2
  :columns="columns"
  :data="data"
  :width="width"
  :height="height"
/>
```

### 4. 防抖节流

```typescript
import { debounce } from 'lodash-es'

const handleSearch = debounce(() => {
  fetchData()
}, 300)
```

---

## ✅ 测试通过标准

### 视觉验收
- [ ] 无横向滚动条 (除表格)
- [ ] 无文字截断
- [ ] 无图片/图表溢出
- [ ] 按钮/链接可点击区域 ≥44px

### 功能验收
- [ ] 所有交互功能正常
- [ ] 表单提交正常
- [ ] 表格分页正常
- [ ] 筛选/搜索正常

### 性能验收
- [ ] 页面加载 < 3s (3G)
- [ ] 动画流畅 (60fps)
- [ ] 无明显卡顿

### 兼容性验收
- [ ] Chrome (最新)
- [ ] Firefox (最新)
- [ ] Safari (最新)
- [ ] Edge (最新)
- [ ] iOS Safari
- [ ] Android Chrome

---

## 🚀 下一步

1. **手动测试**: 按照上述清单逐项测试
2. **修复问题**: 记录并修复响应式问题
3. **真机测试**: 在真实设备上测试
4. **性能优化**: Lighthouse评分 ≥ 90
5. **兼容性测试**: 跨浏览器验证

---

**文档状态**: 🟢 响应式规范已完成 | 🟡 待手动测试验证
