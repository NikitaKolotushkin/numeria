<template>
  <div class="fields-stack">
    <slot />
  </div>
</template>

<style scoped>
.fields-stack {
  display: flex;
  flex-direction: column;
  gap: clamp(0.85rem, 2vh, 1.25rem);
  width: min(100%, 22rem);
}
</style>
