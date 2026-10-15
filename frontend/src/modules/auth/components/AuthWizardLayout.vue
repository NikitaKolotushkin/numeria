<template>
  <div class="wizard-container">
    <header class="wizard-header">
      <BackPill @click="$emit('prev')" />

      <div class="badge-pill">
        {{ headerTitle }}
      </div>

      <slot name="header-end">
        <button
          type="button"
          class="btn-nav btn-circle"
          :disabled="isLoading"
          aria-label="Далее"
          @click="$emit('next')"
        >
          <span v-if="isLoading" class="spinner"></span>
          <svg v-else class="nav-arrow" viewBox="0 0 48 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="10" y1="12" x2="38" y2="12"></line>
            <polyline points="31 5 38 12 31 19"></polyline>
          </svg>
        </button>
      </slot>
    </header>

    <main class="wizard-card" :class="{ 'align-title-media': alignTitleToMedia }">
      <h2 class="card-title">{{ title }}</h2>
      <div class="card-body">
        <slot />
      </div>
    </main>
  </div>
</template>

<script setup>
import BackPill from '@/shared/ui/BackPill.vue'

defineProps({
  title: { type: String, required: true },
  headerTitle: { type: String, default: 'Узнаем немного' },
  isLoading: { type: Boolean, default: false },
  alignTitleToMedia: { type: Boolean, default: false }
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
  --auth-split-columns: minmax(13.5rem, 0.72fr) minmax(0, 1.28fr);
  --auth-split-gap: clamp(1.25rem, 2.8vw, 2.4rem);
  --auth-input-height: clamp(2.55rem, 5.6vh, 2.9rem);
  --auth-field-gap: 0.55rem;
  --auth-group-gap: 0.45rem;
  --auth-stack-gap: clamp(0.85rem, 2vh, 1.25rem);
  --auth-group-title: clamp(0.95rem, 1.15vw, 1.05rem);
  --auth-login-gap: clamp(1.25rem, 2.8vh, 1.75rem);
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: clamp(0.8rem, 1.8vh, 1.15rem);
}

.wizard-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: var(--auth-nav-size);
  gap: 1rem;
}

.wizard-header > :first-child,
.wizard-header > :last-child {
  position: relative;
  z-index: 1;
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

.btn-circle {
  width: calc(0.9rem + 1.2rem + 0.7rem + 1.85rem + 1.05rem);
  border-radius: 9999px;
}

.nav-arrow {
  width: 2.4rem;
  height: 1.2rem;
}

.badge-pill {
  position: absolute;
  left: 50%;
  top: 0;
  z-index: 0;
  height: 100%;
  max-width: min(46%, calc(100% - 16rem));
  transform: translateX(-50%);
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
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
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

.wizard-card.align-title-media {
  display: grid;
  grid-template-columns: var(--auth-split-columns);
  column-gap: var(--auth-split-gap);
  grid-template-rows: auto minmax(0, 1fr);
}

.wizard-card.align-title-media .card-title {
  grid-column: 2;
  grid-row: 1;
  text-align: left;
}

.wizard-card.align-title-media .card-body {
  grid-column: 1 / -1;
  grid-row: 2;
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

@media (orientation: landscape) and (max-height: 520px) {
  .wizard-container {
    flex: 1;
    height: 100%;
    min-height: 0;
    gap: 0.35rem;
    --auth-nav-size: 2.25rem;
    --auth-card-padding: 0.65rem 0.85rem;
    --auth-input-height: clamp(1.85rem, 6.2vh, 2.3rem);
    --auth-field-gap: 0.28rem;
    --auth-group-gap: 0.16rem;
    --auth-stack-gap: 0.35rem;
    --auth-group-title: 0.8rem;
    --auth-login-gap: 0.5rem;
  }

  .wizard-card {
    height: auto;
    flex: 1;
    min-height: 0;
    overflow: hidden;
  }

  .card-title {
    font-size: 1.05rem;
    margin-bottom: 0.3rem;
  }
}
</style>
