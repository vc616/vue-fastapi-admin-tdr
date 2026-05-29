<template>
  <section class="login-page">
    <div class="login-container">
      <div class="login-left">
        <div class="brand-content">
          <div class="brand-icon">
            <icon-custom-logo text-80 color-primary></icon-custom-logo>
          </div>
          <h1 class="brand-title">{{ $t('app_name') }}</h1>
          <p class="brand-subtitle">高效 · 智能 · 安全</p>
          <div class="brand-features">
            <div class="feature-item">
              <n-icon><icon-mdi:shield-check /></n-icon>
              <span>权限精细化控制</span>
            </div>
            <div class="feature-item">
              <n-icon><icon-mdi:chart-line /></n-icon>
              <span>数据可视化分析</span>
            </div>
            <div class="feature-item">
              <n-icon><icon-mdi:cloud-sync /></n-icon>
              <span>实时数据同步</span>
            </div>
          </div>
        </div>
      </div>

      <div class="login-right">
        <div class="login-card">
          <div class="login-card-header">
            <h2>用户登录</h2>
            <p>欢迎使用管理系统</p>
          </div>

          <n-form ref="formRef" :model="loginInfo" :rules="rules" class="login-form">
            <n-form-item path="username" label="用户名">
              <n-input
                v-model:value="loginInfo.username"
                autofocus
                placeholder="请输入用户名"
                size="large"
                :maxlength="20"
                @keypress.enter="handleLogin"
              >
                <template #prefix>
                  <n-icon><icon-mdi:account /></n-icon>
                </template>
              </n-input>
            </n-form-item>

            <n-form-item path="password" label="密码">
              <n-input
                v-model:value="loginInfo.password"
                type="password"
                placeholder="请输入密码"
                size="large"
                show-password-on="mousedown"
                :maxlength="20"
                @keypress.enter="handleLogin"
              >
                <template #prefix>
                  <n-icon><icon-mdi:lock /></n-icon>
                </template>
              </n-input>
            </n-form-item>

            <div class="login-actions">
              <a class="forgot-link" @click="showForgotModal = true">忘记密码？</a>
            </div>

            <n-button
              type="primary"
              size="large"
              block
              :loading="loading"
              :disabled="!loginInfo.username || !loginInfo.password"
              @click="handleLogin"
            >
              {{ loading ? '登录中...' : '登 录' }}
            </n-button>
          </n-form>

          <div class="login-footer">
            <span>默认账号：admin / 123456</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 忘记密码弹窗 -->
    <n-modal v-model:show="showForgotModal" preset="card" title="找回密码" style="max-width: 420px;" :mask-closable="false">
      <n-form ref="forgotFormRef" :model="forgotForm" :rules="forgotRules" label-placement="top">
        <n-form-item label="用户名" path="username">
          <n-input v-model:value="forgotForm.username" placeholder="请输入用户名" size="large">
            <template #prefix>
              <n-icon><icon-mdi:account /></n-icon>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item label="验证码" path="code">
          <div class="verify-code-row">
            <n-input
              v-model:value="forgotForm.code"
              placeholder="请输入验证码"
              size="large"
              :maxlength="6"
            >
              <template #prefix>
                <n-icon><icon-mdi:shield-check /></n-icon>
              </template>
            </n-input>
            <n-button
              size="large"
              :disabled="countdown > 0"
              @click="handleSendCode"
            >
              {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
            </n-button>
          </div>
        </n-form-item>

        <n-form-item label="新密码" path="password">
          <n-input
            v-model:value="forgotForm.password"
            type="password"
            placeholder="请输入新密码"
            size="large"
            show-password-on="mousedown"
            :maxlength="20"
          >
            <template #prefix>
              <n-icon><icon-mdi:lock /></n-icon>
            </template>
          </n-input>
        </n-form-item>

        <n-form-item label="确认密码" path="confirmPassword">
          <n-input
            v-model:value="forgotForm.confirmPassword"
            type="password"
            placeholder="请再次输入新密码"
            size="large"
            show-password-on="mousedown"
            :maxlength="20"
          >
            <template #prefix>
              <n-icon><icon-mdi:lock-check /></n-icon>
            </template>
          </n-input>
        </n-form-item>
      </n-form>

      <template #footer>
        <div class="modal-footer">
          <n-button @click="showForgotModal = false">取消</n-button>
          <n-button type="primary" :loading="forgotLoading" @click="handleResetPassword">确认重置</n-button>
        </div>
      </template>
    </n-modal>
  </section>
</template>

<script setup>
import { lStorage, setToken } from '@/utils'
import api from '@/api'
import { addDynamicRoutes } from '@/router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { query } = useRoute()
const { t } = useI18n({ useScope: 'global' })

const formRef = ref(null)
const forgotFormRef = ref(null)

const loginInfo = ref({
  username: '',
  password: '',
})

const rules = {
  username: { required: true, message: '请输入用户名', trigger: 'blur' },
  password: { required: true, message: '请输入密码', trigger: 'blur' },
}

initLoginInfo()

function initLoginInfo() {
  const localLoginInfo = lStorage.get('loginInfo')
  if (localLoginInfo) {
    loginInfo.value.username = localLoginInfo.username || ''
    loginInfo.value.password = localLoginInfo.password || ''
  }
}

const loading = ref(false)
async function handleLogin() {
  const { username, password } = loginInfo.value
  if (!username || !password) {
    $message.warning('请输入用户名和密码')
    return
  }
  try {
    loading.value = true
    $message.loading('正在验证...')
    const res = await api.login({ username, password: password.toString() })
    $message.success('登录成功')
    setToken(res.data.access_token)
    await addDynamicRoutes()
    if (query.redirect) {
      const path = query.redirect
      Reflect.deleteProperty(query, 'redirect')
      router.push({ path, query })
    } else {
      router.push('/')
    }
  } catch (e) {
    console.error('login error', e.error)
  } finally {
    loading.value = false
  }
}

// 忘记密码相关
const showForgotModal = ref(false)
const forgotLoading = ref(false)
const countdown = ref(0)
let countdownTimer = null

const forgotForm = ref({
  username: '',
  code: '',
  password: '',
  confirmPassword: '',
})

const forgotRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  code: { required: true, message: '请输入验证码', trigger: 'blur' },
  password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value) => value === forgotForm.value.password,
      message: '两次密码输入不一致',
      trigger: 'blur',
    },
  ],
}

