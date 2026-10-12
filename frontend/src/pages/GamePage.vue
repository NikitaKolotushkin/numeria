<template>
  <div class="game-page">
    <div
      class="stage"
      @click="onStageClick"
      @pointermove="onStagePointerMove"
    >
      <div
        v-for="plot in plots"
        :key="plot.id"
        class="plot-anchor"
        :class="`plot-anchor-${plot.id}`"
      >
        <button
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
      </div>

      <aside
        v-if="activePlot && plaquePoint"
        ref="plaqueEl"
        class="plaque"
        :class="{
          'plaque-left': plaquePlacement.horizontal === 'left',
          'plaque-up': plaquePlacement.vertical === 'up',
          'plaque-measuring': !plaqueReady
        }"
        :style="{ '--plaque-x': `${plaquePoint.x}%`, '--plaque-y': `${plaquePoint.y}%` }"
      >
        <p class="plaque-title">{{ activePlot.title }} (ур. {{ buildingInfo[activePlot.id].level }})</p>
        <p class="plaque-line">
          <strong>Освоение модуля:</strong> {{ buildingInfo[activePlot.id].mastery }}
        </p>
        <p class="plaque-line">
          <strong>Текущая тема:</strong> {{ buildingInfo[activePlot.id].topic }}
        </p>
        <p class="plaque-line">
          <strong>Для апгрейда:</strong> {{ buildingInfo[activePlot.id].upgrade }}
        </p>
      </aside>

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
import { computed, nextTick, ref } from 'vue'
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

const buildingInfo = {
  laboratory: {
    level: 1,
    mastery: '2 / 5 тем',
    topic: 'Анализ спроса',
    upgrade: 'Решить кейс «Эластичность цены»'
  },
  factory: {
    level: 1,
    mastery: '3 / 5 тем',
    topic: 'Себестоимость продукции',
    upgrade: 'Решить кейс «Точка безубыточности»'
  },
  office: {
    level: 1,
    mastery: '1 / 5 тем',
    topic: 'Организационная структура',
    upgrade: 'Решить кейс «Делегирование»'
  },
  accounting: {
    level: 1,
    mastery: '4 / 5 тем',
    topic: 'Метод двойной записи',
    upgrade: 'Решить кейс «План счетов»'
  },
  marketing: {
    level: 1,
    mastery: '2 / 5 тем',
    topic: 'Целевая аудитория',
    upgrade: 'Решить кейс «Позиционирование»'
  }
}

const activeBuildingId = ref(null)
const plaquePoint = ref(null)
const plaqueEl = ref(null)
const plaqueReady = ref(false)
const plaquePlacement = ref({ horizontal: 'right', vertical: 'down' })
const alphaMaps = new WeakMap()
let plaquePlaceToken = 0

const playerName = computed(() => authStore.user?.firstName || 'Линад')
const activePlot = computed(() => plots.find((plot) => plot.id === activeBuildingId.value) || null)

function pointOnStage(stage, clientX, clientY) {
  const rect = stage.getBoundingClientRect()
  return {
    x: ((clientX - rect.left) / rect.width) * 100,
    y: ((clientY - rect.top) / rect.height) * 100
  }
}

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
  if (event.target.closest('.nav-pill, .case-card, .player, .plaque')) {
    stage.style.cursor = ''
    return
  }

  stage.style.cursor = buildingAt(stage, event.clientX, event.clientY) ? 'pointer' : ''
}

function closePlaque() {
  plaquePlaceToken += 1
  activeBuildingId.value = null
  plaquePoint.value = null
  plaqueReady.value = false
}

function preferredPlacement(buildingId) {
  return {
    horizontal: buildingId === 'marketing' ? 'left' : 'right',
    vertical: 'down'
  }
}

function fitPlaqueToScreen(stage) {
  const plaque = plaqueEl.value
  if (!plaque) return

  const bounds = stage.getBoundingClientRect()
  const rect = plaque.getBoundingClientRect()
  const next = { ...plaquePlacement.value }

  if (next.vertical === 'down' && rect.bottom > bounds.bottom) next.vertical = 'up'
  if (next.horizontal === 'right' && rect.right > bounds.right) next.horizontal = 'left'
  if (next.horizontal === 'left' && rect.left < bounds.left) next.horizontal = 'right'

  plaquePlacement.value = next
}

