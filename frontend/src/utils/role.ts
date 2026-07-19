/**
 * 角色相关的统一工具函数
 * 确保全站角色文字、样式、权限判断一致
 */

/** 后端角色值 */
export type RoleValue = 'super_admin' | 'admin' | 'user'

/** 角色中文标签 */
export const ROLE_LABELS: Record<string, string> = {
  super_admin: '超级管理员',
  admin: '管理员',
  user: '普通用户'
}

/** 角色 el-tag 类型 */
export const ROLE_TAG_TYPES: Record<string, '' | 'success' | 'info' | 'warning' | 'danger'> = {
  super_admin: 'danger',
  admin: 'warning',
  user: 'info'
}

/** 角色选项（用于下拉选择） */
export const ROLE_OPTIONS = [
  { label: '超级管理员', value: 'super_admin' },
  { label: '管理员', value: 'admin' },
  { label: '普通用户', value: 'user' }
]

/** 获取角色中文标签 */
export function getRoleLabel(role: string | undefined | null): string {
  if (!role) return '未知'
  return ROLE_LABELS[role] || role
}

/** 获取角色 el-tag 类型 */
export function getRoleTagType(role: string | undefined | null): '' | 'success' | 'info' | 'warning' | 'danger' {
  if (!role) return 'info'
  return ROLE_TAG_TYPES[role] || 'info'
}

/** 是否为管理员（含超级管理员） */
export function isAdminRole(role: string | undefined | null): boolean {
  return role === 'admin' || role === 'super_admin'
}

/** 是否为超级管理员 */
export function isSuperAdminRole(role: string | undefined | null): boolean {
  return role === 'super_admin'
}
