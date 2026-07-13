import request from './request'

// 创建日志
export const createLog = (data: any) => {
  return request.post('/logs/', data)
}

// 获取日志列表
export const getLogs = (params: {
  skip?: number
  limit?: number
  equipment_id?: number
  log_type?: string
  status?: string
  keyword?: string
}) => {
  return request.get('/logs/', { params })
}

// 获取日志详情
export const getLogDetail = (id: number) => {
  return request.get(`/logs/${id}`)
}

// 审批日志
export const approveLog = (id: number, approved: boolean, rejection_reason?: string) => {
  return request.post(`/logs/${id}/approve`, {
    approved,
    rejection_reason
  })
}

// 删除日志
export const deleteLog = (id: number) => {
  return request.delete(`/logs/${id}`)
}

// 获取日志类型列表
export const getLogTypes = () => {
  return request.get('/logs/types/list')
}
