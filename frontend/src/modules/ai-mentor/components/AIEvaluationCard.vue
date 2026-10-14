<template>
  <div class="review-wrap">
    <article class="review-card">
      <p class="review-verdict">{{ verdict === 'accepted' ? 'Принято' : 'Доработайте ответ' }}</p>
      <p class="review-score">{{ score }} / 100</p>
      <p class="review-text">{{ reviewText }}</p>
      <ul class="review-zones">
        <li v-for="zone in growthZones" :key="zone">{{ zone }}</li>
      </ul>
    </article>
    <button type="button" class="review-revise" @click="$emit('revise')">Изменить ответ</button>
  </div>
</template>

<script setup>
defineProps({
  score: { type: Number, required: true },
  verdict: { type: String, required: true },
  reviewText: { type: String, default: '' },
  growthZones: { type: Array, default: () => [] }
})

defineEmits(['revise'])
</script>

<style scoped>
.review-wrap {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.85rem;
  width: 100%;
  min-height: 0;
  flex: 1;
}

.review-card {
  overflow: auto;
  min-height: 0;
  padding: 1rem 1.1rem;
  border-radius: clamp(1.15rem, 1.6vw, 1.55rem);
  background: #ffffff;
  color: #12202b;
}

.review-verdict {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
}

.review-score,
.review-text {
  margin: 0.7rem 0 0;
  font-size: 0.95rem;
  font-weight: 400;
  line-height: 1.45;
}

.review-zones {
  margin: 0.85rem 0 0;
  padding-left: 1.15rem;
  font-size: 0.95rem;
  font-weight: 400;
  line-height: 1.45;
}

.review-revise {
  align-self: center;
  padding: 0;
  border: none;
  background: transparent;
  color: #061e27;
  font: inherit;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
}
</style>
