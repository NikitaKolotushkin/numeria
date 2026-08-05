<template>
  <div class="landing-page">
    <!-- Шапка справа -->
    <header class="top-bar">
      <button class="btn-primary" @click="isAuthOpen = true">Регистрация/Вход</button>
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

      <button class="btn-primary btn-large" @click="isAuthOpen = true">
        Регистрация/Вход
      </button>
    </main>

    <!-- Модальное окно из Auth-модуля -->
    <AuthModal :is-open="isAuthOpen" @close="isAuthOpen = false" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AuthModal from '@/modules/auth/components/AuthModal.vue'

const isAuthOpen = ref(false)
</script>

<style scoped>
.landing-page {
  width: 100vw;
  height: 100vh;
  position: relative;
  background: url('/bg_city.png') center/cover no-repeat;
  display: flex;
}

.landing-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(15, 23, 42, 0.4); /* Оверлей поверх картинки */
  backdrop-filter: blur(2px);
}

.top-bar, .left-sidebar, .hero {
  position: relative;
  z-index: 2;
}

.top-bar {
  position: absolute;
  top: 32px;
  right: 48px;
}

.left-sidebar {
  position: absolute;
  left: 48px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.version-title { 
  font-size: 16px; 
  opacity: 0.9; 
  font-weight: 400;
}
.version-num { 
  font-size: 22px; 
  font-weight: 700; 
}

/* Стилизация логотипов партнеров */
.partners-logos {
  display: flex;
  flex-direction: column;
  gap: 20px;
  align-items: flex-start;
}

.partner-logo {
  max-width: 210px;    /* Максимальная ширина логотипа */
  max-height: 70px;    /* Максимальная высота */
  object-fit: contain; /* Сохраняет пропорции картинки */
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3)); /* Легкая тень для читаемости */
}

.hero {
  margin: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 36px;
}

/* Стилизация центрального логотипа */
.logo-box {
  display: flex;
  justify-content: center;
  align-items: center;
}

.main-logo {
  max-width: 380px;   /* Подберите подходящую ширину под ваш PNG */
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.4));
}

.btn-primary {
  background: #061e27; /* Темно-бирюзовый цвет кнопок как на скриншоте */
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 14px 32px;
  border-radius: 30px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  backdrop-filter: blur(10px);
}

.btn-primary:hover {
  background: #0a2d3a;
}

.btn-large {
  padding: 20px 56px;
  font-size: 22px;
  border-radius: 40px;
}
</style>