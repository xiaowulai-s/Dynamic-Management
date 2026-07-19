import request from './request'
import type {
  EquipmentResponse,
  EquipmentDetail,
  EquipmentParams
} from '@/types'

// 创建设备
export const createEquipment = (data: EquipmentParams) => {
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
export const updateEquipment = (id: number, data: Partial<EquipmentParams>) => {
  return request.put(`/equipment/${id}`, data)
}

// 删除设备
export const deleteEquipment = (id: number, force: boolean = false) => {
  return request.delete(`/equipment/${id}`, { params: { force } })
}
