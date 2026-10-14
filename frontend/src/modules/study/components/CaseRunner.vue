<template>
  <div v-if="studyStore.currentCase?.type !== 'open'" class="case-frame">
    <div class="case-body">
      <p v-if="studyStore.isLoading" class="case-status">Загрузка</p>
      <p v-else-if="studyStore.error" class="case-status">{{ studyStore.error }}</p>
      <p
        v-else-if="studyStore.currentCase?.type === 'quiz' && studyStore.theory && !studyStore.quizStarted"
        class="case-theory"
      >{{ studyStore.theory }}</p>
      <QuizView
        v-else-if="studyStore.currentCase?.type === 'quiz'"
        :key="studyStore.currentCase.id"
        :questions="studyStore.questions"
        :answers="studyStore.answers"
        :is-complete="studyStore.isComplete"
        :score="studyStore.score"
        @answer="studyStore.answerQuestion"
        @complete="studyStore.complete"
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
import { computed, onMounted, onUnmounted, watch } from 'vue'
import { useStudyStore } from '@/modules/study/store/useStudyStore'
import { useAIStore } from '@/modules/ai-mentor/store/useAIStore'
import AuthErrorToast from '@/modules/auth/components/common/AuthErrorToast.vue'
import QuizView from '@/modules/study/components/QuizView.vue'
import BossCaseView from '@/modules/study/components/BossCaseView.vue'

const props = defineProps({
  buildingId: { type: String, required: true }
})

const studyStore = useStudyStore()
const aiStore = useAIStore()

let noticeTimer = null

watch(() => studyStore.notice, (value) => {
  clearTimeout(noticeTimer)
  if (!value) return
  noticeTimer = setTimeout(() => {
    studyStore.notice = ''
  }, 3000)
})

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
  clearTimeout(noticeTimer)
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
}

.quiz-nav-host:empty {
  display: none;
}

.case-status,
.case-theory {
  margin: 0;
  color: #12202b;
  font-size: 1.1rem;
  font-weight: 400;
  line-height: 1.45;
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
