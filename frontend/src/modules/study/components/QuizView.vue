<template>
  <div class="quiz-view">
    <div class="quiz-left">
      <div class="quiz-pagination">
        <button
          v-for="(item, index) in questions"
          :key="item.id"
          type="button"
          class="page-btn"
          :class="{ active: currentQuestionIndex === index, wrong: isWrong(index) }"
          @click="currentQuestionIndex = index"
        >
          {{ index + 1 }}
        </button>
      </div>

      <p class="question-text">{{ currentQuestion.question }}</p>
    </div>

    <div class="options-group">
      <button
        v-for="(option, optionIndex) in currentQuestion.options"
        :key="optionIndex"
        type="button"
        class="option-card"
        :class="optionClass(optionIndex)"
        :disabled="isComplete"
        @click="selectAnswer(optionIndex)"
      >
        <span class="radio-indicator"></span>
        <span class="option-text">{{ option }}</span>
      </button>
    </div>

    <Teleport to=".quiz-nav-host">
      <div class="quiz-footer">
        <QuizNav
          :show-back="currentQuestionIndex > 0"
          :show-forward="!isComplete || currentQuestionIndex < questions.length - 1"
          @back="currentQuestionIndex -= 1"
          @forward="goForward"
        />
        <button
          v-if="isComplete && passed === false"
          type="button"
          class="retry-quiz"
          :disabled="retrying"
          @click="$emit('retry')"
        >
          {{ retrying ? 'Загрузка' : 'Заново' }}
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import QuizNav from '@/shared/ui/QuizNav.vue'

const props = defineProps({
  questions: { type: Array, required: true },
  answers: { type: Array, default: () => [] },
  isComplete: { type: Boolean, default: false },
  passed: { default: null },
  correctIndexes: { type: Array, default: () => [] },
  retrying: { type: Boolean, default: false }
})

const emit = defineEmits(['answer', 'complete', 'retry'])

const currentQuestionIndex = ref(0)
const currentQuestion = computed(() => props.questions[currentQuestionIndex.value])

const correctIndex = computed(() => props.correctIndexes[currentQuestionIndex.value])

const isWrong = (index) => {
  if (!props.isComplete) return false
  return props.answers[index] !== props.correctIndexes[index]
}

const optionClass = (optionIndex) => {
  if (!props.isComplete) {
    return { selected: props.answers[currentQuestionIndex.value] === optionIndex }
  }
  return {
    correct: optionIndex === correctIndex.value,
    wrong: props.answers[currentQuestionIndex.value] === optionIndex && optionIndex !== correctIndex.value
  }
}

const selectAnswer = (optionIndex) => {
  if (props.isComplete) return
  emit('answer', currentQuestionIndex.value, optionIndex)
}

const goForward = () => {
  if (currentQuestionIndex.value < props.questions.length - 1) {
    currentQuestionIndex.value += 1
    return
  }
  if (!props.isComplete) emit('complete')
}
</script>

<style scoped>
.quiz-view {
  display: grid;
  grid-template-columns: minmax(14rem, 0.95fr) minmax(0, 1.15fr);
  gap: clamp(1.25rem, 2.8vw, 2.4rem);
  align-items: start;
  height: 100%;
  min-height: 0;
  overflow: auto;
}

.quiz-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: clamp(0.85rem, 1.8vh, 1.2rem);
  min-width: 0;
}

.quiz-pagination {
  display: flex;
  gap: 0.45rem;
  flex-shrink: 0;
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
}

.page-btn.wrong,
.page-btn.active.wrong {
  background: #f4d7de;
  color: #12202b;
}

.question-text {
  margin: 0;
  max-width: 36rem;
  color: #12202b;
  font-size: clamp(1.08rem, 1.4vw, 1.22rem);
  font-weight: 400;
  line-height: 1.5;
}

.options-group {
  display: flex;
  flex-direction: column;
  gap: clamp(0.75rem, 1.6vh, 1.05rem);
  width: 100%;
}

.option-card {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  width: 100%;
  margin: 0;
  padding: 0;
  border: none;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.radio-indicator {
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  border: 0.14rem solid #e6ebed;
  flex-shrink: 0;
  background: #e6ebed;
}

.option-card:disabled {
  cursor: default;
  opacity: 1;
}

.option-card.selected .radio-indicator {
  border-color: #12202b;
  background: #12202b;
}

.option-card.wrong .radio-indicator {
  border-color: #f4d7de;
  background: #f4d7de;
}

.option-card.correct .radio-indicator {
  border-color: #d7e8dc;
  background: #d7e8dc;
}

.option-text {
  color: #12202b;
  font-size: clamp(1.02rem, 1.28vw, 1.15rem);
  font-weight: 400;
  line-height: 1.45;
}

.quiz-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.75rem;
}

.quiz-footer :deep(.quiz-nav-row) {
  flex: 1;
  width: auto;
  margin-top: 0;
}

.retry-quiz {
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
  flex-shrink: 0;
}

.retry-quiz:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@container (max-height: 520px) {
  .quiz-view,
  .quiz-left {
    gap: 0.45rem;
  }

  .question-text,
  .option-text {
    font-size: 0.92rem;
  }

  .page-btn {
    width: 1.95rem;
    height: 1.95rem;
    font-size: 1.05rem;
  }
}
</style>
