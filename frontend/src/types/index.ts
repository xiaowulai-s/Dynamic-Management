// 登录参数
export interface LoginParams {
  username: string
  password: string
}

// 注册参数
export interface RegisterParams {
  username: string
  password: string
  confirm_password: string
}

// 用户信息
export interface UserInfo {
  id: number
  username: string
  role: string
  is_active: boolean
  created_at: string
}

// 设备参数
export interface EquipmentParams {
  code: string
  name: string
  model?: string
  specification?: string
  manufacturer?: string
  purchase_date?: string
  supplier?: string
  location?: string
  status?: 'running' | 'stopped' | 'repairing' | 'scrapped'
  lifecycle_status?: 'active' | 'maintenance' | 'scrapped'
}

// 设备响应
export interface EquipmentResponse extends EquipmentParams {
  id: number
  created_by: number
  created_at: string
  updated_at: string
}

// 设备详情
export interface EquipmentDetail extends EquipmentResponse {
  total_logs: number
  pending_logs: number
  last_maintenance_date?: string
  next_maintenance_date?: string
  total_repair_cost: number
}

// 日志类型
export type LogType =
  | 'installation'
  | 'repair'
  | 'scrap'
  | 'inspection'
  | 'maintenance'
  | 'fault'
  | 'parts'
  | 'calibration'

// 日志状态
export type LogStatus = 'pending' | 'approved' | 'rejected'

// 日志基础
export interface LogBase {
  equipment_id: number
  log_type: LogType
  description?: string
  attachments?: string[]
}

// 安装日志
export interface InstallationLogData extends LogBase {
  log_type: 'installation'
  installation_date: string
  installer?: string
  location?: string
  acceptance_status?: string
}

// 维修日志
export interface RepairLogData extends LogBase {
  log_type: 'repair'
  repair_date: string
  fault_description: string
  solution?: string
  cost?: number
  repair_time?: number
}

// 报废日志
export interface ScrapLogData extends LogBase {
  log_type: 'scrap'
  scrap_date: string
  scrap_reason: string
  residual_value?: number
}

// 巡检日志
export interface InspectionLogData extends LogBase {
  log_type: 'inspection'
  inspection_date: string
  inspector?: string
  inspection_items?: any[]
  result?: 'normal' | 'abnormal'
}

// 保养记录
export interface MaintenanceRecordData extends LogBase {
  log_type: 'maintenance'
  maintenance_date: string
  maintenance_items?: any[]
  next_maintenance_date?: string
}

// 故障报修
export interface FaultReportData extends LogBase {
  log_type: 'fault'
  fault_date: string
  fault_level?: 'minor' | 'major' | 'critical'
  reporter?: string
  fault_description: string
  handle_status?: 'pending' | 'handling' | 'resolved'
}

// 配件更换
export interface PartsReplacementLogData extends LogBase {
  log_type: 'parts'
  replacement_date: string
  parts_name: string
  parts_code?: string
  quantity: number
  cost?: number
}

// 校准记录
export interface CalibrationLogData extends LogBase {
  log_type: 'calibration'
  calibration_date: string
  calibration_org?: string
  calibration_result?: 'qualified' | 'unqualified'
  next_calibration_date?: string
}

// 日志联合类型
export type LogData =
  | InstallationLogData
  | RepairLogData
  | ScrapLogData
  | InspectionLogData
  | MaintenanceRecordData
  | FaultReportData
  | PartsReplacementLogData
  | CalibrationLogData

// 日志响应
export interface LogResponse extends LogBase {
  id: number
  equipment_name?: string
  operator_name: string
  status: LogStatus
  approved_at?: string
  approver_name?: string
  rejection_reason?: string
  created_at: string
}

// 审批配置
export interface ApprovalConfig {
  id: number
  log_type: string
  require_approval: boolean
  created_at: string
}

// 系统配置
export interface SystemConfig {
  id: number
  config_key: string
  config_value: any
  description?: string
  updated_at: string
}
