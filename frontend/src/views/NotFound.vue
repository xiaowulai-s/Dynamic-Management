<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面不存在</p>
    <el-button type="primary" @click="$router.push('/dashboard')">返回首页</el-button>
  </div>
</template>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: var(--surface-page);
}

h1 {
  font-size: 120px;
  font-weight: var(--font-w-bold);
  color: var(--color-primary-400);
  margin-bottom: var(--space-4);
  letter-spacing: -0.04em;
  line-height: 1;
}

p {
  font-size: var(--text-2xl);
  color: var(--text-secondary);
  margin-bottom: var(--space-8);
}
</style>
