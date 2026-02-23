# 04 - Требования к логированию в коде

> Обязательные правила логирования при реализации и модификации кода

## Принцип

**Каждое значимое действие в системе должно быть залогировано.** Логи обеспечивают прозрачность, отладку и аудит. Агенты Coder, Dev, Review и QA обязаны следить за соблюдением этих правил.

---

## Обязательное логирование

### 1. Действия с записью в базу данных

**Что:** Любые CREATE, UPDATE, DELETE операции через ORM.

```python
# После создания
from core.audit import AuditLogService

payment = Payment.objects.create(user=user, amount=amount)
AuditLogService.log_db_create(payment, actor=user, request=request)

# После обновления (сохранить старые значения ДО изменения)
old_values = {'status': order.status, 'amount': str(order.amount)}
order.status = 'paid'
order.save()
AuditLogService.log_db_update(order, old_values, actor=user, request=request)

# После удаления (ДО вызова .delete())
AuditLogService.log_db_delete(instance, actor=user, request=request)
instance.delete()
```

**Правила:**
- Логировать **изменяемые значения** (old → new)
- Защищённые поля (`password`, `token`, `secret`, `api_key` и др.) маскируются автоматически
- actor = текущий пользователь или 'system'

---

### 2. События в event-архитектуре

**Что:** Любые сигналы, events, notifications, callbacks.

```python
AuditLogService.log_event(
    'payment_completed',
    data={'payment_id': payment.id, 'amount': str(payment.amount), 'method': payment.method},
    actor=user,
    request=request,
)

AuditLogService.log_event(
    'notification_sent',
    data={'template': template.name, 'channel': 'telegram', 'recipient_id': user.id},
)
```

**Правила:**
- Указывать **имя события** и **значения** (кроме защищённых)
- Если событие инициировано пользователем — указывать actor

---

### 3. Scheduled/Cron задачи

**Что:** Начало и конец каждой периодической задачи.

```python
from core.decorators import audit_task

@audit_task('channel_post_scheduler')
def run_scheduled_scenarios():
    # ... логика задачи ...
    pass
```

Или вручную:
```python
AuditLogService.log_task_start('jwt_cleanup')
try:
    # ... логика ...
    AuditLogService.log_task_end('jwt_cleanup', 'success', {'cleaned': count})
except Exception as e:
    AuditLogService.log_task_end('jwt_cleanup', 'error', {'error': str(e)})
    raise
```

**Правила:**
- Использовать декоратор `@audit_task` для всех задач APScheduler
- Логировать start + end с результатом (success/error)
- Указывать количество обработанных элементов или метрики

---

### 4. Бизнес-логика

**Что:** Значимые бизнес-события и изменения.

```python
AuditLogService.log_business(
    'referral_bonus_credited',
    f"Начислен реферальный бонус {bonus_amount}₽ пользователю {user.username}",
    data={'user_id': user.id, 'bonus': str(bonus_amount), 'referrer_id': referrer.id},
    actor=user,
    request=request,
)

AuditLogService.log_business(
    'subscription_activated',
    f"Активирована подписка {plan.name} для {user.username}",
    data={'plan_id': plan.id, 'user_id': user.id, 'period': plan.period},
    actor=user,
)
```

**Примеры обязательного логирования:**
- Регистрация/авторизация пользователя
- Платежи и финансовые операции
- Начисление бонусов, реферальные события
- Смена тарифа/подписки
- Модерация контента
- Блокировка/разблокировка пользователя
- Генерация AI-контента (запрос → результат)
- Публикация контента

---

### 5. Медицинские события (Aibolit AI)

**Что:** Все медицинские действия AI-системы. Требования определены в `rules/05-medical-safety.md`.

