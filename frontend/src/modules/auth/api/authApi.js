import { MOCK_AUTH_RESPONSE, MOCK_USER } from '@/modules/auth/api/mockData'

export const authApi = {
  async login({ email, password }) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (!email || !password) {
          reject(new Error('Заполните почту и пароль'))
          return
        }
        resolve(MOCK_AUTH_RESPONSE)
      }, 350)
    })
  },

  async register(registrationData) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (!registrationData.email || !registrationData.password) {
          reject(new Error('Пожалуйста, заполните контактные данные'))
          return
        }

        const fullName = `${registrationData.firstName || ''} ${registrationData.lastName || ''}`.trim() || 'Новый игрок'

        const newUser = {
          ...MOCK_USER,
          id: 'usr_' + Math.floor(Math.random() * 100000),
          email: registrationData.email,
          firstName: registrationData.firstName,
          lastName: registrationData.lastName,
          fullName,
          university: registrationData.university,
          direction: registrationData.direction,
          course: Number(registrationData.course) || 1,
          hobbies: registrationData.hobbies || [],
          nickname: fullName.split(' ')[0] + '_' + Math.floor(Math.random() * 1000)
        }

        resolve({
          ...MOCK_AUTH_RESPONSE,
          user: newUser
        })
      }, 400)
    })
  },

  async getProfile() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve(MOCK_USER)
      }, 200)
    })
  }
}