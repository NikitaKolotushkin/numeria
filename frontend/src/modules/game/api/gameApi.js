import { apiClient } from '@/shared/api/client'

export const gameApi = {
  async getState() {
    const { data } = await apiClient.get('/game/me/state')
    return data
  }
}
