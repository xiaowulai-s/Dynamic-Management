import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getCurrentUser } from '@/api/auth'
import type { LoginParams, UserInfo } from '@/types'

export const useUserStore = defineStore('user', () => {
  // 内部状态
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref<UserInfo | null>(null)

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!userInfo.value)
  const username = computed(() => userInfo.value?.username || '')
  const role = computed(() => userInfo.value?.role || '')
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

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

  // 初始化
  const init = async () => {
    if (token.value && !userInfo.value) {
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
    login,
    logout,
    checkAuth,
    init
  }
})