function handleSendCode() {
  if (!forgotForm.value.username) {
    $message.warning('请先输入用户名')
    return
  }

  api.sendVerifyCode({ email: forgotForm.value.username }).then((res) => {
    if (res.code === 200) {
      $message.success('验证码已发送，请查看邮箱')
      countdown.value = 60
      countdownTimer = setInterval(() => {
        countdown.value--
        if (countdown.value <= 0) {
          clearInterval(countdownTimer)
        }
      }, 1000)
    }
  })
}

function handleResetPassword() {
  forgotFormRef.value?.validate((errors) => {
    if (errors) return

    if (forgotForm.value.password !== forgotForm.value.confirmPassword) {
      $message.error('两次密码输入不一致')
      return
    }

    forgotLoading.value = true
    api
      .resetPassword({
        email: forgotForm.value.username,
        code: forgotForm.value.code,
        new_password: forgotForm.value.password,
      })
      .then((res) => {
        if (res.code === 200) {
          $message.success('密码重置成功，请使用新密码登录')
          showForgotModal.value = false
          forgotForm.value = {
            username: '',
            code: '',
            password: '',
            confirmPassword: '',
          }
          if (countdownTimer) {
            clearInterval(countdownTimer)
            countdown.value = 0
          }
        }
      })
      .finally(() => {
        forgotLoading.value = false
      })
  })
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: #020617;
}

.login-container {
  display: flex;
  min-height: 100vh;
}

.login-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
}

.brand-content {
  text-align: center;
  color: #fff;
}

.brand-icon {
  margin-bottom: 24px;
}

.brand-title {
  font-size: 42px;
  font-weight: 700;
  margin: 0 0 16px 0;
  background: linear-gradient(90deg, #fff 0%, #22C55E 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 48px 0;
  letter-spacing: 8px;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: left;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.85);
}

.feature-item .n-icon {
  font-size: 24px;
  color: #22C55E;
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #0F172A;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 48px 40px;
  background: #1E293B;
  border-radius: 16px;
  border: 1px solid rgba(51, 65, 85, 0.5);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.login-card-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-card-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #F8FAFC;
  margin: 0 0 8px 0;
}

.login-card-header p {
  font-size: 14px;
  color: #94A3B8;
  margin: 0;
}

.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.n-form-item-label__text) {
  font-size: 14px;
  color: #CBD5E1;
  font-weight: 500;
}

.login-form :deep(.n-input) {
  background: #0F172A;
  border-color: #334155;
}

.login-form :deep(.n-input__input-el) {
  color: #F8FAFC;
}

.login-form :deep(.n-input__placeholder) {
  color: #64748B;
}

.login-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

.forgot-link {
  font-size: 14px;
  color: #22C55E;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s ease;
}

.forgot-link:hover {
  color: #4ADE80;
}

.login-footer {
  text-align: center;
  font-size: 12px;
  color: #64748B;
  padding-top: 16px;
  border-top: 1px solid #334155;
}

.verify-code-row {
  display: flex;
  gap: 12px;
}

.verify-code-row .n-input {
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Primary button override */
.login-form :deep(.n-button--primary-type) {
  background: #22C55E !important;
  border-color: #22C55E !important;
}

.login-form :deep(.n-button--primary-type:hover) {
  background: #4ADE80 !important;
  border-color: #4ADE80 !important;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .login-left {
    padding: 60px 20px 30px;
  }

  .brand-title {
    font-size: 28px;
  }

  .brand-features {
    display: none;
  }

  .login-right {
    padding: 20px;
    background: #020617;
  }

  .login-card {
    padding: 32px 24px;
    background: #1E293B;
  }
}
</style>
