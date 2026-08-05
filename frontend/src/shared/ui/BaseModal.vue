<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-backdrop" @click.self="close">
      <div class="modal-container">
        <button class="modal-close" @click="close">&times;</button>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  isOpen: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['close'])

const close = () => {
  emit('close')
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: var(--color-bg-card);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 32px;
  width: 100%;
  max-width: 420px;
  position: relative;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 20px;
  background: none;
  border: none;
  color: var(--color-text-muted);
  font-size: 28px;
  cursor: pointer;
}
.modal-close:hover {
  color: white;
}
</style>
