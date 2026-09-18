<template>
  <AuthErrorToast :message="errorMessage" />

  <RegisterStepWelcome
    v-if="isWelcome"
    :is-loading="authStore.isLoading"
    @start="handleStart"
  />

  <AuthWizardLayout
    v-else
    :title="stepTitles[currentStep]"
    :is-loading="authStore.isLoading"
    @prev="handlePrev"
    @next="handleNext"
  >
    <RegisterStepPersonal
      v-if="currentStep === 1"
      v-model="formData"
    />

    <RegisterStepSecurity
      v-else-if="currentStep === 2"
      v-model="formData"
    />

    <RegisterStepHobbies
      v-else-if="currentStep === 3"
      v-model="formData.hobbies"
    />

    <RegisterStepQuiz
      v-else-if="currentStep === 4"
      v-model="formData.quizAnswers"
      @complete="showWelcome"
    />
  </AuthWizardLayout>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import AuthWizardLayout from '@/modules/auth/components/AuthWizardLayout.vue'
import AuthErrorToast from '@/modules/auth/components/common/AuthErrorToast.vue'
import RegisterStepPersonal from '@/modules/auth/components/steps/RegisterStepPersonal.vue'
import RegisterStepSecurity from '@/modules/auth/components/steps/RegisterStepSecurity.vue'
import RegisterStepHobbies from '@/modules/auth/components/steps/RegisterStepHobbies.vue'
import RegisterStepQuiz from '@/modules/auth/components/steps/RegisterStepQuiz.vue'
import RegisterStepWelcome from '@/modules/auth/components/steps/RegisterStepWelcome.vue'

const router = useRouter()
const authStore = useAuthStore()

const currentStep = ref(1)
const isWelcome = ref(false)
const errorMessage = ref('')

let errorTimer = null

watch(errorMessage, (value) => {
  clearTimeout(errorTimer)
  if (!value) return
  errorTimer = setTimeout(() => {
    errorMessage.value = ''
  }, 3000)
})

const stepTitles = {
  1: 'Познакомимся',
  2: 'Защитимся',
  3: 'Персонализируем',
  4: 'Небольшой тест'
}

const formData = reactive({
  firstName: '',
  lastName: '',
  university: '',
  direction: '',
  course: 1,
  email: '',
  password: '',
  confirmPassword: '',
  hobbies: [],
  quizAnswers: []
})

const showWelcome = () => {
  errorMessage.value = ''
  isWelcome.value = true
}

const handlePrev = () => {
  errorMessage.value = ''
  if (currentStep.value > 1) {
    currentStep.value--
  } else {
    router.push('/')
  }
}

const handleNext = async () => {
  errorMessage.value = ''

  if (currentStep.value === 1) {
    if (!formData.firstName.trim() || !formData.lastName.trim()) {
      errorMessage.value = 'Пожалуйста, укажите имя и фамилию'
      return
    }
    if (!formData.university) {
      errorMessage.value = 'Выберите ваш университет'
      return
    }
    if (!formData.direction) {
      errorMessage.value = 'Выберите направление обучения'
      return
    }
    currentStep.value = 2
    return
  }

  if (currentStep.value === 2) {
    if (!formData.email.trim() || !formData.email.includes('@')) {
      errorMessage.value = 'Введите корректный email'
      return
    }
    if (!formData.password || formData.password.length < 4) {
      errorMessage.value = 'Пароль должен содержать минимум 4 символа'
      return
    }
    if (formData.password !== formData.confirmPassword) {
      errorMessage.value = 'Пароли не совпадают'
      return
    }
    currentStep.value = 3
    return
  }

  if (currentStep.value === 3) {
    if (formData.hobbies.length === 0) {
      errorMessage.value = 'Выберите хотя бы один интерес'
      return
    }
    currentStep.value = 4
    return
  }

  if (currentStep.value === 4) {
    const answeredCount = formData.quizAnswers.filter((answer) => answer !== undefined).length
    if (answeredCount < 5) {
      errorMessage.value = 'Ответьте на все вопросы теста'
      return
    }
    showWelcome()
  }
}

const handleStart = async () => {
  errorMessage.value = ''
  try {
    await authStore.register(formData)
    router.push('/')
  } catch (err) {
    errorMessage.value = err.message || 'Ошибка регистрации'
  }
}
</script>
