<template>
  <div class="login-root">
    <!-- Left brand panel -->
    <div class="brand-panel">
      <div class="brand-content">
        <div class="brand-logo">
          <img src="/icons/logo.svg" alt="SaleAgents" class="logo-img" />
          <div class="logo-glow"></div>
        </div>
        <h1 class="brand-title">SaleAgents</h1>
        <p class="brand-desc">AI 标书智能体平台</p>
        <div class="brand-features">
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>智能招标分析</span>
          </div>
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>自动生成应答文件</span>
          </div>
          <div class="feature-item">
            <div class="feature-dot"></div>
            <span>定价策略优化</span>
          </div>
        </div>
      </div>
      <div class="brand-bg-shape shape1"></div>
      <div class="brand-bg-shape shape2"></div>
    </div>

    <!-- Right login form -->
    <div class="form-panel">
      <div class="form-card">
        <div class="form-header">
          <h2 class="form-title">欢迎回来</h2>
          <p class="form-subtitle">请登录您的账号以继续</p>
        </div>

        <form @submit.prevent="handleLogin" class="form">
          <div class="field" :class="{ 'has-error': errors.username }">
            <label class="label">用户名 / 手机号</label>
            <div class="input-wrap">
              <span class="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
              </span>
              <input v-model="form.username" type="text" class="input" placeholder="请输入用户名" @input="clearError('username')" />
            </div>
            <span v-if="errors.username" class="error-msg">{{ errors.username }}</span>
          </div>

          <div class="field" :class="{ 'has-error': errors.password }">
            <label class="label">密码</label>
            <div class="input-wrap">
              <span class="input-icon">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
              </span>
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'" class="input" placeholder="请输入密码" @input="clearError('password')" />
              <button type="button" class="pwd-toggle" @click="showPwd = !showPwd">
                <svg v-if="!showPwd" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
                <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              </button>
            </div>
            <span v-if="errors.password" class="error-msg">{{ errors.password }}</span>
          </div>

          <transition name="fade">
            <div v-if="errorMsg" class="error-banner">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {{ errorMsg }}
            </div>
          </transition>

          <button type="submit" class="submit-btn" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            <span v-else>登 录</span>
          </button>
        </form>

        <div class="demo-section">
          <div class="demo-divider"><span>或使用演示账号</span></div>
          <div class="demo-items">
            <button type="button" class="demo-btn" @click="fillDemo('admin', 'admin123')">
              <span class="demo-role">管理员</span>
              <span class="demo-creds">admin / admin123</span>
            </button>
            <button type="button" class="demo-btn" @click="fillDemo('user', 'user123')">
              <span class="demo-role">普通用户</span>
              <span class="demo-creds">user / user123</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../store/auth'

const router = useRouter()
const form = reactive({ username: '', password: '' })
const errors = reactive({ username: '', password: '' })
const errorMsg = ref('')
const loading = ref(false)
const showPwd = ref(false)

const clearError = (field) => { errors[field] = '' }

const validate = () => {
  errors.username = form.username ? '' : '请输入用户名'
  errors.password = form.password ? '' : '请输入密码'
  return !errors.username && !errors.password
}

const handleLogin = async () => {
  if (!validate()) return
  errorMsg.value = ''
  loading.value = true
  try {
    await login(form.username, form.password)
    router.push('/home')
  } catch (e) {
    errorMsg.value = e?.message || '登录失败，请检查用户名和密码'
  } finally {
    loading.value = false
  }
}

const fillDemo = (user, pwd) => {
  form.username = user
  form.password = pwd
  clearError('username')
  clearError('password')
  errorMsg.value = ''
}
</script>

<style scoped>
.login-root {
  min-height: 100vh;
  display: flex;
}

/* Left brand panel */
.brand-panel {
  flex: 1;
  background: linear-gradient(135deg, #1A56DB 0%, #2563EB 50%, #3B82F6 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 3rem;
}
.brand-content {
  position: relative;
  z-index: 2;
  max-width: 400px;
}
.brand-logo {
  position: relative;
  width: 72px;
  height: 72px;
  margin-bottom: 1.5rem;
}
.logo-img {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  position: relative;
  z-index: 1;
}
.logo-glow {
  position: absolute;
  inset: -8px;
  background: rgba(255,255,255,0.15);
  border-radius: 24px;
  filter: blur(12px);
}
.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.02em;
}
.brand-desc {
  font-size: 1.1rem;
  color: rgba(255,255,255,0.8);
  margin: 0 0 2.5rem 0;
}
.brand-features {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: rgba(255,255,255,0.9);
  font-size: 0.95rem;
}
.feature-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,0.7);
  flex-shrink: 0;
}
.brand-bg-shape {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
}
.shape1 {
  width: 400px;
  height: 400px;
  bottom: -100px;
  right: -100px;
}
.shape2 {
  width: 300px;
  height: 300px;
  top: -80px;
  left: -80px;
}

/* Right form panel */
.form-panel {
  width: 520px;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
}
.form-card {
  width: 100%;
  max-width: 380px;
}
.form-header {
  margin-bottom: 2rem;
}
.form-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1E293B;
  margin: 0 0 0.5rem 0;
}
.form-subtitle {
  font-size: 0.95rem;
  color: #64748B;
  margin: 0;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}
.input-wrap {
  position: relative;
}
.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF;
  display: flex;
  pointer-events: none;
}
.input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.875rem 1rem 0.875rem 2.75rem;
  background: #F9FAFB;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  color: #1F2937;
  font-size: 0.95rem;
  transition: all 0.2s;
  outline: none;
}
.input::placeholder { color: #9CA3AF; }
.input:focus {
  border-color: #1A56DB;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(26,86,219,0.1);
}
.field.has-error .input { border-color: #EF4444; }
.pwd-toggle {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #9CA3AF;
  cursor: pointer;
  transition: color 0.2s;
  background: none;
  border: none;
  display: flex;
  padding: 0;
}
.pwd-toggle:hover { color: #6B7280; }
.error-msg { font-size: 0.8rem; color: #EF4444; }
.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.875rem 1rem;
  background: #FEF2F2;
  border: 1px solid #FECACA;
  border-radius: 10px;
  color: #DC2626;
  font-size: 0.875rem;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.submit-btn {
  width: 100%;
  padding: 0.9375rem;
  border-radius: 10px;
  font-weight: 600;
  font-size: 1rem;
  background: linear-gradient(to right, #1A56DB, #2563EB);
  color: white;
  box-shadow: 0 4px 14px rgba(26,86,219,0.25);
  transition: all 0.25s;
  cursor: pointer;
  border: none;
  letter-spacing: 0.05em;
  margin-top: 0.25rem;
}
.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(26,86,219,0.35);
}
.submit-btn:active:not(:disabled) { transform: translateY(0); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.demo-section { margin-top: 2rem; }
.demo-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 1rem;
  color: #9CA3AF;
  font-size: 0.8rem;
}
.demo-divider::before, .demo-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #E5E7EB;
}
.demo-items { display: flex; gap: 10px; }
.demo-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 0.875rem 0.75rem;
  background: #F9FAFB;
  border: 1.5px solid #E5E7EB;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.demo-btn:hover {
  background: #F3F4F6;
  border-color: #D1D5DB;
}
.demo-role {
  font-size: 0.75rem;
  font-weight: 600;
  color: #374151;
}
.demo-creds { font-size: 0.7rem; color: #6B7280; }

@media (max-width: 900px) {
  .brand-panel { display: none; }
  .form-panel { width: 100%; }
}
</style>