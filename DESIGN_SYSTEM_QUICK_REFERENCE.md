# 🎨 Design System Quick Reference

**Version**: 3.0
**Updated**: 2026-07-13
**Style**: Industrial Minimalism + Material Design

---

## 📐 Spacing Scale (8px Base)

```css
--space-1:  4px
--space-2:  8px   ★
--space-4:  16px
--space-5:  24px  ★
--space-6:  32px  ★
--space-8:  48px  ★
--space-10: 64px
```

**Usage**:
- Component padding: `--space-6` (32px)
- Component gap: `--space-6` (32px)
- Section spacing: `--space-8` (48px)
- Page margins: `--space-8` (48px)

---

## 🎨 Color Palette

### Primary - Slate Blue

```css
--color-primary-50:  #F8FAFC;
--color-primary-100: #F1F5F9;
--color-primary-200: #E2E8F0;
--color-primary-300: #CBD5E1;
--color-primary-400: #94A3B8;
--color-primary-500: #64748B;  /* ★ Main */
--color-primary-600: #475569;
--color-primary-700: #334155;
--color-primary-800: #1E293B;
--color-primary-900: #0F172A;
```

### Neutral - Monochrome

```css
--color-neutral-0:   #FFFFFF;  /* Pure White */
--color-neutral-50:  #FAFAFA;
--color-neutral-900: #171717;  /* Near Black */
```

### Semantic (Use Sparingly)

```css
Success:  #10B981 (Green)
Warning:  #F59E0B (Orange)
Danger:   #EF4444 (Red)
Info:     #3B82F6 (Blue)
```

---

## ✍️ Typography (16px Base)

```css
/* System Font Stack */
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
             'Helvetica Neue', Arial, 'Noto Sans SC', 'PingFang SC',
             'Microsoft YaHei', sans-serif;

/* Type Scale */
--text-xs:   12px  /* Auxiliary */
--text-sm:   14px  /* Secondary */
--text-base: 16px  /* Body ★ */
--text-md:   18px  /* Emphasis */
--text-lg:   20px  /* Subtitle */
--text-xl:   24px  /* Card Title */
--text-2xl:  32px  /* Section Header */
--text-3xl:  40px  /* Page Title ★ */
```

---

## 🌑 Dark Mode

```css
/* Backgrounds */
--surface-base:     #1A1A2E;  /* Main background */
--surface-sidebar:  #0F0F23;  /* Sidebar */
--surface-hover:    #2A2A45;  /* Hover state */
--surface-selected: #312E81;  /* Selected */

/* Text */
--text-primary:   #E8E8ED;
--text-secondary: #A0A0B8;
```

---

## 🎬 Animation

### Durations

```css
--duration-fast:   150ms;  /* Buttons */
--duration-normal: 250ms;  /* Cards, Dialogs */
--duration-slow:   350ms;  /* Page transitions */
```

### Easing

```css
--ease-default:  cubic-bezier(0.4, 0.0, 0.2, 1);
--ease-in:       cubic-bezier(0.4, 0.0, 1.0, 1.0);
--ease-out:      cubic-bezier(0.0, 0.0, 0.2, 1.0);
--ease-bounce:   cubic-bezier(0.34, 1.56, 0.64, 1);
```

### Key Animations

```css
/* Button click */
.el-button:active {
  transform: scale(0.96);
}

/* Card hover */
.el-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

/* Page transition */
.page-enter-active {
  opacity: 0;
  transform: translate3d(0, 20px, 0);
}
```

---

## 📦 Component Patterns

### Button

```vue
<el-button type="primary">Primary</el-button>
<el-button type="default">Default</el-button>
```

**Hover**: TranslateY(-1px) + shadow increase
**Active**: Scale(0.96)

### Card

```vue
<el-card>
  <template #header>
    <span>Title</span>
  </template>
  Content
</el-card>
```

**Hover**: TranslateY(-4px) + shadow increase

### Table

```vue
<el-table :data="data">
  <el-table-column prop="name" label="Name" />
</el-table>
```

**Cell padding**: 16px
**Header**: Uppercase, semibold, 14px

### Stat Card

```vue
<div class="stat-grid">
  <div class="stat-card">
    <div class="stat-card-value">42</div>
    <div class="stat-card-label">Label</div>
  </div>
</div>
```

**Padding**: 32px
**Value font**: 40px, bold
**Gap**: 32px

---

## 📱 Responsive Breakpoints

```css
/* Desktop */
@media (min-width: 1024px) {
  /* Full layout */
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1023px) {
  /* Collapsed sidebar */
}

/* Mobile */
@media (max-width: 767px) {
  /* Hidden sidebar, hamburger menu */
}
```

### Sidebar Width

| Breakpoint | Width | Behavior |
|-----------|-------|---------|
| ≥1024px | 240px | Full, collapsible to 64px |
| 768-1023px | 64px | Collapsed |
| <768px | 0px | Hidden, slide-in menu |

### Content Padding

| Breakpoint | Padding |
|-----------|---------|
| ≥1024px | 48px (--space-8) |
| 768-1023px | 32px (--space-6) |
| 640-767px | 24px (--space-4) |
| <640px | 16px (--space-3) |

---

## 🎯 Quick Examples

### Page Layout

```vue
<template>
  <div class="page">
    <div class="page-header">
      <h2>Page Title</h2>
      <el-button type="primary">Action</el-button>
    </div>

    <el-card class="search-card">
      <!-- Search filters -->
    </el-card>

    <el-card class="table-card">
      <el-table :data="data">
        <!-- Columns -->
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);
}

.search-card,
.table-card {
  margin-bottom: var(--space-6);
}
</style>
```

### Form Layout

```vue
<el-form :model="form" inline>
  <el-form-item label="Field 1">
    <el-input v-model="form.field1" />
  </el-form-item>

  <el-form-item label="Field 2">
    <el-select v-model="form.field2">
      <el-option label="Option 1" value="1" />
    </el-select>
  </el-form-item>

  <el-form-item>
    <el-button type="primary">Submit</el-button>
    <el-button>Reset</el-button>
  </el-form-item>
</el-form>
```

---

## 🔧 Theme Toggle

```typescript
import { useTheme } from '@/composables/useTheme'

const { theme, toggleTheme, isDark } = useTheme()

// Toggle theme
toggleTheme()

// Check if dark mode
if (isDark.value) {
  // Dark mode code
}
```

```vue
<template>
  <ThemeToggle />
</template>
```

---

## 📚 Resources

- [Design Tokens](design-tokens.css)
- [Animations](animations.css)
- [Global Styles](index.css)
- [Responsive Testing Guide](RESPONSIVE_TESTING.md)
- [Performance Optimization](PERFORMANCE_OPTIMIZATION.md)
- [Final Report](UI_REDESIGN_FINAL_REPORT.md)

---

**Keep it simple, keep it minimal.** 🎯
