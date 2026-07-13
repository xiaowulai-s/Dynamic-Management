<template>
  <div class="upload-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">批量上传与OCR识别</span>
          <el-button type="primary" :disabled="!hasResults" @click="handleConfirmCreate">
            确认创建日志 ({{ selectedResults.length }})
          </el-button>
        </div>
      </template>

      <!-- 文件上传区域 -->
      <div class="upload-section">
        <el-upload
          ref="uploadRef"
          class="upload-dragger"
          drag
          action="#"
          :auto-upload="false"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          :file-list="fileList"
          :limit="20"
          multiple
          accept=".docx,.pdf,.jpg,.jpeg,.png"
        >
          <el-icon class="el-icon--upload"><upload-filled /></el-icon>
          <div class="el-upload__text">
            拖拽文件到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 Word (.docx)、PDF (.pdf)、图片 (.jpg, .jpeg, .png) 格式，最多20个文件
            </div>
          </template>
        </el-upload>
      </div>

      <!-- 识别进度区域 -->
      <div v-if="processingFiles.length > 0" class="processing-section">
        <h3>处理进度</h3>
        <div v-for="file in processingFiles" :key="file.uid" class="processing-item">
          <div class="file-info">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">({{ formatFileSize(file.size) }})</span>
          </div>
          <div class="processing-status">
            <el-tag v-if="file.status === 'uploading'" type="info" :loading="true">
              上传中...
            </el-tag>
            <el-tag v-else-if="file.status === 'waiting'" type="warning">
              等待识别
            </el-tag>
            <el-tag v-else-if="file.status === 'ocr_processing'" type="warning" :loading="true">
              OCR识别中...
            </el-tag>
            <el-tag v-else-if="file.status === 'success'" type="success">
              识别成功
            </el-tag>
            <el-tag v-else-if="file.status === 'error'" type="danger">
              识别失败: {{ file.error }}
            </el-tag>
          </div>
          <div v-if="file.status === 'waiting'" class="action-buttons">
            <el-button
              type="primary"
              size="small"
              @click="handleManualOcr(file)"
            >
              开始识别
            </el-button>
          </div>
          <div v-if="file.status === 'ocr_processing'" class="progress-bar">
            <el-progress :percentage="file.progress || 0" />
          </div>
        </div>
      </div>

      <!-- 识别结果预览 -->
      <div v-if="ocrResults.length > 0" class="results-section">
        <div class="results-header">
          <h3>识别结果</h3>
          <div class="results-actions">
            <el-button size="small" @click="toggleSelectAll">
              {{ allSelected ? '取消全选' : '全选' }}
            </el-button>
            <el-button size="small" type="danger" :disabled="selectedResults.length === 0" @click="handleBatchDelete">
              删除选中 ({{ selectedResults.length }})
            </el-button>
          </div>
        </div>

        <el-table
          :data="ocrResults"
          @selection-change="handleSelectionChange"
          stripe
          border
        >
          <el-table-column type="selection" width="55" />
          <el-table-column prop="file_name" label="文件名" min-width="200" />
          <el-table-column prop="equipment_code" label="设备编号" min-width="120">
            <template #default="{ row }">
              <el-input
                v-model="row.equipment_code"
                size="small"
                placeholder="设备编号"
              />
            </template>
          </el-table-column>
          <el-table-column prop="equipment_name" label="设备名称" min-width="150">
            <template #default="{ row }">
              <el-input
                v-model="row.equipment_name"
                size="small"
                placeholder="设备名称"
              />
            </template>
          </el-table-column>
          <el-table-column prop="log_type" label="日志类型" min-width="120">
            <template #default="{ row }">
              <el-select v-model="row.log_type" size="small" placeholder="选择类型">
                <el-option label="设备安装" value="installation" />
                <el-option label="设备维修" value="repair" />
                <el-option label="设备报废" value="scrap" />
                <el-option label="日常巡检" value="inspection" />
                <el-option label="保养记录" value="maintenance" />
                <el-option label="故障报修" value="fault" />
                <el-option label="配件更换" value="parts" />
                <el-option label="校准记录" value="calibration" />
              </el-select>
            </template>
          </el-table-column>
          <el-table-column prop="confidence" label="置信度" width="100">
            <template #default="{ row }">
              <el-tag :type="getConfidenceType(row.confidence)">
                {{ row.confidence ? Math.round(row.confidence * 100) + '%' : '-' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button
                size="small"
                type="danger"
                link
                @click="handleDeleteResult(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 空状态 -->
      <el-empty v-if="fileList.length === 0 && ocrResults.length === 0" description="请上传文件开始识别" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import {
  uploadFile,
  uploadBatchFiles,
  triggerOcrRecognition,
  getOcrStatus
} from '@/api'

const router = useRouter()
const uploadRef = ref()
const fileList = ref<any[]>([])
const processingFiles = ref<any[]>([])
const ocrResults = ref<any[]>([])
const selectedResults = ref<any[]>([])
const allSelected = computed(() => {
  return ocrResults.value.length > 0 && selectedResults.value.length === ocrResults.value.length
})
const hasResults = computed(() => ocrResults.value.length > 0)

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const getConfidenceType = (confidence: number) => {
  if (!confidence) return 'info'
  if (confidence >= 0.8) return 'success'
  if (confidence >= 0.6) return 'warning'
  return 'danger'
}

const handleFileChange = async (file: any) => {
  // 添加到文件列表
  if (!fileList.value.find(f => f.uid === file.uid)) {
    fileList.value.push(file)
  }

  // 判断文件大小，决定是否自动识别
  const isAutoOcr = file.size < 1024 * 1024 // < 1MB

  if (isAutoOcr) {
    // 自动识别
    await processFileOcr(file, true)
  } else {
    // 大文件需要手动触发
    ElMessage.info(`${file.name} 超过1MB，请手动点击开始识别`)
    file.status = 'waiting'
  }
}

const handleFileRemove = (file: any) => {
  fileList.value = fileList.value.filter(f => f.uid !== file.uid)
  // 同时移除处理记录
  processingFiles.value = processingFiles.value.filter(f => f.uid !== file.uid)
}

const handleManualOcr = async (file: any) => {
  await processFileOcr(file, false)
}

const processFileOcr = async (file: any, autoTrigger: boolean = false) => {
  // 先上传文件
  file.status = 'uploading'
  const processingItem = {
    uid: file.uid,
    name: file.name,
    size: file.size,
    status: 'uploading',
    progress: 0
  }
  processingFiles.value.push(processingItem)

  try {
    // 1. 上传文件
    const uploadRes = await uploadFile(file.raw)
    processingItem.progress = 50

    if (!uploadRes.data.success) {
      throw new Error(uploadRes.data.message || '上传失败')
    }

    processingItem.status = 'ocr_processing'
    processingItem.progress = 60

    // 2. 触发OCR识别
    const ocrRes = await triggerOcrRecognition({
      file_path: uploadRes.data.file_path,
      file_name: file.name
    })

    // 轮询检查识别状态
    const taskId = ocrRes.data.task_id
    let statusRes = await getOcrStatus(taskId)

    while (statusRes.data.status === 'processing') {
      await new Promise(resolve => setTimeout(resolve, 1000))
      statusRes = await getOcrStatus(taskId)
      processingItem.progress = 60 + Math.round((statusRes.data.progress || 0) * 0.4)
    }

    if (statusRes.data.status === 'completed') {
      // 识别成功
      processingItem.status = 'success'
      processingItem.progress = 100

      // 添加到识别结果
      ocrResults.value.push({
        uid: file.uid,
        file_name: file.name,
        file_path: uploadRes.data.file_path,
        equipment_code: statusRes.data.data.equipment_code || '',
        equipment_name: statusRes.data.data.equipment_name || '',
        log_type: statusRes.data.data.log_type || '',
        confidence: statusRes.data.data.confidence || 0,
        raw_data: statusRes.data.data
      })

      ElMessage.success(`${file.name} 识别完成`)
    } else {
      throw new Error(statusRes.data.message || '识别失败')
    }
  } catch (error: any) {
    processingItem.status = 'error'
    processingItem.error = error.response?.data?.detail || error.message || '处理失败'
    ElMessage.error(`${file.name} 处理失败: ${processingItem.error}`)
  }
}

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedResults.value = []
  } else {
    selectedResults.value = [...ocrResults.value]
  }
}

