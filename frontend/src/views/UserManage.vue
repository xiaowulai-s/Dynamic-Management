<template>
  <div class="user-page">
    <!-- 1. 页头 -->
    <header class="page-head">
      <div class="head-left">
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">
          共 <span class="numeric">{{ stats.total }}</span> 个用户 · 管理员 <span class="numeric">{{ stats.admins + stats.superAdmins }}</span> 人 · 普通用户 <span class="numeric">{{ stats.users }}</span> 人
        </p>
      </div>
      <div class="head-right">
        <el-button v-if="userStore.isAdmin" type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          <span>添加用户</span>
        </el-button>
      </div>
    </header>

    <!-- 2. 统计概览条 -->
    <section class="stat-bar card-minimal" :class="{ 'stat-bar-4': userStore.isSuperAdmin }">
      <div class="stat-item">
        <div class="stat-label">
          <el-icon><User /></el-icon>
          <span>总用户数</span>
        </div>
        <div class="stat-value">
          <span class="numeric">{{ stats.total }}</span>
          <span class="trend trend-neutral">人</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-label">
          <el-icon><UserFilled /></el-icon>
          <span>管理员</span>
        </div>
        <div class="stat-value">
          <span class="numeric">{{ stats.admins }}</span>
          <span class="trend trend-neutral">人</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-label">
          <el-icon><Avatar /></el-icon>
          <span>普通用户</span>
        </div>
        <div class="stat-value">
          <span class="numeric">{{ stats.users }}</span>
          <span class="trend trend-neutral">人</span>
        </div>
      </div>
      <div v-if="userStore.isSuperAdmin" class="stat-item">
        <div class="stat-label">
          <el-icon><Histogram /></el-icon>
          <span>超级管理员</span>
        </div>
        <div class="stat-value">
          <span class="numeric">{{ stats.superAdmins }}</span>
          <span class="trend trend-neutral">人</span>
        </div>
      </div>
    </section>

    <!-- 3. 用户表格 -->
    <section class="table-card card-minimal">
      <div class="table-head">
        <h3 class="section-title">用户列表</h3>
        <el-button text @click="fetchUsers" :loading="loading">
          <el-icon><Refresh /></el-icon>
          <span>刷新</span>
        </el-button>
      </div>
      <el-table :data="userList" v-loading="loading" class="user-table">
        <el-table-column prop="username" label="用户名" min-width="200">
          <template #default="{ row }">
            <div class="user-cell">
              <div class="user-avatar" :class="'avatar-' + row.role">
                {{ (row.username || '?').charAt(0).toUpperCase() }}
              </div>
              <div class="user-meta">
                <span class="user-name-text">{{ row.username }}</span>
                <span v-if="row.id === userStore.userInfo?.id" class="user-self">我</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="140" align="center">
          <template #default="{ row }">
            <span class="badge" :class="roleBadgeClass(row.role)">
              <span class="badge-dot"></span>
              {{ getRoleLabel(row.role) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="120" align="center">
          <template #default="{ row }">
            <span class="badge" :class="row.is_active ? 'badge-active' : 'badge-inactive'">
              <span class="badge-dot"></span>
              {{ row.is_active ? '启用' : '禁用' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" align="center">
          <template #default="{ row }">
            <span class="cell-date">{{ formatDate(row.created_at) }}</span>
          </template>
        </el-table-column>
        <el-table-column v-if="userStore.isAdmin" label="操作" min-width="160" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button v-if="userStore.isAdmin" text size="small" @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
                <span>编辑</span>
              </el-button>
              <el-button
                v-if="canDelete(row)"
                text
                size="small"
                class="btn-danger-text"
                @click="handleDelete(row)"
              >
                <el-icon><Delete /></el-icon>
                <span>删除</span>
              </el-button>
            </div>
          </template>
        </el-table-column>

        <template #empty>
          <div class="empty-state">
            <div class="empty-icon">
              <el-icon><User /></el-icon>
            </div>
            <p class="empty-title">暂无用户</p>
            <p class="empty-sub">还没有任何用户，点击下方按钮添加第一个用户</p>
            <el-button v-if="userStore.isAdmin" type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              <span>添加用户</span>
            </el-button>
          </div>
        </template>
      </el-table>
    </section>

    <!-- 4. 添加/编辑用户对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="480px"
      destroy-on-close
      class="form-dialog"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="3-50 位字符"
            :disabled="isEditMode"
            maxlength="50"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            show-password
            :placeholder="isEditMode ? '留空表示不修改密码' : '至少 6 位'"
          />
        </el-form-item>
        <el-form-item label="角色" prop="role">
          <el-select v-model="form.role" placeholder="请选择角色" class="form-full">
            <el-option
              v-for="opt in roleOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="form.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          {{ isEditMode ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  Plus,
  Edit,
  Delete,
  User,
  UserFilled,
  Avatar,
  Histogram,
  Refresh
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getUsers, createUser, updateUser, deleteUser } from '@/api/auth'
import { getRoleLabel } from '@/utils/role'

const userStore = useUserStore()
const loading = ref(false)
const userList = ref<any[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const isEditMode = ref(false)
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()
const submitLoading = ref(false)

const form = reactive({
  username: '',
  password: '',
  role: 'user',
  is_active: true
})

// 表单校验规则（编辑时密码非必填）
const rules = computed<FormRules>(() => ({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度 3-50', trigger: 'blur' }
  ],
  password: isEditMode.value
    ? [{ min: 6, message: '密码至少 6 位', trigger: 'blur' }]
    : [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码至少 6 位', trigger: 'blur' }
      ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }]
}))

// 角色选项（admin 看不到 super_admin 选项）
const roleOptions = computed(() => {
  if (userStore.isSuperAdmin) {
    return [
      { label: '超级管理员', value: 'super_admin' },
      { label: '管理员', value: 'admin' },
      { label: '普通用户', value: 'user' }
    ]
  }
  return [
    { label: '管理员', value: 'admin' },
    { label: '普通用户', value: 'user' }
  ]
})

// 统计
const stats = computed(() => {
  const total = userList.value.length
  const superAdmins = userList.value.filter(u => u.role === 'super_admin').length
  const admins = userList.value.filter(u => u.role === 'admin').length
  const users = userList.value.filter(u => u.role === 'user').length
  return { total, superAdmins, admins, users }
})

const roleBadgeClass = (role: string) => {
  const map: Record<string, string> = {
    super_admin: 'badge-super',
    admin: 'badge-admin',
    user: 'badge-user'
  }
  return map[role] || 'badge-user'
}

const formatDate = (t: string) => (t ? new Date(t).toLocaleString('zh-CN') : '')

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await getUsers()
    userList.value = res.data
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEditMode.value = false
  editingId.value = null
  dialogTitle.value = '添加用户'
  form.username = ''
  form.password = ''
  form.role = 'user'
  form.is_active = true
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEditMode.value = true
  editingId.value = row.id
  dialogTitle.value = '编辑用户'
  form.username = row.username
  form.password = '' // 编辑时密码留空表示不修改
  form.role = row.role
  form.is_active = row.is_active
  dialogVisible.value = true
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
  } catch {
    return
  }
  submitLoading.value = true
  try {
    if (isEditMode.value && editingId.value) {
      const data: { role: string; is_active: boolean; password?: string } = {
        role: form.role,
        is_active: form.is_active
      }
      if (form.password) data.password = form.password
      await updateUser(editingId.value, data)
      ElMessage.success('更新成功')
    } else {
      await createUser({
        username: form.username,
        password: form.password,
        role: form.role,
        is_active: form.is_active
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchUsers()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm(`确定删除用户「${row.username}」吗？此操作不可恢复。`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        await deleteUser(row.id)
        ElMessage.success('删除成功')
        fetchUsers()
      } catch (e: any) {
        ElMessage.error(e?.response?.data?.detail || '删除失败')
      }
    })
    .catch(() => {})
}

// 删除按钮是否可见（不能删自己；admin 不能删 super_admin）
const canDelete = (row: any) => {
  if (row.id === userStore.userInfo?.id) return false // 不能删自己
  if (!userStore.isSuperAdmin && row.role === 'super_admin') return false // admin 不能删 super_admin
  return true
}

const handleDialogClose = () => {
  formRef.value?.resetFields()
  isEditMode.value = false
  editingId.value = null
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
/* ============================================================
   UserManage.vue · 方案A 现代简约风（与 Logs.vue 一致）
   ============================================================ */

.user-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* ===== 通用卡片（细线分隔，无投影） ===== */
.card-minimal {
  background: var(--surface-overlay);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  box-shadow: none;
}

/* ===== 数字 ===== */
.numeric {
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

/* ===== 区块标题竖条 ===== */
.section-title {
  position: relative;
  padding-left: var(--space-3);
  font-size: var(--text-sm);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
}
.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  background: var(--color-primary-600);
  border-radius: 2px;
}

/* ===== 1. 页头 ===== */
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.head-left {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.page-title {
  margin: 0;
  font-size: var(--text-xl);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
  letter-spacing: -0.01em;
  line-height: 1.3;
}

.page-subtitle {
  margin: 0;
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

.page-subtitle .numeric {
  color: var(--text-secondary);
  font-weight: var(--font-w-medium);
}

.head-right {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

/* ===== 2. 统计概览条 ===== */
.stat-bar {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  overflow: hidden;
}

.stat-bar-4 {
  grid-template-columns: repeat(4, 1fr);
}

.stat-item {
  padding: var(--space-4) var(--space-5);
  border-right: 1px solid var(--border-default);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  min-width: 0;
}

.stat-item:last-child {
  border-right: none;
}

.stat-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
  font-weight: var(--font-w-medium);
}

.stat-label .el-icon {
  font-size: 14px;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: var(--space-2);
}

.stat-value .numeric {
  font-size: var(--text-lg);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
  line-height: 1.2;
}

.trend {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-size: var(--text-xs);
  font-weight: var(--font-w-medium);
  font-family: var(--font-mono);
}

.trend-neutral {
  color: var(--text-tertiary);
}

/* ===== 3. 表格卡片 ===== */
.table-card {
  overflow: hidden;
}

.table-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-5);
  border-bottom: 1px solid var(--border-default);
}

.table-head .section-title {
  margin: 0;
}

.user-table {
  width: 100%;
  --el-table-header-bg-color: var(--color-neutral-50);
  --el-table-row-hover-bg-color: var(--color-neutral-100);
  --el-table-border-color: var(--border-default);
  --el-table-border: 1px solid var(--border-default);
}

.table-card :deep(.el-table) {
  border-radius: var(--radius-md);
  border: none;
}

.table-card :deep(.el-table th.el-table__cell) {
  background: var(--color-neutral-50);
  color: var(--text-tertiary);
  font-weight: var(--font-w-medium);
  font-size: var(--text-xs);
  letter-spacing: 0.02em;
  border-bottom: 1px solid var(--border-default);
}

.table-card :deep(.el-table .el-table__cell) {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-default);
}

.table-card :deep(.el-table .el-table__row:hover > td.el-table__cell) {
  background: var(--color-neutral-100) !important;
}

.table-card :deep(.el-table__inner-wrapper::before),
.table-card :deep(.el-table::before) {
  display: none;
}

.table-card :deep(.el-table--border .el-table__inner-wrapper::after),
.table-card :deep(.el-table__border-left-patch) {
  display: none;
}

/* 用户名单元格 */
.user-cell {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-xs);
  font-weight: var(--font-w-semibold);
  flex-shrink: 0;
  background: var(--color-primary-50);
  color: var(--color-primary-700);
}

.user-avatar.avatar-super_admin {
  background: color-mix(in srgb, var(--color-danger-500) 16%, transparent);
  color: var(--color-danger-600);
}

.user-avatar.avatar-admin {
  background: color-mix(in srgb, var(--color-primary-600) 14%, transparent);
  color: var(--color-primary-600);
}

.user-avatar.avatar-user {
  background: var(--color-neutral-100);
  color: var(--text-tertiary);
}

.user-meta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.user-name-text {
  font-weight: var(--font-w-medium);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-self {
  font-size: 10px;
  font-weight: var(--font-w-semibold);
  color: var(--color-primary-600);
  background: color-mix(in srgb, var(--color-primary-600) 12%, transparent);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.cell-date {
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  font-variant-numeric: tabular-nums;
}

/* 行操作按钮 */
.row-actions {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  flex-wrap: wrap;
}

.row-actions :deep(.el-button) {
  padding: 4px 6px;
  height: auto;
}

.row-actions :deep(.el-button .el-icon + span) {
  margin-left: 2px;
  font-size: var(--text-xs);
}

.btn-danger-text {
  color: var(--color-danger-600) !important;
}

.btn-danger-text:hover {
  color: var(--color-danger-700) !important;
  background: var(--color-danger-50) !important;
}

/* ===== Badge 系统 ===== */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  line-height: 1.5;
  white-space: nowrap;
  border: 1px solid transparent;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  flex-shrink: 0;
}

.badge-super {
  background: color-mix(in srgb, var(--color-danger-500) 12%, transparent);
  color: var(--color-danger-600);
}

.badge-admin {
  background: color-mix(in srgb, var(--color-primary-600) 12%, transparent);
  color: var(--color-primary-600);
}

.badge-user {
  background: var(--color-neutral-100);
  color: var(--text-tertiary);
}

.badge-active {
  background: color-mix(in srgb, var(--color-success-500) 12%, transparent);
  color: var(--color-success-600);
}

.badge-inactive {
  background: color-mix(in srgb, var(--color-danger-500) 12%, transparent);
  color: var(--color-danger-600);
}

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-8) var(--space-4);
  gap: var(--space-2);
}

.empty-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-neutral-100);
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-2);
}

