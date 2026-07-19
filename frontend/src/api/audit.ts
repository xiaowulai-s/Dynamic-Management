import request from './request'

// 获取审计日志列表
export const getAuditLogs = (params?: {
  skip?: number
  limit?: number
  action?: string
  start_date?: string
  end_date?: string
}) => {
  return request.get('/audit/', { params })
}

// 获取审计统计
export const getAuditStats = (params?: {
  start_date?: string
  end_date?: string
}) => {
  return request.get('/audit/stats', { params })
}