const handleSelectionChange = (selection: any[]) => {
  selectedResults.value = selection
}

const handleDeleteResult = (row: any) => {
  ElMessageBox.confirm(`确定删除 ${row.file_name} 的识别结果？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    ocrResults.value = ocrResults.value.filter(r => r.uid !== row.uid)
    ElMessage.success('已删除')
  }).catch(() => {})
}

const handleBatchDelete = () => {
  ElMessageBox.confirm(`确定删除选中的 ${selectedResults.value.length} 个识别结果？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const uids = selectedResults.value.map(r => r.uid)
    ocrResults.value = ocrResults.value.filter(r => !uids.includes(r.uid))
    selectedResults.value = []
    ElMessage.success('已删除')
  }).catch(() => {})
}

const handleConfirmCreate = () => {
  if (selectedResults.value.length === 0) {
    ElMessage.warning('请先选择要创建的日志')
    return
  }

  // 跳转到日志页面，传递选中的识别结果
  router.push({
    path: '/logs',
    query: {
      from: 'upload',
      results: btoa(JSON.stringify(selectedResults.value))
    }
  })
}
</script>

<style scoped>
.upload-container {
  /* padding 由 .content 全局控制 */
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .title {
  font-size: var(--text-xl);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
}

.upload-section {
  margin-bottom: var(--space-8);
}

.upload-dragger {
  width: 100%;
}

.upload-dragger :deep(.el-upload) {
  width: 100%;
}

.upload-dragger :deep(.el-upload-dragger) {
  width: 100%;
  padding: 60px var(--space-5);
}

.processing-section {
  margin: var(--space-8) 0;
  padding: var(--space-5);
  background: var(--surface-hover);
  border-radius: var(--radius-md);
}

.processing-section h3 {
  margin: 0 0 var(--space-5) 0;
  font-size: var(--text-lg);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
}

.processing-item {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-4);
  padding: var(--space-3);
  background: var(--surface-card);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-default);
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-weight: var(--font-w-medium);
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  color: var(--text-tertiary);
  margin-left: var(--space-2);
  font-size: var(--text-sm);
}

.processing-status {
  margin-left: var(--space-5);
}

.action-buttons {
  margin-left: auto;
}

.progress-bar {
  width: 100%;
  margin-top: var(--space-3);
}

.results-section {
  margin-top: var(--space-8);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-5);
}

.results-header h3 {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
}

.results-actions {
  display: flex;
  gap: var(--space-3);
}
</style>
