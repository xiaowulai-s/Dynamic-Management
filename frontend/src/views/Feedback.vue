<template>
  <div class="fb-page">
    <div class="page-header"><h2>用户反馈</h2></div>

    <!-- 提交反馈弹窗触发 -->
    <n-card size="small" style="margin-bottom:16px">
      <n-space align="center" justify="space-between">
        <span style="color:var(--text-secondary)">遇到问题？请提交反馈，管理员会尽快回复</span>
        <n-button type="primary" @click="showForm=true">提交反馈</n-button>
      </n-space>
    </n-card>

    <!-- 提交弹窗 -->
    <n-modal v-model:show="showForm" title="提交反馈" preset="card" style="width:480px">
      <n-form ref="formRef" :model="form" :rules="rules">
        <n-form-item path="title" label="标题"><n-input v-model:value="form.title" maxlength="200" placeholder="简要描述问题" /></n-form-item>
        <n-form-item path="content" label="内容"><n-input v-model:value="form.content" type="textarea" :rows="4" maxlength="2000" placeholder="详细描述" /></n-form-item>
      </n-form>
      <template #footer><n-space justify="end"><n-button @click="showForm=false">取消</n-button><n-button type="primary" @click="handleSubmit" :loading="submitting">提交</n-button></n-space></template>
    </n-modal>

    <!-- 反馈列表 -->
    <n-spin :show="loading">
      <n-empty v-if="!items.length" description="暂无反馈" />
      <div v-else class="fb-list">
        <div v-for="fb in items" :key="fb.id" class="fb-item" :class="{unread:!fb.is_read&&fb.reply}">
          <div class="fb-header">
            <div>
              <n-tag :type="fb.status==='open'?'warning':fb.status==='replied'?'success':'default'" size="small">{{ fb.status==='open'?'待回复':fb.status==='replied'?'已回复':'已关闭' }}</n-tag>
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
            <n-input v-model:value="replyTexts[fb.id]" type="textarea" placeholder="输入回复..." :rows="2" size="small" />
            <n-button size="tiny" type="primary" style="margin-top:4px" @click="handleReply(fb.id)" :loading="replyingId===fb.id">回复</n-button>
          </div>
        </div>
      </div>
    </n-spin>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useMessage } from 'naive-ui'
import { NCard, NButton, NSpace, NModal, NForm, NFormItem, NInput, NTag, NSpin, NEmpty } from 'naive-ui'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const msg = useMessage()
const userStore = useUserStore()
const base = import.meta.env.VITE_API_URL||'/api'
const h=()=>({Authorization:'Bearer '+userStore.token})
const isAdmin = computed(()=>userStore.role==='admin'||userStore.role==='super_admin')

const loading=ref(false); const showForm=ref(false); const submitting=ref(false); const replyingId=ref<number|null>(null)
const items=ref<any[]>([]); const formRef=ref(); const replyTexts=ref<Record<number,string>>({})
const form=reactive({title:'',content:''})
const rules={title:[{required:true,message:'请输入标题'}],content:[{required:true,message:'请输入内容'}]}
const formatTime=(t:string)=>t?new Date(t).toLocaleString('zh-CN'):'-'

const fetchAll=async()=>{loading.value=true;try{const r=await axios.get(base+'/feedback',{headers:h()});items.value=r.data}catch{}finally{loading.value=false}}

const handleSubmit=async()=>{try{await formRef.value?.validate()}catch{return};submitting.value=true;try{await axios.post(base+'/feedback',form,{headers:h()});msg.success('反馈已提交');showForm.value=false;form.title='';form.content='';fetchAll()}catch{msg.error('提交失败')}finally{submitting.value=false}}

const handleReply=async(id:number)=>{const text=replyTexts.value[id];if(!text){msg.warning('请输入回复内容');return};replyingId.value=id;try{await axios.put(base+'/feedback/'+id+'/reply',{reply:text},{headers:h()});msg.success('已回复');replyTexts.value[id]='';fetchAll()}catch{msg.error('回复失败')}finally{replyingId.value=null}}

onMounted(()=>fetchAll())
</script>

<style scoped>
.fb-page { /* padding */ }
.page-header { margin-bottom:24px; }
.page-header h2 { margin:0;font-size:24px;font-weight:600; }
.fb-list { display:flex;flex-direction:column;gap:12px; }
.fb-item { background:var(--surface-card);border:1px solid var(--border-default);border-radius:8px;padding:14px; }
.fb-item.unread { border-color:var(--color-warning); }
.fb-header { display:flex;justify-content:space-between;align-items:center;margin-bottom:8px; }
.fb-title { margin-left:8px;font-weight:600; }
.fb-time { font-size:12px;color:var(--text-muted); }
.fb-content { font-size:13px;color:var(--text-secondary);margin-bottom:8px;white-space:pre-wrap; }
.fb-reply { background:var(--surface-subtle);padding:10px;border-radius:6px;font-size:13px;margin-top:8px; }
.fb-reply-time { display:block;font-size:11px;color:var(--text-muted);margin-top:4px; }
.fb-admin-reply { margin-top:8px; }
</style>
