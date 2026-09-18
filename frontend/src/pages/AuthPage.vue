<template>
  <div class="auth-page">
    <div class="auth-container">
      <AuthWizard />
    </div>
  </div>
</template>

<script setup>
import AuthWizard from '@/modules/auth/components/AuthWizard.vue'
</script>

<style scoped>
.auth-page {
  min-height: 100dvh;
  width: 100%;
  background: url('/bg_city.png') center/cover no-repeat;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(1rem, 4vh, 2rem) clamp(1.25rem, 3vw, 2rem);
}

.auth-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(0.75rem);
}

.auth-container {
  position: relative;
  z-index: 2;
  width: min(88vw, 74rem);
}
</style>