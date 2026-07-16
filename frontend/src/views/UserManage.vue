<template>
  <div class="user-page">
    <div class="page-header">
      <h2>用户管理</h2>
      <n-button type="primary" @click="openCreate">添加用户</n-button>
    </div>

    <n-collapse :default-expanded-names="['super_admin','admin','user']">
      <n-collapse-item v-for="g in groups" :key="g.role" :name="g.role">
        <template #header>
          <n-space align="center">
            <n-tag :type="g.tagType" size="small">{{ g.label }}</n-tag>
            <span style="font-size:14px;color:var(--text-muted)">{{ g.users.length }} 人</span>
          </n-space>
        </template>
        <n-empty v-if="!g.users.length" :description="'暂无'+g.label" />
        <div v-else class="user-list">
          <div v-for="u in g.users" :key="u.id" class="user-row">
            <span class="user-name">{{ u.username }}<span v-if="u.nickname" class="user-nick">({{ u.nickname }})</span></span>
            <n-tag :type="u.is_active?'success':'default'" size="tiny" style="margin-left:12px">{{ u.is_active?'启用':'禁用' }}</n-tag>
            <span class="user-time">{{ formatDate(u.created_at) }}</span>
            <n-space size="small" style="margin-left:auto">
              <n-button size="tiny" @click="openEdit(u)">编辑</n-button>
              <n-button size="tiny" @click="handleResetPwd(u)">重置密码</n-button>
              <n-button v-if="u.id!==userStore.userInfo?.id && g.role!=='super_admin'" size="tiny" type="error" @click="handleDelete(u)">删除</n-button>
            </n-space>
          </div>
        </div>
      </n-collapse-item>
    </n-collapse>

    <!-- 编辑/创建弹窗同上 -->
    <n-modal v-model:show="editVisible" title="编辑用户" preset="card" style="width:420px">
      <n-form><n-form-item label="用户名"><n-input v-model:value="editUsername" minlength="3" maxlength="20" /></n-form-item>
        <n-form-item label="角色"><n-select v-model:value="editRole" :options="roleOptions" /></n-form-item>
        <n-form-item label="状态"><n-switch v-model:value="editActive" :checked-value="true" :unchecked-value="false"><template #checked>启用</template><template #unchecked>禁用</template></n-switch></n-form-item>
      </n-form>
      <template #footer><n-space justify="end"><n-button @click="editVisible=false">取消</n-button><n-button type="primary" @click="handleSave" :loading="saving">保存</n-button></n-space></template>
    </n-modal>

    <n-modal v-model:show="createVisible" title="添加用户" preset="card" style="width:420px">
      <n-form ref="createFormRef" :model="createForm" :rules="createRules">
        <n-form-item path="username" label="用户名"><n-input v-model:value="createForm.username" placeholder="3-20位" /></n-form-item>
        <n-form-item path="password" label="密码"><n-input v-model:value="createForm.password" placeholder="默认123456" /></n-form-item>
        <n-form-item path="role" label="角色"><n-select v-model:value="createForm.role" :options="[{label:'用户',value:'user'},{label:'管理员',value:'admin'}]" /></n-form-item>
      </n-form>
      <template #footer><n-space justify="end"><n-button @click="createVisible=false">取消</n-button><n-button type="primary" @click="handleCreate" :loading="saving">创建</n-button></n-space></template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import { NButton, NSpace, NTag, NModal, NForm, NFormItem, NInput, NSelect, NSwitch, NCollapse, NCollapseItem, NEmpty } from 'naive-ui'
import { useUserStore } from '@/stores/user'
import axios from 'axios'

