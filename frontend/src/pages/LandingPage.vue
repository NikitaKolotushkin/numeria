<template>
  <div class="landing-page">
    <!-- Шапка справа -->
    <header class="top-bar">
      <div v-if="!authStore.isAuthenticated" class="auth-buttons">
        <router-link to="/auth?mode=login" class="btn-primary">Вход</router-link>
        <router-link to="/auth?mode=register" class="btn-primary btn-outline">Регистрация</router-link>
      </div>
      <button
        v-else
        type="button"
        class="btn-primary"
        @click="authStore.logout"
      >
        Выйти
      </button>
    </header>

    <aside v-if="authStore.isAuthenticated" class="player-panel">
      <div class="player-row">
        <img
          class="player-avatar"
          src="@/assets/images/hub/avatar.png"
          alt=""
        />
        <span>{{ authStore.user?.firstName || authStore.user?.nickname }}</span>
      </div>
      <div class="player-row">
        <img class="player-icon" src="@/assets/images/hub/coin.png" alt="" />
        <span>{{ authStore.user?.stats?.capital?.toLocaleString('ru-RU') }}</span>
      </div>
      <div class="player-row">
        <img class="player-icon" src="@/assets/images/hub/trophy.png" alt="" />
        <span>Топ-{{ authStore.user?.stats?.rankPosition }}</span>
      </div>
    </aside>

    <!-- Сайдбар слева -->
    <aside class="left-sidebar">
      <div class="version">
        <p class="version-title">Версия игры</p>
        <p class="version-num">0.1.1</p>
      </div>

      <!-- Логотипы университетов и партнеров -->
      <div class="partners-logos">
        <img src="@/assets/images/guu.png" alt="ГУУ" class="partner-logo" />
        <img src="@/assets/images/spbgu.png" alt="СПбГУ" class="partner-logo" />
        <img src="@/assets/images/sgtu.png" alt="СГТУ" class="partner-logo" />
        <img src="@/assets/images/tvoy_hod.png" alt="Твой Ход" class="partner-logo" />
      </div>
    </aside>

    <!-- Центр -->
    <main class="hero">
      <!-- Центральный PNG логотип -->
      <div class="logo-box">
        <img src="@/assets/images/logo_numeria.png" alt="Нумерия" class="main-logo" />
      </div>

      <!-- СОСТОЯНИЕ 1: ГОСТЬ -->
      <div v-if="!authStore.isAuthenticated" class="guest-cta">
        <router-link to="/auth?mode=register" class="btn-primary btn-large">
          Начать игру
        </router-link>
      </div>

      <div v-else class="guest-cta">
        <router-link to="/game" class="btn-primary btn-large">
          Играть!
        </router-link>
      </div>
    </main>
  </div>
</template>

<script setup>
  import { useAuthStore } from '@/modules/auth/store/useAuthStore'

  const authStore = useAuthStore()
</script>

<style scoped>
  .landing-page {
    width: 100%;
    height: 100dvh;
    position: relative;
    background: url('/bg_city.png') center/cover no-repeat;
    display: flex;
  }

  .landing-page::before {
    content: '';
    position: absolute;
    inset: 0;
    background: rgba(15, 23, 42, 0.4);
    backdrop-filter: blur(2px);
  }

  .top-bar, .left-sidebar, .player-panel, .hero {
    position: relative;
    z-index: 2;
  }

  .top-bar {
    position: absolute;
    top: clamp(1.25rem, 3.2vh, 2rem);
    right: clamp(1.5rem, 3.2vw, 3rem);
  }

  .auth-buttons {
    display: flex;
    gap: 0.75rem;
  }

  .player-panel {
    position: absolute;
    right: clamp(1.5rem, 3.2vw, 3rem);
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    flex-direction: column;
    gap: clamp(0.85rem, 2.2vh, 1.35rem);
  }

  .player-row {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    color: #fff;
    font-size: clamp(1rem, 1.6vw, 1.35rem);
    font-weight: 400;
  }

  .player-icon,
  .player-avatar {
    width: clamp(2.25rem, 3.4vw, 3rem);
    height: clamp(2.25rem, 3.4vw, 3rem);
    flex-shrink: 0;
    display: block;
    object-fit: contain;
    filter: drop-shadow(0 0.1rem 0.2rem rgba(0, 0, 0, 0.35));
  }

  .player-avatar {
    border-radius: 50%;
    object-fit: cover;
  }

  .left-sidebar {
    position: absolute;
    left: clamp(1.5rem, 3.2vw, 3rem);
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    flex-direction: column;
    gap: clamp(1.25rem, 3.2vh, 2rem);
    max-width: min(18vw, 14rem);
  }

  .version-title {
    font-size: clamp(1.25rem, 2.1vw, 2rem);
    opacity: 0.9;
    font-weight: 700;
  }
  .version-num {
    font-size: clamp(1rem, 1.6vw, 1.5rem);
    font-weight: 400;
  }

  .partners-logos {
    display: flex;
    flex-direction: column;
    gap: clamp(0.75rem, 2vh, 1.25rem);
    align-items: flex-start;
  }

  .partner-logo {
    max-width: 100%;
    width: min(11vw, 13.125rem);
    max-height: 4.375rem;
    object-fit: contain;
    filter: drop-shadow(0 0.125rem 0.25rem rgba(0, 0, 0, 0.3));
  }

  .hero {
    margin: auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: clamp(1.25rem, 3.2vh, 2rem);
  }

  .logo-box {
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .main-logo {
    width: min(38vw, 32.5rem);
    max-width: 100%;
    height: auto;
    object-fit: contain;
    filter: drop-shadow(0 0.625rem 1.25rem rgba(0, 0, 0, 0.4));
  }

  .btn-primary {
    display: inline-block;
    text-decoration: none;
    background: #061e27;
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 0.875rem 2rem;
    border-radius: 9999px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    backdrop-filter: blur(0.625rem);
  }

  .btn-outline {
    background: transparent;
  }

  .btn-large {
    padding: 1.125rem 3.25rem;
    font-size: 1.25rem;
    border-radius: 9999px;
  }

</style>