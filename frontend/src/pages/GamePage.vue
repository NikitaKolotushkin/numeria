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
        :class="{ 'is-focused': focusedBuildingId === plot.id }"
        :style="{
          '--plot-width': plot.place.width,
          '--plot-left': plot.place.left,
          '--plot-top': plot.place.top,
          '--plot-base-width': plot.place.baseWidth,
          '--plot-anchor-foot': plot.place.anchorFoot,
          '--plot-foot': plot.place.foot
        }"
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
        <p class="plaque-title">{{ activePlot.title }} (ур. {{ activePlot.level }})</p>
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

      <div
        class="stage-blur"
        :class="{ 'is-active': blurActive }"
        aria-hidden="true"
        @transitionend="onBlurTransitionEnd"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, ref } from 'vue'
import { useAuthStore } from '@/modules/auth/store/useAuthStore'

const buildingSprites = import.meta.glob(
  '../assets/images/game/buildings/*/*.png',
  { eager: true, import: 'default' }
)

const spriteFolders = {
  laboratory: '01-laboratory',
  factory: '02-factory',
  office: '03-office',
  accounting: '04-accounting',
  marketing: '05-marketing'
}

const CANVAS = 1984
const LEVEL_GROWTH = 0.34
const LEVEL_MAX_SCALE = 1.5

const buildingLayouts = {
  laboratory: { width: 27.792, left: 3.604, top: 25.28, anchorFoot: 1442 },
  factory: { width: 24.498, left: 21.331, top: 61.25, anchorFoot: 1466 },
  office: { width: 24.228, left: 38.256, top: 28.8, anchorFoot: 1507 },
  accounting: { width: 23.436, left: 55.012, top: 62.47, anchorFoot: 1467 },
  marketing: { width: 21.717, left: 72.837, top: 32.17, anchorFoot: 1507 }
}

const buildingBounds = {
  laboratory: {
    1: [582, 1392, 567, 1440],
    2: [413, 1596, 490, 1509],
    3: [257, 1759, 393, 1570],
    4: [178, 1798, 364, 1609],
    5: [164, 1811, 11, 1618]
  },
  factory: {
    1: [537, 1456, 523, 1466],
    2: [402, 1568, 413, 1583],
    3: [190, 1836, 339, 1696],
    4: [86, 1945, 168, 1780],
    5: [53, 1822, 15, 1978]
  },
  office: {
    1: [526, 1455, 601, 1506],
    2: [538, 1456, 524, 1476],
    3: [581, 1398, 393, 1593],
    4: [68, 1902, 268, 1834],
    5: [5, 1925, 44, 1880]
  },
  accounting: {
    1: [511, 1470, 496, 1467],
    2: [344, 1664, 303, 1628],
    3: [306, 1706, 243, 1654],
    4: [212, 1801, 146, 1746],
    5: [48, 1857, 7, 1829]
  },
  marketing: {
    1: [474, 1509, 467, 1507],
    2: [150, 1831, 385, 1590],
    3: [110, 1869, 352, 1743],
    4: [152, 1831, 207, 1711],
    5: [3, 1977, 0, 1841]
  }
}

function buildingSpan(box) {
  const [minX, maxX, minY, maxY] = box
  return {
    minX,
    maxX,
    maxY,
    width: maxX - minX + 1,
    height: maxY - minY + 1,
    center: (minX + maxX) / 2
  }
}

function placeBuilding(id, level) {
  const layout = buildingLayouts[id]
  const base = buildingSpan(buildingBounds[id][1])
  const box = buildingSpan(buildingBounds[id][level])
  const natural = Math.max(box.width / base.width, box.height / base.height)
  const desired = Math.min(LEVEL_MAX_SCALE, 1 + Math.max(0, natural - 1) * LEVEL_GROWTH)
  const scale = desired / natural
  const width = layout.width * scale
  const anchorCenter = layout.left + layout.width * (base.center / CANVAS)
  return {
    width,
    left: anchorCenter - width * (box.center / CANVAS),
    top: layout.top,
    baseWidth: layout.width,
    anchorFoot: layout.anchorFoot,
    foot: level === 1 ? layout.anchorFoot : box.maxY
  }
}

function spriteSrc(id, level) {
  const folder = spriteFolders[id]
  const entry = Object.entries(buildingSprites).find(([path]) =>
    path.endsWith(`/${folder}/level-${level}.png`)
  )
  return entry ? entry[1] : ''
}

const authStore = useAuthStore()

const plots = [
  { id: 'laboratory', title: 'Лаборатория' },
  { id: 'factory', title: 'Завод' },
  { id: 'office', title: 'Офис' },
  { id: 'accounting', title: 'Бухгалтерия' },
  { id: 'marketing', title: 'Маркетинг' }
].map((plot) => {
  const level = 1
  return {
    ...plot,
    level,
    place: placeBuilding(plot.id, level),
    src: spriteSrc(plot.id, level)
  }
})

const buildingInfo = {
  laboratory: {
    mastery: '2 / 5 тем',
    topic: 'Анализ спроса',
    upgrade: 'Решить кейс «Эластичность цены»'
  },
  factory: {
    mastery: '3 / 5 тем',
    topic: 'Себестоимость продукции',
    upgrade: 'Решить кейс «Точка безубыточности»'
  },
  office: {
    mastery: '1 / 5 тем',
    topic: 'Организационная структура',
    upgrade: 'Решить кейс «Делегирование»'
  },
  accounting: {
    mastery: '4 / 5 тем',
    topic: 'Метод двойной записи',
    upgrade: 'Решить кейс «План счетов»'
  },
  marketing: {
    mastery: '2 / 5 тем',
    topic: 'Целевая аудитория',
    upgrade: 'Решить кейс «Позиционирование»'
  }
}

