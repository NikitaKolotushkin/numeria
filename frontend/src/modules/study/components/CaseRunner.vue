<template>
  <div v-if="studyStore.currentCase?.type !== 'open'" class="case-split">
    <div class="case-split-test">
      <p v-if="studyStore.isLoading" class="case-status">Загрузка</p>
      <p v-else-if="studyStore.error" class="case-status">{{ studyStore.error }}</p>
      <template v-else-if="studyStore.currentCase?.type === 'quiz'">
        <p v-if="studyStore.theory" class="case-theory">{{ studyStore.theory }}</p>
        <QuizView
          :key="studyStore.currentCase.id"
          :questions="studyStore.questions"
          :answers="studyStore.answers"
          :is-complete="studyStore.isComplete"
          :score="studyStore.score"
          @answer="studyStore.answerQuestion"
          @complete="studyStore.complete"
        />
      </template>
    </div>
    <div v-if="studyStore.currentCase?.type !== 'open'" class="case-split-side"></div>
  </div>
  <BossCaseView
    v-if="!studyStore.isLoading && !studyStore.error && studyStore.currentCase?.type === 'open'"
    :prompt="studyStore.theory"
    :draft="studyStore.draft"
    :submitting="studyStore.isSubmitting"
    :field-error="studyStore.fieldError"
    @update:draft="studyStore.draft = $event"
    @submit="studyStore.submitBoss"
  />
</template>

<script setup>
import { onMounted, onUnmounted, watch } from 'vue'
import { useStudyStore } from '@/modules/study/store/useStudyStore'
import QuizView from '@/modules/study/components/QuizView.vue'
import BossCaseView from '@/modules/study/components/BossCaseView.vue'

const props = defineProps({
  buildingId: { type: String, required: true }
})

const studyStore = useStudyStore()

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
  margin-bottom: 1rem;
}
</style>
