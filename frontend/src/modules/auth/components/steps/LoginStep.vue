<template>
  <AuthSplitLayout>
    <template #left>
      <div class="login-form">
        <AuthFieldsStack>
          <AuthFieldGroup title="Почта">
            <AuthInput
              v-model="modelValue.email"
              type="email"
              placeholder="Почта @guu.ru"
              autocomplete="email"
            />
          </AuthFieldGroup>

          <AuthFieldGroup title="Пароль">
            <AuthInput
              v-model="modelValue.password"
              type="password"
              placeholder="Пароль"
              autocomplete="current-password"
            />
          </AuthFieldGroup>
        </AuthFieldsStack>

        <button
          type="button"
          class="login-submit"
          :disabled="isLoading"
          @click="$emit('submit')"
        >
          <span v-if="isLoading" class="spinner"></span>
          <span v-else>Войти</span>
        </button>
      </div>
    </template>

    <template #right>
      <AuthMediaCard :image="securityArt" title="Войдем" />
    </template>
  </AuthSplitLayout>
</template>

<script setup>
import AuthSplitLayout from '@/modules/auth/components/common/AuthSplitLayout.vue'
import AuthMediaCard from '@/modules/auth/components/common/AuthMediaCard.vue'
import AuthFieldsStack from '@/modules/auth/components/common/AuthFieldsStack.vue'
import AuthFieldGroup from '@/modules/auth/components/common/AuthFieldGroup.vue'
import AuthInput from '@/modules/auth/components/common/AuthInput.vue'
import securityArt from '@/assets/images/auth/step-security.png'

defineProps({
  modelValue: { type: Object, required: true },
  isLoading: { type: Boolean, default: false }
})

defineEmits(['submit'])
</script>

<style scoped>
.login-form {
  display: flex;
  flex-direction: column;
  gap: clamp(1.25rem, 2.8vh, 1.75rem);
  width: min(100%, 22rem);
}

.login-submit {
  align-self: center;
  min-width: 8.5rem;
  height: clamp(2.55rem, 5.6vh, 2.9rem);
  padding: 0 1.75rem;
  border: none;
  border-radius: 9999px;
  background: #061e27;
  color: #ffffff;
  font-size: 0.95rem;
  font-weight: 500;
  font-family: inherit;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 1.15rem;
  height: 1.15rem;
  border: 2px solid rgba(255, 255, 255, 0.25);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
