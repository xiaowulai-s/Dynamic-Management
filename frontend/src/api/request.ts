import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 添加token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 如果是文件上传，不设置Content-Type，让浏览器自动设置
    if (config.headers['Content-Type'] === 'multipart/form-data') {
      delete config.headers['Content-Type']
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const url: string = error.config?.url || ''
    const isAuthEndpoint = url.startsWith('/auth/login') || url.startsWith('/auth/register')

    // 处理错误
    if (error.response?.status === 401) {
      // 登录/注册接口的 401 直接抛给调用方显示错误，不要跳转
      if (!isAuthEndpoint) {
        // 已经在登录页时不再跳转，避免 401 死循环刷新
        const isOnLoginPage = window.location.pathname === '/login' || window.location.pathname === '/register'
        if (!isOnLoginPage) {
          // token过期或无效，清除本地存储并跳转到登录页
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          window.location.href = '/login'
        }
      }
    } else if (error.response?.status === 403) {
      // 权限不足，跳转到403页面或显示提示
      ElMessage.error('权限不足，无法访问该资源')
    }

    return Promise.reject(error)
  }
)

export default request
