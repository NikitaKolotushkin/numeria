<template>
  <div class="game-page">
    <div
      class="stage"
      @click="onStageClick"
      @pointermove="onStagePointerMove"
    >
      <button
        v-for="plot in plots"
        :key="plot.id"
        type="button"
        class="plot"
        :class="`plot-${plot.id}`"
        :data-building="plot.id"
        :aria-pressed="activeBuildingId === plot.id"
        :aria-label="plot.title"
      >
        <img class="plot-image" :src="plot.src" alt="" />
        <span class="plot-label">{{ plot.title }}</span>
      </button>

      <router-link to="/" class="nav-pill" aria-label="Назад">
        <span class="nav-back" aria-hidden="true">
          <svg viewBox="0 0 24 24">
            <path
              d="M14.5 5.5 8 12l6.5 6.5"
              fill="none"
              stroke="currentColor"
              stroke-width="2.4"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <img class="nav-mark" src="@/assets/images/auth/logo-mark.png" alt="" />
      </router-link>

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
import { computed, ref } from 'vue'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'
import laboratory from '@/assets/images/game/buildings/01-laboratory/level-1.png'
import factory from '@/assets/images/game/buildings/02-factory/level-1.png'
import office from '@/assets/images/game/buildings/03-office/level-1.png'
import accounting from '@/assets/images/game/buildings/04-accounting/level-1.png'
import marketing from '@/assets/images/game/buildings/05-marketing/level-1.png'

const authStore = useAuthStore()

const plots = [
  { id: 'laboratory', title: 'Лаборатория', src: laboratory },
  { id: 'factory', title: 'Завод', src: factory },
  { id: 'office', title: 'Офис', src: office },
  { id: 'accounting', title: 'Бухгалтерия', src: accounting },
  { id: 'marketing', title: 'Маркетинг', src: marketing }
]

const activeBuildingId = ref(null)
const alphaMaps = new WeakMap()

const playerName = computed(() => authStore.user?.firstName || 'Линад')

function alphaAt(img, clientX, clientY) {
  if (!img?.complete || !img.naturalWidth) return 0

  const rect = img.getBoundingClientRect()
  const x = clientX - rect.left
  const y = clientY - rect.top
  if (x < 0 || y < 0 || x >= rect.width || y >= rect.height) return 0

  let map = alphaMaps.get(img)
  if (!map) {
    const canvas = document.createElement('canvas')
    canvas.width = img.naturalWidth
    canvas.height = img.naturalHeight
    const context = canvas.getContext('2d', { willReadFrequently: true })
    context.drawImage(img, 0, 0)
    map = context.getImageData(0, 0, canvas.width, canvas.height)
    alphaMaps.set(img, map)
  }

  const px = Math.min(map.width - 1, Math.floor((x / rect.width) * map.width))
  const py = Math.min(map.height - 1, Math.floor((y / rect.height) * map.height))
  return map.data[(py * map.width + px) * 4 + 3]
}

function onBuildingLabel(stage, clientX, clientY) {
  return [...stage.querySelectorAll('.plot-label')].some((label) => {
    const rect = label.getBoundingClientRect()
    return clientX >= rect.left && clientX <= rect.right
      && clientY >= rect.top && clientY <= rect.bottom
  })
}

function buildingAt(stage, clientX, clientY) {
  if (onBuildingLabel(stage, clientX, clientY)) return null

  const nodes = [...stage.querySelectorAll('.plot')]
  const ordered = nodes
    .map((node, index) => ({ node, index }))
    .sort((a, b) => {
      const za = Number(getComputedStyle(a.node).zIndex) || 0
      const zb = Number(getComputedStyle(b.node).zIndex) || 0
      if (za !== zb) return zb - za
      return b.index - a.index
    })

  for (const { node } of ordered) {
    const img = node.querySelector('.plot-image')
    if (alphaAt(img, clientX, clientY) > 24) return node
  }

  return null
}

function onStagePointerMove(event) {
  const stage = event.currentTarget
  if (event.target.closest('.nav-pill, .case-card, .player')) {
    stage.style.cursor = ''
    return
  }

  stage.style.cursor = buildingAt(stage, event.clientX, event.clientY) ? 'pointer' : ''
}

function onStageClick(event) {
  if (event.target.closest('.nav-pill, .case-card, .player')) return

  const fromKeyboard = event.detail === 0 ? event.target.closest('.plot') : null
  const plot = fromKeyboard || buildingAt(event.currentTarget, event.clientX, event.clientY)
  if (!plot) return

  activeBuildingId.value = plot.dataset.building
}

const capitalLabel = computed(() => {
  const value = authStore.user?.stats?.capital ?? 1600
  return String(value)
})
</script>

<style scoped>
.game-page {
  width: 100%;
  height: 100dvh;
  overflow: hidden;
  background: #5f8a0c;
}

.stage {
  --inset: 0.42em;
  --stack: 0.7em;
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  container-type: size;
  font-size: 1.5625cqw;
  background: url('@/assets/images/game/map.png') center / 100% 100% no-repeat;
}

.plot {
  position: absolute;
  z-index: 1;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  appearance: none;
  pointer-events: none;
}

.plot-image {
  display: block;
  width: 100%;
  height: auto;
  filter: drop-shadow(0 0.45rem 0.35rem rgba(20, 40, 10, 0.28));
}

.plot-label {
  position: absolute;
  left: 50%;
  z-index: 2;
  transform: translate(-50%, 0);
  padding: 0.42em 0.95em;
  border-radius: 9999px;
  background: rgba(42, 49, 56, 0.75);
  color: #fff;
  font-size: calc(0.86em - 2px);
  font-weight: 600;
  line-height: 1.1;
  white-space: nowrap;
  box-shadow: 0 0.28rem 0.55rem rgba(16, 24, 16, 0.28);
}

.plot-laboratory .plot-label {
  top: 72.7%;
}

.plot-factory .plot-label {
  top: 73.9%;
}

.plot-office .plot-label {
  top: 76%;
}

.plot-accounting .plot-label {
  top: 73.9%;
}

.plot-marketing .plot-label {
  top: 76%;
}

.plot-laboratory {
  width: 30.88%;
  left: 2.06%;
  top: calc(21.29cqh + (30.88cqh * 1442 / 1984) * (16 / 9) - (30.88cqw * 1442 / 1984));
}

.plot-factory {
  z-index: 2;
  width: 27.22%;
  left: 19.97%;
  top: calc(57.67cqh + (27.22cqh * 1466 / 1984) * (16 / 9) - (27.22cqw * 1466 / 1984));
}

.plot-office {
  width: 26.92%;
  left: 36.91%;
  top: calc(25.16cqh + (26.92cqh * 1507 / 1984) * (16 / 9) - (26.92cqw * 1507 / 1984));
}

.plot-accounting {
  z-index: 2;
  width: 26.04%;
  left: 53.71%;
  top: calc(59.05cqh + (26.04cqh * 1467 / 1984) * (16 / 9) - (26.04cqw * 1467 / 1984));
}

.plot-marketing {
  width: 24.13%;
  left: 71.63%;
  top: calc(28.91cqh + (24.13cqh * 1507 / 1984) * (16 / 9) - (24.13cqw * 1507 / 1984));
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
  width: 10.43%;
  height: 9.201%;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--inset);
  gap: var(--stack);
  color: #1a1f1c;
  text-decoration: none;
  cursor: pointer;
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
  justify-content: center;
  gap: 0.65em;
  padding: var(--inset) 1em;
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
