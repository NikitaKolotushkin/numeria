import { ref } from 'vue'
import { defineStore } from 'pinia'
import { studyApi } from '@/modules/study/api/studyApi'
import { useGameStore } from '@/modules/game/store/useGameStore'

export const useStudyStore = defineStore('study', () => {
  const currentCase = ref(null)
  const questions = ref([])
  const answers = ref([])
  const theory = ref('')
  const blockId = ref('')
  const optionIds = ref([])
  const draft = ref('')
  const fieldError = ref('')
  const isSubmitting = ref(false)
  const isLoading = ref(false)
  const quizStarted = ref(false)
  const isComplete = ref(false)
  const isRemote = ref(false)
  const score = ref(0)
  const error = ref('')

  let requestId = 0

  function hasSession() {
    return Boolean(localStorage.getItem('access_token'))
  }

  async function openCase(buildingId) {
    const id = ++requestId
    isLoading.value = true
    error.value = ''
    isComplete.value = false
    quizStarted.value = false
    isRemote.value = false
    answers.value = []
    questions.value = []
    theory.value = ''
    blockId.value = ''
    optionIds.value = []
    draft.value = ''
    fieldError.value = ''
    isSubmitting.value = false
    score.value = 0
    currentCase.value = null

    try {
      if (!hasSession()) {
        const data = await studyApi.getCase(buildingId)
        if (id !== requestId) return
        currentCase.value = data
        questions.value = (data.questions || []).map(({ id: questionId, question, options }) => ({
          id: questionId,
          question,
          options
        }))
        return
      }

      isRemote.value = true
      const track = await studyApi.getTrack(buildingId)
      if (id !== requestId) return
      const step = track.steps.find((item) => item.status === 'available' || item.status === 'retake_required')
      if (!step) {
        const boss = track.steps.find((item) => item.kind === 'boss')
        error.value = boss?.status === 'passed' ? 'Модуль сдан' : 'Сейчас нет открытого блока'
        return
      }
      if (step.kind === 'boss') {
        const boss = await studyApi.getBoss(step.id)
        if (id !== requestId) return
        blockId.value = boss.id
        theory.value = boss.promptMarkdown || ''
        currentCase.value = { id: boss.id, type: 'open', title: boss.title }
        return
      }
      blockId.value = step.id
      const block = await studyApi.getBlock(step.id)
      if (id !== requestId) return
      theory.value = block.theoryMarkdown || ''
      optionIds.value = block.questions.map((question) => question.options.map((option) => option.id))
      questions.value = block.questions.map((question) => ({
        id: question.id,
        question: question.prompt,
        options: question.options.map((option) => option.body)
      }))
      currentCase.value = { id: block.id, type: 'quiz', title: block.title }
    } catch (err) {
      if (id !== requestId) return
      error.value = err.message || 'Не удалось открыть кейс'
    } finally {
      if (id === requestId) isLoading.value = false
    }
  }

  function startQuiz() {
    quizStarted.value = true
  }

  function answerQuestion(questionIndex, optionIndex) {
    const next = [...answers.value]
    next[questionIndex] = optionIndex
    answers.value = next
  }

  async function submitBoss() {
    if (!draft.value.trim()) {
      fieldError.value = 'Напишите ответ'
      return
    }
    fieldError.value = ''
    isSubmitting.value = true
    try {
      await studyApi.submitBoss(blockId.value, draft.value.trim())
      const gameStore = useGameStore()
      await gameStore.load()
    } catch (err) {
      fieldError.value = err.message || 'Не удалось отправить ответ'
    } finally {
      isSubmitting.value = false
    }
  }

  async function complete() {
    try {
      await finish()
    } catch (err) {
      error.value = err.message || 'Не удалось отправить ответы'
    }
  }

  async function finish() {
    if (!isRemote.value) {
      const questionsSource = currentCase.value?.questions || []
      score.value = questionsSource.reduce((sum, question, index) => {
        return sum + (answers.value[index] === question.correctAnswerIndex ? 1 : 0)
      }, 0)
      isComplete.value = true
      return
    }

    const payload = questions.value.map((question, index) => ({
      questionId: question.id,
      optionId: optionIds.value[index]?.[answers.value[index]]
    }))
    const result = await studyApi.submitBlock(blockId.value, payload)
    score.value = result.correctCount
    isComplete.value = true
    const gameStore = useGameStore()
    await gameStore.load()
  }

  function closeCase() {
    requestId += 1
    currentCase.value = null
    questions.value = []
    answers.value = []
    theory.value = ''
    blockId.value = ''
    optionIds.value = []
    draft.value = ''
    fieldError.value = ''
    isSubmitting.value = false
    isLoading.value = false
    isComplete.value = false
    quizStarted.value = false
    isRemote.value = false
    score.value = 0
    error.value = ''
  }

  return {
    currentCase,
    questions,
    answers,
    theory,
    draft,
    fieldError,
    isSubmitting,
    isLoading,
    isComplete,
    quizStarted,
    score,
    error,
    openCase,
    startQuiz,
    answerQuestion,
    complete,
    submitBoss,
    closeCase
  }
})
