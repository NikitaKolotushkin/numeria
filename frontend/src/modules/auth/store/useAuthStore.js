import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)

  // Заглушка авторизации
  async function login(email, password) {
    console.log('Попытка входа:', email, password)
    // В будущем тут будет API вызов к микросервису USERS:
    // const res = await apiClient.post('/users/login', { email, password })
    isAuthenticated.value = true
  }

  return { user, isAuthenticated, login }
})
