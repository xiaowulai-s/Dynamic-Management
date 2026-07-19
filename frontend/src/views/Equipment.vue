<template>
  <div class="equipment-page">
    <div class="page-header">
      <h2>设备管理</h2>
      <el-button type="primary" @click="handleAdd" v-if="userStore.isAdmin">
        <el-icon><Plus /></el-icon>
        新增设备
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="运行中" value="running" />
            <el-option label="停机" value="stopped" />
            <el-option label="维修中" value="repairing" />
            <el-option label="已报废" value="scrapped" />
          </el-select>
        </el-form-item>

        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="设备名称/编号/型号"
            clearable
            class="keyword-input"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 设备列表 -->
    <el-card class="table-card">
      <el-table
        :data="equipmentList"
        v-loading="loading"
        class="w-full"
      >
        <el-table-column prop="code" label="设备编号" min-width="120" show-overflow-tooltip />
        <el-table-column prop="name" label="设备名称" min-width="140" show-overflow-tooltip />
        <el-table-column prop="model" label="型号" min-width="100" show-overflow-tooltip />
        <el-table-column prop="location" label="位置" min-width="100" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" min-width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lifecycle_status" label="生命周期" min-width="90" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ getLifecycleLabel(row.lifecycle_status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" min-width="150" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="180" fixed="right" align="center">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" size="small" @click="handleView(row)">
                查看
              </el-button>
              <el-button type="warning" size="small" @click="handleEdit(row)" v-if="userStore.isAdmin">
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(row)" v-if="userStore.isAdmin">
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <template #empty>
        <el-empty description="暂无设备数据，请添加设备" />
      </template>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchEquipments"
          @current-change="fetchEquipments"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备编号" prop="code">
              <el-input v-model="formData.code" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备名称" prop="name">
              <el-input v-model="formData.name" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="型号">
              <el-input v-model="formData.model" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="安装位置">
              <el-input v-model="formData.location" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生产厂家">
              <el-input v-model="formData.manufacturer" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商">
              <el-input v-model="formData.supplier" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="购置日期">
              <el-date-picker
                v-model="formData.purchase_date"
                type="date"
                placeholder="选择日期"
                class="form-full"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备状态">
              <el-select v-model="formData.status" class="form-full">
                <el-option label="运行中" value="running" />
                <el-option label="停机" value="stopped" />
                <el-option label="维修中" value="repairing" />
                <el-option label="已报废" value="scrapped" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="规格">
          <el-input
            v-model="formData.specification"
            type="textarea"
            :rows="2"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 设备详情对话框 -->
    <el-dialog v-model="detailVisible" title="设备详情" width="900px">
      <div v-if="currentEquipment" class="equipment-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="设备编号">{{ currentEquipment.code }}</el-descriptions-item>
          <el-descriptions-item label="设备名称">{{ currentEquipment.name }}</el-descriptions-item>
          <el-descriptions-item label="型号">{{ currentEquipment.model || '-' }}</el-descriptions-item>
          <el-descriptions-item label="安装位置">{{ currentEquipment.location || '-' }}</el-descriptions-item>
          <el-descriptions-item label="生产厂家">{{ currentEquipment.manufacturer || '-' }}</el-descriptions-item>
          <el-descriptions-item label="供应商">{{ currentEquipment.supplier || '-' }}</el-descriptions-item>
          <el-descriptions-item label="购置日期">
            {{ currentEquipment.purchase_date || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="设备状态">
            <el-tag :type="getStatusType(currentEquipment.status)">
              {{ getStatusLabel(currentEquipment.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h4>统计信息</h4>
        <el-row :gutter="20" class="stats">
          <el-col :span="8">
            <el-statistic title="总日志数" :value="currentEquipment.total_logs" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="待审批日志" :value="currentEquipment.pending_logs" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="累计维修费用" :value="currentEquipment.total_repair_cost" />
          </el-col>
        </el-row>

        <el-divider />

        <div class="actions">
          <el-button type="primary" @click="goToLogs(currentEquipment.id)">
            <el-icon><Document /></el-icon>
            查看日志
          </el-button>
          <el-button type="success" @click="goToAddLog(currentEquipment.id)">
            <el-icon><Edit /></el-icon>
            提交日志
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import { Plus, Document, Edit } from '@element-plus/icons-vue'
import {
  getEquipments,
  createEquipment,
  updateEquipment,
  deleteEquipment,
  getEquipment
} from '@/api/equipment'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const equipmentList = ref([])

const searchForm = reactive({
  status: '',
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const dialogVisible = ref(false)
const dialogTitle = ref('新增设备')
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const submitLoading = ref(false)

const detailVisible = ref(false)
const currentEquipment = ref<any>(null)

const formData = reactive({
  code: '',
  name: '',
  model: '',
  specification: '',
  manufacturer: '',
  purchase_date: '',
  supplier: '',
  location: '',
  status: 'running',
  lifecycle_status: 'active'
})

const formRules = {
  code: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }]
}

const fetchEquipments = async () => {
  loading.value = true
  try {
    const res = await getEquipments({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm
    })
    equipmentList.value = res.data || []
    pagination.total = (res as any).total || res.data.length
  } catch (error) {
    ElMessage.error('获取设备列表失败')
  } finally {
    loading.value = false
  }
}

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    running: 'success',
    stopped: 'info',
    repairing: 'warning',
    scrapped: 'danger'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    running: '运行中',
    stopped: '停机',
    repairing: '维修中',
    scrapped: '已报废'
  }
  return labels[status] || status
}

const getLifecycleLabel = (status: string) => {
  const labels: Record<string, string> = {
    active: '在用',
    maintenance: '保养中',
    scrapped: '已报废'
  }
  return labels[status] || status
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const handleSearch = () => {
  pagination.page = 1
  fetchEquipments()
}

const handleReset = () => {
  searchForm.status = ''
  searchForm.keyword = ''
  handleSearch()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增设备'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  dialogTitle.value = '编辑设备'
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleView = async (row: any) => {
  try {
    const res = await getEquipment(row.id)
    currentEquipment.value = res.data
    detailVisible.value = true
  } catch (error) {
    ElMessage.error('获取设备详情失败')
  }
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除设备 "${row.name}" 吗？此操作不可恢复。`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    try {
      await deleteEquipment(row.id)
      ElMessage.success('删除成功')
      fetchEquipments()
    } catch (err: any) {
      const detail = err?.response?.data?.detail || ''
      // 识别"有关联日志"错误，提供强制删除二次确认
      if (detail.includes('关联日志')) {
        try {
          await ElMessageBox.confirm(
            `${detail}\n\n强制删除将一并清除该设备的所有日志记录，是否继续？`,
            '需要确认',
            {
              confirmButtonText: '强制删除',
              cancelButtonText: '取消',
              type: 'warning'
            }
          )
          await deleteEquipment(row.id, true)
          ElMessage.success('删除成功')
          fetchEquipments()
        } catch (e2: any) {
          if (e2 !== 'cancel') {
            ElMessage.error(e2?.response?.data?.detail || '删除失败')
          }
        }
      } else {
        ElMessage.error(detail || '删除失败')
      }
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.response?.data?.detail || '删除失败')
    }
  }
}

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    submitLoading.value = true
    // 转换日期格式
    const submitData = {
      ...formData,
      purchase_date: formData.purchase_date
        ? new Date(formData.purchase_date).toISOString().split('T')[0]
        : null
    }

    if (isEdit.value) {
      await updateEquipment(submitData.id, submitData)
      ElMessage.success('更新成功')
    } else {
      await createEquipment(submitData)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    fetchEquipments()
  } catch (error: any) {
    if (error !== false) {
      ElMessage.error(error?.message || '操作失败')
    }
  } finally {
    submitLoading.value = false
  }
}

const handleDialogClose = () => {
  resetForm()
}

const resetForm = () => {
  formData.code = ''
  formData.name = ''
  formData.model = ''
  formData.specification = ''
  formData.manufacturer = ''
  formData.purchase_date = ''
  formData.supplier = ''
  formData.location = ''
  formData.status = 'running'
  formData.lifecycle_status = 'active'
  formRef.value?.resetFields()
}

const goToLogs = (equipmentId: number) => {
  router.push(`/logs?equipment_id=${equipmentId}`)
}

const goToAddLog = (equipmentId: number) => {
  router.push(`/logs?equipment_id=${equipmentId}&action=add`)
}

onMounted(() => {
  fetchEquipments()
})
</script>

<style scoped>
.equipment-page {
  /* padding 由 .content 全局控制 */
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-6);  /* 32px */
}

.page-header h2 {
  margin: 0;
}

.search-card {
  margin-bottom: var(--space-6);  /* 32px */
}

/* 搜索卡片优化 */
.search-card :deep(.el-card__body) {
  padding: var(--space-6);
}

.search-card :deep(.el-form-item) {
  margin-bottom: 0;
}

.table-card {
  margin-bottom: var(--space-6);  /* 32px */
  overflow: hidden;
}

/* 表格优化 */
.table-card :deep(.el-table) {
  border-radius: var(--radius-md);
}

.table-card :deep(.el-table__cell) {
  padding: var(--space-4) var(--space-5);
}

/* 操作列按钮始终一行显示，不换行 */
.table-actions {
  display: flex;
  flex-wrap: nowrap;
  gap: 4px;
  align-items: center;
}

.table-actions .el-button {
  margin-left: 0;
  flex-shrink: 0;
}

/* 分页 */
.pagination {
  margin-top: var(--space-6);  /* 32px */
  display: flex;
  justify-content: flex-end;
  padding: 0 var(--space-4);
}

.equipment-detail {
  padding: var(--space-5);
}

.stats {
  margin: var(--space-6) 0;
}

.actions {
  margin-top: var(--space-6);
  display: flex;
  gap: var(--space-4);
}

.form-full {
  width: 100%;
}

/* 对话框优化 */
.equipment-dialog :deep(.el-dialog) {
  border-radius: var(--radius-lg);
}

.equipment-dialog :deep(.el-dialog__header) {
  padding: var(--space-6);
}

.equipment-dialog :deep(.el-dialog__body) {
  padding: var(--space-6);
}
</style>
