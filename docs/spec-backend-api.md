# Контракты API пилота «Нумерия»

Схема таблиц: `docs/spec-backend-schema.md`. Границы сервисов: `docs/spec-backend.md`.

Реализованы разделы «Пользователи», «Учёба» и «Игра», кроме живого вызова GigaChat: без `ai` открытие пустого среза и оценка босса отвечают `504`. Разделы «Кризисы», «Карьера» и «Уведомления» остаются контрактом, сервисов под них нет. Клиент со сессией вызывает вход, `GET /game/me/state`, трек и попытку блока.

Браузер видит только префиксы nginx: `/api/users`, `/api/study`, `/api/game`, `/api/crisis`, `/api/career`, `/api/notifications`. Пути ниже даны так, как их принимает сам сервис: nginx срезает префикс. Пример: `POST /api/users/auth/login` попадает в `users` как `POST /auth/login`.

`/api/ai` с браузера не используется. Оценка, персонализация и черновик кризиса — внутренние вызовы с заголовком `X-Service-Token`. Тот же заголовок обязателен на `/internal/*` у `study`, `game`, `crisis` и `notifications`. Nginx эти пути не публикует отдельным `location`; сервисы всё равно отвергают запрос без токена кодом 401.

JSON, кодировка UTF-8. Имена полей в телах — camelCase, как уже ждёт клиент у `accessToken`.

Ошибка везде одна:

```json
{ "error": { "code": "consent_required", "message": "Нужны три согласия" } }
```

`message` можно показать человеку. `code` стабилен для ветки в клиенте.

| HTTP | Когда |
| --- | --- |
| 400 | Тело не разбирается |
| 401 | Нет токена, токен просрочен или отозван |
| 403 | Роль не пускает на маршрут |
| 404 | Нет такой сущности у этого игрока |
| 409 | Шаг ещё закрыт, кризис уже отвечен, письмо-дубль |
| 422 | Поля есть, но не проходят правила |
| 504 | GigaChat не ответил за отведённое время |

Токен доступа — JWT HS256, подписывает только `users`. Остальные сервисы проверяют подпись общим секретом и не ходят в `users` на каждый запрос. В токене `sub` (uuid игрока), `role`, `jti`, `exp`. Срок доступа 30 минут, срок обновления 14 дней. `jti` отозванного доступа лежит в `access_denylist` до `exp`.

Дальше заголовок `Authorization: Bearer` обозначен как «сессия». Игрок берётся из `sub`. Поле `userId` в теле студенческого запроса не читается.

---

## 1. Пользователи

### `POST /auth/register`

Без сессии.

```json
{
  "firstName": "Данил",
  "lastName": "Зенин",
  "university": "ГУУ",
  "direction": "Прикладная информатика",
  "course": 3,
  "email": "student@guu.ru",
  "password": "secret",
  "hobbies": ["sport", "cinema"],
  "onboardingAnswers": [{ "questionId": 1, "optionIndex": 2 }],
  "consents": {
    "personalData": true,
    "terms": true,
    "aiAssessment": true,
    "policyVersion": "2026-06-01"
  }
}
```

Правила, код `validation_error` и статус 422, если не сказано иначе:

- имя, фамилия, вуз и направление после обрезки пробелов не пустые; имя и фамилия не длиннее 80 символов, вуз и направление не длиннее 160;
- курс — целое от 1 до 6;
- пароль от 4 до 128 символов;
- почта обрезается, приводится к нижнему регистру и содержит локальную часть и домен без пробелов;
- хобби — от одного до шести разных id из набора мастера: `sport`, `cinema`, `music`, `auto`, `creativity`, `books`;
- онбординг — ровно вопросы 1, 2, 3, 4 и 5, каждый один раз, индекс варианта от 0 до 3;
- `policyVersion` после обрезки не пустой и не длиннее 32 символов.

Хотя бы одно из трёх согласий не `true` — 422 `consent_required`, даже если остальные поля тоже плохие. Домен `@guu.ru` не требуется. Повтор почты — 409 `email_taken`.

Коды этого сервиса: `consent_required`, `validation_error`, `email_taken`, `invalid_credentials`, `token_invalid`.

Ответ 201 — тот же конверт, что у входа. Пароль в ответе не появляется.

После фиксации аккаунта `users` один раз вызывает `POST /internal/players`, `POST /internal/personalize` и `POST /internal/welcome`. Пустой базовый URL, таймаут или ошибка соседа не откатывает аккаунт и не меняет 201.

### `POST /auth/login`

```json
{ "email": "student@guu.ru", "password": "secret" }
```

Неверная пара — 401 `invalid_credentials`. Ответ 200:

