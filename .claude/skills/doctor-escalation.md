# Skill: Doctor Escalation

> Система эскалации к живым врачам: urgency scoring, handoff protocol, SLA

## Назначение

Реализация системы передачи консультации от AI-агента живому врачу при обнаружении состояний, требующих экспертной оценки. Обеспечение безопасности пациентов через своевременную эскалацию.

---

## Использование

| Агент | Применение |
|-------|-----------|
| AI-Agents | Встраивание escalation nodes в LangGraph |
| Coder | Реализация escalation service |
| Medical-Domain | Определение триггеров и SLA |
| QA | Тестирование escalation flow end-to-end |

---

## Уровни срочности (Urgency)

```yaml
Level 1 — Информационный:
  description: "AI справился, но рекомендует консультацию врача"
  examples:
    - Общие вопросы о здоровье с рекомендацией профосмотра
    - Запрос второго мнения по результатам
  SLA: "48 часов (рабочие дни)"
  notification: "В очередь к врачу"
  auto_trigger: false

Level 2 — Плановый:
  description: "Требуется врачебная консультация в плановом порядке"
  examples:
    - Хронические заболевания с контролируемыми показателями
    - Плановое обследование по результатам анализов
    - Коррекция терапии
  SLA: "24 часа (рабочие дни)"
  notification: "Уведомление врачу"
  auto_trigger: false

Level 3 — Приоритетный:
  description: "Требуется врачебная оценка в ближайшее время"
  examples:
    - Значительные отклонения в анализах (не критические)
    - Неконтролируемая гипертензия (150-180 мм рт.ст.)
    - Подозрение на инфекционное заболевание
    - Неясный диагноз с умеренной тревогой
  SLA: "4 часа"
  notification: "Push-уведомление врачу + пациенту"
  auto_trigger: true (при определённых паттернах)

Level 4 — Срочный:
  description: "Требуется немедленная врачебная оценка"
  examples:
    - Неконтролируемая гипертензия (>180/120)
    - Критические значения анализов
    - Подозрение на тромбоз, аппендицит
    - Впервые выявленные опухолевые образования
    - Дебют диабета с высокими сахарами
  SLA: "1 час"
  notification: "Звонок/SMS врачу + предупреждение пациенту"
  auto_trigger: true (по red flags из 05-medical-safety.md)

Level 5 — Экстренный:
  description: "Угроза жизни — вызов скорой помощи"
  examples:
    - Острая боль в груди + одышка
    - Инсульт (FAST-тест положительный)
    - Анафилаксия
    - Суицидальные намерения
    - Обильное кровотечение
    - Потеря сознания
  SLA: "НЕМЕДЛЕННО"
  notification: |
    1. Пациенту: "Вызовите скорую: 103 (112)"
    2. Врачу: экстренное уведомление
    3. Системе: создать incident
  auto_trigger: true (ВСЕГДА при red flags level 5)
```

---

## Автоматические триггеры

### Red Flag триггеры (Level 5 — экстренный)

```yaml
Источник: rules/05-medical-safety.md → red_flags_immediate

Триггеры:
  cardiac:
    symptoms: [острая_боль_в_груди, иррадиация_в_левую_руку, одышка_в_покое]
    action: "Вызовите скорую 103"

  neurological:
    symptoms: [внезапная_слабость_одной_стороны, потеря_зрения, громоподобная_головная_боль]
    action: "Вызовите скорую 103 — подозрение на инсульт"

  anaphylaxis:
    symptoms: [отёк_горла, затруднённое_дыхание, сыпь_и_падение_давления]
    action: "Вызовите скорую 103 — анафилаксия"

  psychiatric:
    symptoms: [суицидальные_мысли, суицидальные_намерения]
    action: "Вызовите скорую 112. Телефон доверия: 8-800-2000-122"

  pediatric:
    symptoms: [лихорадка_39_до_3_месяцев, отказ_от_еды_грудной, судороги_у_ребёнка]
    action: "Вызовите детскую скорую 103"

  obstetric:
    symptoms: [кровотечение_при_беременности, отхождение_вод, снижение_шевелений]
    action: "Вызовите скорую 103"
```

### Триггеры по анализам (Level 4)

```yaml
Критические значения:
  glucose: {low: 2.8, high: 30.0, unit: "ммоль/л"}
  potassium: {low: 2.5, high: 6.5, unit: "ммоль/л"}
  sodium: {low: 120, high: 160, unit: "ммоль/л"}
  hemoglobin: {low: 60, high: 200, unit: "г/л"}
  platelets: {low: 20, high: 1000, unit: "×10⁹/л"}
  creatinine: {high: 800, unit: "мкмоль/л"}

При критическом значении:
  urgency: 4
  message: "Критическое значение [показатель]: [значение]. Требуется срочная консультация врача."
```

### Триггеры по imaging (Level 4)

```yaml
При обнаружении:
  melanoma_suspicion: {confidence: ">0.3", urgency: 4}
  pneumothorax: {confidence: ">0.5", urgency: 4}
  mass_detected: {confidence: ">0.5", urgency: 4}
  cardiomegaly: {confidence: ">0.7", urgency: 3}
```

---

## Handoff Protocol

### Процесс передачи

