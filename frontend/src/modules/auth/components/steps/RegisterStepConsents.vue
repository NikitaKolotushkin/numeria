<template>
  <AuthSplitLayout>
    <template #left>
      <AuthFieldsStack>
        <AuthFieldGroup title="Согласия">
          <label class="consent">
            <input v-model="modelValue.consents.personalData" type="checkbox" />
            <span>Обработка персональных данных</span>
          </label>
          <label class="consent">
            <input v-model="modelValue.consents.aiAssessment" type="checkbox" />
            <span>Автоматизированная оценка ответов</span>
          </label>
        </AuthFieldGroup>
      </AuthFieldsStack>
    </template>

    <template #right>
      <AuthMediaCard :image="securityArt" title="Согласимся" />
    </template>
  </AuthSplitLayout>
</template>

<script setup>
import AuthSplitLayout from '@/modules/auth/components/common/AuthSplitLayout.vue'
import AuthMediaCard from '@/modules/auth/components/common/AuthMediaCard.vue'
import AuthFieldsStack from '@/modules/auth/components/common/AuthFieldsStack.vue'
import AuthFieldGroup from '@/modules/auth/components/common/AuthFieldGroup.vue'
import securityArt from '@/assets/images/auth/step-security.png'

defineProps({
  modelValue: { type: Object, required: true }
})
</script>

<style scoped>
.consent {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  color: #12202b;
  font-size: 0.9rem;
  font-weight: 400;
  line-height: 1.35;
}

.consent input {
  margin-top: 0.2rem;
  accent-color: #12202b;
}
</style>
