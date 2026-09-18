<template>
  <div class="section-group">
    <h4 class="group-title">{{ title }}</h4>
    <div class="group-inputs">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true }
})
</script>

<style scoped>
.section-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.group-title {
  font-size: clamp(0.95rem, 1.15vw, 1.05rem);
  font-weight: 600;
  color: #12202b;
  margin: 0 0 0 0.55rem;
  letter-spacing: -0.01em;
}

.group-inputs {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}
</style>
