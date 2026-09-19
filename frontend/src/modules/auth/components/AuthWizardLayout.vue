<template>
  <div class="wizard-container">
    <header class="wizard-header">
      <button
        type="button"
        class="btn-nav btn-pill"
        aria-label="Назад"
        @click="$emit('prev')"
      >
        <svg class="nav-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12"></line>
          <polyline points="12 19 5 12 12 5"></polyline>
        </svg>
        <img class="brand-mark" src="@/assets/images/auth/logo-mark.png" alt="" />
      </button>

      <div class="badge-pill">
        {{ headerTitle }}
      </div>

      <button
        type="button"
        class="btn-nav btn-circle"
        :disabled="isLoading"
        aria-label="Далее"
        @click="$emit('next')"
      >
        <span v-if="isLoading" class="spinner"></span>
        <svg v-else class="nav-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <line x1="5" y1="12" x2="19" y2="12"></line>
          <polyline points="12 5 19 12 12 19"></polyline>
        </svg>
      </button>
    </header>

    <main class="wizard-card">
      <h2 class="card-title">{{ title }}</h2>
      <div class="card-body">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  headerTitle: { type: String, default: 'Узнаем немного' },
  isLoading: { type: Boolean, default: false }
})

defineEmits(['prev', 'next'])
</script>

<style scoped>
.wizard-container {
  --auth-ink: #12202b;
  --auth-input-bg: #e7eef3;
  --auth-nav-size: clamp(2.85rem, 6.2vh, 3.35rem);
  --auth-card-height: min(76vh, 45rem);
  --auth-card-padding: clamp(1.4rem, 2.4vmin, 2.15rem);
  --auth-radius: clamp(1.75rem, 2.4vw, 2.5rem);
  --auth-media-radius: clamp(1.15rem, 1.6vw, 1.55rem);
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: clamp(0.8rem, 1.8vh, 1.15rem);
}

.wizard-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: var(--auth-nav-size);
  gap: 1rem;
}

.btn-nav {
  height: 100%;
  background: #ffffff;
  border: none;
  cursor: pointer;
  box-shadow: 0 0.3rem 1rem rgba(18, 32, 43, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--auth-ink);
  flex-shrink: 0;
}

.btn-nav:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-pill {
  border-radius: 9999px;
  padding: 0 1.05rem 0 0.9rem;
  gap: 0.7rem;
}

.brand-mark {
  width: 1.85rem;
  height: 1.85rem;
  display: block;
  object-fit: contain;
  border-radius: 0.55rem;
}

.btn-circle {
  width: var(--auth-nav-size);
  border-radius: 50%;
}

.nav-arrow {
  width: 1.2rem;
  height: 1.2rem;
}

.badge-pill {
  height: 100%;
  background: #ffffff;
  border-radius: 9999px;
  padding: 0 clamp(1.6rem, 3vw, 2.8rem);
  font-size: clamp(0.95rem, 1.15vw, 1.125rem);
  font-weight: 500;
  color: var(--auth-ink);
  box-shadow: 0 0.3rem 1rem rgba(18, 32, 43, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  min-width: 0;
}

.wizard-card {
  height: var(--auth-card-height);
  background: #ffffff;
  border-radius: var(--auth-radius);
  padding: var(--auth-card-padding);
  box-shadow: 0 1.25rem 3rem rgba(18, 32, 43, 0.14);
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.card-title {
  flex-shrink: 0;
  text-align: center;
  font-size: clamp(1.2rem, 1.55vw, 1.5rem);
  font-weight: 700;
  color: var(--auth-ink);
  margin: 0 0 clamp(0.55rem, 1.3vh, 0.95rem) 0;
  letter-spacing: -0.02em;
}

.card-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.card-body > :deep(*) {
  flex: 1;
  min-height: 0;
  height: 100%;
}

.spinner {
  width: 1.15rem;
  height: 1.15rem;
  border: 2px solid rgba(18, 32, 43, 0.2);
  border-top-color: var(--auth-ink);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
