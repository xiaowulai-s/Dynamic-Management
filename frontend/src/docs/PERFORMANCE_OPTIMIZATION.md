# 性能优化指南 v3.0

**版本**: 2026-07-13
**目标**: Lighthouse Performance ≥ 90

---

## 📊 性能指标目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| **First Contentful Paint (FCP)** | < 1.8s | 首次内容绘制 |
| **Largest Contentful Paint (LCP)** | < 2.5s | 最大内容绘制 |
| **First Input Delay (FID)** | < 100ms | 首次输入延迟 |
| **Cumulative Layout Shift (CLS)** | < 0.1 | 累积布局偏移 |
| **Time to Interactive (TTI)** | < 3.8s | 可交互时间 |

---

## ⚡ 前端性能优化

### 1. 代码分割 (Code Splitting)

#### 1.1 路由懒加载

```typescript
// router/index.ts
const routes = [
  {
    path: '/analytics',
    component: () => import('@/views/Analytics.vue')  // 按需加载
  },
  {
    path: '/upload',
    component: () => import('@/views/Upload.vue')
  }
]
```

**收益**: 减少首屏 bundle 大小 ~40%

#### 1.2 组件懒加载

```vue
<script setup>
import { defineAsyncComponent } from 'vue'

// 重型组件异步加载
const HeavyComponent = defineAsyncComponent(() =>
  import('@/components/HeavyComponent.vue')
)
</script>
```

#### 1.3 Vendor 代码分割

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // 将 node_modules 拆分为多个 chunk
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-element': ['element-plus'],
          'vendor-charts': ['echarts'],
          'vendor-utils': ['axios', 'dayjs']
        }
      }
    }
  }
})
```

### 2. 资源优化

#### 2.1 图片优化

```vue
<!-- 使用 WebP 格式 -->
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="描述" loading="lazy" />
</picture>

<!-- 响应式图片 -->
<img
  src="image-800w.jpg"
  srcset="
    image-400w.jpg 400w,
    image-800w.jpg 800w,
    image-1200w.jpg 1200w
  "
  sizes="(max-width: 600px) 400px, 800px"
  loading="lazy"
  alt="描述"
/>
```

#### 2.2 字体优化

```css
/* 使用 system font stack (已实现) */
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

/* 字体显示策略 */
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2') format('woff2');
  font-display: swap; /* 关键：避免 FOIT */
}
```

#### 2.3 预加载关键资源

```html
<head>
  <!-- 预连接到关键源 -->
  <link rel="preconnect" href="https://api.example.com">

  <!-- 预加载关键字体 -->
  <link rel="preload" href="/fonts/critical.woff2" as="font" type="font/woff2" crossorigin>

  <!-- DNS 预获取 -->
  <link rel="dns-prefetch" href="https://cdn.example.com">
</head>
```

### 3. 渲染优化

#### 3.1 虚拟滚动 (长列表)

```vue
<!-- Element Plus 虚拟滚动 -->
<el-table-v2
  :columns="columns"
  :data="largeData"
  :width="width"
  :height="500"
/>

<!-- 自定义虚拟滚动 -->
<div ref="scrollContainer" @scroll="handleScroll">
  <div :style="{ height: totalHeight + 'px' }">
    <div
      v-for="item in visibleItems"
      :key="item.id"
      :style="{ transform: `translateY(${item.offset}px)` }"
    >
      {{ item.content }}
    </div>
  </div>
</div>
```

**收益**: 万级数据渲染从 3s → 50ms

#### 3.2 防抖节流

```typescript
import { debounce, throttle } from 'lodash-es'

// 搜索防抖 (300ms)
const handleSearch = debounce(() => {
  fetchData()
}, 300)

// 滚动节流 (100ms)
const handleScroll = throttle(() => {
  updateScrollPosition()
}, 100)
```

#### 3.3 列表懒加载

```typescript
// 无限滚动
const observer = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) {
    loadMoreData()
  }
})

observer.observe(document.querySelector('.load-more-trigger'))
```

### 4. 状态管理优化

#### 4.1 Pinia 持久化

```typescript
// stores/user.ts
import { defineStore } from 'pinia'
import { persist } from 'pinia-plugin-persist'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)

  return { user }
}, {
  persist: {
    key: 'user',
    storage: localStorage,
    // 仅持久化必要字段
    pick: ['user.token', 'user.username']
  }
})
```

#### 4.2 避免不必要重渲染

```vue
<script setup>
import { computed, watch } from 'vue'

// ✅ 使用 computed 缓存计算结果
const filteredData = computed(() => {
  return data.value.filter(item => item.active)
})

// ✅ 使用 watch 深度监听
watch(
  () => searchForm.value.keyword,
  (newVal) => {
    // 仅当 keyword 变化时执行
    fetchData(newVal)
  }
)
</script>
```

### 5. HTTP 优化

#### 5.1 请求拦截器缓存

```typescript
// api/request.ts
const request = axios.create({
  baseURL: import.meta.env.VITE_API_URL
})

// 请求缓存
const cache = new Map()

request.interceptors.request.use((config) => {
  if (config.method === 'get') {
    const key = `${config.url}?${JSON.stringify(config.params)}`
    if (cache.has(key)) {
      return Promise.reject({ cached: true, data: cache.get(key) })
    }
  }
  return config
})

