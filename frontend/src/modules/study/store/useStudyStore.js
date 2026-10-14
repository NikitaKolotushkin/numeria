import { ref } from 'vue'
import { defineStore } from 'pinia'
import { studyApi } from '@/modules/study/api/studyApi'
import { useGameStore } from '@/modules/game/store/useGameStore'
import { useAIStore } from '@/modules/ai-mentor/store/useAIStore'

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
  const correctIndexes = ref([])
  const passed = ref(null)
  const quizGeneration = ref(0)
  const error = ref('')
  const notice = ref('')

  let requestId = 0

  function hasSession() {
    return Boolean(localStorage.getItem('access_token'))
  }

  async function openCase(buildingId) {
    const id = ++requestId
    isLoading.value = true
    error.value = ''
    notice.value = ''
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
    correctIndexes.value = []
    passed.value = null
    quizGeneration.value = 0
    currentCase.value = null
    useAIStore().clear()

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
    const aiStore = useAIStore()
    aiStore.isLoading = true
    try {
      const result = await studyApi.submitBoss(blockId.value, draft.value.trim())
      aiStore.saveReview({
        score: result.score,
        verdict: result.verdict,
        reviewText: result.reviewText,
        growthZones: result.growthZones || []
      })
      const gameStore = useGameStore()
      await gameStore.load()
    } catch (err) {
      fieldError.value = err.message || 'Не удалось отправить ответ'
    } finally {
      isSubmitting.value = false
      aiStore.isLoading = false
    }
  }

  async function complete() {
    const unanswered = questions.value.some((_, index) => answers.value[index] === undefined)
    if (unanswered) {
      notice.value = 'Ответьте на все вопросы теста'
      return
    }
    try {
      await finish()
    } catch (err) {
      notice.value = err.message || 'Не удалось отправить ответы'
    }
  }

  async function finish() {
    if (!isRemote.value) {
      const questionsSource = currentCase.value?.questions || []
      correctIndexes.value = questionsSource.map((question) => question.correctAnswerIndex)
      const correctCount = correctIndexes.value.filter((value, index) => answers.value[index] === value).length
      passed.value = questions.value.length > 0 && correctCount / questions.value.length >= 0.7
      isComplete.value = true
      return
    }

    const payload = questions.value.map((question, index) => ({
      questionId: question.id,
      optionId: optionIds.value[index]?.[answers.value[index]]
    }))
    const result = await studyApi.submitBlock(blockId.value, payload)
    const correctByQuestion = Object.fromEntries(
      (result.results || []).map((item) => [item.questionId, item.correctOptionId])
    )
    correctIndexes.value = questions.value.map((question, index) => (
      optionIds.value[index]?.indexOf(correctByQuestion[question.id])
    ))
    passed.value = result.passed
    isComplete.value = true
    const gameStore = useGameStore()
    await gameStore.load()
  }

  async function regenerate() {
    if (passed.value !== false || isSubmitting.value) return
    isSubmitting.value = true
    notice.value = ''
    try {
      if (isRemote.value) {
        const block = await studyApi.regenerateBlock(blockId.value)
        optionIds.value = block.questions.map((question) => question.options.map((option) => option.id))
        questions.value = block.questions.map((question) => ({
          id: question.id,
          question: question.prompt,
          options: question.options.map((option) => option.body)
        }))
      }
      answers.value = []
      correctIndexes.value = []
      passed.value = null
      isComplete.value = false
      quizGeneration.value += 1
    } catch (err) {
      notice.value = err.message || 'Не удалось обновить тест'
    } finally {
      isSubmitting.value = false
    }
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
    correctIndexes.value = []
    passed.value = null
    error.value = ''
    notice.value = ''
    useAIStore().clear()
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
    correctIndexes,
    passed,
    quizGeneration,
    error,
    notice,
    openCase,
    startQuiz,
    answerQuestion,
    complete,
    regenerate,
    submitBoss,
    closeCase
  }
})
