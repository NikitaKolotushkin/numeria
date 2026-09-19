<template>
  <AuthSplitLayout>
    <template #left>
      <AuthFieldsStack>
        <AuthFieldGroup title="Контакты">
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
            autocomplete="new-password"
          />
          <AuthInput
            v-model="modelValue.confirmPassword"
            type="password"
            placeholder="Повторите пароль"
            autocomplete="new-password"
          />
        </AuthFieldGroup>
      </AuthFieldsStack>
    </template>

    <template #right>
      <AuthMediaCard :image="securityArt" title="Защитимся" />
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
  modelValue: { type: Object, required: true }
})
</script>