async function openPlaque(stage, clientX, clientY, buildingId) {
  const token = ++plaquePlaceToken
  activeBuildingId.value = buildingId
  plaquePoint.value = pointOnStage(stage, clientX, clientY)
  plaquePlacement.value = preferredPlacement(buildingId)
  plaqueReady.value = false
  await nextTick()
  if (token !== plaquePlaceToken || !plaqueEl.value) return
  fitPlaqueToScreen(stage)
  plaqueReady.value = true
}

function onStageClick(event) {
  if (event.target.closest('.nav-pill, .case-card, .player, .plaque')) return

  const stage = event.currentTarget
  const fromKeyboard = event.detail === 0 ? event.target.closest('.plot') : null
  const plot = fromKeyboard || buildingAt(stage, event.clientX, event.clientY)
  if (!plot) {
    closePlaque()
    return
  }

  if (fromKeyboard) {
    const image = plot.querySelector('.plot-image')
    const rect = image.getBoundingClientRect()
    openPlaque(stage, rect.left + rect.width / 2, rect.top + rect.height * 0.4, plot.dataset.building)
    return
  }

  openPlaque(stage, event.clientX, event.clientY, plot.dataset.building)
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

.plot-anchor {
  position: absolute;
  pointer-events: none;
}

.plot {
  position: relative;
  z-index: 1;
  display: block;
  width: 100%;
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

.plot-factory,
.plot-accounting {
  z-index: 2;
}

.plot-anchor-laboratory {
  --plot-image-height: calc(30.88cqw * 1442 / 1984);
  width: 30.88%;
  left: 2.06%;
  top: calc(21.29cqh + (30.88cqh * 1442 / 1984) * (16 / 9) - (30.88cqw * 1442 / 1984));
}

.plot-anchor-factory {
  --plot-image-height: calc(27.22cqw * 1466 / 1984);
  width: 27.22%;
  left: 19.97%;
  top: calc(57.67cqh + (27.22cqh * 1466 / 1984) * (16 / 9) - (27.22cqw * 1466 / 1984));
}

.plot-anchor-office {
  --plot-image-height: calc(26.92cqw * 1507 / 1984);
  width: 26.92%;
  left: 36.91%;
  top: calc(25.16cqh + (26.92cqh * 1507 / 1984) * (16 / 9) - (26.92cqw * 1507 / 1984));
}

.plot-anchor-accounting {
  --plot-image-height: calc(26.04cqw * 1467 / 1984);
  width: 26.04%;
  left: 53.71%;
  top: calc(59.05cqh + (26.04cqh * 1467 / 1984) * (16 / 9) - (26.04cqw * 1467 / 1984));
}

.plot-anchor-marketing {
  --plot-image-height: calc(24.13cqw * 1507 / 1984);
  width: 24.13%;
  left: 71.63%;
  top: calc(28.91cqh + (24.13cqh * 1507 / 1984) * (16 / 9) - (24.13cqw * 1507 / 1984));
}

.plaque {
  position: absolute;
  z-index: 4;
  left: var(--plaque-x);
  top: var(--plaque-y);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.1em;
  width: max-content;
  margin: 0;
  padding: 0.78em 1.02em 0.86em;
  border-radius: 0.7em;
  border-top-left-radius: 0;
  background: #3e5964;
  color: #fff;
  pointer-events: auto;
  cursor: default;
  white-space: nowrap;
  box-shadow: 0 0.4em 1em rgba(16, 28, 32, 0.28);
}

.plaque-measuring {
  visibility: hidden;
}

.plaque-left {
  transform: translateX(-100%);
  border-top-left-radius: 0.7em;
  border-top-right-radius: 0;
}

.plaque-up {
  transform: translateY(-100%);
  border-top-left-radius: 0.7em;
  border-bottom-left-radius: 0;
}

.plaque-left.plaque-up {
  transform: translate(-100%, -100%);
  border-top-left-radius: 0.7em;
  border-top-right-radius: 0.7em;
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0.7em;
}

.plaque-title {
  margin: 0 0 0.28em;
  font-size: 1.12em;
  font-weight: 600;
  line-height: 1.25;
}

.plaque-line {
  margin: 0;
  font-size: 0.86em;
  font-weight: 400;
  line-height: 1.35;
}

.plaque-line strong {
  font-weight: 700;
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
