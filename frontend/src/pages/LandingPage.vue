<template>
  <div class="landing-page">
    <!-- Шапка справа -->
    <header class="top-bar">
      <!-- Состояние гостя -->
      <div v-if="!authStore.isAuthenticated" class="auth-buttons">
        <router-link to="/auth?mode=login" class="btn-primary">Вход</router-link>
        <router-link to="/auth?mode=register" class="btn-primary btn-outline">Регистрация</router-link>
      </div>

      <!-- Состояние игрока -->
      <div v-else class="user-header-card">
        <div class="user-avatar">{{ authStore.user?.nickname?.charAt(0) || 'Н' }}</div>
        <div class="user-meta">
          <span class="user-name">{{ authStore.user?.nickname }}</span>
          <span class="user-rank">Топ #{{ authStore.user?.stats?.rankPosition }}</span>
        </div>
        <button class="btn-logout" @click="authStore.logout" title="Выйти">✕</button>
      </div>
    </header>

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

      <!-- СОСТОЯНИЕ 2: АВТОРИЗОВАННЫЙ ИГРОК (ХАБ) -->
      <div v-else class="player-hub-card">
        <div class="hub-stats">
          <div class="stat-box">
            <span class="stat-label">Капитал</span>
            <span class="stat-val">{{ authStore.user?.stats?.capital?.toLocaleString('ru-RU') }} ₽</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-box">
            <span class="stat-label">Энергия</span>
            <span class="stat-val">{{ authStore.user?.stats?.energy }}/{{ authStore.user?.stats?.maxEnergy }}</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-box">
            <span class="stat-label">Институт</span>
            <span class="stat-val">{{ authStore.user?.group }}</span>
          </div>
        </div>

        <router-link to="/game" class="btn-primary btn-large btn-play">
          Продолжить игру →
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

  .top-bar, .left-sidebar, .hero {
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

  .user-header-card {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 0.5rem 1rem;
    border-radius: 9999px;
    backdrop-filter: blur(0.625rem);
  }

  .user-avatar {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
    font-weight: 700;
    color: #fff;
    text-transform: uppercase;
  }

  .user-meta {
    display: flex;
    flex-direction: column;
  }

  .user-name {
    font-size: 0.875rem;
    font-weight: 700;
    color: #fff;
  }

  .user-rank {
    font-size: 0.6875rem;
    color: var(--color-accent);
  }

  .btn-logout {
    background: transparent;
    border: none;
    color: var(--color-text-muted);
    cursor: pointer;
    font-size: 0.875rem;
    margin-left: 0.5rem;
    padding: 0.25rem;
  }

  .btn-logout:hover {
    color: #ef4444;
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

  .player-hub-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1.5rem;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.15);
    padding: 1.5rem 2.25rem;
    border-radius: 1.5rem;
    backdrop-filter: blur(0.75rem);
    box-shadow: 0 1.25rem 2.5rem rgba(0, 0, 0, 0.4);
  }

  .hub-stats {
    display: flex;
    align-items: center;
    gap: 1.5rem;
  }

  .stat-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
  }

  .stat-label {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }

  .stat-val {
    font-size: 1rem;
    font-weight: 700;
    color: #fff;
  }

  .stat-divider {
    width: 1px;
    height: 2rem;
    background: rgba(255, 255, 255, 0.15);
  }

  .btn-play {
    background: #061e27;
    border: 1px solid var(--color-accent);
    box-shadow: 0 0 1.25rem rgba(56, 189, 248, 0.2);
  }
</style>