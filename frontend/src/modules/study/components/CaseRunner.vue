<template>
  <div v-if="studyStore.currentCase?.type !== 'open'" class="case-split">
    <div class="case-split-test">
      <p v-if="studyStore.isLoading" class="case-status">Загрузка</p>
      <p v-else-if="studyStore.error" class="case-status">{{ studyStore.error }}</p>
      <template v-else-if="studyStore.currentCase?.type === 'quiz' && studyStore.theory && !studyStore.quizStarted">
        <p class="case-theory">{{ studyStore.theory }}</p>
        <button type="button" class="theory-next" @click="studyStore.startQuiz">К тесту</button>
      </template>
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
    <div v-if="studyStore.currentCase?.type !== 'open'" class="case-split-side"></div>
  </div>
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
import { onMounted, onUnmounted, watch } from 'vue'
import { useStudyStore } from '@/modules/study/store/useStudyStore'
import { useAIStore } from '@/modules/ai-mentor/store/useAIStore'
import QuizView from '@/modules/study/components/QuizView.vue'
import BossCaseView from '@/modules/study/components/BossCaseView.vue'

const props = defineProps({
  buildingId: { type: String, required: true }
})

const studyStore = useStudyStore()
const aiStore = useAIStore()

onMounted(() => {
  studyStore.openCase(props.buildingId)
})

watch(() => props.buildingId, (buildingId) => {
  studyStore.openCase(buildingId)
})

onUnmounted(() => {
  studyStore.closeCase()
})
</script>

<style scoped>
.case-split {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(1.25rem, 2.8vw, 2.4rem);
  height: 100%;
  min-height: 0;
}

.case-split-test,
.case-split-side {
  min-width: 0;
  min-height: 0;
}

.case-split-test {
  overflow: auto;
}

.case-split-side {
  border-radius: clamp(1.15rem, 1.6vw, 1.55rem);
  background: #e6ebed;
}

.case-status,
.case-theory {
  margin: 0;
  color: #12202b;
  font-size: 0.95rem;
  font-weight: 400;
  line-height: 1.45;
}

.case-theory {
  margin-bottom: 1.25rem;
}

.theory-next {
  min-width: 8.5rem;
  height: clamp(2.55rem, 5.6vh, 2.9rem);
  padding: 0 1.75rem;
  border: none;
  border-radius: 9999px;
  background: #061e27;
  color: #ffffff;
  font: inherit;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
}
</style>
