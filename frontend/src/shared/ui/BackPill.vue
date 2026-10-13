<template>
  <component
    :is="to ? 'router-link' : 'button'"
    v-bind="to ? { to } : { type: 'button' }"
    class="back-pill"
    aria-label="Назад"
  >
    <svg class="nav-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <line x1="19" y1="12" x2="5" y2="12"></line>
      <polyline points="12 19 5 12 12 5"></polyline>
    </svg>
    <img class="brand-mark" src="@/assets/images/auth/logo-mark.png" alt="" />
  </component>
</template>

<script setup>
defineProps({
  to: { type: [String, Object], default: null }
})
</script>

<style scoped>
.back-pill {
  --auth-ink: #12202b;
  height: var(--auth-nav-size, clamp(2.85rem, 6.2vh, 3.35rem));
  background: #ffffff;
  border: none;
  cursor: pointer;
  box-shadow: 0 0.3rem 1rem rgba(18, 32, 43, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--auth-ink);
  flex-shrink: 0;
  border-radius: 9999px;
  padding: 0 1.05rem 0 0.9rem;
  gap: 0.7rem;
  text-decoration: none;
}

.brand-mark {
  width: 1.85rem;
  height: 1.85rem;
  display: block;
  object-fit: contain;
  border-radius: 0.55rem;
}

.nav-arrow {
  width: 1.2rem;
  height: 1.2rem;
}
</style>
