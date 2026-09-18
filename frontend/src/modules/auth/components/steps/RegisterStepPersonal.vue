<template>
  <AuthSplitLayout>
    <template #left>
      <AuthFieldsStack>
        <AuthFieldGroup title="О Вас">
          <AuthInput v-model="modelValue.firstName" placeholder="Имя" />
          <AuthInput v-model="modelValue.lastName" placeholder="Фамилия" />
        </AuthFieldGroup>

        <AuthFieldGroup title="Учеба">
          <AuthInput
            v-model="modelValue.university"
            type="select"
            placeholder="Университет"
            :options="UNIVERSITIES"
          />
          <AuthInput
            v-model="modelValue.direction"
            type="select"
            placeholder="Направление"
            :options="STUDY_DIRECTIONS"
          />
          <AuthInput
            v-model="modelValue.course"
            type="select"
            placeholder="Курс"
            :options="COURSES"
          />
        </AuthFieldGroup>
      </AuthFieldsStack>
    </template>

    <template #right>
      <AuthMediaCard :image="personalArt" title="Познакомимся" />
    </template>
  </AuthSplitLayout>
</template>

<script setup>
import AuthSplitLayout from '@/modules/auth/components/common/AuthSplitLayout.vue'
import AuthMediaCard from '@/modules/auth/components/common/AuthMediaCard.vue'
import AuthFieldsStack from '@/modules/auth/components/common/AuthFieldsStack.vue'
import AuthFieldGroup from '@/modules/auth/components/common/AuthFieldGroup.vue'
import AuthInput from '@/modules/auth/components/common/AuthInput.vue'
import { UNIVERSITIES, STUDY_DIRECTIONS, COURSES } from '@/modules/auth/api/mockData'
import personalArt from '@/assets/images/auth/step-personal.png'

defineProps({
  modelValue: { type: Object, required: true }
})
</script>
