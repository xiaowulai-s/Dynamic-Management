import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getCurrentUser } from '@/api/auth'
import type { LoginParams, UserInfo } from '@/types'

export const useUserStore = defineStore('user', () => {
  // 内部状态 - 从 localStorage 恢复
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>((() => {
    const stored = localStorage.getItem('userInfo')
    try { return stored ? JSON.parse(stored) : null } catch { return null }
  })())

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!userInfo.value)
  const username = computed(() => userInfo.value?.username || '')
  const role = computed(() => userInfo.value?.role || '')
  const isAdmin = computed(() => userInfo.value?.role === 'admin' || userInfo.value?.role === 'super_admin')
  const isSuperAdmin = computed(() => userInfo.value?.role === 'super_admin')
  // 普通用户（非 admin、非 super_admin）
  const isNormalUser = computed(() => userInfo.value?.role === 'user')

  // 登录
  const login = async (params: LoginParams) => {
    try {
      const res = await loginApi(params)
      token.value = res.data.access_token
      userInfo.value = res.data.user

      // 保存到本地存储
      localStorage.setItem('token', token.value)
      localStorage.setItem('userInfo', JSON.stringify(userInfo.value))

      return res.data
    } catch (error) {
      throw error
    }
  }

  // 检查认证状态
  const checkAuth = async () => {
    if (!token.value) {
      return false
    }

    try {
      const userInfoRes = await getCurrentUser()
      userInfo.value = userInfoRes.data
      return true
    } catch (error) {
      // token无效或过期
      logout()
      return false
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    userInfo.value = null

    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  // 初始化 - 有 token 时始终验证有效性
  const init = async () => {
    if (token.value) {
      await checkAuth()
    }
  }

  return {
    token,
    userInfo,
    isAuthenticated,
    username,
    role,
    isAdmin,
    isSuperAdmin,
    isNormalUser,
    login,
    logout,
    checkAuth,
    init
  }
})
