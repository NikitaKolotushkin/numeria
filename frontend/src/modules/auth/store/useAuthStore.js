import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/modules/auth/api/authApi'
import { clearStoredSession } from '@/shared/api/client'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('access_token') || null)
  const savedUser = localStorage.getItem('user_data')
  const user = ref(savedUser ? JSON.parse(savedUser) : null)
  const isLoading = ref(false)

  const isAuthenticated = computed(() => !!token.value && !!user.value)

  function saveSession(authData) {
    token.value = authData.accessToken
    user.value = authData.user
    localStorage.setItem('access_token', authData.accessToken)
    localStorage.setItem('user_data', JSON.stringify(authData.user))
    if (authData.refreshToken) {
      localStorage.setItem('refresh_token', authData.refreshToken)
    }
  }

  async function login(credentials) {
    isLoading.value = true
    try {
      const response = await authApi.login(credentials)
      saveSession(response)
      return response
    } finally {
      isLoading.value = false
    }
  }

  async function register(registrationData) {
    isLoading.value = true
    try {
      const response = await authApi.register(registrationData)
      saveSession(response)
      return response
    } finally {
      isLoading.value = false
    }
  }

  function clearSession() {
    token.value = null
    user.value = null
    clearStoredSession()
  }

  async function logout() {
    try {
      await authApi.logout()
    } finally {
      clearSession()
    }
  }

  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    clearSession
  }
})