import { defineStore } from 'pinia'
import { ref } from 'vue'
import { gameApi } from '@/modules/game/api/gameApi'

export const useGameStore = defineStore('game', () => {
  const capital = ref(0)
  const xp = ref(0)
  const rankPosition = ref(null)
  const buildings = ref([])
  const loaded = ref(false)

  function building(buildingId) {
    return buildings.value.find((item) => item.buildingId === buildingId) || null
  }

  function levelOf(buildingId) {
    return building(buildingId)?.level ?? 1
  }

  async function load() {
    const data = await gameApi.getState()
    capital.value = data.capital
    xp.value = data.xp
    rankPosition.value = data.rankPosition
    buildings.value = data.buildings || []
    loaded.value = true
  }

  function reset() {
    capital.value = 0
    xp.value = 0
    rankPosition.value = null
    buildings.value = []
    loaded.value = false
  }

  return {
    capital,
    xp,
    rankPosition,
    buildings,
    loaded,
    building,
    levelOf,
    load,
    reset
  }
})
