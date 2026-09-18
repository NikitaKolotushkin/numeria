<template>
  <div class="auth-input-wrapper">
    <div v-if="type === 'select'" class="select-container">
      <select
        :value="modelValue"
        class="auth-input custom-select"
        @change="$emit('update:modelValue', $event.target.value)"
      >
        <option value="" disabled>{{ placeholder }}</option>
        <option
          v-for="opt in options"
          :key="typeof opt === 'object' ? opt.value : opt"
          :value="typeof opt === 'object' ? opt.value : opt"
        >
          {{ typeof opt === 'object' ? opt.label : opt }}
        </option>
      </select>
      <svg class="select-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="6 9 12 15 18 9"></polyline>
      </svg>
    </div>

    <input
      v-else
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      class="auth-input"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  autocomplete: { type: String, default: 'off' }
})

defineEmits(['update:modelValue'])
</script>

<style scoped>
.auth-input-wrapper {
  width: 100%;
}

.select-container {
  position: relative;
  width: 100%;
}

.auth-input {
  width: 100%;
  height: clamp(2.55rem, 5.6vh, 2.9rem);
  background: #e7eef3;
  border: none;
  border-radius: 9999px;
  padding: 0 1.2rem;
  font-size: 0.95rem;
  font-weight: 400;
  color: #12202b;
  outline: none;
  font-family: inherit;
}

.auth-input::placeholder {
  color: #94a3b8;
  font-weight: 400;
}

.custom-select {
  appearance: none;
  cursor: pointer;
  padding-right: 2.6rem;
}

.select-chevron {
  position: absolute;
  right: 1.05rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: #64748b;
  pointer-events: none;
}
</style>
