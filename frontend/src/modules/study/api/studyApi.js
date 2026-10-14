import { BUILDING_CASES } from '@/modules/study/api/mockData'

export const studyApi = {
  async getCase(buildingId) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const item = BUILDING_CASES[buildingId]
        if (!item) {
          reject(new Error('Кейс не найден'))
          return
        }

        resolve(structuredClone(item))
      }, 320)
    })
  }
}