```json
{
  "accessToken": "...",
  "refreshToken": "...",
  "tokenType": "bearer",
  "user": {
    "id": "uuid",
    "email": "student@guu.ru",
    "firstName": "Данил",
    "lastName": "Зенин",
    "university": "ГУУ",
    "direction": "Прикладная информатика",
    "course": 3,
    "hobbies": ["sport", "cinema"],
    "role": "student"
  }
}
```

Капитал и опыт в этот объект не входят. Их читает `GET /api/game/me/state`.

### `POST /auth/refresh`

```json
{ "refreshToken": "..." }
```

Ответ 200 — новая пара токенов и тот же `user`. Старый refresh помечается отозванным. Чужой или просроченный refresh — 401.

### `POST /auth/logout`

Сессия. Тело `{ "refreshToken": "..." }`. Refresh отзывается, только если он принадлежит тому же игроку, что и токен доступа. Чужой, просроченный или уже отозванный refresh — 401 `token_invalid`, доступ при этом не гасится. Свой refresh отзывается, его `jti` доступа попадает в запретный список. Ответ 204. Пустое тело — 422 `validation_error`.

### `GET /me`

Сессия. Ответ 200 — объект `user` из входа.

### `PATCH /me`

Сессия. Любой набор из `firstName`, `lastName`, `university`, `direction`, `course`, `hobbies`. Переданное поле проходит те же правила, что при регистрации. `hobbies`, если ключ есть, заменяет прежний набор целиком. Почта, роль и пароль этим маршрутом не меняются. Ответ 200 — обновлённый `user`.

---

## 2. Учёба

Все маршруты этого раздела, кроме `/internal/*` и `/admin/*`, требуют сессию студента. Куратор проходит туда же, где ему нужно видеть свой прогресс, но чужие попытки читает только админский раздел.

### `GET /tracks/{buildingId}`

`buildingId` — одно из пяти зданий. Ответ 200:

```json
{
  "buildingId": "laboratory",
  "moduleId": "analytics",
  "moduleTitle": "Аналитика и статистика",
  "bossUnlocked": false,
  "steps": [
    {
      "kind": "block",
      "id": "uuid",
      "title": "Выборка и среднее",
      "status": "available",
      "questionCount": 12
    },
    {
      "kind": "boss",
      "id": "uuid",
      "title": "Кейс модуля",
      "status": "locked"
    }
  ]
}
```

`status` блока: `locked`, `available`, `passed`, `retake_required`. У босса `locked`, `available`, `passed`. Теории и вариантов в этом ответе нет.

### `GET /blocks/{blockId}`

404, если блок чужого прогресса не существует. 409 `step_locked`, если статус `locked`. Для `available`, `passed` и `retake_required` сервис смотрит срез этого игрока. Среза нет — один вызов `ai`, запись `block_snapshots` и вопросов, затем ответ 200. Повторный запрос генерацию не повторяет. Сбой модели — 504 `ai_timeout`, пустой слот остаётся пустым.

```json
{
  "id": "uuid",
  "title": "Выборка и среднее",
  "theoryMarkdown": "...",
  "questions": [
    {
      "id": "uuid",
      "prompt": "Что оценивает выборочное среднее?",
      "options": [
        { "id": "uuid", "body": "Среднее по выборке" }
      ]
    }
  ]
}
```

Поля `isCorrect` нет.

### `POST /blocks/{blockId}/attempts`

409, если блок `locked` или уже `passed`. На `retake_required` и `available` попытка принимается.

```json
{
  "answers": [
    { "questionId": "uuid", "optionId": "uuid" }
  ]
}
```

В массиве каждый вопрос среза этого игрока ровно один раз, вариант принадлежит этому вопросу. Иначе 422 `answers_incomplete`. Невыбранный вопрос не допускается: клиент шлёт полный набор.

Ответ 200:

```json
{
  "attemptId": "uuid",
  "correctCount": 8,
  "totalCount": 12,
  "score": 67,
  "passed": false
}
```

`score = round(correctCount / totalCount * 100)`. `passed` истинен при `score >= 70`. При сдаче статус блока становится `passed`, следующий шаг открывается, в `game` уходит `block_passed` с `sourceId = attemptId`. При провале статус не меняется, награда не шлётся. Какой вариант был верным, ответ не содержит.

### `GET /bosses/{bossId}`

409 `step_locked`, пока босс не `available` и не `passed`. Если среза этого игрока ещё нет, текст кейса один раз пишет `ai` и кладёт в `boss_snapshots`. Ответ 200: `id`, `title`, `promptMarkdown`. Разбора прошлых попыток здесь нет. Сбой модели — 504 `ai_timeout`.

### `POST /bosses/{bossId}/attempts`

