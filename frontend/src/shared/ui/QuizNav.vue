<template>
  <div class="quiz-nav-row" :class="{ 'has-back': showBack && showForward, 'only-back': showBack && !showForward }">
    <button
      v-if="showBack"
      type="button"
      class="quiz-nav"
      aria-label="Назад"
      @click="$emit('back')"
    >
      <svg class="nav-arrow" viewBox="0 0 48 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="38" y1="12" x2="10" y2="12"></line>
        <polyline points="17 5 10 12 17 19"></polyline>
      </svg>
    </button>
    <button
      v-if="showForward"
      type="button"
      class="quiz-nav"
      aria-label="Вперед"
      @click="$emit('forward')"
    >
      <svg class="nav-arrow" viewBox="0 0 48 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="10" y1="12" x2="38" y2="12"></line>
        <polyline points="31 5 38 12 31 19"></polyline>
      </svg>
    </button>
  </div>
</template>

<script setup>
defineProps({
  showBack: { type: Boolean, default: false },
  showForward: { type: Boolean, default: true }
})

defineEmits(['back', 'forward'])
</script>

<style scoped>
.quiz-nav-row {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  margin-top: auto;
  flex-shrink: 0;
}

.quiz-nav-row.has-back {
  justify-content: space-between;
}

.quiz-nav-row.only-back {
  justify-content: flex-start;
}

.quiz-nav {
  width: calc(0.9rem + 1.2rem + 0.7rem + 1.85rem + 1.05rem);
  height: var(--auth-nav-size, clamp(2.85rem, 6.2vh, 3.35rem));
  border: none;
  border-radius: 9999px;
  background: #061e27;
  color: #ffffff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-arrow {
  width: 2.4rem;
  height: 1.2rem;
}
</style>
