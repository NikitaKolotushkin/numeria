<template>
  <div class="hobbies-step">
    <p class="hobbies-subtitle">Что Вы любите?</p>

    <div class="hobbies-grid">
      <button
        v-for="item in HOBBIES_LIST"
        :key="item.id"
        type="button"
        class="hobby-card"
        :class="{ active: isSelected(item.id) }"
        @click="toggleHobby(item.id)"
      >
        <div class="hobby-media">
          <img v-if="item.image" :src="item.image" :alt="item.title" class="hobby-img" />
          <div v-if="isSelected(item.id)" class="selection-badge">
            <svg class="check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          </div>
        </div>
        <span class="hobby-title">{{ item.title }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { HOBBIES_LIST } from '@/modules/auth/api/mockData'

const props = defineProps({
  modelValue: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue'])

const isSelected = (id) => props.modelValue.includes(id)

const toggleHobby = (id) => {
  const current = [...props.modelValue]
  const index = current.indexOf(id)

  if (index > -1) {
    current.splice(index, 1)
  } else {
    current.push(id)
  }

  emit('update:modelValue', current)
}
</script>

<style scoped>
.hobbies-step {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  width: 100%;
  height: 100%;
  min-height: 0;
}

.hobbies-subtitle {
  flex-shrink: 0;
  font-size: clamp(1.05rem, 1.35vw, 1.25rem);
  font-weight: 600;
  color: #12202b;
  margin: 0 0 clamp(0.7rem, 1.6vh, 1.05rem) 0;
  text-align: center;
}

.hobbies-grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-template-rows: 1fr 1fr;
  gap: clamp(0.55rem, 1.5vh, 0.9rem) clamp(0.8rem, 1.6vw, 1.35rem);
}

.hobby-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.45rem;
  min-height: 0;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: inherit;
  font-family: inherit;
}

.hobby-media {
  width: 100%;
  flex: 1;
  min-height: 0;
  border-radius: clamp(0.9rem, 1.3vw, 1.25rem);
  overflow: hidden;
  position: relative;
  background: #e7eef3;
}

.hobby-card.active .hobby-media {
  box-shadow: 0 0 0 0.14rem #12202b;
}

.hobby-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.selection-badge {
  position: absolute;
  top: 0.45rem;
  right: 0.45rem;
  width: 1.35rem;
  height: 1.35rem;
  background: #12202b;
  color: #ffffff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.check-icon {
  width: 0.8rem;
  height: 0.8rem;
}

.hobby-title {
  flex-shrink: 0;
  font-size: clamp(0.95rem, 1.15vw, 1.05rem);
  font-weight: 600;
  color: #12202b;
  text-align: center;
}
</style>
