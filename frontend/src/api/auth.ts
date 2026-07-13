import request from './request'

export interface LoginParams {
  username: string
  password: string
}

export interface UserInfo {
  id: number
  username: string
  role: string
  is_active: boolean
  created_at: string
}

export interface RegisterParams {
  username: string
  password: string
  confirm_password: string
}

// 登录
export const login = (params: LoginParams) => {
  // 使用FormData格式（OAuth2标准）
  const formData = new FormData()
  formData.append('username', params.username)
  formData.append('password', params.password)

  return request.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
}

// 注册
export const register = (params: RegisterParams) => {
  return request.post('/auth/register', params)
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return request.get('/auth/me')
}

// 修改密码
export const changePassword = (oldPassword: string, newPassword: string) => {
  return request.post('/auth/change-password', {
    old_password: oldPassword,
    new_password: newPassword
  })
}

// 获取用户列表
export const getUsers = (params: { skip?: number; limit?: number }) => {
  return request.get('/auth/users', { params })
}
