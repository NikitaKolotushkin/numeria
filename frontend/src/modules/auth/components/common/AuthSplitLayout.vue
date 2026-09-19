<template>
  <div class="split-layout" :class="`variant-${variant}`">
    <div class="split-left">
      <slot name="left" />
    </div>
    <div class="split-right">
      <slot name="right" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'form'
  }
})
</script>

<style scoped>
.split-layout {
  display: grid;
  height: 100%;
  min-height: 0;
  gap: clamp(1.25rem, 2.8vw, 2.4rem);
  align-items: stretch;
}

.variant-form {
  grid-template-columns: minmax(13.5rem, 0.72fr) minmax(0, 1.28fr);
}

.variant-quiz {
  grid-template-columns: minmax(14rem, 0.95fr) minmax(0, 1.15fr);
}

.split-left,
.split-right {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 0;
}

.variant-form .split-left {
  justify-content: flex-start;
}

.variant-form .split-right {
  justify-content: stretch;
}

.variant-quiz .split-left,
.variant-quiz .split-right {
  justify-content: flex-start;
  padding-top: clamp(0.35rem, 1.2vh, 0.8rem);
}
</style>
