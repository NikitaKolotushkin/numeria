# Схема баз пилота «Нумерия»

Границы сервисов: `docs/spec-backend.md`. Тела HTTP: `docs/spec-backend-api.md`. Продукт: `docs/spec-product.md`.

Таблицы `numeria_users`, `numeria_study` и `numeria_game` уже создаются миграциями этих сервисов. Сервис `ai` запущен, но базу `numeria_ai` не использует: ниша, тон и access token живут в памяти процесса. Базы `numeria_crisis`, `numeria_career`, `numeria_ai` и `numeria_notifications` в compose названы, таблиц в них ещё нет. Ниже описан полный пилотный состав, включая ещё не собранные базы.

Семь баз на одном Postgres 15. Внешних ключей между базами нет: чужой идентификатор хранится как `uuid` или `text` без `REFERENCES`. Время — `timestamptz`. Деньги и опыт — `integer`. Первичные ключи строк — `uuid`, кроме справочника модулей и дисциплин: у них стабильные текстовые id.

Миграции — Alembic, по одной цепочке на сервис.

---

## 1. Решения, из которых собрана схема

1. Каталог учёбы и попытки живут только в `numeria_study`. Капитал и уровень — только в `numeria_game`. Повтор одной и той же попытки не начисляет награду второй раз: в журнале `game.ledger` уникальна пара `(reason, source_id)`.
2. Верный вариант теста и верный вариант кризиса не лежат в таблице, которую сервис отдаёт студенту целиком. Они есть в базе, маршруты студента их не выбирают.
3. Уровень здания хранится уже посчитанным, чтобы карта читалась одним запросом. Пишется заново на каждое событие прогресса по формуле из продуктовой спеки.
4. `career` не копирует прогресс. Единственная её таблица — публичный код карточки.
5. Журнал `ai` не хранит текст ответа студента, только хэш. Сам текст остаётся в `study.boss_attempts`.
6. Игровая строка создаётся в момент регистрации, с капиталом 0, опытом 0 и пятью зданиями 1 уровня. До этого на карте гостя действуют экранные «Линад» и 1600, в базу они не пишутся.

Справочник `content_binding.v1` зашит сидами `study`, не отдельной базой.

| module_id | building_id | title |
| --- | --- | --- |
| `foundations` | `office` | Основы и введение |
| `production` | `factory` | Производство |
| `analytics` | `laboratory` | Аналитика и статистика |
| `foreign` | `marketing` | Международные связи |
| `books` | `accounting` | Бухгалтерский учет |

| discipline_id | module_id | title |
| --- | --- | --- |
| `intro_theory` | `foundations` | Введение в экономическую теорию |
| `management` | `foundations` | Менеджмент |
| `macro` | `foundations` | Макроэкономика |
| `enterprise` | `production` | Экономика предприятия |
| `micro` | `production` | Микроэкономика |
| `math_stat` | `analytics` | Математическая статистика |
| `econometrics` | `analytics` | Эконометрика |
| `marketing` | `foreign` | Маркетинг |
| `international` | `foreign` | Международная экономика |
| `accounting` | `books` | Бухгалтерский учет |

Порядок внутри модуля — `sort_order`, начиная с 0. У каждой дисциплины в пилоте три блока. Заголовок пустого блока — «{название дисциплины}, блок N», где N начинается с 1. Заголовок босса — «Битва с боссом». Текста теории в сиде нет.

---

## 2. `numeria_users`

```text
users
  id              uuid pk
  email           text unique not null
  password_hash   text not null
  first_name      text not null
  last_name       text not null
  university      text not null
  direction       text not null
  course          smallint not null check (course between 1 and 6)
  role            text not null default 'student'
                  check (role in ('student', 'curator', 'admin'))
  created_at      timestamptz not null
  updated_at      timestamptz not null

consents
  user_id            uuid pk references users
  personal_data_at   timestamptz not null
  terms_at           timestamptz not null
  ai_assessment_at   timestamptz not null
  policy_version     text not null

hobbies
  user_id    uuid references users
  hobby_id   text not null
             check (hobby_id in ('sport','cinema','music','auto','creativity','books'))
  primary key (user_id, hobby_id)

onboarding_answers
  user_id       uuid references users
  question_id   smallint not null check (question_id between 1 and 5)
  option_index  smallint not null check (option_index between 0 and 3)
  primary key (user_id, question_id)

refresh_tokens
  id           uuid pk
  user_id      uuid not null references users
  token_hash   text not null unique
  expires_at   timestamptz not null
  revoked_at   timestamptz
  created_at   timestamptz not null

access_denylist
  jti         uuid pk
  expires_at  timestamptz not null
```

