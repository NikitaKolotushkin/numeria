<template>
  <div class="game-page">
    <div class="stage">
      <img
        v-for="plot in plots"
        :key="plot.id"
        class="plot"
        :class="`plot-${plot.id}`"
        :src="plot.src"
        alt=""
      />

      <div class="nav-pill">
        <router-link to="/" class="nav-back" aria-label="Назад">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path
              d="M14.5 5.5 8 12l6.5 6.5"
              fill="none"
              stroke="currentColor"
              stroke-width="2.4"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </router-link>
        <img class="nav-mark" src="@/assets/images/auth/logo-mark.png" alt="" />
      </div>

      <section class="case-card">
        <h1 class="case-title">Кейс 2. Блок 3</h1>
        <p class="case-subtitle">Затраты предприятия</p>
        <button type="button" class="case-next">Вперед!</button>
      </section>

      <aside class="player">
        <div class="player-pill">
          <img class="player-avatar" src="@/assets/images/hub/avatar.png" alt="" />
          <span>{{ playerName }}</span>
        </div>

        <div class="player-pill">
          <img class="player-coin" src="@/assets/images/hub/coin.png" alt="" />
          <span>{{ capitalLabel }}</span>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import laboratory from '@/assets/images/game/buildings/01-laboratory/level-1.png'
import factory from '@/assets/images/game/buildings/02-factory/level-1.png'
import office from '@/assets/images/game/buildings/03-office/level-1.png'
import accounting from '@/assets/images/game/buildings/04-accounting/level-1.png'
import marketing from '@/assets/images/game/buildings/05-marketing/level-1.png'

const authStore = useAuthStore()

const plots = [
  { id: 'laboratory', src: laboratory },
  { id: 'factory', src: factory },
  { id: 'office', src: office },
  { id: 'accounting', src: accounting },
  { id: 'marketing', src: marketing }
]

const playerName = computed(() => authStore.user?.firstName || 'Линад')

const capitalLabel = computed(() => {
  const value = authStore.user?.stats?.capital ?? 1600
  return String(value)
})
</script>

<style scoped>
.game-page {
  width: 100%;
  height: 100dvh;
  display: grid;
  place-items: center;
  background: #5f8a0c;
}

.stage {
  --inset: 0.42em;
  --stack: 0.7em;
  position: relative;
  width: min(100vw, calc(100dvh * 16 / 9));
  aspect-ratio: 16 / 9;
  container-type: size;
  font-size: 1.5625cqw;
  background: url('@/assets/images/game/map.jpg') center / 100% 100% no-repeat;
}

.plot {
  position: absolute;
  height: auto;
  pointer-events: none;
  z-index: 1;
  filter: drop-shadow(0 0.45rem 0.35rem rgba(20, 40, 10, 0.28));
}

.plot-laboratory {
  width: 30.88%;
  left: 2.06%;
  top: 21.29%;
}

.plot-factory {
  z-index: 2;
  width: 27.22%;
  left: 19.97%;
  top: 57.67%;
}

.plot-office {
  width: 26.92%;
  left: 36.91%;
  top: 25.16%;
}

.plot-accounting {
  z-index: 2;
  width: 26.04%;
  left: 53.71%;
  top: 59.05%;
}

.plot-marketing {
  width: 24.13%;
  left: 71.63%;
  top: 28.91%;
}

.nav-pill,
.case-card,
.player-pill {
  position: absolute;
  z-index: 3;
  background: #fff;
  box-shadow: 0 0.35rem 0.9rem rgba(16, 32, 16, 0.16);
}

.nav-pill {
  left: 4.785%;
  top: 3.819%;
  width: 13.574%;
  height: 9.201%;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--inset);
  gap: var(--stack);
}

.nav-back {
  flex: 0 0 1.35em;
  width: 1.35em;
  height: 1.35em;
  display: grid;
  place-items: center;
  padding: 0;
  border: 0;
  background: transparent;
  color: #1a1f1c;
  cursor: pointer;
  text-decoration: none;
}

.nav-back svg {
  width: 100%;
  height: 100%;
}

.nav-mark {
  width: calc(9.201cqh - (var(--inset) * 2));
  height: calc(9.201cqh - (var(--inset) * 2));
  flex: 0 0 auto;
  display: block;
}

.case-card {
  left: 32.52%;
  top: 3.819%;
  width: 35.059%;
  height: 23.958%;
  border-radius: 1.25em;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75em;
  padding: 1.05em 1.45em;
}

.case-title {
  margin: 0;
  color: #0e191b;
  font-size: 1.25em;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.case-subtitle {
  margin: 0;
  color: #66727a;
  font-size: 0.95em;
  font-weight: 500;
  line-height: 1.25;
}

.case-next {
  margin-top: 0.2em;
  background: #002126;
  color: #fff;
  border: 0;
  border-radius: 9999px;
  padding: 0.55em 1.45em;
  font-size: 0.9em;
  font-weight: 700;
  line-height: 1;
  font-family: inherit;
  cursor: pointer;
}

.player {
  position: absolute;
  z-index: 3;
  left: 78.32%;
  top: 3.819%;
  width: 16.992%;
  display: flex;
  flex-direction: column;
  gap: 0.7em;
}

.player-pill {
  position: relative;
  height: 9.201cqh;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  gap: 0.65em;
  padding: var(--inset) 1em var(--inset) var(--inset);
  color: #121816;
  font-size: 1.05em;
  font-weight: 700;
  line-height: 1;
}

.player-avatar,
.player-coin {
  width: calc(9.201cqh - (var(--inset) * 2));
  height: calc(9.201cqh - (var(--inset) * 2));
  flex-shrink: 0;
  display: block;
}

.player-avatar {
  border-radius: 0.45em;
  object-fit: cover;
}

.player-coin {
  object-fit: contain;
}
</style>
