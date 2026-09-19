<template>
  <div
    class="portrait-warning"
    :class="{ 'is-portrait': isPortrait }"
    role="alert"
    aria-live="polite"
    :aria-hidden="!isPortrait"
  >
    <svg class="rotate-icon" viewBox="0 0 72 72" fill="none" aria-hidden="true">
      <g transform="rotate(-30 36 36)">
        <rect
          x="23"
          y="8"
          width="26"
          height="56"
          rx="6"
          stroke="currentColor"
          stroke-width="3"
        />
        <path
          d="M32 15h8"
          stroke="currentColor"
          stroke-width="3"
          stroke-linecap="round"
        />
        <rect
          x="33"
          y="55"
          width="6"
          height="3.5"
          rx="1.75"
          fill="currentColor"
        />
      </g>
    </svg>
    <p class="warning-text">Переверните экран</p>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const isPortrait = ref(false)

const updateOrientation = () => {
  isPortrait.value = window.innerHeight > window.innerWidth
  document.body.classList.toggle('portrait-lock', isPortrait.value)
}

onMounted(() => {
  updateOrientation()
  window.addEventListener('resize', updateOrientation)
  window.addEventListener('orientationchange', updateOrientation)
  window.visualViewport?.addEventListener('resize', updateOrientation)
})

onUnmounted(() => {
  window.removeEventListener('resize', updateOrientation)
  window.removeEventListener('orientationchange', updateOrientation)
  window.visualViewport?.removeEventListener('resize', updateOrientation)
  document.body.classList.remove('portrait-lock')
})
</script>

<style scoped>
.portrait-warning {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 10000;
  width: 100vw;
  height: 100dvh;
  background: rgba(15, 23, 42, 0.96);
  backdrop-filter: blur(0.75rem);
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(1.25rem, 4vh, 2rem);
  padding: 1.5rem;
  text-align: center;
}

.portrait-warning.is-portrait {
  display: flex;
}

@media (orientation: portrait) {
  .portrait-warning {
    display: flex;
  }
}

.rotate-icon {
  width: clamp(4.5rem, 18vmin, 7rem);
  height: clamp(4.5rem, 18vmin, 7rem);
  color: var(--color-accent);
}

.warning-text {
  color: var(--color-text-main);
  font-size: clamp(1.5rem, 6vmin, 2.25rem);
  font-weight: 700;
  line-height: 1.2;
}
</style>
