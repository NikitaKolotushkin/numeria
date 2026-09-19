<template>
  <div class="auth-input-wrapper">
    <input
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      :inputmode="inputmode"
      :maxlength="maxlength"
      class="auth-input"
      @input="handleInput"
    />
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  type: { type: String, default: 'text' },
  placeholder: { type: String, default: '' },
  autocomplete: { type: String, default: 'off' },
  inputmode: { type: String, default: 'text' },
  maxlength: { type: [Number, String], default: undefined },
  digitsOnly: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue'])

const handleInput = (event) => {
  let value = event.target.value

  if (props.digitsOnly) {
    value = value.replace(/\D/g, '')
    event.target.value = value
  }

  emit('update:modelValue', value)
}
</script>

<style scoped>
.auth-input-wrapper {
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
</style>
