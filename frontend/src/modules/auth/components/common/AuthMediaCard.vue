<template>
  <div class="media-card">
    <img
      v-if="image"
      :src="image"
      :alt="title || 'Numeria'"
      class="media-cover-image"
    />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  image: { type: String, default: '' }
})
</script>

<style scoped>
.media-card {
  width: 100%;
  height: 100%;
  min-height: 0;
  border-radius: clamp(1.15rem, 1.6vw, 1.55rem);
  overflow: hidden;
  background: #e7eef3;
}

.media-cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
</style>