```python
# AI-консультация
AuditLogService.log_medical(
    'ai_consultation_started',
    data={
        'patient_id': patient.id,
        'agent_code': 'cardiologist',
        'symptoms_count': len(symptoms),
        'session_id': session.id,
    },
    actor=patient,
    request=request,
)

# Предположительный диагноз
AuditLogService.log_medical(
    'ai_diagnosis_suggested',
    data={
        'consultation_id': consultation.id,
        'icd10_codes': ['I10', 'I25.1'],
        'confidence_levels': [0.75, 0.45],
        'differential_count': 3,
    },
    actor='system',
)

# Эскалация к врачу
AuditLogService.log_medical(
    'doctor_escalation_triggered',
    data={
        'consultation_id': consultation.id,
        'reason': 'red_flag_chest_pain',
        'urgency_level': 5,
        'red_flag_type': 'cardiac',
    },
    actor='system',
)

# Анализ медицинского изображения
AuditLogService.log_medical(
    'ai_imaging_analysis_completed',
    data={
        'consultation_id': consultation.id,
        'modality': 'chest_xray',
        'model_used': 'torchxrayvision',
        'findings_count': 2,
        'max_confidence': 0.82,
    },
    actor='system',
)

# Проверка взаимодействия лекарств
AuditLogService.log_medical(
    'drug_interaction_detected',
    data={
        'consultation_id': consultation.id,
        'drug_pair': ['warfarin', 'aspirin'],
        'severity': 'major',
        'source': 'drugbank',
    },
    actor='system',
)

# Тревога по витальным показателям
AuditLogService.log_medical(
    'vital_alert_triggered',
    data={
        'patient_id': patient.id,
        'parameter': 'blood_pressure_systolic',
        'value': 185,
        'threshold': 180,
        'alert_type': 'critical_high',
    },
    actor='system',
)
```

**Полный список медицинских событий:**

```yaml
Консультации:
  - ai_consultation_started
  - ai_consultation_completed
  - ai_followup_scheduled

Диагностика:
  - ai_symptoms_analyzed
  - ai_diagnosis_suggested
  - ai_diagnosis_ruled_out
  - ai_lab_analysis_completed
  - ai_imaging_analysis_completed

Лечение:
  - ai_treatment_recommended
  - ai_drug_mentioned
  - drug_interaction_detected
  - contraindication_detected

Безопасность:
  - red_flag_detected
  - doctor_escalation_triggered
  - doctor_escalation_accepted
  - doctor_escalation_completed
  - medical_disclaimer_shown

Мониторинг:
  - vital_recorded
  - vital_alert_triggered
  - medication_reminder_sent
  - medication_taken_confirmed
  - daily_survey_completed

Врачебный модуль:
  - doctor_login
  - doctor_case_reviewed
  - doctor_recommendation_sent
```

**Правила медицинского логирования:**
- Уровень `INFO` для штатных медицинских событий
- Уровень `WARNING` для red flags и обнаруженных взаимодействий лекарств
- Уровень `CRITICAL` для неработающей эскалации и критических значений витальных
- Медицинские данные (диагнозы, анализы) хранятся **только в зашифрованном виде**
- Все медицинские логи имеют увеличенный retention: **5 лет** (вместо 90 дней)
- Запрещено логировать полные результаты анализов в открытом виде — только summary

---

## Защищённые поля (автоматическое маскирование)

Значения следующих полей автоматически заменяются на `***MASKED***`:

```yaml
- password
- token
- secret
- api_key
- private_key
- card_number
- cvv
- ssn
- access_token
- refresh_token
- yookassa_secret
- bot_token
# Медицинские защищённые поля (Aibolit AI)
- diagnosis_code
- diagnosis_text
- lab_results
- imaging_findings
- medication_list
- allergy_info
- genetic_data
- psychiatric_notes
- reproductive_data
- hiv_status
- substance_abuse
```

Конфигурация: `settings.AUDIT_MASKED_FIELDS`

---

## Уровни логирования

| Уровень | Когда использовать |
|---------|-------------------|
| `DEBUG` | Отладочная информация (не в production) |
| `INFO` | Штатные операции (CRUD, events, tasks) — **по умолчанию** |
| `WARNING` | Нештатные ситуации (retry, fallback, deprecated) |
| `ERROR` | Ошибки, которые не прерывают работу |
| `CRITICAL` | Критические сбои (потеря данных, недоступность) |

