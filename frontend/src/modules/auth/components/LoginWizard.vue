<template>
  <AuthErrorToast :message="errorMessage" />

  <AuthWizardLayout
    title="Войдем"
    header-title="С возвращением"
    :is-loading="authStore.isLoading"
    @prev="handlePrev"
    @next="handleNext"
  >
    <LoginStep
      v-model="formData"
      :is-loading="authStore.isLoading"
      @submit="handleNext"
    />
  </AuthWizardLayout>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import AuthWizardLayout from '@/modules/auth/components/AuthWizardLayout.vue'
import AuthErrorToast from '@/modules/auth/components/common/AuthErrorToast.vue'
import LoginStep from '@/modules/auth/components/steps/LoginStep.vue'
import { isAllowedRegistrationEmail } from '@/modules/auth/api/mockData'

const router = useRouter()
const authStore = useAuthStore()

const errorMessage = ref('')
const formData = reactive({
  email: '',
  password: ''
})

let errorTimer = null

watch(errorMessage, (value) => {
  clearTimeout(errorTimer)
  if (!value) return
  errorTimer = setTimeout(() => {
    errorMessage.value = ''
  }, 3000)
})

const handlePrev = () => {
  errorMessage.value = ''
  router.push('/')
}

const handleNext = async () => {
  errorMessage.value = ''

  if (!formData.email.trim() || !formData.email.includes('@')) {
    errorMessage.value = 'Введите корректный email'
    return
  }

  if (!isAllowedRegistrationEmail(formData.email)) {
    errorMessage.value = 'Вход доступен только для почты @guu.ru'
    return
  }

  if (!formData.password || formData.password.length < 4) {
    errorMessage.value = 'Пароль должен содержать минимум 4 символа'
    return
  }

  try {
    await authStore.login({
      email: formData.email.trim(),
      password: formData.password
    })
    router.push('/')
  } catch (err) {
    errorMessage.value = err.message || 'Ошибка входа'
  }
}
</script>