request.interceptors.response.use((response) => {
  if (response.config.method === 'get') {
    const key = `${response.config.url}?${JSON.stringify(response.config.params)}`
    cache.set(key, response.data)
    // 5分钟过期
    setTimeout(() => cache.delete(key), 5 * 60 * 1000)
  }
  return response
})
```

#### 5.2 取消重复请求

```typescript
// 使用 AbortController
const controller = new AbortController()

const fetchData = async () => {
  try {
    const res = await axios.get('/api/data', {
      signal: controller.signal
    })
    return res.data
  } catch (error) {
    if (axios.isCancel(error)) {
      console.log('Request canceled:', error.message)
    }
  }
}

// 取消请求
controller.abort()
```

### 6. CSS 优化

#### 6.1 减少重排重绘

```css
/* ✅ 仅使用 transform 和 opacity */
.animate-element {
  transform: translate3d(0, 0, 0); /* GPU加速 */
  opacity: 0.5;
  transition: transform 250ms ease, opacity 250ms ease;
}

/* ❌ 避免触发重排的属性 */
.bad-animation {
  width: 100px;        /* 触发重排 */
  margin-left: 20px;   /* 触发重排 */
  top: 10px;           /* 触发重排 */
}
```

#### 6.2 CSS Containment

```css
/* 限制浏览器重绘范围 */
.stat-card {
  contain: layout style paint;
}

/* 独立渲染上下文 */
.chart-container {
  contain: strict;
}
```

#### 6.3 will-change 优化

```css
.animated-element {
  will-change: transform, opacity;
}

/* 动画结束后移除 */
.animated-element.done {
  will-change: auto;
}
```

### 7. 缓存策略

#### 7.1 Service Worker

```typescript
// vite.config.ts
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\./i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 // 24小时
              }
            }
          }
        ]
      }
    })
  ]
})
```

#### 7.2 LocalStorage 缓存

```typescript
// 缓存静态数据
const CACHE_KEY = 'equipment-cache'
const CACHE_TTL = 5 * 60 * 1000 // 5分钟

const fetchEquipments = async () => {
  const cached = localStorage.getItem(CACHE_KEY)
  if (cached) {
    const { data, timestamp } = JSON.parse(cached)
    if (Date.now() - timestamp < CACHE_TTL) {
      return data
    }
  }

  const res = await api.getEquipments()
  localStorage.setItem(CACHE_KEY, JSON.stringify({
    data: res.data,
    timestamp: Date.now()
  }))

  return res.data
}
```

### 8. 打包优化

#### 8.1 Vite 配置

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    target: 'es2015', // 现代浏览器
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 移除 console
        drop_debugger: true
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue': ['vue', 'vue-router', 'pinia'],
          'vendor-element': ['element-plus'],
          'vendor-charts': ['echarts']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['element-plus']
  }
})
```

#### 8.2 Gzip/Brotli 压缩

```typescript
// vite.config.ts
import viteCompression from 'vite-plugin-compression'

export default defineConfig({
  plugins: [
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz',
      threshold: 10240 // 10KB以上才压缩
    }),
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 10240
    })
  ]
})
```

---

## 🔍 性能监控

### 1. Lighthouse CI

```yaml
# .lighthouserc.js
module.exports = {
  ci: {
    collect: {
      urls: ['http://localhost:5173'],
      numberOfRuns: 3
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'first-contentful-paint': ['error', { maxNumericValue: 1800 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }]
      }
    }
  }
}
```

### 2. Web Vitals 监控

```typescript
// 监控 Core Web Vitals
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

getCLS(console.log)
getFID(console.log)
getFCP(console.log)
getLCP(console.log)
getTTFB(console.log)
```

### 3. 性能埋点

```typescript
// utils/performance.ts
export function measurePerformance(name: string, fn: () => void) {
  const start = performance.now()
  fn()
  const end = performance.now()
  console.log(`${name} 耗时: ${(end - start).toFixed(2)}ms`)

  // 发送到监控系统
  // analytics.track('performance', { name, duration: end - start })
}
```

---

## 📦 构建优化检查清单

- [x] 启用代码分割 (路由懒加载)
- [x] Vendor 代码分割 (vue/element/charts)
- [x] Gzip/Brotli 压缩
- [x] Tree-shaking (移除未使用代码)
- [x] 图片优化 (WebP + lazy loading)
- [x] 字体优化 (system font stack)
- [x] CSS 优化 (containment, GPU acceleration)
- [x] 预加载关键资源
- [x] Service Worker 缓存
- [x] Console 移除 (生产环境)

---

## 🎯 预期性能提升

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| **首屏加载** | ~3.5s | ~1.8s | ⬇️ 49% |
| **LCP** | ~3.2s | ~2.2s | ⬇️ 31% |
| **FID** | ~150ms | ~50ms | ⬇️ 67% |
| **CLS** | ~0.25 | ~0.05 | ⬇️ 80% |
| **Bundle 大小** | ~2.5MB | ~850KB | ⬇️ 66% |
| **Lighthouse** | ~65 | ~92 | ⬆️ 42% |

---

## ✅ 性能测试工具

1. **Lighthouse** (Chrome DevTools)
2. **WebPageTest** (https://webpagetest.org)
3. **PageSpeed Insights** (https://pagespeed.web.dev)
4. **Chrome Performance Tab**
5. **Web Vitals Extension**

---

**文档状态**: 🟢 性能优化指南已完成
**下一步**: 在实际项目中应用这些优化，并验证性能指标
