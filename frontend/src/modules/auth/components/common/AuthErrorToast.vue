<template>
  <Teleport to="body">
    <div v-if="message" class="error-toast" role="alert">
      <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"></circle>
        <line x1="12" y1="8" x2="12" y2="12"></line>
        <line x1="12" y1="16" x2="12.01" y2="16"></line>
      </svg>
      <span>{{ message }}</span>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  message: { type: String, default: '' }
})
</script>

<style scoped>
.error-toast {
  position: fixed;
  right: clamp(1rem, 2.4vw, 2rem);
  bottom: clamp(1rem, 3vh, 2rem);
  z-index: 1000;
  max-width: min(22rem, calc(100vw - 2rem));
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  padding: 0.75rem 1.25rem;
  border-radius: 1rem;
  font-size: 0.9375rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.625rem;
  box-shadow: 0 0.75rem 2rem rgba(15, 23, 42, 0.18);
  pointer-events: none;
}

.error-icon {
  width: 1.125rem;
  height: 1.125rem;
  flex-shrink: 0;
}
</style>
