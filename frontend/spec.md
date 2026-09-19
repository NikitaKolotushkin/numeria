# ТЕХНИЧЕСКАЯ СПЕЦИФИКАЦИЯ: FRONTEND СЕРВИС («НУМЕРИЯ»)

* **Версия сервиса:** 0.1.5 (MVP in active dev)
* **Архитектурный подход:** Feature-Based / Domain-Driven (FSD Lite) Single Page Application (SPA)
* **Стратегия разработки:** Frontend-First / Mock-Driven (изолированный UI с контрактами данных до появления бэкенда)
* **Основной стек:** Vue 3 (Composition API, `<script setup>`), Vite, Pinia, Vue Router, Axios
* **Шрифт интерфейса:** Geologica (Google Fonts) — на всём UI, включая инпуты и селекты
* **Целевое окружение:** Docker (Multi-stage build -> Nginx Alpine static server)

---

## 1. Назначение и архитектура ключевых экранов

Фронтенд-приложение образовательной экономической стратегии «Нумерия». Визуальная структура приложения базируется на следующих экранах:

1. **Главный экран / Хаб (`pages/LandingPage.vue`):**
   * **Состояние гостя (по умолчанию, без сессии):** промо-страница, партнерские блоки вузов (ГУУ, СПбГУ, СГТУ, «Твой Ход»), кнопки «Вход» / «Регистрация» справа сверху, «Начать игру» под логотипом.
   * **Состояние игрока (есть сессия в Pinia / `localStorage`):** справа сверху капсула «Выйти» (`authStore.logout`); справа по центру имя, капитал и `Топ-N` с PNG `hub/avatar.png`, `hub/coin.png`, `hub/trophy.png`; под логотипом кнопка «Играть!» (переход на `/game`).

2. **Страница аутентификации и онбординга (`pages/AuthPage.vue`):**
   * Полноэкранный каркас мастера `AuthWizardLayout.vue` с навигационной шапкой (`[← logo-mark.png]`, капсула «Узнаем немного», `[→]`).
   * **Единый каркас шагов 1–4:** ширина и высота белой карточки фиксированы между этапами; внутренний padding одинаковый со всех сторон (`--auth-card-padding`). Масштаб с вьюпортом (`rem` / `vmin` / `vh` / `vw` / `clamp`, ландшафт).
   * **Толщины шрифта мастера:** заголовок шага 700, капсула шапки 500, поля / подписи / квиз / хобби 400.
   * **Модульный мастер регистрации (`AuthWizard.vue`):**
     * **Шаг 1 («Познакомимся» / `RegisterStepPersonal.vue`):** Сплит `form`. ФИО, вуз и направление — свободный ввод; курс — только цифра 1–6 + 3D-иллюстрация `step-personal.png`.
     * **Шаг 2 («Защитимся» / `RegisterStepSecurity.vue`):** Сплит `form`. Email только `@guu.ru`, пароль, подтверждение + 3D-иллюстрация `step-security.png`.
     * **Шаг 3 («Персонализируем» / `RegisterStepHobbies.vue`):** Сетка 3×2 интересов (Спорт, Кино, Музыка, Авто, Творчество, Книги) с PNG-постерами и SVG-галочкой выбора.
     * **Шаг 4 («Небольшой тест» / `RegisterStepQuiz.vue`):** Сплит `quiz`. 5 экономических вопросов, пагинация 1–5, варианты как радиокнопки без карточек. Пауза 1 с после выбора ответа; после последнего вопроса — переход на welcome.
     * **Экран готовности (`RegisterStepWelcome.vue`):** без шапки мастера. Логотип, «Ваша персонализация готова! / Добро пожаловать!», кнопка «Начнем» (регистрация в стор + редирект на `/`).
   * **Ошибки валидации:** тост `AuthErrorToast.vue` справа внизу поверх интерфейса, автоскрытие через 3 с. Каркас мастера не сдвигается.
   * **Экран входа (`LoginWizard.vue`, `/auth?mode=login`):** тот же каркас мастера. Капсула «С возвращением», заголовок «Войдем». Сплит `form`: почта `@guu.ru` + пароль слева, компактная кнопка «Войти» по центру под полями, иллюстрация `step-security.png` справа. Кнопка и стрелка «Далее» вызывают `authStore.login` и редирект на `/`.
   * Сессия пишется в Pinia (`useAuthStore`) и `localStorage`.

3. **Главное игровое поле (`pages/GamePage.vue`):**
   * Пока заглушка (приветствие и возврат в хаб). Карта корпорации, ResourceBar и модалки зданий — в дорожной карте.

4. **Универсальный раннер кейсов (`pages/CaseRunnerPage.vue`)** *(в разработке):*
   * Единый движок прохождения тестов (Quiz), развернутых кейсов (с симуляцией рецензии GigaChat через `AIEvaluationCard.vue`) и кризисных ситуаций с таймером принятия решений.

