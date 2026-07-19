<template>
  <div class="login-page">
    <div class="login-shell">
      <!-- 左侧品牌区 -->
      <aside class="brand-panel">
        <div class="brand-head">
          <div class="brand-logo">
            <el-icon :size="20"><Histogram /></el-icon>
          </div>
          <div class="brand-name">
            <span class="brand-title">{{ siteTitleZh }}</span>
            <span class="brand-sub">{{ siteTitleEn }}</span>
          </div>
        </div>

        <div class="brand-body">
          <h1 class="brand-slogan">{{ siteTitleZh }}</h1>
          <p class="brand-desc">
            面向现场工程师与管理员的内网效率工具，覆盖安装到报废的全过程记录与审核。
          </p>

          <ul class="feature-list">
            <li class="feature-item">
              <div class="feature-icon"><el-icon :size="14"><Check /></el-icon></div>
              <div class="feature-text">
                <span class="feature-title">8类设备日志</span>
                <span class="feature-sub">标准化录入与审核流程</span>
              </div>
            </li>
            <li class="feature-item">
              <div class="feature-icon"><el-icon :size="14"><Check /></el-icon></div>
              <div class="feature-text">
                <span class="feature-title">实时可视化</span>
                <span class="feature-sub">设备状态与日志数据看板</span>
              </div>
            </li>
            <li class="feature-item">
              <div class="feature-icon"><el-icon :size="14"><Check /></el-icon></div>
              <div class="feature-text">
                <span class="feature-title">权限与留痕</span>
                <span class="feature-sub">角色审批与内网安全部署</span>
              </div>
            </li>
          </ul>
        </div>

        <div class="brand-foot">© 2026 {{ siteTitleZh }} · 内网部署 v1.0</div>
      </aside>

      <!-- 右侧表单区 -->
      <section class="form-panel">
        <div class="form-wrap">
          <div class="form-head">
            <h2 class="form-title">欢迎登录</h2>
            <p class="form-subtitle">请输入您的账号信息以继续</p>
          </div>

          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="rules"
            label-width="0"
            size="large"
            class="login-form"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="请输入用户名"
                :prefix-icon="User"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                @click="handleLogin"
                class="login-btn"
              >
                <span>{{ loading ? '登录中...' : '登录' }}</span>
                <el-icon v-if="!loading" class="btn-arrow"><ArrowRight /></el-icon>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="form-foot">
            <span class="foot-text">内网系统 · 仅授权用户可访问</span>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { User, Lock, ArrowRight, Histogram, Check } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { useSiteTitle } from '@/composables/useSiteTitle'

const { siteTitleZh, siteTitleEn, loadSiteTitle } = useSiteTitle()

onMounted(() => {
  loadSiteTitle()
})

const router = useRouter()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度应在3-50个字符之间', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  try {
    await loginFormRef.value?.validate()

    loading.value = true
    await userStore.login({
      username: loginForm.username,
      password: loginForm.password
    })

    ElMessage.success('登录成功')

    await nextTick()
    router.push('/dashboard')
  } catch (error: any) {
    const detail = error?.response?.data?.detail
    ElMessage.error(detail || error?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-page);
  padding: var(--space-5);
}

.login-shell {
  display: grid;
  grid-template-columns: 1fr 1fr;
  width: 100%;
  max-width: 960px;
  min-height: 560px;
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

/* ===== 左侧品牌区 ===== */
.brand-panel {
  background: linear-gradient(135deg, var(--color-primary-600) 0%, var(--color-primary-700) 100%);
  color: #FFFFFF;
  padding: var(--space-6);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.brand-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 28px 28px;
  pointer-events: none;
}

.brand-head {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  position: relative;
  z-index: 1;
}

.brand-logo {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.brand-name {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.brand-title {
  font-size: var(--text-sm);
  font-weight: var(--font-w-semibold);
}

.brand-sub {
  font-size: var(--text-xs);
  opacity: 0.8;
}

.brand-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: var(--space-5);
  position: relative;
  z-index: 1;
  padding: var(--space-5) 0;
}

.brand-slogan {
  font-size: var(--text-xl);
  font-weight: var(--font-w-bold);
  line-height: 1.35;
  letter-spacing: -0.01em;
}

.brand-desc {
  font-size: var(--text-sm);
  line-height: 1.7;
  opacity: 0.85;
  max-width: 320px;
}

.feature-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.06);
}

.feature-icon {
  width: 24px;
  height: 24px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}

.feature-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.feature-title {
  font-size: var(--text-sm);
  font-weight: var(--font-w-medium);
}

.feature-sub {
  font-size: var(--text-xs);
  opacity: 0.75;
}

.brand-foot {
  font-size: var(--text-xs);
  opacity: 0.6;
  position: relative;
  z-index: 1;
}

/* ===== 右侧表单区 ===== */
.form-panel {
  background: var(--surface-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
}

.form-wrap {
  width: 100%;
  max-width: 340px;
}

.form-head {
  margin-bottom: var(--space-6);
}

.form-title {
  font-size: var(--text-xl);
  font-weight: var(--font-w-semibold);
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.form-subtitle {
  font-size: var(--text-sm);
  color: var(--text-tertiary);
  margin-top: var(--space-1);
}

.login-form :deep(.el-input__wrapper) {
  border-radius: var(--radius-sm);
}

.login-btn {
  width: 100%;
  font-weight: var(--font-w-medium);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
}

.btn-arrow {
  font-size: 14px;
}

.form-foot {
  margin-top: var(--space-5);
  text-align: center;
}

.foot-text {
  font-size: var(--text-xs);
  color: var(--text-tertiary);
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .login-shell {
    grid-template-columns: 1fr;
    max-width: 420px;
    min-height: auto;
  }

  .brand-panel {
    display: none;
  }
}
</style>