Только из статуса `available`. Тело `{ "answerText": "..." }`. Пустая строка — 422 `empty_answer`.

Сервис синхронно вызывает `ai` и держит запрос не дольше 25 секунд. Ответ 200:

```json
{
  "attemptId": "uuid",
  "score": 84,
  "verdict": "accepted",
  "passed": true,
  "reviewText": "...",
  "growthZones": ["Где заканчиваются полномочия сотрудника"]
}
```

`verdict` — `accepted` или `retry`. `passed` совпадает с `accepted`. При сдаче босс становится `passed`, в `game` уходит `boss_passed`. При `retry` босс остаётся `available`, награда не шлётся.

Если модель не ответила, попытка сохраняется с `verdict = error`, `passed = false`, клиент получает 504 `ai_timeout`. Прогресс не меняется, повторная отправка создаёт новую попытку.

### `GET /me/progress`

Ответ 200 — список зданий с числами `passedSteps`, `totalSteps` и id текущих пересдач. Это учебный вид. Уровень и капитал здесь не дублируются.

### `POST /internal/retake`

Заголовок сервиса. Вызывает `crisis` после неверного кризиса.

```json
{ "userId": "uuid", "blockId": "uuid", "sourceId": "uuid" }
```

Блок переводится в `retake_required`, босс модуля локается, если ещё не сдан. В `game` уходит `retake_required` с тем же `sourceId`. Повтор того же `sourceId` ничего не меняет. Ответ 204.

### Админка

Сессия роли `curator` или `admin`. В пилоте это чтение, не заливка банка.

- `GET /admin/students/{userId}/attempts` — попытки тестов и боссов этого игрока, включая тексты ответов. Менять чужой балл и чужой срез нельзя.

---

## 3. Игра

### `GET /me/state`

Сессия. Если строки игрока ещё нет, она создаётся пустой. Ответ 200:

```json
{
  "capital": 0,
  "xp": 0,
  "rankPosition": 12,
  "totalPlayers": 250,
  "buildings": [
    {
      "buildingId": "laboratory",
      "level": 1,
      "passedSteps": 0,
      "totalSteps": 7,
      "mastery": "0 / 7",
      "currentTitle": "Выборка и среднее",
      "nextCondition": "Пройти теорию и тест"
    }
  ]
}
```

`rankPosition` — место по убыванию монет (`capital`). При равенстве выше тот, у кого меньше `userId`. Опыт на место не влияет и уровень здания не меняет. `totalSteps` для лаборатории, завода и маркетинга равен 7 (шесть блоков и босс), для офиса 10, для бухгалтерии 4.

### `GET /leaderboard?limit=20`

Сессия. `limit` от 1 до 50, по умолчанию 20. Элемент: `rankPosition`, `firstName`, `capital`. Фамилия и почта не отдаются. Имя читается `POST /internal/profiles` сервиса `users`: тело `{ "userIds": ["uuid"] }`, ответ `{ "users": [{ "userId", "firstName" }] }`. Заголовок `X-Service-Token`.

`POST /internal/players` запрашивает у `study` `GET /internal/players/{userId}/buildings`. Если `study` не ответил, берутся известные размеры модулей: офис 10, завод, лаборатория и маркетинг по 7, бухгалтерия 4. Уровень при создании — 1.

### `POST /internal/players`

```json
{ "userId": "uuid" }
```

Создаёт игрока и пять зданий. Повтор того же `userId` — 204 без второй строки. `totalSteps` и подписи текущих шагов берутся из `study` в этом же вызове.

### `POST /internal/progress`

```json
{
  "userId": "uuid",
  "reason": "block_passed",
  "sourceId": "uuid",
  "buildingId": "laboratory",
  "passedSteps": 1,
  "totalSteps": 7,
  "currentTitle": "Дисперсия",
  "nextCondition": "Пройти теорию и тест"
}
```

`reason`: `block_passed`, `boss_passed`, `crisis_failed`, `retake_required`.

Начисление:

- `block_passed` — плюс `quiz_capital` и `quiz_xp`;
- `boss_passed` — плюс `boss_capital` и `boss_xp`;
- `crisis_failed` — минус `crisis_penalty`, капитал не ниже 0, опыт не уменьшается;
- `retake_required` — дельты 0, `passedSteps` уменьшается на 1, но не ниже 0.

Уровень пересчитывается и записывается. Повтор той же пары `(reason, sourceId)` возвращает 204 и не двигает баланс. Ответ первого применения — 204.

Для `crisis_failed` тело дополнительно содержит только штрафные поля выше; `passedSteps` при штрафе не меняется, пока следом не придёт отдельный `retake_required`.

---

## 4. Кризисы

### `GET /me/active`