---

## 2. Актуальная структура директорий проекта

```text
frontend/
├── Dockerfile
├── nginx.conf
├── index.html
├── package.json
├── vite.config.js                      # алиас '@' -> 'src'
├── spec.md
├── .dockerignore
│
├── public/
│   └── bg_city.png
│
└── src/
    ├── app/
    │   ├── router/
    │   │   └── index.js                # маршруты '/', '/auth', '/game'
    │   └── styles/
    │       └── main.css                # Geologica, токены, ландшафтный масштаб html
    │
    ├── assets/
    │   └── images/
    │       ├── guu.png
    │       ├── logo_numeria.png
    │       ├── sgtu.png
    │       ├── spbgu.png
    │       ├── tvoy_hod.png
    │       ├── auth/                   # 3D-иллюстрации онбординга
    │       │   ├── logo-mark.png
    │       │   ├── step-personal.png
    │       │   ├── step-security.png
    │       │   ├── hobby-sport.png
    │       │   ├── hobby-cinema.png
    │       │   ├── hobby-music.png
    │       │   ├── hobby-auto.png
    │       │   ├── hobby-creativity.png
    │       │   └── hobby-books.png
    │       └── hub/                    # иконки хаба авторизованного игрока
    │           ├── avatar.png
    │           ├── coin.png
    │           └── trophy.png
    │
    ├── shared/
    │   ├── api/
    │   │   └── client.js               # Axios + Bearer из localStorage
    │   └── ui/
    │       └── BaseModal.vue
    │
    ├── modules/
    │   ├── auth/
    │   │   ├── api/
    │   │   │   ├── authApi.js
    │   │   │   └── mockData.js
    │   │   ├── components/
    │   │   │   ├── common/
    │   │   │   │   ├── AuthInput.vue
    │   │   │   │   ├── AuthMediaCard.vue
    │   │   │   │   ├── AuthSplitLayout.vue   # variant: form | quiz
    │   │   │   │   ├── AuthFieldsStack.vue
    │   │   │   │   ├── AuthFieldGroup.vue
    │   │   │   │   └── AuthErrorToast.vue
    │   │   │   ├── steps/
    │   │   │   │   ├── RegisterStepPersonal.vue
    │   │   │   │   ├── RegisterStepSecurity.vue
    │   │   │   │   ├── RegisterStepHobbies.vue
    │   │   │   │   ├── RegisterStepQuiz.vue
    │   │   │   │   ├── RegisterStepWelcome.vue
    │   │   │   │   └── LoginStep.vue
    │   │   │   ├── AuthWizard.vue
    │   │   │   ├── LoginWizard.vue
    │   │   │   └── AuthWizardLayout.vue
    │   │   └── store/
    │   │       └── useAuthStore.js
    │   ├── game/                       # (ещё не развёрнут)
    │   ├── study/
    │   ├── ai-mentor/
    │   ├── crisis/
    │   ├── career/
    │   └── notifications/
    │
    ├── pages/
    │   ├── LandingPage.vue
    │   ├── AuthPage.vue
    │   └── GamePage.vue
    │
    ├── App.vue
    └── main.js
```

---

## 3. Что уже реализовано (Status: Done)

1. **Базовый каркас и инфраструктура:**
   * Vite + Vue 3 (Composition API), алиас `@` -> `src`.
   * Шрифт **Geologica**, тёмная тема, CSS-токены.
   * Ландшафтная адаптивность: `html { font-size: clamp(16px, 1.8vmin, 20px) }` при `orientation: landscape`; размеры UI в `rem` / `clamp` / `vh` / `vw`. Портрет пока не нормирован.
   * Docker (Node 20 -> Nginx Alpine), SPA `try_files`.

2. **Маршрутизация:**
   * `/`, `/auth`, `/game`; обновление `document.title`.

3. **Онбординг и сессия:**
   * `useAuthStore` + мок `authApi` / `mockData`.
   * Шаги 1–4 в общем каркасе + welcome-экран после квиза.
   * Экран входа в том же каркасе (`/auth?mode=login`).
   * Тост ошибок поверх UI (3 с).
   * 3D-постеры шагов «Познакомимся», «Защитимся» и сетки хобби.

4. **Главный экран:**
   * Гость — промо, партнёры, вход/регистрация.
   * Игрок — панель `hub/` (аватар, монета, кубок), «Играть!», «Выйти».

---

## 4. Дорожная карта разработки (Frontend-First Roadmap)