.empty-icon .el-icon {
  font-size: 24px;
}

.empty-title {
  margin: 0;
  font-size: var(--text-sm);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
}

.empty-sub {
  margin: 0 0 var(--space-3) 0;
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* ===== 对话框 ===== */
.form-dialog :deep(.el-dialog) {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-default);
  box-shadow: var(--shadow-2xl);
}

.form-dialog :deep(.el-dialog__header) {
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--border-default);
  margin-bottom: 0;
}

.form-dialog :deep(.el-dialog__title) {
  font-size: var(--text-md);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
}

.form-dialog :deep(.el-dialog__body) {
  padding: var(--space-5);
}

.form-dialog :deep(.el-dialog__footer) {
  padding: var(--space-3) var(--space-5);
  border-top: 1px solid var(--border-default);
}

.form-full {
  width: 100%;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .page-head {
    flex-direction: column;
    align-items: stretch;
  }

  .head-right {
    justify-content: flex-start;
  }

  .stat-bar,
  .stat-bar-4 {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-item:nth-child(2) {
    border-right: none;
  }

  .stat-item:nth-child(1),
  .stat-item:nth-child(2) {
    border-bottom: 1px solid var(--border-default);
  }

  .table-card :deep(.el-table) {
    font-size: var(--text-xs);
  }

  .table-card :deep(.el-table .el-table__cell) {
    padding: 8px;
  }
}
</style>