Сессия. Нет открытого кризиса — `{ "event": null }`. Если игроку уже есть что выдавать (есть сданный блок, нет пересдачи, нет черновика), сервис в фоне начинает генерацию и всё равно отвечает `event: null`, пока статус не `open`. Клиент повторяет запрос.

Открытый кризис:

```json
{
  "event": {
    "id": "uuid",
    "prompt": "...",
    "deadlineAt": "2026-07-01T12:00:00Z",
    "options": [
      { "id": "uuid", "body": "..." }
    ]
  }
}
```

Верный ключ не входит. `deadlineAt` — 90 секунд от перевода в `open`, если конфиг не переопределён.

### `POST /events/{eventId}/answer`

```json
{ "optionId": "uuid" }
```

Чужое или уже закрытое событие — 404. Ответ после дедлайна обрабатывается как молчание: 200 с `correct: false`, `timedOut: true`. Вовремя:

```json
{ "correct": true, "timedOut": false }
```

Неверный исход и молчание вызывают `game` (`crisis_failed`, `sourceId` = id события) и `study` (`/internal/retake`, тот же `sourceId`). Верный исход только закрывает событие. Второй ответ — 409 `already_answered`.

---

## 5. ИИ

Только `X-Service-Token`. Ответ модели наружу браузеру не проксируется.

### `POST /internal/personalize`

```json
{
  "userId": "uuid",
  "hobbies": ["sport"],
  "onboardingAnswers": [{ "questionId": 1, "optionIndex": 2 }]
}
```

Ответ 200: `{ "niche": "...", "tone": "..." }`. Повтор для того же игрока заменяет профиль.

### `POST /internal/material`

Срез пустого слота. `kind` — `block` или `boss`.

```json
{
  "userId": "uuid",
  "kind": "block",
  "slotTitle": "Выборка и среднее",
  "disciplineTitle": "Математическая статистика",
  "niche": "...",
  "tone": "..."
}
```

Ответ 200 для блока: `theoryMarkdown` и `questions` из четырёх вариантов, ровно один с `isCorrect: true`. Для босса: `promptMarkdown`. Этот ответ видит только `study`. Таймаут 25 секунд.

### `POST /internal/review`

```json
{
  "userId": "uuid",
  "bossId": "uuid",
  "promptMarkdown": "...",
  "theoryMarkdown": "...",
  "answerText": "...",
  "passScore": 70
}
```

Ответ 200:

```json
{
  "score": 84,
  "verdict": "accepted",
  "reviewText": "...",
  "growthZones": ["..."]
}
```

`verdict` выставляет сервис сравнением `score` и `passScore`, не текст модели. Модель просят вернуть балл, разбор логики, прикладную ценность и зоны роста и не добавлять факты вне условия и теории. Таймаут вызова — 25 секунд, наружу это 504.

### `POST /internal/crisis-draft`

```json
{
  "userId": "uuid",
  "blockId": "uuid",
  "theoryMarkdown": "...",
  "niche": "...",
  "tone": "..."
}
```

Ответ 200: `prompt` и `options` из трёх или четырёх элементов, ровно один с `isCorrect: true`. Этот ответ видит только `crisis-engine`.

---

## 6. Карьера

### `GET /me/card`

Сессия. Если `slug` ещё нет, он создаётся. Ответ 200 — карточка и `slug`.

### `GET /cards/{slug}`

Без сессии. Неизвестный slug — 404. Ответ 200:

```json
{
  "firstName": "Данил",
  "university": "ГУУ",
  "capital": 1200,
  "xp": 340,
  "buildings": [
    { "buildingId": "laboratory", "title": "Лаборатория", "level": 2 }
  ],
  "bosses": [
    { "moduleTitle": "Аналитика и статистика", "passed": false }
  ],
  "disciplines": [
    { "title": "Эконометрика", "passedBlocks": 1, "totalBlocks": 3 }
  ]
}
```

Почты, фамилии, ответов и баллов отдельных попыток нет.

---

## 7. Уведомления

С браузера маршрутов нет. Внутренние вызовы с токеном сервиса, ответ 202, если запись поставлена в `pending`.

### `POST /internal/welcome`

`{ "userId", "email", "firstName" }`. Ключ идемпотентности `welcome:{userId}`.

### `POST /internal/crisis`

`{ "userId", "email", "eventId", "deadlineAt" }`. Ключ `crisis:{eventId}`.

### `POST /internal/digest`

`{ "userId", "email", "utcDate" }`. Ключ `digest:{userId}:{utcDate}`. Если за эти сутки не было сдачи и кризиса, `study` и `crisis` этот вызов не делают.

Тело письма в контракт не входит. Ошибка SMTP оставляет строку `failed` и не возвращается игровому сервису как ошибка исходного действия.
