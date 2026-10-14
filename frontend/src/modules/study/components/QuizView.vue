<template>
  <div class="quiz-view">
    <div class="quiz-pagination">
      <button
        v-for="(item, index) in questions"
        :key="item.id"
        type="button"
        class="page-btn"
        :class="{ active: currentQuestionIndex === index }"
        @click="currentQuestionIndex = index"
      >
        {{ index + 1 }}
      </button>
    </div>

    <p v-if="isComplete" class="quiz-score">Баллы: {{ score }} из {{ questions.length }}</p>

    <p class="question-text">{{ currentQuestion.question }}</p>

    <div class="options-group">
      <button
        v-for="(option, optionIndex) in currentQuestion.options"
        :key="optionIndex"
        type="button"
        class="option-card"
        :class="{ selected: answers[currentQuestionIndex] === optionIndex }"
        @click="selectAnswer(optionIndex)"
      >
        <span class="radio-indicator"></span>
        <span class="option-text">{{ option }}</span>
      </button>
    </div>

    <Teleport to=".quiz-nav-host">
      <QuizNav
        v-if="!isComplete"
        :show-back="currentQuestionIndex > 0"
        @back="currentQuestionIndex -= 1"
        @forward="goForward"
      />
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
  score: { type: Number, default: 0 }
})

const emit = defineEmits(['answer', 'complete'])

const currentQuestionIndex = ref(0)
const currentQuestion = computed(() => props.questions[currentQuestionIndex.value])

const selectAnswer = (optionIndex) => {
  emit('answer', currentQuestionIndex.value, optionIndex)
}

const goForward = () => {
  if (currentQuestionIndex.value >= props.questions.length - 1) {
    emit('complete')
    return
  }
  currentQuestionIndex.value += 1
}
</script>

<style scoped>
.quiz-view {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: clamp(0.85rem, 1.8vh, 1.2rem);
  height: 100%;
  min-height: 0;
  overflow: auto;
}

.quiz-pagination {
  display: flex;
  gap: 0.45rem;
  flex-shrink: 0;
}

.page-btn {
  width: 1.85rem;
  height: 1.85rem;
  border-radius: 50%;
  border: none;
  background: transparent;
  color: #12202b;
  font-weight: 400;
  font-size: 0.95rem;
  font-family: inherit;
  cursor: pointer;
}

.page-btn.active {
  background: #12202b;
  color: #ffffff;
}

.quiz-score {
  margin: 0;
  color: #12202b;
  font-size: clamp(0.95rem, 1.15vw, 1.05rem);
  font-weight: 700;
  line-height: 1.3;
}

.question-text {
  margin: 0;
  max-width: 36rem;
  color: #12202b;
  font-size: clamp(0.95rem, 1.2vw, 1.08rem);
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
  align-items: flex-start;
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
  width: 1.1rem;
  height: 1.1rem;
  margin-top: 0.15rem;
  border-radius: 50%;
  border: 0.14rem solid #c5d0da;
  flex-shrink: 0;
  background: #ffffff;
}

.option-card.selected .radio-indicator {
  border-color: #12202b;
  background: #12202b;
}

.option-text {
  color: #12202b;
  font-size: clamp(0.9rem, 1.1vw, 1rem);
  font-weight: 400;
  line-height: 1.45;
}

@container (max-height: 520px) {
  .quiz-view {
    gap: 0.45rem;
  }

  .question-text,
  .option-text,
  .quiz-score {
    font-size: 0.8rem;
  }

  .page-btn {
    width: 1.5rem;
    height: 1.5rem;
    font-size: 0.8rem;
  }
}
</style>
