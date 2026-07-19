import request from './request'
import type {
  LogData,
  LogResponse,
  LogType,
  ApprovalConfig,
  SystemConfig,
  MaintenanceRecordData,
  RepairLogData,
  InstallationLogData,
  ScrapLogData,
  InspectionLogData,
  FaultReportData,
  PartsReplacementLogData,
  CalibrationLogData
} from '@/types'

// ========== 日志管理 API ==========

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

// 更新日志
export const updateLog = (id: number, data: any) => {
  return request.put(`/logs/${id}`, data)
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

// ========== 统计分析 API ==========

// 故障率统计
export const getFaultRate = (params: {
  start_date: string
  end_date: string
  group_by?: 'day' | 'week' | 'month'
}) => {
  return request.get('/analytics/fault-rate', { params })
}

// 维修成本统计
export const getMaintenanceCost = (params: {
  start_date: string
  end_date: string
  group_by?: 'day' | 'week' | 'month'
}) => {
  return request.get('/analytics/maintenance-cost', { params })
}

// 保养计划统计
export const getMaintenanceSchedule = (days?: number) => {
  return request.get('/analytics/maintenance-schedule', { params: { days } })
}

// 设备状态统计
export const getEquipmentStatus = () => {
  return request.get('/analytics/equipment-status')
}

// 日志类型统计
export const getLogTypeStats = (params?: {
  start_date?: string
  end_date?: string
}) => {
  return request.get('/analytics/log-type-stats', { params })
}

// 维修频率排名
export const getRepairRanking = (limit?: number) => {
  return request.get('/analytics/repair-ranking', { params: { limit } })
}

// 维修成本分析
export const getCostAnalysis = (params?: {
  start_date?: string
  end_date?: string
}) => {
  return request.get('/analytics/cost-analysis', { params })
}

// 配件消耗统计
export const getPartsUsage = (params?: {
  start_date?: string
  end_date?: string
}) => {
  return request.get('/analytics/parts-usage', { params })
}

// ========== 系统设置 API ==========

// 获取审批配置
export const getApprovalConfigs = () => {
  return request.get('/settings/approval-configs')
}

// 更新审批配置
export const updateApprovalConfig = (id: number, data: {
  log_type: string
  require_approval: boolean
}) => {
  return request.put(`/settings/approval-configs/${id}`, data)
}

// 获取系统配置
export const getSystemConfigs = () => {
  return request.get('/settings/system-configs')
}

// 获取单个系统配置
export const getSystemConfig = (key: string) => {
  return request.get(`/settings/system-configs/${key}`)
}

// 更新系统配置
export const updateSystemConfig = (key: string, data: {
  config_key: string
  config_value: any
  description?: string
}) => {
  return request.put(`/settings/system-configs/${key}`, data)
}

// 初始化默认配置
export const initDefaultConfigs = () => {
  return request.post('/settings/init-configs')
}

// ========== 设备管理 API ==========

// 创建设备
export const createEquipment = (data: any) => {
  return request.post('/equipment/', data)
}

// 获取设备列表
export const getEquipments = (params: {
  skip?: number
  limit?: number
  status?: string
  keyword?: string
}) => {
  return request.get('/equipment/', { params })
}

// 获取设备详情
export const getEquipment = (id: number) => {
  return request.get(`/equipment/${id}`)
}

// 更新设备
export const updateEquipment = (id: number, data: any) => {
  return request.put(`/equipment/${id}`, data)
}

// 删除设备
export const deleteEquipment = (id: number) => {
  return request.delete(`/equipment/${id}`)
}

// ========== 文件上传与OCR API ==========

// 上传单个文件
export const uploadFile = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upload/single', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 批量上传文件
export const uploadBatchFiles = (files: File[]) => {
  const formData = new FormData()
  files.forEach(file => {
    formData.append('files', file)
  })
  return request.post('/upload/batch', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 触发OCR识别
export const triggerOcrRecognition = (data: {
  file_path: string
  file_name: string
}) => {
  return request.post('/upload/ocr', data)
}

// 获取OCR识别状态
export const getOcrStatus = (taskId: string) => {
  return request.get(`/upload/ocr-status/${taskId}`)
}

// ========== 通知管理 API ==========

// 获取通知列表
export const getNotifications = (params?: {
  skip?: number
  limit?: number
  is_read?: boolean
}) => {
  return request.get('/notifications/', { params })
}

// 获取未读通知数量
export const getUnreadCount = () => {
  return request.get('/notifications/unread-count')
}

// 标记通知为已读
export const markNotificationRead = (id: number) => {
  return request.post(`/notifications/${id}/read`)
}

// 全部标记为已读
export const markAllRead = () => {
  return request.post('/notifications/read-all')
}

// 删除通知
export const deleteNotification = (id: number) => {
  return request.delete(`/notifications/${id}`)
}

// ========== 报表导出 API ==========

// 导出故障率统计
export const exportFaultRate = (data: {
  start_date: string
  end_date: string
  group_by?: 'day' | 'week' | 'month'
  format: 'excel' | 'pdf'
}) => {
  return request.post('/export/fault-rate', data, {
    responseType: 'blob'
  })
}

// 导出维修成本分析
export const exportMaintenanceCost = (data: {
  start_date: string
  end_date: string
  group_by?: 'day' | 'week' | 'month'
  format: 'excel' | 'pdf'
}) => {
  return request.post('/export/maintenance-cost', data, {
    responseType: 'blob'
  })
}

// 导出保养计划
export const exportMaintenanceSchedule = (data: {
  days: number
  format: 'excel' | 'pdf'
}) => {
  return request.post('/export/maintenance-schedule', data, {
    responseType: 'blob'
  })
}

// 导出配件消耗统计
export const exportPartsUsage = (data: {
  start_date?: string
  end_date?: string
  format: 'excel' | 'pdf'
}) => {
  return request.post('/export/parts-usage', data, {
    responseType: 'blob'
  })
}

// 导出维修频率排名
export const exportRepairRanking = (data: {
  limit?: number
  format: 'excel' | 'pdf'
}) => {
  return request.post('/export/repair-ranking', data, {
    responseType: 'blob'
  })
}

// 导出成本分析
export const exportCostAnalysis = (data: {
  start_date?: string
  end_date?: string
  format: 'excel' | 'pdf'
}) => {
  return request.post('/export/cost-analysis', data, {
    responseType: 'blob'
  })
}

// ========== 客户管理 API ==========

export { getCustomers, createCustomer, updateCustomer, deleteCustomer } from './customers'

// ========== 用户反馈 API ==========

export { getFeedbacks, submitFeedback, replyFeedback, markFeedbackRead } from './feedback'

// ========== 审计日志 API ==========

export { getAuditLogs } from './audit'

// ========== 认证与用户管理 API ==========

export {
  login,
  register,
  getCurrentUser,
  changePassword,
  getUsers,
  createUser,
  updateUser,
  deleteUser
} from './auth'