const activeBuildingId = ref(null)
const plaquePoint = ref(null)
const plaqueEl = ref(null)
const plaqueReady = ref(false)
const blurActive = ref(false)
const focusedBuildingId = ref(null)
const plaquePlacement = ref({ horizontal: 'right', vertical: 'down' })
const alphaMaps = new WeakMap()
let plaquePlaceToken = 0
let pendingOpen = null

const playerName = computed(() => authStore.user?.firstName || 'Линад')
const activePlot = computed(() => plots.find((plot) => plot.id === activeBuildingId.value) || null)

function pointOnStage(stage, clientX, clientY) {
  const rect = stage.getBoundingClientRect()
  return {
    x: ((clientX - rect.left) / rect.width) * 100,
    y: ((clientY - rect.top) / rect.height) * 100
  }
}

function imageAlphaMap(img) {
  if (!img?.complete || !img.naturalWidth) return null

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

  return map
}

function alphaAt(img, clientX, clientY) {
  const map = imageAlphaMap(img)
  if (!map) return 0

  const rect = img.getBoundingClientRect()
  const x = clientX - rect.left
  const y = clientY - rect.top
  if (x < 0 || y < 0 || x >= rect.width || y >= rect.height) return 0

  const px = Math.min(map.width - 1, Math.floor((x / rect.width) * map.width))
  const py = Math.min(map.height - 1, Math.floor((y / rect.height) * map.height))
  return map.data[(py * map.width + px) * 4 + 3]
}

const opaqueCenterXByImage = new WeakMap()

function buildingCenterClientX(img) {
  const rect = img.getBoundingClientRect()
  const map = imageAlphaMap(img)
  if (!map) return rect.left + rect.width / 2

  let center = opaqueCenterXByImage.get(img)
  if (center == null) {
    let minX = map.width
    let maxX = -1
    for (let index = 0; index < map.width * map.height; index += 1) {
      if (map.data[index * 4 + 3] <= 24) continue
      const x = index % map.width
      if (x < minX) minX = x
      if (x > maxX) maxX = x
    }
    center = maxX < 0 ? map.width / 2 : (minX + maxX) / 2
    opaqueCenterXByImage.set(img, center)
  }

  return rect.left + (center / img.naturalWidth) * rect.width
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

function onBlurTransitionEnd(event) {
  if (event.propertyName !== 'backdrop-filter' && event.propertyName !== '-webkit-backdrop-filter') return
  if (blurActive.value) return

  const next = pendingOpen
  pendingOpen = null
  focusedBuildingId.value = null
  if (next) openPlaque(next.stage, next.clientX, next.clientY, next.buildingId)
}

function closePlaque({ keepPending = false } = {}) {
  if (!keepPending) pendingOpen = null
  plaquePlaceToken += 1
  activeBuildingId.value = null
  plaquePoint.value = null
  plaqueReady.value = false
  const blurWasOn = blurActive.value
  blurActive.value = false
  if (!blurWasOn) focusedBuildingId.value = null
}

function requestPlaque(stage, clientX, clientY, buildingId) {
  const blurEngaged = blurActive.value || focusedBuildingId.value !== null
  if (blurEngaged && activeBuildingId.value !== buildingId) {
    pendingOpen = { stage, clientX, clientY, buildingId }
    if (blurActive.value) closePlaque({ keepPending: true })
    return
  }

  pendingOpen = null
  openPlaque(stage, clientX, clientY, buildingId)
}

function preferredPlacement(stage, clientX, buildingId) {
  const image = stage.querySelector(`.plot[data-building="${buildingId}"] .plot-image`)
  const horizontal = image && clientX < buildingCenterClientX(image) ? 'left' : 'right'

  return {
    horizontal,
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
  plaquePlacement.value = preferredPlacement(stage, clientX, buildingId)
  plaqueReady.value = false
  await nextTick()
  if (token !== plaquePlaceToken || !plaqueEl.value) return
  fitPlaqueToScreen(stage)
  focusedBuildingId.value = buildingId
  plaqueReady.value = true
  blurActive.value = true
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
    requestPlaque(stage, rect.left + rect.width / 2, rect.top + rect.height * 0.4, plot.dataset.building)
    return
  }

  requestPlaque(stage, event.clientX, event.clientY, plot.dataset.building)
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
  width: calc(var(--plot-width) * 1%);
  left: calc(var(--plot-left) * 1%);
  top: calc(
    var(--plot-top) * 1cqh
    + (var(--plot-base-width) * var(--plot-anchor-foot) / 1984) * (16 / 9) * 1cqh
    - (var(--plot-width) * var(--plot-foot) / 1984) * 1cqw
  );
}

.plot-anchor.is-focused {
  z-index: 6;
}

.stage-blur {
  position: absolute;
  inset: 0;
  z-index: 5;
  pointer-events: none;
  background-color: transparent;
  backdrop-filter: blur(0px);
  -webkit-backdrop-filter: blur(0px);
  transition:
    backdrop-filter 0.4s ease,
    -webkit-backdrop-filter 0.4s ease;
}

.stage-blur.is-active {
  background-color: rgb(0 0 0 / 1%);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
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
  top: calc(var(--plot-foot) / 1984 * 100%);
  box-shadow: 0 0.28rem 0.55rem rgba(16, 24, 16, 0.28);
}

.plot-factory,
.plot-accounting {
  z-index: 2;
}

.plaque {
  position: absolute;
  z-index: 7;
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
  background: #002126;
  font-size: 0.8em;
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
  font-weight: 400;
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
