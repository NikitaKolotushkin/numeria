<template>
  <div class="welcome-step">
    <div class="welcome-brand">
      <div class="welcome-mark" aria-hidden="true">
        <span class="welcome-mark-letter">H</span>
      </div>
      <span class="welcome-name">Нумерия</span>
    </div>

    <p class="welcome-title">
      Ваша персонализация готова!<br>
      Добро пожаловать!
    </p>

    <button
      type="button"
      class="welcome-cta"
      :disabled="isLoading"
      @click="$emit('start')"
    >
      <span v-if="isLoading" class="spinner"></span>
      <span v-else>Начнем</span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  isLoading: { type: Boolean, default: false }
})

defineEmits(['start'])
</script>

<style scoped>
.welcome-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: clamp(1.5rem, 4vh, 2.75rem);
  width: min(40rem, 90vw);
  margin: 0 auto;
}

.welcome-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.85rem;
}

.welcome-mark {
  width: clamp(3.25rem, 5vw, 4.25rem);
  height: clamp(3.25rem, 5vw, 4.25rem);
  border-radius: 1.05rem;
  background: #061e27;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.welcome-mark-letter {
  color: #ffffff;
  font-size: clamp(1.6rem, 2.4vw, 2.1rem);
  font-weight: 800;
  line-height: 1;
}

.welcome-name {
  color: #ffffff;
  font-size: clamp(2.1rem, 3.6vw, 3.15rem);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1;
}

.welcome-title {
  margin: 0;
  color: #ffffff;
  font-size: clamp(1.35rem, 2.4vw, 2rem);
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: -0.02em;
}

.welcome-cta {
  min-width: clamp(10rem, 16vw, 14rem);
  height: 3.5rem;
  padding: 0 2.5rem;
  border: none;
  border-radius: 9999px;
  background: #061e27;
  color: #ffffff;
  font-size: 1.125rem;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-cta:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
