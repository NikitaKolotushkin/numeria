import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useAIStore = defineStore('ai', () => {
  const review = ref(null)
  const isLoading = ref(false)

  function saveReview(payload) {
    review.value = payload
  }

  function clear() {
    review.value = null
    isLoading.value = false
  }

  return { review, isLoading, saveReview, clear }
})