const msg = useMessage(); const dialog = useDialog(); const userStore = useUserStore()
const users = ref<any[]>([])
const editVisible=ref(false); const editingUser=ref<any>(null); const editUsername=ref(''); const editRole=ref(''); const editActive=ref(true)
const saving=ref(false)
const createVisible=ref(false); const createFormRef=ref(); const createForm=reactive({username:'',password:'123456',role:'user'})
const createRules={username:[{required:true,message:'请输入用户名'},{min:3,max:20,message:'3-20位'}],password:[{required:true,message:'请输入密码'},{min:6,max:20,message:'6-20位'}]}
const baseURL=import.meta.env.VITE_API_URL||'/api'; const authHeaders=()=>({Authorization:`Bearer ${userStore.token}`})
const roleOptions=[{label:'超级管理员',value:'super_admin'},{label:'管理员',value:'admin'},{label:'用户',value:'user'}]
const roleLabels:Record<string,string>={super_admin:'超级管理员',admin:'管理员',user:'用户'}

const groups = computed(()=>{
  const byRole:Record<string,any[]>={super_admin:[],admin:[],user:[]}
  users.value.forEach(u=>{if(byRole[u.role]) byRole[u.role].push(u)})
  return Object.entries(byRole).map(([role,list])=>{
    const sorted=[...list].sort((a,b)=>a.username.localeCompare(b.username))
    return {role,label:roleLabels[role]||role,tagType:({super_admin:'error',admin:'warning',user:'info'} as any)[role]||'default',users:sorted}
  })
})

const formatDate=(t:string)=>t?new Date(t).toLocaleDateString('zh-CN'):''
const fetchUsers=async()=>{try{const r=await axios.get(baseURL+'/auth/users',{headers:authHeaders()});users.value=r.data}catch{msg.error('获取用户列表失败')}}
const openEdit=(u:any)=>{editingUser.value=u;editUsername.value=u.username;editRole.value=u.role;editActive.value=u.is_active;editVisible.value=true}
const handleSave=async()=>{saving.value=true;try{await axios.put(baseURL+'/auth/users/'+editingUser.value.id,{username:editUsername.value,role:editRole.value,is_active:editActive.value},{headers:authHeaders()});msg.success('更新成功');editVisible.value=false;fetchUsers()}catch(e:any){msg.error(e?.response?.data?.detail||'更新失败')}finally{saving.value=false}}
const handleDelete=(u:any)=>{dialog.warning({title:'确认删除',content:'确定删除"'+u.username+'"？',positiveText:'确定',negativeText:'取消',onPositiveClick:async()=>{try{await axios.delete(baseURL+'/auth/users/'+u.id,{headers:authHeaders()});msg.success('已删除');fetchUsers()}catch(e:any){msg.error(e?.response?.data?.detail||'删除失败')}}})}
const openCreate=()=>{createForm.username='';createForm.password='123456';createForm.role='user';createVisible.value=true}
const handleCreate=async()=>{try{await createFormRef.value?.validate()}catch{return};saving.value=true;try{await axios.post(baseURL+'/auth/users',createForm,{headers:authHeaders()});msg.success('创建成功');createVisible.value=false;fetchUsers()}catch(e:any){msg.error(e?.response?.data?.detail||'创建失败')}finally{saving.value=false}}
const handleResetPwd=(u:any)=>{dialog.warning({title:'重置密码',content:'确定将"'+u.username+'"密码重置为123456？',positiveText:'确定',negativeText:'取消',onPositiveClick:async()=>{try{await axios.post(baseURL+'/auth/users/'+u.id+'/reset-password',{},{headers:authHeaders()});msg.success('已重置')}catch{msg.error('失败')}}})}
onMounted(()=>fetchUsers())
</script>

<style scoped>
.user-page { /* padding */ }
.page-header { display:flex;justify-content:space-between;align-items:center;margin-bottom:24px; }
.page-header h2 { margin:0;font-size:24px;font-weight:600; }
.user-list { margin-left:8px; }
.user-row { display:flex;align-items:center;gap:8px;padding:6px 8px;font-size:13px;border-radius:6px; }
.user-row:hover { background:var(--surface-hover); }
.user-name { min-width:120px;font-weight:500; }
.user-nick { color:var(--text-muted);font-weight:400;font-size:12px; }
.user-time { margin-left:auto;margin-right:12px;font-size:11px;color:var(--text-muted); }
</style>
