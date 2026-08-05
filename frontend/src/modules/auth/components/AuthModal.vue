<template>
  <BaseModal :is-open="isOpen" @close="handleClose">
    <div class="auth-form">
      <h2>{{ isRegister ? 'Регистрация' : 'Вход в систему' }}</h2>

      <form @submit.prevent="handleSubmit">
        <!-- Поле Имени (только при регистрации) -->
        <div class="form-group" v-if="isRegister">
          <label>Имя пользователя</label>
          <input 
            type="text" 
            v-model="form.username" 
            required 
            placeholder="Иван Иванов" 
          />
        </div>

        <!-- Поле Email с валидацией -->
        <div class="form-group">
          <label>Учебная почта ГУУ (@guu.ru)</label>
          <input 
            type="email" 
            v-model="form.email" 
            required 
            placeholder="danil_zenin@guu.ru"
            :class="{ 'input-error': errorMessage }"
            @input="errorMessage = ''" 
          />
          <!-- Отрисовка сообщения об ошибке -->
          <span v-if="errorMessage" class="error-text">{{ errorMessage }}</span>
        </div>

        <!-- Поле Пароля -->
        <div class="form-group">
          <label>Пароль</label>
          <input 
            type="password" 
            v-model="form.password" 
            required 
            placeholder="••••••••" 
          />
        </div>

        <button type="submit" class="submit-btn">
          {{ isRegister ? 'Создать аккаунт' : 'Войти' }}
        </button>
      </form>

      <!-- Переключение режимов Вход / Регистрация -->
      <div class="switch-mode">
        <span @click="toggleMode">
          {{ isRegister ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Зарегистрироваться' }}
        </span>
      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, reactive } from 'vue'
import BaseModal from '@/shared/ui/BaseModal.vue'
import { useAuthStore } from '../store/useAuthStore'

defineProps({ isOpen: Boolean })
const emit = defineEmits(['close'])

const authStore = useAuthStore()
const isRegister = ref(false)
const errorMessage = ref('')

const form = reactive({
  username: '',
  email: '',
  password: ''
})

// Функция проверки домена почты
const validateEmailDomain = (email) => {
  const cleanEmail = email.trim().toLowerCase()
  return cleanEmail.endsWith('@guu.ru')
}

// Переключение режим Вход <-> Регистрация
const toggleMode = () => {
  isRegister.value = !isRegister.value
  errorMessage.value = ''
}

// Очистка при закрытии модалки
const handleClose = () => {
  errorMessage.value = ''
  emit('close')
}

// Обработка отправки формы
const handleSubmit = async () => {
  errorMessage.value = ''

  // 1. Проверяем домен почты
  if (!validateEmailDomain(form.email)) {
    errorMessage.value = 'Доступ разрешен только для почты с доменом @guu.ru'
    return
  }

  // 2. Если всё ок — вызываем стор авторизации
  try {
    const cleanEmail = form.email.trim().toLowerCase()
    await authStore.login(cleanEmail, form.password)
    handleClose()
  } catch (err) {
    errorMessage.value = err.message || 'Ошибка при входе'
  }
}
</script>

<style scoped>
.auth-form h2 {
  margin-bottom: 24px;
  text-align: center;
  font-size: 22px;
}

.form-group {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  color: var(--color-text-muted);
}

.form-group input {
  background: #0f172a;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 12px;
  border-radius: 8px;
  color: white;
  outline: none;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: var(--color-accent);
}

/* Красная рамка при ошибке */
.form-group input.input-error {
  border-color: #ef4444;
}

/* Текст ошибки под инпутом */
.error-text {
  color: #ef4444;
  font-size: 12px;
  margin-top: 2px;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background: #061e27;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  margin-top: 8px;
  transition: background 0.2s;
}

.submit-btn:hover {
  background: #0a2d3a;
}

.switch-mode {
  margin-top: 18px;
  text-align: center;
  font-size: 13px;
  color: var(--color-accent);
  cursor: pointer;
  user-select: none;
}

.switch-mode:hover {
  text-decoration: underline;
}
</style>