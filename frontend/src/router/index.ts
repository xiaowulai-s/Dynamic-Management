import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/views/Layout.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: '仪表盘', icon: 'Odometer' }
        },
        {
          path: 'equipment',
          name: 'Equipment',
          component: () => import('@/views/Equipment.vue'),
          meta: { title: '设备管理', icon: 'Box' }
        },
        {
          path: 'logs',
          name: 'Logs',
          component: () => import('@/views/Logs.vue'),
          meta: { title: '日志管理', icon: 'Document' }
        },
        {
          path: 'analytics',
          name: 'Analytics',
          component: () => import('@/views/Analytics.vue'),
          meta: { title: '统计分析', icon: 'TrendCharts' }
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/Settings.vue'),
          meta: { title: '系统设置', icon: 'Setting' }
        },
        {
          path: 'upload',
          name: 'Upload',
          component: () => import('@/views/Upload.vue'),
          meta: { title: '批量上传', icon: 'Upload' }
        },
        {
          path: 'profile',
          name: 'Profile',
          component: () => import('@/views/Profile.vue'),
          meta: { title: '个人资料', icon: 'User' }
        },
        {
          path: 'logs/:id',
          name: 'LogDetail',
          component: () => import('@/views/LogDetail.vue'),
          meta: { title: '日志详情' }
        },
        {
          path: 'notifications',
          name: 'Notifications',
          component: () => import('@/views/Notifications.vue'),
          meta: { title: '通知中心', icon: 'Bell' }
        }
      ]
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { title: '登录' }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/Register.vue'),
      meta: { title: '注册' }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue'),
      meta: { title: '404' }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()

  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 设备管理系统` : '设备管理系统'

  // 需要认证的路由
  if (to.path !== '/login' && to.path !== '/register') {
    // 如果还没有认证，先初始化
    if (!userStore.isAuthenticated) {
      await userStore.init()
    }

    // 检查认证状态
    if (!userStore.isAuthenticated) {
      next('/login')
      return
    }
  }

  next()
})

export default router
