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
  // OAuth2PasswordRequestForm 要求 application/x-www-form-urlencoded
  // 使用 URLSearchParams 保证按 x-www-form-urlencoded 编码（FormData 会被浏览器按 multipart 发送）
  const formBody = new URLSearchParams()
  formBody.append('username', params.username)
  formBody.append('password', params.password)

  return request.post('/auth/login', formBody, {
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

// 用户管理（管理员）
export const getUsers = () => request.get('/auth/users')
export const createUser = (data: { username: string; password: string; role: string; is_active: boolean }) =>
  request.post('/auth/users', data)
export const updateUser = (id: number, data: { role?: string; is_active?: boolean; password?: string }) =>
  request.put(`/auth/users/${id}`, data)
export const deleteUser = (id: number) => request.delete(`/auth/users/${id}`)