### Этап 1: Главный экран, Доводка регистрации и Вход (Auth & Hub)
- [x] Создать страницу `pages/AuthPage.vue` и зарегистрировать маршрут `/auth`.
- [x] Настроить стор `useAuthStore.js` и мок-слой `authApi.js` / `mockData.js`.
- [x] Реализовать логику шагов регистрации и welcome-экрана (`AuthWizard.vue`).
- [x] Реализовать двухрежимный экран `LandingPage.vue` (Гость / Игрок).
- [x] Подогнать UI регистрации под макет: общий каркас шагов, капсульные инпуты, сплит, веса Geologica.
- [x] Подключить 3D-иллюстрации шагов 1–3 (`src/assets/images/auth/`).
- [x] Реализовать форму входа для уже зарегистрированных игроков (логин по email/паролю).
- [x] Собрать хаб игрока по макету: панель `hub/`, «Играть!», «Выйти».

### Этап 2: Игровое поле и Экономика (Game Core)
- [ ] Разработать Pinia-стор `modules/game/store/useGameStore.js` (управление балансом, энергией, зданиями).
- [ ] Сформировать Mock API слой `modules/game/api/gameApi.js` и `mockData.js`.
- [ ] Создать верхнюю панель ресурсов `modules/game/components/ResourceBar.vue`.
- [ ] Разработать интерактивную карту `modules/game/components/CorporationMap.vue` (сетка секторов, 5 уровней прокачки зданий, визуальные состояния).
- [ ] Реализовать модальное окно сектора/здания `modules/game/components/BuildingModal.vue` с механикой улучшения.
- [ ] Собрать экран `pages/GamePage.vue`.

### Этап 3: Универсальный раннер кейсов и ИИ-ментор (Study & AI)
- [ ] Создать страницу `pages/CaseRunnerPage.vue` и раннер `modules/study/components/CaseRunner.vue`.
- [ ] Разработать компонент тестирования `QuizView.vue` (выбор вариантов, подсчет баллов).
- [ ] Разработать компонент открытых кейсов `BossCaseView.vue` с симуляцией рецензирования GigaChat через `AIEvaluationCard.vue`.
- [ ] Реализовать сторы `useStudyStore.js` и `useAIStore.js`.

### Этап 4: Кризисный движок и Система нотификаций (Crisis & Notifications)
- [ ] Разработать модалку ЧП `modules/crisis/components/CrisisDecisionModal.vue` с таймером принятия решений.
- [ ] Создать стор `useCrisisStore.js`.
- [ ] Вынести тосты из `auth` в глобальный модуль notifications (сейчас тост ошибок есть только в онбординге).

### Этап 5: Финальная интеграция с бэкендом (FastAPI Microservices)
- [ ] Заменить моковые промисы в `modules/*/api/` на реальные эндпоинты через `shared/api/client.js`.
- [ ] Настроить Navigation Guards (`router.beforeEach`) для защиты приватных маршрутов (`/game`, `/study`).
- [ ] Настроить глобальный перехватчик Axios для ошибок 401/403 с редиректом на авторизацию.

---

## 5. Регламенты и стандарты разработки фронтенда

1. **Компонентный стиль:**
   * Использовать **исключительно** Composition API (`<script setup>`).
   * Стили компонентов строго изолированы (`<style scoped>`), без инлайн-стилей `style="..."`.
   * DRY: общие паттерны разметки выносятся в `modules/auth/components/common/`.

2. **Графика и дизайн-система (Zero-Emoji Policy):**
   * **Категорически запрещено** использовать Unicode-эмодзи в UI.
   * Иконки навигации мастера и галочка хобби — **SVG**. Иконки хаба игрока — **PNG** в `src/assets/images/hub/` (`avatar.png`, `coin.png`, `trophy.png`).
   * Капсульные инпуты и кнопки: `border-radius: 9999px`.
   * Без hover-подъёма (`translateY`) и без появления обводки у кнопок.
   * 3D-постеры онбординга лежат в `src/assets/images/auth/` с фиксированными именами (`logo-mark.png`, `step-personal.png`, `step-security.png`, `hobby-*.png`).

3. **Адаптивность:**
   * Пока нормирован только **ландшафт** (`orientation: landscape`).
   * Каркас мастера (шапка + карточка) одинаков на шагах 1–4; масштабируется относительными единицами, а не отдельными брейкпоинтами на каждый шаг.
   * Портретная вёрстка — отдельная задача.

4. **Управление состоянием (Pinia):**
   * Бизнес-логика сессии, баланса и ресурсов — только в `modules/<module_name>/store/`.

5. **Mock-First регламент сетевого слоя:**
   * Все запросы в `modules/<module_name>/api/`.
   * До бэкенда — `Promise` с задержкой 200–400 мс.
   * Моковые данные не хранить внутри `.vue`.

6. **Импорты путей:**
   * Только алиас `@/`. Относительные пути `../../` запрещены.
