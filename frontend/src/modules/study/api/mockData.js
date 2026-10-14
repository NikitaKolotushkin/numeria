export function caseTitle(buildingId) {
  return BUILDING_CASES[buildingId]?.title || ''
}

export const BUILDING_CASES = {
  laboratory: {
    id: 'laboratory-elasticity',
    buildingId: 'laboratory',
    type: 'quiz',
    title: 'Эластичность цены',
    questions: [
      {
        id: 'lab-1',
        question: 'Цена выросла на 10%, спрос упал на 20%. Какой это спрос?',
        options: [
          'Неэластичный',
          'Эластичный',
          'С единичной эластичностью',
          'Абсолютно неэластичный'
        ],
        correctAnswerIndex: 1
      },
      {
        id: 'lab-2',
        question: 'При эластичном спросе рост цены чаще всего приводит к тому, что выручка...',
        options: ['Растет', 'Падает', 'Не меняется', 'Становится равной себестоимости'],
        correctAnswerIndex: 1
      },
      {
        id: 'lab-3',
        question: 'Товары первой необходимости обычно имеют спрос...',
        options: ['Эластичный', 'Неэластичный', 'Абсолютно эластичный', 'Сезонный'],
        correctAnswerIndex: 1
      }
    ]
  },
  factory: {
    id: 'factory-breakeven',
    buildingId: 'factory',
    type: 'quiz',
    title: 'Точка безубыточности',
    questions: [
      {
        id: 'factory-1',
        question: 'Постоянные расходы 300 000 ₽, маржа с единицы 1 500 ₽. Точка безубыточности?',
        options: ['150 единиц', '200 единиц', '300 единиц', '450 единиц'],
        correctAnswerIndex: 1
      },
      {
        id: 'factory-2',
        question: 'В точке безубыточности прибыль равна...',
        options: ['Выручке', 'Нулю', 'Постоянным расходам', 'Марже одной единицы'],
        correctAnswerIndex: 1
      },
      {
        id: 'factory-3',
        question: 'Маржинальный доход единицы — это...',
        options: [
          'Цена минус переменные затраты',
          'Выручка минус налог',
          'Сумма постоянных расходов',
          'Чистая прибыль за месяц'
        ],
        correctAnswerIndex: 0
      }
    ]
  },
  office: {
    id: 'office-delegation',
    buildingId: 'office',
    type: 'quiz',
    title: 'Делегирование',
    questions: [
      {
        id: 'office-1',
        question: 'Делегирование — это передача...',
        options: [
          'Поручения без права решать',
          'Полномочий вместе с задачей',
          'Всех решений компании',
          'Личной ответственности руководителя'
        ],
        correctAnswerIndex: 1
      },
      {
        id: 'office-2',
        question: 'После делегирования ответственность за итог перед компанией остается у...',
        options: ['Только у сотрудника', 'Руководителя, который делегировал', 'Клиента', 'Бухгалтерии'],
        correctAnswerIndex: 1
      },
      {
        id: 'office-3',
        question: 'Что передают сотруднику вместе с задачей?',
        options: [
          'Полномочия принять решение в рамках задачи',
          'Доступ ко всем счетам компании',
          'Весь бюджет фирмы',
          'Обязанности остальных отделов'
        ],
        correctAnswerIndex: 0
      }
    ]
  },
  accounting: {
    id: 'accounting-chart',
    buildingId: 'accounting',
    type: 'quiz',
    title: 'План счетов',
    questions: [
      {
        id: 'accounting-1',
        question: 'План счетов — это...',
        options: [
          'Систематизированный перечень счетов компании',
          'График отпусков',
          'Прайс для клиентов',
          'Налоговая декларация'
        ],
        correctAnswerIndex: 0
      },
      {
        id: 'accounting-2',
        question: 'В двойной записи сумма дебета равна сумме...',
        options: ['Выручки', 'Кредита', 'Налога', 'Скидки'],
        correctAnswerIndex: 1
      },
      {
        id: 'accounting-3',
        question: 'Увеличение актива обычно отражается по...',
        options: ['Дебету', 'Кредиту', 'Забалансовому счету', 'Резерву'],
        correctAnswerIndex: 0
      }
    ]
  },
  marketing: {
    id: 'marketing-positioning',
    buildingId: 'marketing',
    type: 'quiz',
    title: 'Позиционирование',
    questions: [
      {
        id: 'marketing-1',
        question: 'Позиционирование — это...',
        options: [
          'Место бренда в восприятии клиента рядом с конкурентами',
          'Размер скидки на полке',
          'Адрес офиса',
          'Число публикаций в неделю'
        ],
        correctAnswerIndex: 0
      },
      {
        id: 'marketing-2',
        question: 'Перед выбором позиции сначала определяют...',
        options: ['Целевую аудиторию', 'Цвет логотипа', 'Штат компании', 'Курс валюты'],
        correctAnswerIndex: 0
      },
      {
        id: 'marketing-3',
        question: 'Рабочее позиционирование дает клиенту...',
        options: [
          'Понятное отличие от конкурентов',
          'Самую низкую цену любой ценой',
          'Отказ от аудитории',
          'Копию лидера рынка'
        ],
        correctAnswerIndex: 0
      }
    ]
  }
}
