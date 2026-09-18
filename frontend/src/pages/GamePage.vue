<template>
  <div class="game-page">
    <div class="game-container">
      <h1>Игровое поле корпорации</h1>
      <p>Добро пожаловать, {{ authStore.user?.nickname || 'Игрок' }}!</p>
      <div class="actions">
        <router-link to="/" class="btn-back">← Вернуться в хаб</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
    import { useAuthStore } from '@/modules/auth/store/useAuthStore'
    const authStore = useAuthStore()
</script>

<style scoped>
    .game-page {
    min-height: 100dvh;
    width: 100%;
    background: url('/bg_city.png') center/cover no-repeat;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: clamp(1rem, 4vh, 2.5rem);
    }

    .game-container {
    background: var(--color-bg-card);
    padding: clamp(1.5rem, 4vh, 2.5rem);
    border-radius: 1.25rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    text-align: center;
    }

    .btn-back {
    display: inline-block;
    margin-top: 1.25rem;
    color: var(--color-accent);
    text-decoration: none;
    }
</style>