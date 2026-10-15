<template>
  <div v-if="studyStore.currentCase?.type !== 'open'" class="case-frame">
    <div class="case-body">
      <p v-if="studyStore.isLoading" class="case-status case-loading">
        <span>Загрузка</span><span class="case-loading-dots">{{ loadingDots }}</span>
      </p>
      <p v-else-if="studyStore.error" class="case-status">{{ studyStore.error }}</p>
      <div
        v-else-if="studyStore.currentCase?.type === 'quiz' && studyStore.theory && !studyStore.quizStarted"
        class="case-theory"
      >
        <template v-for="(part, index) in theoryParts" :key="index">
          <h3 v-if="part.heading" class="theory-heading">{{ part.heading }}</h3>
          <p v-if="part.text" class="theory-paragraph">{{ part.text }}</p>
        </template>
      </div>
      <QuizView
        v-else-if="studyStore.currentCase?.type === 'quiz'"
        :key="`${studyStore.currentCase.id}-${studyStore.quizGeneration}`"
        :questions="studyStore.questions"
        :answers="studyStore.answers"
        :is-complete="studyStore.isComplete"
        :passed="studyStore.passed"
        :correct-indexes="studyStore.correctIndexes"
        :explanations="studyStore.explanations"
        :reviewing="studyStore.isReviewing"
        :retrying="studyStore.isSubmitting"
        @answer="studyStore.answerQuestion"
        @complete="studyStore.complete"
        @retry="studyStore.regenerate"
      />
    </div>
    <button
      v-if="showTheoryNext"
      type="button"
      class="theory-next"
      @click="studyStore.startQuiz"
    >К тесту</button>
    <div class="quiz-nav-host"></div>
  </div>
  <AuthErrorToast :message="studyStore.notice" />
  <BossCaseView
    v-if="!studyStore.isLoading && !studyStore.error && studyStore.currentCase?.type === 'open'"
    :prompt="studyStore.theory"
    :draft="studyStore.draft"
    :submitting="studyStore.isSubmitting"
    :field-error="studyStore.fieldError"
    :review="aiStore.review"
    @update:draft="studyStore.draft = $event"
    @submit="studyStore.submitBoss"
    @revise="aiStore.clear()"
  />
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useStudyStore } from '@/modules/study/store/useStudyStore'
import { useAIStore } from '@/modules/ai-mentor/store/useAIStore'
import AuthErrorToast from '@/modules/auth/components/common/AuthErrorToast.vue'
import QuizView from '@/modules/study/components/QuizView.vue'
import BossCaseView from '@/modules/study/components/BossCaseView.vue'
import { theoryParts as splitTheory } from '@/shared/text/plainText'

const props = defineProps({
  buildingId: { type: String, required: true }
})

const emit = defineEmits(['passed'])

const studyStore = useStudyStore()
const aiStore = useAIStore()

const LOADING_DOTS = ['', '.', '..', '...']
const loadingDots = ref('')
let dotsTimer = null
let noticeTimer = null
let passTimer = null

watch(() => studyStore.passed, (passed) => {
  clearTimeout(passTimer)
  if (passed !== true) return
  passTimer = setTimeout(() => emit('passed'), 2500)
})

watch(() => studyStore.isLoading, (loading) => {
  clearInterval(dotsTimer)
  loadingDots.value = ''
  if (!loading) return
  let step = 0
  dotsTimer = setInterval(() => {
    step = (step + 1) % LOADING_DOTS.length
    loadingDots.value = LOADING_DOTS[step]
  }, 400)
}, { immediate: true })

watch(() => studyStore.notice, (value) => {
  clearTimeout(noticeTimer)
  if (!value) return
  noticeTimer = setTimeout(() => {
    studyStore.notice = ''
  }, 3000)
})

const theoryParts = computed(() => splitTheory(studyStore.theory))

const showTheoryNext = computed(() => (
  studyStore.currentCase?.type === 'quiz'
  && studyStore.theory
  && !studyStore.quizStarted
  && !studyStore.isLoading
  && !studyStore.error
))

onMounted(() => {
  studyStore.openCase(props.buildingId)
})

watch(() => props.buildingId, (buildingId) => {
  studyStore.openCase(buildingId)
})

onUnmounted(() => {
  clearInterval(dotsTimer)
  clearTimeout(noticeTimer)
  clearTimeout(passTimer)
  studyStore.closeCase()
})
</script>

<style scoped>
.case-frame {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  gap: clamp(0.85rem, 1.8vh, 1.2rem);
}

.case-body {
  flex: 1;
  min-width: 0;
  min-height: 0;
  overflow: auto;
  scrollbar-gutter: stable;
  scrollbar-width: thin;
  scrollbar-color: #c5ced4 transparent;
}

.case-body::-webkit-scrollbar {
  width: 8px;
}

.case-body::-webkit-scrollbar-thumb {
  background: #c5ced4;
  border-radius: 9999px;
}

.quiz-nav-host:empty {
  display: none;
}

.case-body:has(.case-loading) {
  display: flex;
  align-items: center;
  justify-content: center;
}

.case-status {
  margin: 0;
  color: #12202b;
  font-size: 1.1rem;
  font-weight: 400;
  line-height: 1.45;
}

.case-theory {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
  min-height: 0;
  overflow: auto;
}

.theory-heading {
  margin: 0.35rem 0 0;
  color: #12202b;
  font-size: 1.2rem;
  font-weight: 700;
  line-height: 1.35;
}

.theory-paragraph {
  margin: 0;
  color: #12202b;
  font-size: 1.1rem;
  font-weight: 400;
  line-height: 1.55;
}

.case-loading {
  display: flex;
  align-items: baseline;
}

.case-loading-dots {
  display: inline-block;
  width: 1.5em;
  text-align: left;
}

.theory-next {
  align-self: flex-end;
  flex-shrink: 0;
  min-width: 8.5rem;
  height: var(--auth-nav-size, clamp(2.85rem, 6.2vh, 3.35rem));
  padding: 0 1.75rem;
  border: none;
  border-radius: 9999px;
  background: #061e27;
  color: #ffffff;
  font: inherit;
  font-size: 1.05rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
