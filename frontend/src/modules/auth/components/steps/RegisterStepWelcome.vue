<template>
  <div class="welcome-step">
    <img src="@/assets/images/logo_numeria.png" alt="Нумерия" class="welcome-logo" />

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
  font-family: 'Geologica', sans-serif;
}

.welcome-logo {
  width: min(28rem, 70vw);
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 0.625rem 1.25rem rgba(0, 0, 0, 0.4));
}

.welcome-title {
  margin: 0;
  color: #ffffff;
  font-size: clamp(1.35rem, 2.4vw, 2rem);
  font-weight: 700;
  line-height: 1.35;
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
  font-family: 'Geologica', sans-serif;
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
