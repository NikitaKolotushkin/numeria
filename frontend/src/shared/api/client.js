import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || '/api'

export const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let refreshPromise = null

function isAuthRequest(url = '') {
  return url.includes('/auth/login') || url.includes('/auth/refresh') || url.includes('/auth/register') || url.includes('/auth/logout')
}

export async function refreshAccess() {
  const refreshToken = localStorage.getItem('refresh_token')
  if (!refreshToken) {
    throw new Error('Сессия недействительна')
  }
  const { data } = await axios.post(`${baseURL}/users/auth/refresh`, { refreshToken })
  localStorage.setItem('access_token', data.accessToken)
  if (data.refreshToken) {
    localStorage.setItem('refresh_token', data.refreshToken)
  }
  if (data.user) {
    localStorage.setItem('user_data', JSON.stringify(data.user))
  }
  return data.accessToken
}

export function clearStoredSession() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user_data')
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 403) {
      clearStoredSession()
      if (!window.location.pathname.startsWith('/auth')) {
        window.location.assign('/auth?mode=login')
      }
      return Promise.reject(error)
    }
    if (error.response?.status !== 401 || !original || original._retry || isAuthRequest(original.url)) {
      return Promise.reject(error)
    }
    original._retry = true
    try {
      if (!refreshPromise) {
        refreshPromise = refreshAccess().finally(() => {
          refreshPromise = null
        })
      }
      const token = await refreshPromise
      original.headers.Authorization = `Bearer ${token}`
      return apiClient(original)
    } catch (refreshError) {
      clearStoredSession()
      if (!window.location.pathname.startsWith('/auth')) {
        window.location.assign('/auth?mode=login')
      }
      return Promise.reject(refreshError)
    }
  }
)
