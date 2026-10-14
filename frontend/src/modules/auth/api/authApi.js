import { apiClient } from '@/shared/api/client'

const POLICY_VERSION = '2026-06-01'

function apiMessage(error, fallback) {
  return error?.response?.data?.error?.message || fallback
}

export const authApi = {
  async login({ email, password }) {
    try {
      const { data } = await apiClient.post('/users/auth/login', { email, password })
      return data
    } catch (error) {
      throw new Error(apiMessage(error, 'Ошибка входа'))
    }
  },

  async register(registrationData) {
    try {
      const { data } = await apiClient.post('/users/auth/register', {
        firstName: registrationData.firstName.trim(),
        lastName: registrationData.lastName.trim(),
        university: registrationData.university.trim(),
        direction: registrationData.direction.trim(),
        course: Number(registrationData.course),
        email: registrationData.email.trim(),
        password: registrationData.password,
        hobbies: registrationData.hobbies,
        onboardingAnswers: registrationData.quizAnswers.map((optionIndex, index) => ({
          questionId: index + 1,
          optionIndex
        })),
        consents: {
          personalData: Boolean(registrationData.consents?.personalData),
          terms: Boolean(registrationData.consents?.terms),
          aiAssessment: Boolean(registrationData.consents?.aiAssessment),
          policyVersion: POLICY_VERSION
        }
      })
      return data
    } catch (error) {
      throw new Error(apiMessage(error, 'Ошибка регистрации'))
    }
  }
}