Индекс `access_denylist (expires_at)` нужен для чистки просроченных `jti`. Пароль хранится только как хэш argon2id. Почта перед записью обрезается и приводится к нижнему регистру, поэтому отдельное расширение `citext` не нужно. Онбординговые пять ответов не связаны со слотами `study`.

---

## 3. `numeria_study`

```text
modules
  id           text pk
  building_id  text not null unique
  title        text not null
  sort_order   int not null unique

disciplines
  id           text pk
  module_id    text not null references modules
  title        text not null
  sort_order   int not null
  unique (module_id, sort_order)

blocks
  id               uuid pk
  discipline_id    text not null references disciplines
  title            text not null
  sort_order       int not null
  unique (discipline_id, sort_order)

block_snapshots
  user_id          uuid not null
  block_id         uuid not null references blocks
  theory_markdown  text not null
  created_at       timestamptz not null
  primary key (user_id, block_id)

questions
  id           uuid pk
  user_id      uuid not null
  block_id     uuid not null references blocks
  prompt       text not null
  sort_order   int not null
  unique (user_id, block_id, sort_order)

options
  id           uuid pk
  question_id  uuid not null references questions
  body         text not null
  is_correct   boolean not null
  sort_order   int not null
  unique (question_id, sort_order)

bosses
  id           uuid pk
  module_id    text not null unique references modules
  title        text not null
  pass_score   int not null default 70 check (pass_score between 0 and 100)

boss_snapshots
  user_id          uuid not null
  boss_id          uuid not null references bosses
  prompt_markdown  text not null
  created_at       timestamptz not null
  primary key (user_id, boss_id)

quiz_attempts
  id             uuid pk
  user_id        uuid not null
  block_id       uuid not null references blocks
  correct_count  int not null
  total_count    int not null
  score          int not null check (score between 0 and 100)
  passed         boolean not null
  created_at     timestamptz not null

quiz_attempt_answers
  attempt_id   uuid references quiz_attempts
  question_id  uuid not null references questions
  option_id    uuid not null references options
  primary key (attempt_id, question_id)

boss_attempts
  id            uuid pk
  user_id       uuid not null
  boss_id       uuid not null references bosses
  answer_text   text not null
  score         int check (score between 0 and 100)
  verdict       text check (verdict in ('accepted', 'retry', 'error'))
  review_text   text
  growth_zones  jsonb not null default '[]'
  passed        boolean
  created_at    timestamptz not null

block_progress
  user_id            uuid not null
  block_id           uuid not null references blocks
  status             text not null
                     check (status in ('locked', 'available', 'passed', 'retake_required'))
  passed_attempt_id  uuid references quiz_attempts
  updated_at         timestamptz not null
  primary key (user_id, block_id)

boss_progress
  user_id            uuid not null
  boss_id            uuid not null references bosses
  status             text not null
                     check (status in ('locked', 'available', 'passed'))
  passed_attempt_id  uuid references boss_attempts
  updated_at         timestamptz not null
  primary key (user_id, boss_id)
```

Частичный уникальный индекс: один верный вариант на вопрос.

```text
unique (question_id) where is_correct
```

Индексы попыток: `(user_id, block_id, created_at desc)` и `(user_id, boss_id, created_at desc)`.

Повтор `POST /internal/retake` с тем же `sourceId` не меняет прогресс. Для этого хранится пара, которой нет в остальных таблицах:

```text
applied_commands
  reason      text not null
  source_id   uuid not null
  primary key (reason, source_id)
```

Строки `block_progress` создаются при регистрации на все слоты блоков: первый блок каждого модуля `available`, остальные `locked`. Срез теории и вопросов появляется отдельно, при первом открытии слота, и к регистрации не привязан. Вопрос из чужого среза в попытку не принимается.

Порядок шагов здания: дисциплины по `sort_order`, внутри них блоки по `sort_order`, босс после последнего блока. Следующий блок становится `available` только когда предыдущий `passed` и ни один блок модуля не в `retake_required`. Босс `available`, когда все блоки модуля `passed`. Пересдача ставит этот блок в `retake_required` и босса обратно в `locked`, если босс ещё не `passed`. Сданный босс не отзывается пересдачей блока.

---

## 4. `numeria_game`

