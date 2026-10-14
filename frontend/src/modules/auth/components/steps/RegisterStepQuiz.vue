<template>
  <div class="quiz-step">
    <AuthSplitLayout variant="quiz">
      <template #left>
        <div class="quiz-info">
          <div class="quiz-pagination">
            <button
              v-for="(q, idx) in ONBOARDING_QUIZ"
              :key="q.id"
              class="page-btn"
              :class="{ active: currentQuestionIndex === idx, answered: userAnswers[idx] !== undefined }"
              @click="currentQuestionIndex = idx"
            >
              {{ idx + 1 }}
            </button>
          </div>

          <p class="question-text">{{ currentQuestion.question }}</p>
        </div>
      </template>

      <template #right>
        <div class="options-group">
          <label
            v-for="(opt, optIdx) in currentQuestion.options"
            :key="optIdx"
            class="option-card"
            :class="{ selected: userAnswers[currentQuestionIndex] === optIdx }"
            @click="selectAnswer(optIdx)"
          >
            <span class="radio-indicator"></span>
            <span class="option-text">{{ opt }}</span>
          </label>
        </div>
      </template>
    </AuthSplitLayout>
    <QuizNav
      :show-back="currentQuestionIndex > 0"
      @back="currentQuestionIndex -= 1"
      @forward="goForward"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AuthSplitLayout from '@/modules/auth/components/common/AuthSplitLayout.vue'
import QuizNav from '@/shared/ui/QuizNav.vue'
import { ONBOARDING_QUIZ } from '@/modules/auth/api/mockData'

const props = defineProps({
  modelValue: { type: Array, default: () => [] }
})
const emit = defineEmits(['update:modelValue', 'complete'])

const currentQuestionIndex = ref(0)
const userAnswers = ref([...props.modelValue])
const currentQuestion = computed(() => ONBOARDING_QUIZ[currentQuestionIndex.value])

const selectAnswer = (optionIndex) => {
  userAnswers.value[currentQuestionIndex.value] = optionIndex
  emit('update:modelValue', userAnswers.value)
}

const goForward = () => {
  if (currentQuestionIndex.value >= ONBOARDING_QUIZ.length - 1) {
    emit('complete')
    return
  }
  currentQuestionIndex.value += 1
}
</script>

<style scoped>
.quiz-step {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  gap: clamp(0.85rem, 1.8vh, 1.2rem);
}

.quiz-info {
  display: flex;
  flex-direction: column;
  gap: clamp(0.9rem, 2vh, 1.35rem);
}

.quiz-pagination {
  display: flex;
  gap: 0.45rem;
}

.page-btn {
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 50%;
  border: none;
  background: #e6ebed;
  color: #12202b;
  font-weight: 400;
  font-size: 1.22rem;
  font-family: inherit;
  cursor: pointer;
}

.page-btn.active {
  background: #12202b;
  color: #ffffff;
  font-weight: 400;
}

.question-text {
  max-width: 28rem;
  font-size: clamp(0.95rem, 1.2vw, 1.08rem);
  line-height: 1.5;
  font-weight: 400;
  color: #12202b;
  margin: 0;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: clamp(0.85rem, 1.8vh, 1.2rem);
}

.option-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  cursor: pointer;
}

.radio-indicator {
  width: 1.1rem;
  height: 1.1rem;
  border-radius: 50%;
  border: 0.14rem solid #e6ebed;
  flex-shrink: 0;
  background: #e6ebed;
}

.option-card.selected .radio-indicator {
  border-color: #12202b;
  background: #12202b;
}

.option-text {
  font-size: clamp(0.9rem, 1.1vw, 1rem);
  line-height: 1.45;
  color: #12202b;
  font-weight: 400;
}
</style>