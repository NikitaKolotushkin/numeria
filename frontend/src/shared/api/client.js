import axios from 'axios'

export const apiClient = axios.create({
  // Берет URL API Gateway из .env файла или дефолтный адрес локального nginx
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Задел на будущее: перехватчик для добавления JWT токена
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