```yaml
1. Trigger Detection:
   - AI-агент обнаруживает триггер эскалации
   - Определяет urgency level
   - Логирует: doctor_escalation_triggered

2. Patient Notification:
   - Level 5: "🚨 Вызовите скорую: 103/112"
   - Level 4: "⚠️ Ваша консультация передаётся врачу для срочной оценки"
   - Level 3: "ℹ️ Рекомендуем консультацию врача. Мы передали ваш случай."
   - Level 1-2: "Рекомендуем обратиться к врачу для уточнения"

3. Case Assembly:
   - Собрать полный контекст консультации:
     - Жалобы пациента (исходный текст)
     - Анализ AI: симптомы, дифференциальный диагноз
     - Red flags (если обнаружены)
     - Результаты анализов / imaging (если были)
     - Текущие лекарства (если известны)
     - Анамнез (если собран)
   - Сформировать case summary для врача

4. Doctor Matching:
   - По специализации (из differential diagnosis)
   - По доступности (online / schedule)
   - По нагрузке (наименее загруженный)
   - Fallback: дежурный терапевт

5. Doctor Notification:
   - Push notification с case summary
   - Urgency badge
   - Quick actions: Accept / Redirect / Decline

6. Handoff:
   - Врач принимает кейс
   - Получает полный контекст
   - Может общаться с пациентом через бота
   - AI-агент переходит в режим "ассистент врача"
   - Логирует: doctor_escalation_accepted

7. Resolution:
   - Врач завершает консультацию
   - Записывает рекомендации
   - AI возвращается в нормальный режим
   - Логирует: doctor_escalation_completed
```

### Case Summary для врача

```yaml
Формат:
  patient:
    age: int
    gender: str
    known_conditions: list[str]
    current_medications: list[str]

  escalation:
    urgency: int (1-5)
    reason: str
    red_flags: list[str]
    triggered_by: str (ai_agent / manual)

  ai_assessment:
    symptoms: list[str]
    differential_diagnosis:
      - diagnosis: str
        icd10: str
        confidence: float
    recommended_tests: list[str]

  conversation_summary: str  # Краткое резюме диалога с пациентом

  attachments:
    lab_results: list  # Если были загружены
    images: list       # Если были загружены
```

---

## Fallback Chain

```yaml
Если врач не принял кейс в рамках SLA:

Level 5 (экстренный):
  1. Повторное уведомление всем онлайн врачам (через 2 мин)
  2. SMS/звонок дежурному врачу (через 5 мин)
  3. Уведомление администратору системы (через 10 мин)
  4. Пациенту: повторное сообщение "Вызовите скорую 103"

Level 4 (срочный):
  1. Расширить пул врачей (смежные специальности) (через 30 мин)
  2. Уведомление дежурному терапевту (через 45 мин)
  3. Уведомление администратору (через 1 час)
  4. Пациенту: "Рекомендуем обратиться в поликлинику/приёмный покой"

Level 3 (приоритетный):
  1. Расширить пул (через 2 часа)
  2. Перевести в очередь (через 4 часа)
  3. Пациенту: "Врач ответит в течение [нового SLA]"

Level 1-2 (плановый):
  1. Поставить в очередь
  2. Уведомить при появлении свободного врача
```

---

## Режим "AI-ассистент врача"

```yaml
Когда врач принял эскалацию:
  AI может:
    - Предоставлять справочную информацию по запросу врача
    - Показывать историю консультации
    - Выполнять поиск в медицинских базах
    - Помогать с кодированием (МКБ-10)
    - Форматировать рекомендации

  AI НЕ может:
    - Вмешиваться в рекомендации врача
    - Оспаривать решение врача
    - Самостоятельно общаться с пациентом (пока врач ведёт кейс)
    - Закрывать кейс без врача
```

---

## Метрики эскалации

```yaml
SLA Compliance:
  - % кейсов принятых в рамках SLA по каждому уровню
  - Среднее время до принятия (per urgency level)
  - % кейсов, потребовавших fallback

Quality:
  - % ложных эскалаций (false positive)
  - % пропущенных эскалаций (false negative) → КРИТИЧЕСКАЯ метрика, цель: 0%
  - Удовлетворённость пациента после эскалации
  - Удовлетворённость врача качеством case summary

Volume:
  - Количество эскалаций в день/неделю
  - Распределение по urgency levels
  - Распределение по специализациям
  - Пиковые часы
```

---

## Тестирование

```yaml
Обязательные тесты:

  Unit Tests:
    - Каждый red flag триггер корректно определяется
    - Urgency level корректно рассчитывается
    - Case summary формируется полностью

  Integration Tests:
    - Notification delivery (push, SMS)
    - Doctor matching алгоритм
    - Fallback chain активация

  E2E Tests:
    - Полный flow: trigger → notification → accept → resolve
    - Timeout scenarios (SLA expired)
    - Multiple concurrent escalations

  Safety Tests:
    - False negative rate < 5% для red flags
    - Level 5 triggers ВСЕГДА работают
    - Пациент ВСЕГДА получает emergency message при Level 5
```

---

## Ссылки

- **Red flags:** `.claude/rules/05-medical-safety.md`
- **AI-агенты:** `.claude/agents/ai-agents.md`
- **Medical-Domain:** `.claude/agents/medical-domain.md`
- **Clinical Reasoning:** `.claude/skills/clinical-reasoning.md`
- **Логирование:** `.claude/rules/04-logging.md`

---

*Спецификация навыка v1.0 | Aibolit AI — Claude Code Agent System*
