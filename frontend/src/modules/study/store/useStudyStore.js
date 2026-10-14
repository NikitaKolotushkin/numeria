import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { studyApi } from '@/modules/study/api/studyApi'

export const useStudyStore = defineStore('study', () => {
  const currentCase = ref(null)
  const answers = ref([])
  const isLoading = ref(false)
  const isComplete = ref(false)
  const error = ref('')

  let requestId = 0

  const score = computed(() => {
    const questions = currentCase.value?.questions || []
    return questions.reduce((sum, question, index) => {
      return sum + (answers.value[index] === question.correctAnswerIndex ? 1 : 0)
    }, 0)
  })

  const questions = computed(() => {
    return (currentCase.value?.questions || []).map(({ id, question, options }) => ({
      id,
      question,
      options
    }))
  })

  async function openCase(buildingId) {
    const id = ++requestId
    isLoading.value = true
    error.value = ''
    isComplete.value = false
    answers.value = []
    currentCase.value = null

    try {
      const data = await studyApi.getCase(buildingId)
      if (id !== requestId) return
      currentCase.value = data
    } catch (err) {
      if (id !== requestId) return
      error.value = err.message || 'Не удалось открыть кейс'
    } finally {
      if (id === requestId) isLoading.value = false
    }
  }

  function answerQuestion(questionIndex, optionIndex) {
    const next = [...answers.value]
    next[questionIndex] = optionIndex
    answers.value = next
  }

  function complete() {
    isComplete.value = true
  }

  function closeCase() {
    requestId += 1
    currentCase.value = null
    answers.value = []
    isLoading.value = false
    isComplete.value = false
    error.value = ''
  }

  return {
    currentCase,
    answers,
    questions,
    isLoading,
    isComplete,
    error,
    score,
    openCase,
    answerQuestion,
    complete,
    closeCase
  }
})
