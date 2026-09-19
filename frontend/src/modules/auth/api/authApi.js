import { MOCK_AUTH_RESPONSE, MOCK_USER, isAllowedCourse, isAllowedRegistrationEmail } from '@/modules/auth/api/mockData'

export const authApi = {
  async login({ email, password }) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (!email || !password) {
          reject(new Error('Заполните почту и пароль'))
          return
        }

        if (!isAllowedRegistrationEmail(email)) {
          reject(new Error('Вход доступен только для почты @guu.ru'))
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

        if (!isAllowedRegistrationEmail(registrationData.email)) {
          reject(new Error('Регистрация доступна только для почты @guu.ru'))
          return
        }

        if (!isAllowedCourse(registrationData.course)) {
          reject(new Error('Укажите курс цифрой от 1 до 6'))
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
          university: String(registrationData.university || '').trim(),
          direction: String(registrationData.direction || '').trim(),
          course: Number(registrationData.course),
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