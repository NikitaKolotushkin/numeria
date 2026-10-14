<template>
  <div class="boss-case">
    <p class="boss-prompt">{{ prompt }}</p>
    <div class="boss-side">
      <textarea
        :value="draft"
        class="boss-input"
        placeholder="Ваш ответ"
        :disabled="submitting"
        @input="$emit('update:draft', $event.target.value)"
      ></textarea>
      <button
        type="button"
        class="boss-submit"
        :disabled="submitting"
        @click="$emit('submit')"
      >
        {{ submitting ? 'Отправка' : 'Отправить' }}
      </button>
      <p v-if="fieldError" class="boss-error">{{ fieldError }}</p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  prompt: { type: String, default: '' },
  draft: { type: String, default: '' },
  submitting: { type: Boolean, default: false },
  fieldError: { type: String, default: '' }
})

defineEmits(['update:draft', 'submit'])
</script>

<style scoped>
.boss-case {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: clamp(1.25rem, 2.8vw, 2.4rem);
  height: 100%;
  min-height: 0;
}

.boss-prompt,
.boss-side {
  min-width: 0;
  min-height: 0;
}

.boss-prompt {
  margin: 0;
  overflow: auto;
  color: #12202b;
  font-size: clamp(0.95rem, 1.2vw, 1.08rem);
  font-weight: 400;
  line-height: 1.5;
}

.boss-side {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
  padding: clamp(0.85rem, 1.6vh, 1.2rem);
  border-radius: clamp(1.15rem, 1.6vw, 1.55rem);
  background: #e6ebed;
}

.boss-input {
  width: 100%;
  flex: 1;
  min-height: 8rem;
  margin: 0;
  padding: 1rem 1.1rem;
  border: none;
  border-radius: clamp(1.15rem, 1.6vw, 1.55rem);
  resize: none;
  background: #ffffff;
  color: #12202b;
  font: inherit;
  font-size: 0.95rem;
  font-weight: 400;
  line-height: 1.45;
  outline: none;
}

.boss-input::placeholder {
  color: #94a3b8;
}

.boss-submit {
  min-width: 8.5rem;
  height: clamp(2.55rem, 5.6vh, 2.9rem);
  padding: 0 1.75rem;
  border: none;
  border-radius: 9999px;
  background: #061e27;
  color: #ffffff;
  font: inherit;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
}

.boss-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.boss-error {
  margin: 0;
  color: #b91c1c;
  font-size: 0.9rem;
  font-weight: 400;
  text-align: center;
}
</style>
