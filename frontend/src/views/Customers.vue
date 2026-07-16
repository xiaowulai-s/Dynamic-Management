<template>
  <div class="cs-page"><div class="page-header"><h2>客户管理</h2><n-button type="primary" @click="openAdd">添加客户</n-button></div>
    <n-data-table :columns="cols" :data="items" :loading="loading" :pagination="false" striped size="small" />

    <n-modal v-model:show="showForm" :title="editId?'编辑客户':'添加客户'" preset="card" style="width:520px">
      <n-form ref="formRef" :model="form" :rules="rules" label-placement="left" label-width="80">
        <n-grid :cols="2" :x-gap="12">
          <n-form-item-gi label="名称" path="name"><n-input v-model:value="form.name" /></n-form-item-gi>
          <n-form-item-gi label="联系人"><n-input v-model:value="form.contact" /></n-form-item-gi>
          <n-form-item-gi label="电话"><n-input v-model:value="form.phone" /></n-form-item-gi>
          <n-form-item-gi label="邮箱"><n-input v-model:value="form.email" /></n-form-item-gi>
        </n-grid>
        <n-form-item label="地址"><n-input v-model:value="form.address" /></n-form-item>
        <n-form-item label="备注"><n-input v-model:value="form.remark" type="textarea" :rows="2" /></n-form-item>
      </n-form>
      <template #footer><n-space justify="end"><n-button @click="showForm=false">取消</n-button><n-button type="primary" @click="handleSave" :loading="saving">保存</n-button></n-space></template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref,reactive,onMounted,h } from 'vue'
import { useMessage,useDialog } from 'naive-ui'
import { NCard,NButton,NSpace,NModal,NForm,NFormItem,NFormItemGi,NGrid,NInput,NDataTable,NTag } from 'naive-ui'
import { useUserStore } from '@/stores/user'
import axios from 'axios'
const msg=useMessage();const dialog=useDialog();const userStore=useUserStore();const base=import.meta.env.VITE_API_URL||'/api';const hdrs=()=>({Authorization:'Bearer '+userStore.token})
const loading=ref(false);const items=ref<any[]>([]);const showForm=ref(false);const saving=ref(false);const formRef=ref();const editId=ref<number|null>(null)
const form=reactive({name:'',contact:'',phone:'',email:'',address:'',remark:''})
const rules={name:[{required:true,message:'请输入名称'}]}

const cols=[{title:'名称',key:'name',ellipsis:{tooltip:true}},{title:'联系人',key:'contact',width:100},{title:'电话',key:'phone',width:120},{title:'设备数',key:'equipment_count',width:80},{title:'创建时间',key:'created_at',width:160,render:(r:any)=>new Date(r.created_at).toLocaleDateString('zh-CN')},{title:'操作',key:'actions',width:140,render:(row:any)=>h(NSpace,{size:'small'},{default:()=>[h(NButton,{size:'tiny',onClick:()=>openEdit(row)},{default:()=>'编辑'}),h(NButton,{size:'tiny',type:'error',onClick:()=>handleDel(row)},{default:()=>'删除'})]})}]

const fetchAll=async()=>{loading.value=true;try{const r=await axios.get(base+'/customers/',{headers:hdrs()});items.value=r.data}catch{}finally{loading.value=false}}
const openAdd=()=>{editId.value=null;Object.assign(form,{name:'',contact:'',phone:'',email:'',address:'',remark:''});showForm.value=true}
const openEdit=(r:any)=>{editId.value=r.id;Object.assign(form,{name:r.name,contact:r.contact||'',phone:r.phone||'',email:r.email||'',address:r.address||'',remark:r.remark||''});showForm.value=true}
const handleSave=async()=>{try{await formRef.value?.validate()}catch{return};saving.value=true;try{if(editId.value){await axios.put(base+'/customers/'+editId.value,form,{headers:hdrs()})}else{await axios.post(base+'/customers/',form,{headers:hdrs()})};msg.success('已保存');showForm.value=false;fetchAll()}catch(e:any){msg.error(e?.response?.data?.detail||'失败')}finally{saving.value=false}}
const handleDel=(r:any)=>{dialog.warning({title:'确认删除',content:'确定删除客户"'+r.name+'"？',positiveText:'确定',negativeText:'取消',onPositiveClick:async()=>{try{await axios.delete(base+'/customers/'+r.id,{headers:hdrs()});msg.success('已删除');fetchAll()}catch{msg.error('失败')}}})}
onMounted(()=>fetchAll())
</script>

<style scoped>.cs-page{/*padding*/}.page-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}.page-header h2{margin:0;font-size:24px;font-weight:600}</style>
