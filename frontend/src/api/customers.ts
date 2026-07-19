import request from './request'

// 获取客户列表
export const getCustomers = (params?: {
  skip?: number
  limit?: number
  keyword?: string
}) => {
  return request.get('/customers/', { params })
}

// 创建客户
export const createCustomer = (data: {
  name: string
  contact?: string
  phone?: string
  email?: string
  address?: string
  remark?: string
}) => {
  return request.post('/customers/', data)
}

// 更新客户
export const updateCustomer = (id: number, data: Partial<{
  name: string
  contact?: string
  phone?: string
  email?: string
  address?: string
  remark?: string
}>) => {
  return request.put(`/customers/${id}`, data)
}

// 删除客户
export const deleteCustomer = (id: number) => {
  return request.delete(`/customers/${id}`)
}