---

## Файловые логи и ротация

### Файлы

| Файл | Содержимое |
|------|-----------|
| `logs/app.log` | Общий лог приложения |
| `logs/audit.log` | Аудит-лог (все AuditLogService записи) |
| `logs/scheduler.log` | Логи scheduled-задач |
| `logs/errors.log` | Только ERROR и CRITICAL |
| `logs/medical.log` | Медицинские события (encrypted, retention 5 лет) |
| `logs/escalation.log` | Эскалации к врачам (retention 5 лет) |

### Ротация

```yaml
Файлы:
  max_size: 10 MB (настраивается: LOG_MAX_BYTES)
  backup_count: 5 (настраивается: LOG_BACKUP_COUNT)

БД (AuditLog):
  retention: 90 дней (настраивается: AUDIT_LOG_RETENTION_DAYS)
  cleanup: ежедневно в 03:00 через APScheduler
```

---

## Просмотр в Admin

Модель `AuditLog` доступна в Django Admin (`/admin/core/auditlog/`):
- **Фильтры:** уровень, действие, категория, тип сущности, тип актора
- **Поиск:** по сообщению, типу/ID сущности, имени актора, request_id
- **Иерархия дат:** по timestamp
- **Read-only:** логи нельзя редактировать, удалять может только superuser

---

## Обязанности агентов

### Coder Agent

```yaml
При реализации ЛЮБОГО кода:
  - Добавлять AuditLogService вызовы во все CRUD-операции
  - Оборачивать scheduled-задачи в @audit_task
  - Логировать events и бизнес-события
  - НЕ логировать защищённые данные напрямую (использовать сервис)
```

### Review Agent

```yaml
При code review ПРОВЕРЯТЬ:
  - [ ] Все CRUD-операции сопровождаются аудит-логом
  - [ ] Все events/signals логируются
  - [ ] Scheduled-задачи используют @audit_task
  - [ ] Бизнес-события логируются
  - [ ] Нет прямого логирования защищённых данных
  - [ ] Уровень логирования корректен
```

### QA Agent

```yaml
При тестировании ПРОВЕРЯТЬ:
  - [ ] AuditLog записи создаются при CRUD
  - [ ] Маскирование работает для защищённых полей
  - [ ] @audit_task корректно логирует start/end/error
  - [ ] Ротация работает (файлы, БД cleanup)
  - [ ] Admin-интерфейс отображает логи корректно
```

### Dev Agent

```yaml
При создании технических спецификаций:
  - Включать секцию "Logging Requirements"
  - Определять какие события логируются
  - Указывать уровни логирования
  - Определять data для каждого лог-события
```

---

## Антипаттерны (НЕ делать)

```python
# НЕ логировать защищённые данные напрямую
logger.info(f"User password: {user.password}")  # ЗАПРЕЩЕНО!

# НЕ забывать про actor
AuditLogService.log_db_create(instance)  # actor=None — допустимо только для system

# НЕ игнорировать ошибки в логировании, но и НЕ прерывать основной flow
try:
    AuditLogService.log_db_create(instance, actor=user)
except Exception:
    logger.exception("Failed to write audit log")  # Лог ошибки, но продолжаем

# НЕ использовать print() вместо logging
print("Debug info")  # ЗАПРЕЩЕНО! Использовать logger.debug()
```

---

## Ссылки

- **ADR:** `docs/architecture/adrs/ADR-001-structured-logging-system.md`
- **Tech Spec:** `docs/development/specs/SPEC-001-logging-system.md`
- **Модель:** `backend/core/models.py` → `AuditLog`
- **Сервис:** `backend/core/audit.py` → `AuditLogService`
- **Декоратор:** `backend/core/decorators.py` → `@audit_task`

---

*Правило версии 1.1 | Aibolit AI — Claude Code Agent System*
