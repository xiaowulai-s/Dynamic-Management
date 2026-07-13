<template>
  <div class="logs-page">
    <div class="page-header">
      <h2>日志管理</h2>
      <div class="header-actions">
        <el-button type="primary" @click="handleBatchUpload">
          <el-icon><Upload /></el-icon>
          批量上传识别
        </el-button>
        <el-button type="success" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          提交日志
        </el-button>
      </div>
    </div>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="日志类型">
          <el-select v-model="searchForm.log_type" placeholder="全部" clearable>
            <el-option label="设备安装" value="installation" />
            <el-option label="设备维修" value="repair" />
            <el-option label="设备报废" value="scrap" />
            <el-option label="日常巡检" value="inspection" />
            <el-option label="保养记录" value="maintenance" />
            <el-option label="故障报修" value="fault" />
            <el-option label="配件更换" value="parts" />
            <el-option label="校准记录" value="calibration" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>

        <el-form-item label="设备">
          <el-select
            v-model="searchForm.equipment_id"
            placeholder="全部设备"
            clearable
            filterable
            style="width: 200px"
          >
            <el-option
              v-for="eq in equipmentList"
              :key="eq.id"
              :label="`${eq.code} - ${eq.name}`"
              :value="eq.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="搜索描述..."
            clearable
            style="width: 200px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 日志列表 -->
    <el-card class="table-card">
      <el-table
        :data="logList"
        v-loading="loading"
        class="form-full"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="created_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="equipment_name" label="设备名称" min-width="150" />
        <el-table-column prop="log_type" label="日志类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getLogTypeColor(row.log_type)">
              {{ getLogTypeLabel(row.log_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator_name" label="提交人" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button
              v-if="row.status === 'pending' && (userStore.isAdmin || row.operator_name === userStore.username)"
              type="warning"
              size="small"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'pending' && userStore.isAdmin"
              type="success"
              size="small"
              @click="handleApprove(row)"
            >
              审批
            </el-button>
            <el-button
              v-if="row.status === 'pending' && (userStore.isAdmin || row.operator_name === userStore.username)"
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <template #empty>
        <el-empty description="暂无日志数据" />
      </template>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchLogs"
          @current-change="fetchLogs"
        />
      </div>
    </el-card>

    <!-- 新增/编辑日志对话框 -->
    <el-dialog
      v-model="formDialogVisible"
      :title="formDialogTitle"
      width="900px"
      @close="handleFormDialogClose"
      destroy-on-close
    >
      <el-form
        ref="logFormRef"
        :model="logForm"
        :rules="logFormRules"
        label-width="120px"
      >
        <!-- 基础信息 -->
        <el-divider content-position="left">基础信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备" prop="equipment_id">
              <el-select
                v-model="logForm.equipment_id"
                placeholder="选择设备"
                filterable
                class="form-full"
              >
                <el-option
                  v-for="eq in equipmentList"
                  :key="eq.id"
                  :label="`${eq.code} - ${eq.name}`"
                  :value="eq.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="日志类型" prop="log_type">
              <el-select
                v-model="logForm.log_type"
                placeholder="选择日志类型"
                @change="handleLogTypeChange"
                class="form-full"
              >
                <el-option label="设备安装" value="installation" />
                <el-option label="设备维修" value="repair" />
                <el-option label="设备报废" value="scrap" />
                <el-option label="日常巡检" value="inspection" />
                <el-option label="保养记录" value="maintenance" />
                <el-option label="故障报修" value="fault" />
                <el-option label="配件更换" value="parts" />
                <el-option label="校准记录" value="calibration" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="描述">
          <el-input
            v-model="logForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入描述信息"
          />
        </el-form-item>

        <!-- 动态表单：根据日志类型显示不同字段 -->
        <el-divider content-position="left">详细信息</el-divider>

        <!-- 设备安装 -->
        <div v-if="logForm.log_type === 'installation'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="安装日期" prop="installation_date">
                <el-date-picker
                  v-model="logForm.installation_date"
                  type="datetime"
                  placeholder="选择安装日期"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="安装人员">
                <el-input v-model="logForm.installer" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="安装位置">
                <el-input v-model="logForm.location" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="验收状态">
                <el-select v-model="logForm.acceptance_status" class="form-full">
                  <el-option label="合格" value="合格" />
                  <el-option label="不合格" value="不合格" />
                  <el-option label="待验收" value="待验收" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 设备维修 -->
        <div v-if="logForm.log_type === 'repair'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="维修日期" prop="repair_date">
                <el-date-picker
                  v-model="logForm.repair_date"
                  type="datetime"
                  placeholder="选择维修日期"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="维修费用">
                <el-input-number
                  v-model="logForm.cost"
                  :min="0"
                  :precision="2"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="故障描述" prop="fault_description">
            <el-input
              v-model="logForm.fault_description"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
          <el-form-item label="解决方案">
            <el-input
              v-model="logForm.solution"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
          <el-form-item label="维修时长（小时）">
            <el-input-number v-model="logForm.repair_time" :min="0" />
          </el-form-item>
        </div>

        <!-- 设备报废 -->
        <div v-if="logForm.log_type === 'scrap'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="报废日期" prop="scrap_date">
                <el-date-picker
                  v-model="logForm.scrap_date"
                  type="datetime"
                  placeholder="选择报废日期"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="残值">
                <el-input-number
                  v-model="logForm.residual_value"
                  :min="0"
                  :precision="2"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="报废原因" prop="scrap_reason">
            <el-input
              v-model="logForm.scrap_reason"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
        </div>

        <!-- 日常巡检 -->
        <div v-if="logForm.log_type === 'inspection'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="巡检日期" prop="inspection_date">
                <el-date-picker
                  v-model="logForm.inspection_date"
                  type="datetime"
                  placeholder="选择巡检日期"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="巡检人员">
                <el-input v-model="logForm.inspector" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="巡检结果">
            <el-radio-group v-model="logForm.result">
              <el-radio value="normal">正常</el-radio>
              <el-radio value="abnormal">异常</el-radio>
            </el-radio-group>
          </el-form-item>
        </div>

        <!-- 保养记录 -->
        <div v-if="logForm.log_type === 'maintenance'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="保养日期" prop="maintenance_date">
                <el-date-picker
                  v-model="logForm.maintenance_date"
                  type="datetime"
                  placeholder="选择保养日期"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="下次保养日期">
                <el-date-picker
                  v-model="logForm.next_maintenance_date"
                  type="date"
                  placeholder="选择下次保养日期"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 故障报修 -->
        <div v-if="logForm.log_type === 'fault'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="故障时间" prop="fault_date">
                <el-date-picker
                  v-model="logForm.fault_date"
                  type="datetime"
                  placeholder="选择故障时间"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="故障等级">
                <el-select v-model="logForm.fault_level" class="form-full">
                  <el-option label="一般" value="minor" />
                  <el-option label="严重" value="major" />
                  <el-option label="紧急" value="critical" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="报修人">
            <el-input v-model="logForm.reporter" />
          </el-form-item>
          <el-form-item label="故障描述" prop="fault_description">
            <el-input
              v-model="logForm.fault_description"
              type="textarea"
              :rows="3"
            />
          </el-form-item>
        </div>

        <!-- 配件更换 -->
        <div v-if="logForm.log_type === 'parts'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="更换日期" prop="replacement_date">
                <el-date-picker
                  v-model="logForm.replacement_date"
                  type="datetime"
                  placeholder="选择更换日期"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="配件名称" prop="parts_name">
                <el-input v-model="logForm.parts_name" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="配件编号">
                <el-input v-model="logForm.parts_code" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="数量" prop="quantity">
                <el-input-number v-model="logForm.quantity" :min="1" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="费用">
            <el-input-number
              v-model="logForm.cost"
              :min="0"
              :precision="2"
            />
          </el-form-item>
        </div>

        <!-- 校准记录 -->
        <div v-if="logForm.log_type === 'calibration'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="校准日期" prop="calibration_date">
                <el-date-picker
                  v-model="logForm.calibration_date"
                  type="datetime"
                  placeholder="选择校准日期"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="校准机构">
                <el-input v-model="logForm.calibration_org" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="校准结果">
                <el-select v-model="logForm.calibration_result" class="form-full">
                  <el-option label="合格" value="qualified" />
                  <el-option label="不合格" value="unqualified" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="下次校准日期">
                <el-date-picker
                  v-model="logForm.next_calibration_date"
                  type="date"
                  placeholder="选择下次校准日期"
                  class="form-full"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 附件上传 -->
        <el-form-item label="附件">
          <el-upload
            v-model:file-list="fileList"
            :action="uploadUrl"
            :headers="uploadHeaders"
            multiple
            :on-success="handleUploadSuccess"
            :on-remove="handleUploadRemove"
          >
            <el-button type="primary">点击上传</el-button>
            <template #tip>
              <div class="el-upload__tip">
                支持 .pdf, .docx, .jpg, .jpeg, .png 格式文件，单个文件不超过10MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleLogSubmit" :loading="submitLoading">
          提交
        </el-button>
      </template>
    </el-dialog>

    <!-- 审批对话框 -->
    <el-dialog v-model="approveDialogVisible" title="审批日志" width="500px">
      <el-form label-width="100px">
        <el-form-item label="审批结果">
          <el-radio-group v-model="approveAction">
            <el-radio :label="true">通过</el-radio>
            <el-radio :label="false">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="驳回原因" v-if="!approveAction">
          <el-input
            v-model="rejectionReason"
            type="textarea"
            :rows="3"
            placeholder="请输入驳回原因"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleApproveSubmit" :loading="submitLoading">
          确认
        </el-button>
      </template>
    </el-dialog>

    <!-- 日志详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="日志详情" width="900px">
      <div v-if="currentLog">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="日志类型">
            <el-tag :type="getLogTypeColor(currentLog.log_type)">
              {{ getLogTypeLabel(currentLog.log_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="设备名称">
            {{ currentLog.equipment_name }}
          </el-descriptions-item>
          <el-descriptions-item label="提交人">
            {{ currentLog.operator_name }}
          </el-descriptions-item>
          <el-descriptions-item label="提交时间">
            {{ formatDate(currentLog.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusType(currentLog.status)">
              {{ getStatusLabel(currentLog.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="审批人">
            {{ currentLog.approver_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="审批时间">
            {{ currentLog.approved_at ? formatDate(currentLog.approved_at) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="驳回原因">
            {{ currentLog.rejection_reason || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <h4>详细信息</h4>
        <div v-if="currentLog.detail_data">
          <el-descriptions :column="2" border>
            <template v-for="(value, key) in currentLog.detail_data" :key="key">
              <el-descriptions-item :label="getDetailLabel(key)">
                {{ formatDetailValue(key, value) }}
              </el-descriptions-item>
            </template>
          </el-descriptions>
        </div>

        <el-divider />

        <div v-if="currentLog.attachments && currentLog.attachments.length > 0">
          <h4>附件</h4>
          <div class="attachments">
            <el-link
              v-for="(file, index) in currentLog.attachments"
              :key="index"
              :href="`/uploads/${file}`"
              target="_blank"
              type="primary"
              style="margin-right: 20px"
            >
              <el-icon><Document /></el-icon>
              附件{{ index + 1 }}
            </el-link>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance } from 'element-plus'
import {
  Plus,
  Upload,
  Document
} from '@element-plus/icons-vue'
import {
  getLogs,
  createLog,
  updateLog,
  deleteLog,
  approveLog as apiApproveLog,
  getLogDetail,
  getLogTypes,
  getEquipments
} from '@/api'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loading = ref(false)
const logList = ref([])
const equipmentList = ref([])

const searchForm = reactive({
  log_type: '',
  status: '',
  equipment_id: undefined,
  keyword: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const logTypeLabels: Record<string, string> = {
  installation: '设备安装',
  repair: '设备维修',
  scrap: '设备报废',
  inspection: '日常巡检',
  maintenance: '保养记录',
  fault: '故障报修',
  parts: '配件更换',
  calibration: '校准记录'
}

const logTypeColors: Record<string, string> = {
  installation: 'primary',
  repair: 'warning',
  scrap: 'danger',
  inspection: 'info',
  maintenance: 'success',
  fault: 'danger',
  parts: 'warning',
  calibration: 'primary'
}

const getLogTypeLabel = (type: string) => logTypeLabels[type] || type
const getLogTypeColor = (type: string) => logTypeColors[type] || 'info'

const getStatusType = (status: string) => {
  const types: Record<string, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'danger'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    pending: '待审批',
    approved: '已通过',
    rejected: '已驳回'
  }
  return labels[status] || status
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

const fetchLogs = async () => {
  loading.value = true
  try {
    const params: any = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }

    if (searchForm.log_type) params.log_type = searchForm.log_type
    if (searchForm.status) params.status = searchForm.status
    if (searchForm.equipment_id) params.equipment_id = searchForm.equipment_id
    if (searchForm.keyword) params.keyword = searchForm.keyword

    const res = await getLogs(params)
    logList.value = res.data || []
    pagination.total = (res as any).total || res.data.length
  } catch (error) {
    ElMessage.error('获取日志列表失败')
  } finally {
    loading.value = false
  }
}

const fetchEquipmentList = async () => {
  try {
    const res = await getEquipments({ limit: 1000 })
    equipmentList.value = res.data || []
  } catch (error) {
    ElMessage.error('获取设备列表失败')
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchLogs()
}

const handleReset = () => {
  searchForm.log_type = ''
  searchForm.status = ''
  searchForm.equipment_id = undefined
  searchForm.keyword = ''
  handleSearch()
}

// 新增/编辑表单
const formDialogVisible = ref(false)
const formDialogTitle = ref('提交日志')
const isEditMode = ref(false)
const editingLogId = ref<number | null>(null)
const logFormRef = ref<FormInstance>()
const submitLoading = ref(false)

const resetLogForm = () => {
  logForm.equipment_id = undefined
  logForm.log_type = ''
  logForm.description = ''
  logForm.installation_date = ''
  logForm.installer = ''
  logForm.location = ''
  logForm.acceptance_status = ''
  logForm.repair_date = ''
  logForm.fault_description = ''
  logForm.solution = ''
  logForm.cost = 0
  logForm.repair_time = 0
  logForm.scrap_date = ''
  logForm.scrap_reason = ''
  logForm.residual_value = 0
  logForm.inspection_date = ''
  logForm.inspector = ''
  logForm.result = 'normal'
  logForm.maintenance_date = ''
  logForm.maintenance_items = []
  logForm.next_maintenance_date = ''
  logForm.fault_date = ''
  logForm.fault_level = 'minor'
  logForm.reporter = ''
  logForm.handle_status = 'pending'
  logForm.replacement_date = ''
  logForm.parts_name = ''
  logForm.parts_code = ''
  logForm.quantity = 1
  logForm.calibration_date = ''
  logForm.calibration_org = ''
  logForm.calibration_result = 'qualified'
  logForm.next_calibration_date = ''
}

const logForm = reactive({
  equipment_id: undefined as number | undefined,
  log_type: '' as any,
  description: '',
  installation_date: '',
  installer: '',
  location: '',
  acceptance_status: '',
  repair_date: '',
  fault_description: '',
  solution: '',
  repair_cost: 0,
  repair_time: 0,
  scrap_date: '',
  scrap_reason: '',
  residual_value: 0,
  inspection_date: '',
  inspector: '',
  result: 'normal',
  maintenance_date: '',
  maintenance_items: [],
  next_maintenance_date: '',
  fault_date: '',
  fault_level: 'minor',
  reporter: '',
  handle_status: 'pending',
  replacement_date: '',
  parts_name: '',
  parts_code: '',
  quantity: 1,
  parts_cost: 0,
  calibration_date: '',
  calibration_org: '',
  calibration_result: 'qualified',
  next_calibration_date: ''
})

const logFormRules = {
  equipment_id: [{ required: true, message: '请选择设备', trigger: 'change' }],
  log_type: [{ required: true, message: '请选择日志类型', trigger: 'change' }],
  installation_date: [{ required: true, message: '请选择安装日期', trigger: 'change' }],
  repair_date: [{ required: true, message: '请选择维修日期', trigger: 'change' }],
  scrap_date: [{ required: true, message: '请选择报废日期', trigger: 'change' }],
  fault_description: [{ required: true, message: '请输入故障描述', trigger: 'blur' }]
}

const handleAdd = () => {
  formDialogTitle.value = '提交日志'
  isEditMode.value = false
  editingLogId.value = null
  resetLogForm()
  formDialogVisible.value = true
}

const handleLogTypeChange = (newType: string) => {
  if (!logForm.log_type || logForm.log_type === newType) return

  // 通用字段
  const commonFields = ['equipment_id', 'description']

  // 检查是否有非通用字段有值
  const typeSpecificFields: Record<string, string[]> = {
    installation: ['installation_date', 'installer', 'location', 'acceptance_status'],
    repair: ['repair_date', 'fault_description', 'solution', 'cost', 'repair_time'],
    scrap: ['scrap_date', 'scrap_reason', 'residual_value'],
    inspection: ['inspection_date', 'inspector', 'inspection_items', 'result'],
    maintenance: ['maintenance_date', 'maintenance_items', 'next_maintenance_date'],
    fault: ['fault_date', 'fault_level', 'reporter', 'fault_description', 'handle_status'],
    parts: ['replacement_date', 'parts_name', 'parts_code', 'quantity', 'cost'],
    calibration: ['calibration_date', 'calibration_org', 'calibration_result', 'next_calibration_date']
  }

  // 收集当前有值的类型专属字段
  const currentTypeFields = typeSpecificFields[logForm.log_type] || []
  const fieldsWithValue: string[] = []

  currentTypeFields.forEach(field => {
    const value = logForm[field as keyof typeof logForm]
    if (value && value !== '' && value !== 0 && (!Array.isArray(value) || value.length > 0)) {
      fieldsWithValue.push(field)
    }
  })

  // 如果有非通用字段有值，显示确认对话框
  if (fieldsWithValue.length > 0) {
    ElMessageBox.confirm(
      `切换日志类型后，以下字段将被清空：\n${fieldsWithValue.map(f => `- ${getFieldLabel(f)}`).join('\n')}\n\n是否继续？`,
      '确认切换',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(() => {
      // 清空当前类型的专属字段
      fieldsWithValue.forEach(field => {
        (logForm as any)[field] = ''
      })
      // 设置新类型
      logForm.log_type = newType
      ElMessage.success('已切换到' + getLogTypeLabel(newType))
    }).catch(() => {
      // 用户取消，恢复原来的类型
      logForm.log_type = logForm.log_type
    })
  } else {
    // 没有非通用字段，直接切换
    logForm.log_type = newType
    ElMessage.success('已切换到' + getLogTypeLabel(newType))
  }
}

const getFieldLabel = (field: string): string => {
  const labels: Record<string, string> = {
    installation_date: '安装日期',
    installer: '安装人员',
    location: '安装位置',
    acceptance_status: '验收状态',
    repair_date: '维修日期',
    fault_description: '故障描述',
    solution: '解决方案',
    cost: '费用',
    repair_time: '维修时长',
    scrap_date: '报废日期',
    scrap_reason: '报废原因',
    residual_value: '残值',
    inspection_date: '巡检日期',
    inspector: '巡检人员',
    inspection_items: '巡检项目',
    result: '巡检结果',
    maintenance_date: '保养日期',
    maintenance_items: '保养项目',
    next_maintenance_date: '下次保养日期',
    fault_date: '故障日期',
    fault_level: '故障等级',
    reporter: '报告人',
    handle_status: '处理状态',
    replacement_date: '更换日期',
    parts_name: '配件名称',
    parts_code: '配件编号',
    quantity: '数量',
    calibration_date: '校准日期',
    calibration_org: '校准机构',
    calibration_result: '校准结果',
    next_calibration_date: '下次校准日期'
  }
  return labels[field] || field
}

const handleLogSubmit = async () => {
  try {
    await logFormRef.value?.validate()

    // 根据类型验证必填字段
    validateLogForm()

    submitLoading.value = true

    const formData = { ...logForm }

    if (isEditMode.value && editingLogId.value) {
      // 编辑模式
      await updateLog(editingLogId.value, formData)
      ElMessage.success('日志更新成功')
    } else {
      // 新增模式
      await createLog(formData)
      ElMessage.success('日志提交成功')
    }

    formDialogVisible.value = false
    fetchLogs()
  } catch (error: any) {
    if (error !== false) {
      ElMessage.error(error?.message || '提交失败')
    }
  } finally {
    submitLoading.value = false
  }
}

const validateLogForm = () => {
  if (logForm.log_type === 'repair' && !logForm.fault_description) {
    ElMessage.error('请输入故障描述')
    return false
  }
  if (logForm.log_type === 'scrap' && !logForm.scrap_reason) {
    ElMessage.error('请输入报废原因')
    return false
  }
  if (logForm.log_type === 'fault' && !logForm.fault_description) {
    ElMessage.error('请输入故障描述')
    return false
  }
  if (logForm.log_type === 'parts' && !logForm.parts_name) {
    ElMessage.error('请输入配件名称')
    return false
  }
  return true
}

const handleFormDialogClose = () => {
  logFormRef.value?.resetFields()
  resetLogForm()
  // 重置编辑模式
  isEditMode.value = false
  editingLogId.value = null
}

// 查看详情
const detailDialogVisible = ref(false)
const currentLog = ref<any>(null)

const handleView = async (row: any) => {
  try {
    const res = await getLogDetail(row.id)
    currentLog.value = res.data
    detailDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取日志详情失败')
  }
}

// 编辑
const handleEdit = (row: any) => {
  // 设置编辑模式
  isEditMode.value = true
  editingLogId.value = row.id
  formDialogTitle.value = '编辑日志'

  // 填充表单
  Object.assign(logForm, {
    equipment_id: row.equipment_id,
    log_type: row.log_type,
    description: row.description,
    ...row.details  // 展开特定日志类型的字段
  })

  formDialogVisible.value = true
}

// 删除
const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条日志吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteLog(row.id)
    ElMessage.success('删除成功')
    fetchLogs()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error?.message || '删除失败')
    }
  }
}

// 审批
const approveDialogVisible = ref(false)
const currentApproveLog = ref<any>(null)
const approveAction = ref(true)
const rejectionReason = ref('')

const handleApprove = (row: any) => {
  currentApproveLog.value = row
  approveAction.value = true
  rejectionReason.value = ''
  approveDialogVisible.value = true
}

const handleApproveSubmit = async () => {
  if (!approveAction.value && !rejectionReason.value) {
    ElMessage.error('请输入驳回原因')
    return
  }

  try {
    submitLoading.value = true
    await apiApproveLog(currentApproveLog.value.id, approveAction.value, rejectionReason.value)

    ElMessage.success(approveAction.value ? '审批通过' : '已驳回')
    approveDialogVisible.value = false
    fetchLogs()
  } catch (error) {
    ElMessage.error('审批失败')
  } finally {
    submitLoading.value = false
  }
}

// 批量上传
const uploadUrl = ref(`${import.meta.env.VITE_API_URL || '/api'}/upload/batch`)
const uploadHeaders = {
  Authorization: `Bearer ${localStorage.getItem('token')}`
}
const fileList = ref([])

const handleBatchUpload = () => {
  router.push('/upload')
}

const handleUploadSuccess = (response: any, file: any) => {
  ElMessage.success(`${file.name} 上传成功`)
}

const handleUploadRemove = (file: any) => {
  console.log('文件已删除', file)
}

const getDetailLabel = (key: string) => {
  const labels: Record<string, string> = {
    installation_date: '安装日期',
    installer: '安装人员',
    location: '安装位置',
    acceptance_status: '验收状态',
    repair_date: '维修日期',
    fault_description: '故障描述',
    solution: '解决方案',
    cost: '费用',
    repair_time: '维修时长',
    scrap_date: '报废日期',
    scrap_reason: '报废原因',
    residual_value: '残值',
    inspection_date: '巡检日期',
    inspector: '巡检人员',
    inspection_items: '巡检项目',
    result: '巡检结果',
    maintenance_date: '保养日期',
    maintenance_items: '保养项目',
    next_maintenance_date: '下次保养日期',
    fault_date: '故障时间',
    fault_level: '故障等级',
    reporter: '报修人',
    handle_status: '处理状态',
    replacement_date: '更换日期',
    parts_name: '配件名称',
    parts_code: '配件编号',
    quantity: '数量',
    calibration_date: '校准日期',
    calibration_org: '校准机构',
    calibration_result: '校准结果',
    next_calibration_date: '下次校准日期'
  }
  return labels[key] || key
}

const formatDetailValue = (key: string, value: any) => {
  if (value === null || value === undefined) return '-'

  if (key === 'fault_level') {
    const labels: Record<string, string> = { minor: '一般', major: '严重', critical: '紧急' }
    return labels[value] || value
  }

  if (key === 'result') {
    return value === 'normal' ? '正常' : '异常'
  }

  if (key === 'calibration_result') {
    return value === 'qualified' ? '合格' : '不合格'
  }

  if (key === 'maintenance_items' && Array.isArray(value)) {
    return value.join(', ')
  }

  if (key === 'inspection_items' && Array.isArray(value)) {
    return value.join(', ')
  }

  return value
}

onMounted(() => {
  fetchEquipmentList()
  fetchLogs()

  // 检查URL参数，如果是从设备详情页过来的，自动设置设备筛选
  const equipment_id = route.query.equipment_id
  if (equipment_id) {
    searchForm.equipment_id = Number(equipment_id)
    fetchLogs()
  }
})
</script>

<style scoped>
.logs-page {
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

.header-actions {
  display: flex;
  gap: var(--space-4);  /* 16px */
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

/* 分页 */
.pagination {
  margin-top: var(--space-6);  /* 32px */
  display: flex;
  justify-content: flex-end;
  padding: 0 var(--space-4);
}

.attachments {
  margin-top: var(--space-4);
}

.form-full {
  width: 100%;
}

/* 日志类型标签颜色优化 */
.log-type-tag {
  font-weight: 500;
}

/* 详情对话框 */
.detail-dialog :deep(.el-descriptions) {
  margin-top: var(--space-4);
}

.detail-dialog :deep(.el-descriptions__label) {
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
}

.detail-dialog :deep(.el-divider) {
  margin: var(--space-6) 0;
}

/* 表单对话框 */
.form-dialog :deep(.el-dialog) {
  border-radius: var(--radius-lg);
}

.form-dialog :deep(.el-dialog__header) {
  padding: var(--space-6);
}

.form-dialog :deep(.el-dialog__body) {
  padding: var(--space-6);
}

/* 响应式优化 */
@media (max-width: 768px) {
  .header-actions {
    flex-direction: column;
    gap: var(--space-3);
  }

  .search-card :deep(.el-form) {
    flex-direction: column;
  }

  .table-card :deep(.el-table) {
    font-size: var(--text-sm);
  }

  .table-card :deep(.el-table__cell) {
    padding: var(--space-3) var(--space-4);
  }
}
</style>
