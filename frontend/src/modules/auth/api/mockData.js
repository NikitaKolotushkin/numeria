import hobbySport from '@/assets/images/auth/hobby-sport.png'
import hobbyCinema from '@/assets/images/auth/hobby-cinema.png'
import hobbyMusic from '@/assets/images/auth/hobby-music.png'
import hobbyAuto from '@/assets/images/auth/hobby-auto.png'
import hobbyCreativity from '@/assets/images/auth/hobby-creativity.png'
import hobbyBooks from '@/assets/images/auth/hobby-books.png'

export const ALLOWED_EMAIL_DOMAIN = 'guu.ru'

export const AUTH_TEMPORARILY_UNAVAILABLE = true
export const AUTH_REGISTER_UNAVAILABLE_MESSAGE = 'Попробуйте позже'
export const AUTH_LOGIN_UNAVAILABLE_MESSAGE = 'Почта или пароль неверны'

export const isAllowedRegistrationEmail = (email) => {
  const normalized = String(email || '').trim().toLowerCase()
  const at = normalized.lastIndexOf('@')
  if (at <= 0) return false

  const local = normalized.slice(0, at)
  const domain = normalized.slice(at + 1)

  return Boolean(local) && !local.includes(' ') && domain === ALLOWED_EMAIL_DOMAIN
}

export const MIN_COURSE = 1
export const MAX_COURSE = 6

export const isAllowedCourse = (course) => {
  const normalized = String(course || '').trim()
  if (!/^\d+$/.test(normalized)) return false

  const value = Number(normalized)
  return value >= MIN_COURSE && value <= MAX_COURSE
}

export const HOBBIES_LIST = [
  { id: 'sport', title: 'Спорт', image: hobbySport },
  { id: 'cinema', title: 'Кино', image: hobbyCinema },
  { id: 'music', title: 'Музыка', image: hobbyMusic },
  { id: 'auto', title: 'Авто', image: hobbyAuto },
  { id: 'creativity', title: 'Творчество', image: hobbyCreativity },
  { id: 'books', title: 'Книги', image: hobbyBooks }
]

export const ONBOARDING_QUIZ = [
  {
    id: 1,
    question: 'Ты открываешь свою первую кофейню. Прошел месяц, выручка растет, но денег на счете почему-то становится всё меньше. Твое первое действие?',
    options: [
      'Все 500 000 рублей сразу стали расходами периода.',
      'Вся сумма стала себестоимостью, так как деньги уже ушли поставщику.',
      '500 000 рублей — это изначальный актив, а 250 000 рублей стали затратами после передачи в производство.',
      'Затраты возникнут только тогда, когда эти товары купят розничные магазины.'
    ],
    correctAnswerIndex: 2
  },
  {
    id: 2,
    question: 'Компании требуется привлечь дополнительное финансирование для закупки нового оборудования. Какой вариант не увеличивает долговую нагрузку?',
    options: [
      'Оформление банковского овердрафта.',
      'Выпуск и продажа дополнительного пакета акций инвесторам.',
      'Облигационный займ на бирже.',
      'Коммерческий кредит от поставщика.'
    ],
    correctAnswerIndex: 1
  },
  {
    id: 3,
    question: 'Постоянные расходы бизнеса составляют 300 000 ₽ в месяц. Маржинальность одного продукта — 1 500 ₽. Сколько единиц продукции нужно продать для выхода в безубыточность?',
    options: [
      '150 единиц',
      '200 единиц',
      '300 единиц',
      '450 единиц'
    ],
    correctAnswerIndex: 1
  },
  {
    id: 4,
    question: 'Какой показатель лучше всего отражает реальную операционную эффективность бизнеса без учета налогов и кредитов?',
    options: [
      'Чистая прибыль (Net Profit)',
      'Выручка (Revenue)',
      'EBITDA (Прибыль до вычета процентов, налогов и амортизации)',
      'Валовая маржа (Gross Margin)'
    ],
    correctAnswerIndex: 2
  },
  {
    id: 5,
    question: 'Внезапный рост инфляции привел к удорожанию сырья на 20%. Что позволит минимизировать потери без потери клиентов?',
    options: [
      'Резко поднять розничную цену на 30%.',
      'Оптимизировать цепочки поставок и повысить внутреннюю производительность.',
      'Полностью остановить продажи до стабилизации цен.',
      'Взять срочный микрозайм под высокий процент.'
    ],
    correctAnswerIndex: 1
  }
]

export const MOCK_USER = {
  id: 'usr_guu_9921',
  email: 'student@guu.ru',
  firstName: 'Данил',
  lastName: 'Зенин',
  fullName: 'Данил Зенин',
  university: 'Государственный университет управления (ГУУ)',
  direction: 'Прикладная информатика',
  course: 3,
  hobbies: ['sport', 'cinema'],
  nickname: 'CyberTycoon',
  avatarUrl: null,
  role: 'STUDENT',
  stats: {
    capital: 250000,
    energy: 85,
    maxEnergy: 100,
    rankPosition: 12,
    totalPlayers: 1480,
    level: 1
  }
}

export const MOCK_AUTH_RESPONSE = {
  accessToken: 'mock_jwt_token_numeria_guu_2026',
  tokenType: 'bearer',
  user: MOCK_USER
}