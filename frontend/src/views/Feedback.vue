<template>
  <div class="fb-page">
    <div class="page-header"><h2>用户反馈</h2></div>

    <!-- 提交反馈卡片 -->
    <el-card class="mb-4" shadow="never">
      <div class="flex-between">
        <span style="color:var(--text-secondary)">遇到问题？请提交反馈，管理员会尽快回复</span>
        <el-button type="primary" @click="showForm=true">提交反馈</el-button>
      </div>
    </el-card>

    <!-- 提交弹窗 -->
    <el-dialog v-model="showForm" title="提交反馈" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" maxlength="200" placeholder="简要描述问题" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="4" maxlength="2000" placeholder="详细描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showForm=false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">提交</el-button>
      </template>
    </el-dialog>

    <!-- 反馈列表 -->
    <el-card shadow="never" v-loading="loading">
      <el-empty v-if="!items.length" description="暂无反馈" />
      <div v-else class="fb-list">
        <div v-for="fb in items" :key="fb.id" class="fb-item" :class="{unread:!fb.is_read&&fb.reply}">
          <div class="fb-header">
            <div>
              <el-tag :type="fb.status==='open'?'warning':fb.status==='replied'?'success':'info'" size="small">
                {{ fb.status==='open'?'待回复':fb.status==='replied'?'已回复':'已关闭' }}
              </el-tag>
              <span class="fb-title">{{ fb.title }}</span>
            </div>
            <span class="fb-time">{{ formatTime(fb.created_at) }}</span>
          </div>
          <div class="fb-content">{{ fb.content }}</div>
          <div v-if="fb.reply" class="fb-reply">
            <strong>{{ fb.replied_by_name }} 回复：</strong>{{ fb.reply }}
            <span class="fb-reply-time">{{ formatTime(fb.replied_at) }}</span>
          </div>
          <!-- 管理员回复表单 -->
          <div v-if="isAdmin && fb.status==='open'" class="fb-admin-reply">
            <el-input v-model="replyTexts[fb.id]" type="textarea" placeholder="输入回复..." :rows="2" />
            <el-button size="small" type="primary" style="margin-top:8px" @click="handleReply(fb.id)" :loading="replyingId===fb.id">回复</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getFeedbacks, submitFeedback, replyFeedback } from '@/api'

const userStore = useUserStore()
const isAdmin = computed(()=>userStore.role==='admin'||userStore.role==='super_admin')

const loading=ref(false)
const showForm=ref(false)
const submitting=ref(false)
const replyingId=ref<number|null>(null)
const items=ref<any[]>([])
const formRef=ref<FormInstance>()
const replyTexts=ref<Record<number,string>>({})
const form=reactive({title:'',content:''})
const rules={
  title:[{required:true,message:'请输入标题',trigger:'blur'}],
  content:[{required:true,message:'请输入内容',trigger:'blur'}]
}
const formatTime=(t:string)=>t?new Date(t).toLocaleString('zh-CN'):'-'

const fetchAll = async () => {
  loading.value = true
  try {
    const res = await getFeedbacks()
    items.value = res.data
  } catch (error) {
    console.error('获取反馈列表失败:', error)
    ElMessage.error('获取反馈列表失败')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  try { await formRef.value.validate() } catch { return }
  submitting.value = true
  try {
    await submitFeedback(form)
    ElMessage.success('反馈已提交')
    showForm.value = false
    form.title = ''
    form.content = ''
    fetchAll()
  } catch (error) {
    console.error('提交反馈失败:', error)
    ElMessage.error('提交失败')
  } finally {
    submitting.value = false
  }
}

const handleReply = async (id: number) => {
  const text = replyTexts.value[id]
  if (!text) { ElMessage.warning('请输入回复内容'); return }
  replyingId.value = id
  try {
    await replyFeedback(id, text)
    ElMessage.success('已回复')
    replyTexts.value[id] = ''
    fetchAll()
  }catch{ElMessage.error('回复失败')}finally{replyingId.value=null}
}

onMounted(()=>fetchAll())
</script>

<style scoped>
.fb-page { /* padding */ }
.page-header { margin-bottom:24px; }
.page-header h2 { margin:0;font-size:24px;font-weight:600; }
.fb-list { display:flex;flex-direction:column;gap:12px; }
.fb-item { background:var(--surface-card);border:1px solid var(--border-default);border-radius:8px;padding:14px; }
.fb-item.unread { border-color:var(--color-warning-500); }
.fb-header { display:flex;justify-content:space-between;align-items:center;margin-bottom:8px; }
.fb-title { margin-left:8px;font-weight:600; }
.fb-time { font-size:12px;color:var(--text-tertiary); }
.fb-content { font-size:13px;color:var(--text-secondary);margin-bottom:8px;white-space:pre-wrap; }
.fb-reply { background:var(--surface-hover);padding:10px;border-radius:6px;font-size:13px;margin-top:8px; }
.fb-reply-time { display:block;font-size:11px;color:var(--text-tertiary);margin-top:4px; }
.fb-admin-reply { margin-top:8px; }
.mb-4 { margin-bottom:16px; }
</style>