```text
players
  user_id     uuid pk
  capital     int not null default 0 check (capital >= 0)
  xp          int not null default 0 check (xp >= 0)
  updated_at  timestamptz not null

buildings
  user_id       uuid not null references players
  building_id   text not null
                check (building_id in ('office','factory','laboratory','marketing','accounting'))
  level         int not null default 1 check (level between 1 and 5)
  passed_steps  int not null default 0 check (passed_steps >= 0)
  total_steps   int not null check (total_steps > 0)
  current_title text not null
  next_condition text not null
  primary key (user_id, building_id)

ledger
  id             uuid pk
  user_id        uuid not null references players
  reason         text not null
                 check (reason in ('block_passed', 'boss_passed', 'crisis_failed', 'retake_required'))
  source_id      uuid not null
  capital_delta  int not null
  xp_delta       int not null default 0
  created_at     timestamptz not null
  unique (reason, source_id)

balance_config
  key    text pk
  value  int not null check (value >= 0)
```

Сиды `balance_config`, стартовый баланс альфа-теста, не часть формулы уровня: `quiz_capital = 100`, `quiz_xp = 10`, `boss_capital = 400`, `boss_xp = 30`, `crisis_penalty = 50`.

`retake_required` пишет в журнал строку с нулевыми дельтами. Её `source_id` — id кризиса, который потребовал пересдачу, а не id старой попытки теста. Повтор того же кризиса не снимает шаг второй раз. Новая сдача после пересдачи приходит как `block_passed` с новым `source_id` попытки и снова начисляет награду. Уровень пересчитывается в обоих случаях: при пересдаче `passed_steps` уменьшается на 1, но не ниже 0.

Индекс рейтинга: `players (capital desc, user_id)`. Место определяется монетами. При равном капитале выше тот, у кого меньше `user_id`.

`current_title` и `next_condition` денормализованы из `study` в момент события, чтобы плашка здания не ходила в учёбу на каждый кадр карты. Источник истины шага всё равно `study.block_progress`.

---

## 5. `numeria_crisis`

```text
events
  id           uuid pk
  user_id      uuid not null
  block_id     uuid not null
  prompt       text not null
  status       text not null
               check (status in ('draft', 'open', 'resolved_ok', 'resolved_fail'))
  deadline_at  timestamptz
  created_at   timestamptz not null
  resolved_at  timestamptz

options
  id          uuid pk
  event_id    uuid not null references events
  body        text not null
  is_correct  boolean not null
  sort_order  int not null
  unique (event_id, sort_order)

answers
  id          uuid pk
  event_id    uuid not null unique references events
  option_id   uuid references options
  is_correct  boolean not null
  timed_out   boolean not null default false
  created_at  timestamptz not null
```

Один незакрытый кризис на игрока:

```text
unique (user_id) where status in ('draft', 'open')
```

Один верный вариант на событие:

```text
unique (event_id) where is_correct
```

`draft` не отдаётся клиенту. В `open` он переходит только когда записаны текст и варианты. `deadline_at` ставится в этот момент. Ответ после дедлайна пишется как `timed_out = true`, `option_id = null`, `is_correct = false`, статус `resolved_fail`.

---

## 6. `numeria_ai`

```text
setting_profiles
  user_id     uuid pk
  niche       text not null
  tone        text not null
  updated_at  timestamptz not null

request_log
  id             uuid pk
  user_id        uuid not null
  kind           text not null
                 check (kind in ('personalize', 'material', 'review', 'crisis_draft'))
  model          text not null
  answer_sha256  text
  score          int
  latency_ms     int not null
  created_at     timestamptz not null
```

Индекс `(user_id, kind, created_at desc)`.

Таблица ещё не создаётся миграцией. Вид `material` зарезервирован под генерацию среза. Пока журнал не пишется, профиль сеттинга перезапуск контейнера не переживает.

---

## 7. `numeria_career`

```text
public_slugs
  user_id  uuid pk
  slug     text not null unique
```

`slug` — непрозрачная строка, не почта и не последовательный номер. Карточка каждый раз собирается из `users`, `study` и `game`.

---

## 8. `numeria_notifications`

```text
deliveries
  id           uuid pk
  user_id      uuid not null
  kind         text not null
               check (kind in ('welcome', 'crisis', 'digest'))
  dedupe_key   text not null unique
  status       text not null
               check (status in ('pending', 'sent', 'failed'))
  attempts     int not null default 0
  last_error   text
  created_at   timestamptz not null
  sent_at      timestamptz
```

Ключ дайджеста — `digest:{user_id}:{utc_date}`. Ключ приветствия — `welcome:{user_id}`. Ключ кризиса — `crisis:{event_id}`. Повторная вставка с тем же ключом не создаёт второе письмо.
