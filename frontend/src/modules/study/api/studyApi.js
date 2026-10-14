import { apiClient } from '@/shared/api/client'
import { BUILDING_CASES } from '@/modules/study/api/mockData'

function apiMessage(error, fallback) {
  return error?.response?.data?.error?.message || fallback
}

export const studyApi = {
  async getCase(buildingId) {
    const item = BUILDING_CASES[buildingId]
    if (!item) {
      throw new Error('Кейс не найден')
    }
    return structuredClone(item)
  },

  async getTrack(buildingId) {
    try {
      const { data } = await apiClient.get(`/study/tracks/${buildingId}`)
      return data
    } catch (error) {
      throw new Error(apiMessage(error, 'Не удалось открыть кейс'))
    }
  },

  async getBlock(blockId) {
    try {
      const { data } = await apiClient.get(`/study/blocks/${blockId}`)
      return data
    } catch (error) {
      throw new Error(apiMessage(error, 'Не удалось подготовить задание'))
    }
  },

  async submitBlock(blockId, answers) {
    try {
      const { data } = await apiClient.post(`/study/blocks/${blockId}/attempts`, { answers })
      return data
    } catch (error) {
      throw new Error(apiMessage(error, 'Не удалось отправить ответы'))
    }
  }
}
