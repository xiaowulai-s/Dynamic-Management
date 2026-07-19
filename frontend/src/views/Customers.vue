<template>
  <div class="cs-page">
    <div class="page-header">
      <h2>客户管理</h2>
      <el-button type="primary" @click="openAdd">添加客户</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="items" v-loading="loading" stripe size="small">
        <el-table-column prop="name" label="名称" show-overflow-tooltip />
        <el-table-column prop="contact" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="120" />
        <el-table-column prop="equipment_count" label="设备数" width="80" align="center" />
        <el-table-column label="创建时间" width="160" align="center">
          <template #default="{row}">{{ new Date(row.created_at).toLocaleDateString('zh-CN') }}</template>
        </el-table-column>
        <el-table-column label="操作" min-width="140" align="center">
          <template #default="{row}">
            <div class="table-actions">
              <el-button size="small" @click="openEdit(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="handleDel(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showForm" :title="editId?'编辑客户':'添加客户'" width="520px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="名称" prop="name"><el-input v-model="form.name" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系人"><el-input v-model="form.contact" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="地址"><el-input v-model="form.address" /></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForm=false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getCustomers, createCustomer, updateCustomer, deleteCustomer } from '@/api'

const userStore = useUserStore()

const loading = ref(false)
const items = ref<any[]>([])
const showForm = ref(false)
const saving = ref(false)
const formRef = ref<FormInstance>()
const editId = ref<number | null>(null)
const form = reactive({ name: '', contact: '', phone: '', email: '', address: '', remark: '' })
const rules = { name: [{ required: true, message: '请输入名称', trigger: 'blur' }] }

const fetchAll = async () => {
  loading.value = true
  try {
    const res = await getCustomers()
    items.value = res.data
  } catch (error) {
    console.error('获取客户列表失败:', error)
    ElMessage.error('获取客户列表失败')
  } finally {
    loading.value = false
  }
}
const openAdd = () => {
  editId.value = null
  Object.assign(form, { name: '', contact: '', phone: '', email: '', address: '', remark: '' })
  showForm.value = true
}
const openEdit = (r: any) => {
  editId.value = r.id
  Object.assign(form, { name: r.name, contact: r.contact || '', phone: r.phone || '', email: r.email || '', address: r.address || '', remark: r.remark || '' })
  showForm.value = true
}
const handleSave = async () => {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  saving.value = true
  try {
    if (editId.value) {
      await updateCustomer(editId.value, form)
    } else {
      await createCustomer(form)
    }
    ElMessage.success('已保存')
    showForm.value = false
    fetchAll()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}
const handleDel = (r: any) => {
  ElMessageBox.confirm('确定删除客户"' + r.name + '"？', '确认删除', { type: 'warning' })
    .then(async () => {
      try {
        await deleteCustomer(r.id)
        ElMessage.success('已删除')
        fetchAll()
      } catch (error) {
        console.error('删除客户失败:', error)
        ElMessage.error('删除失败')
      }
    })
    .catch(() => { })
}
onMounted(() => fetchAll())
</script>

<style scoped>
.cs-page { /* padding */ }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px }
.page-header h2 { margin: 0; font-size: 24px; font-weight: 600 }
</style>
