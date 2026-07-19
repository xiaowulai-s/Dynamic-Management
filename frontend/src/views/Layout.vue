<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '224px'" class="sidebar" :class="{ 'sidebar-collapsed': isCollapse }">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <el-icon :size="16"><Histogram /></el-icon>
        </div>
        <div v-if="!isCollapse" class="logo-text-wrap">
          <span class="logo-title">{{ siteTitleZh }}</span>
          <span class="logo-sub">{{ siteTitleEn }}</span>
        </div>
      </div>

      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>

        <el-menu-item index="/equipment">
          <el-icon><Box /></el-icon>
          <template #title>设备管理</template>
        </el-menu-item>

        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <template #title>日志管理</template>
        </el-menu-item>

        <el-menu-item index="/analytics">
          <el-icon><TrendCharts /></el-icon>
          <template #title>统计分析</template>
        </el-menu-item>

        <el-menu-item index="/settings" v-if="userStore.isAdmin">
          <el-icon><Setting /></el-icon>
          <template #title>系统设置</template>
        </el-menu-item>

        <el-menu-item index="/customers" v-if="userStore.isAdmin">
          <el-icon><User /></el-icon>
          <template #title>客户管理</template>
        </el-menu-item>

        <el-menu-item index="/feedback">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>用户反馈</template>
        </el-menu-item>

        <el-menu-item index="/audit" v-if="userStore.isAdmin">
          <el-icon><List /></el-icon>
          <template #title>审计日志</template>
        </el-menu-item>

        <el-menu-item index="/user-manage" v-if="userStore.isAdmin">
          <el-icon><UserFilled /></el-icon>
          <template #title>用户管理</template>
        </el-menu-item>
      </el-menu>

      <!-- 侧栏底部用户卡 -->
      <div v-if="!isCollapse" class="sidebar-user">
        <el-dropdown placement="top-start">
          <div class="user-card">
            <div class="user-avatar">{{ userStore.username?.charAt(0)?.toUpperCase() || 'U' }}</div>
            <div class="user-info">
              <span class="user-name">{{ userStore.username }}</span>
              <span class="user-role">{{ getRoleLabel(userStore.userInfo?.role) }}</span>
            </div>
            <el-icon class="user-chevron"><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="$router.push('/profile')">个人信息</el-dropdown-item>
              <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </el-aside>

    <!-- 移动端遮罩 -->
    <div class="mobile-overlay" v-if="mobileMenuOpen" @click="closeMobileMenu"></div>

    <!-- 主体内容 -->
    <div class="main-content">
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <button class="collapse-btn" @click="toggleSidebar">
            <el-icon :size="16"><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
          </button>
          <el-breadcrumb separator="/" class="header-crumb">
            <el-breadcrumb-item :to="{ path: '/' }">设备信息动态</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta.title">{{ route.meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <div class="header-search">
            <el-icon class="search-icon"><Search /></el-icon>
            <input
              v-model="searchKeyword"
              type="text"
              placeholder="搜索设备、日志编号"
              class="search-input"
              @keyup.enter="handleSearch"
            />
          </div>

          <ThemeToggle />
          <NotificationsPopover />

          <el-dropdown>
            <div class="header-avatar">
              {{ userStore.username?.charAt(0)?.toUpperCase() || 'U' }}
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/profile')">个人信息</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区域 -->
      <div class="content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useSiteTitle } from '@/composables/useSiteTitle'
import { getRoleLabel } from '@/utils/role'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Odometer,
  Box,
  Document,
  TrendCharts,
  Setting,
  User,
  ArrowDown,
  Expand,
  Fold,
  ChatDotRound,
  List,
  UserFilled,
  Histogram,
  Search
} from '@element-plus/icons-vue'
import NotificationsPopover from '@/components/NotificationsPopover.vue'
import ThemeToggle from '@/components/ThemeToggle.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { siteTitleZh, siteTitleEn, loadSiteTitle } = useSiteTitle()

const isCollapse = ref(false)
const mobileMenuOpen = ref(false)
const searchKeyword = ref('')

onMounted(() => {
  loadSiteTitle()
})

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

const handleSearch = () => {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/logs', query: { search: searchKeyword.value.trim() } })
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  }).catch(() => {})
}
</script>

<style scoped>
.layout-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ===== 侧边栏 ===== */
.sidebar {
  background: var(--surface-sidebar);
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  transition: width var(--transition-base);
  flex-shrink: 0;
}

.sidebar-logo {
  height: var(--header-height);
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--border-default);
  flex-shrink: 0;
}

.logo-icon {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  background: var(--color-primary-600);
  color: #FFFFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.logo-text-wrap {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
  min-width: 0;
  padding-top: 2px;
}

.logo-title {
  font-size: var(--text-sm);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logo-sub {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.02em;
}

.sidebar-menu {
  flex: 1;
  border-right: none;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 侧栏底部用户卡 */
.sidebar-user {
  padding: var(--space-3);
  border-top: 1px solid var(--border-default);
  flex-shrink: 0;
}

.user-card {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.user-card:hover {
  background: var(--surface-hover);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-primary-50);
  color: var(--color-primary-700);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: var(--font-w-semibold);
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: var(--text-sm);
  font-weight: var(--font-w-medium);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

.user-chevron {
  color: var(--text-tertiary);
  flex-shrink: 0;
}

/* ===== 主内容区 ===== */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  overflow: hidden;
}

.header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--space-4);
  background: var(--surface-overlay);
  border-bottom: 1px solid var(--border-default);
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.collapse-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.collapse-btn:hover {
  background: var(--surface-hover);
  color: var(--text-primary);
}

.header-crumb {
  font-size: var(--text-sm);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.header-search {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-tertiary);
  font-size: 14px;
  pointer-events: none;
}

.search-input {
  height: 36px;
  width: 240px;
  padding: 0 var(--space-3) 0 32px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-sm);
  background: var(--surface-overlay);
  color: var(--text-primary);
  font-size: var(--text-sm);
  font-family: var(--font-sans);
  outline: none;
  transition: all var(--transition-fast);
}

.search-input::placeholder {
  color: var(--text-tertiary);
}

.search-input:focus {
  border-color: var(--color-primary-600);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.header-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-primary-50);
  color: var(--color-primary-700);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: var(--font-w-semibold);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.header-avatar:hover {
  background: var(--color-primary-100);
}

.content {
  flex: 1;
  padding: var(--space-5);
  overflow-y: auto;
  background: var(--surface-page);
}

/* 移动端 */
.mobile-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: calc(var(--z-modal) - 1);
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: var(--z-modal);
    transform: translateX(-100%);
  }
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  .mobile-overlay {
    display: block;
  }
  .content {
    padding: var(--space-4);
  }
  .header-search {
    display: none;
  }
}

@media (max-width: 480px) {
  .content {
    padding: var(--space-3);
  }
}
</style>
