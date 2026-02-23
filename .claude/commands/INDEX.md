# Реестр команд

> Все команды системы Claude Code Agent System

## Обзор

Система включает **7 основных команд** для управления проектом и агентами.

---

## Команды

| Команда | Файл | Описание |
|---------|------|----------|
| `/start-project` | [start-project.md](start-project.md) | Инициализация нового проекта |
| `/status` | [status.md](status.md) | Текущее состояние проекта |
| `/route` | [route.md](route.md) | Выполнить задачу как агент |
| `/checkpoint` | [checkpoint.md](checkpoint.md) | Создать checkpoint |
| `/summary` | [summary.md](summary.md) | Сжатое резюме состояния |
| `/deploy-vps` | [deploy-vps.md](deploy-vps.md) | Деплой на VPS |
| `/medical-review` | [medical-review.md](medical-review.md) | Верификация медицинского AI-ответа |

---

## Синтаксис

```
/command [arguments]
```

### Примеры

```bash
# Начать новый проект
/start-project Платформа для онлайн-курсов с AI-ассистентом

# Проверить статус
/status

# Выполнить задачу как конкретный агент
/route product Создать PRD для MVP
/route coder Реализовать endpoint GET /api/articles/

# Создать checkpoint
/checkpoint

# Получить краткое резюме
/summary

# Деплой на VPS
/deploy-vps staging

# Верификация медицинского AI
/medical-review backend/ai/agents/cardiologist.py
```

---

## Когда использовать

| Ситуация | Команда |
|----------|---------|
| Начало нового проекта | `/start-project` |
| Узнать текущее состояние | `/status` |
| Делегировать конкретному агенту | `/route` |
| Сохранить прогресс | `/checkpoint` |
| Получить краткое резюме для передачи | `/summary` |
| Развернуть на сервере | `/deploy-vps` |
| Верифицировать медицинский AI | `/medical-review` |

---

## Роль по умолчанию

Если команда не указана, работает **Orchestrator Agent**:
- Анализирует задачу
- Определяет подходящих агентов
- Делегирует выполнение
- Контролирует качество

---

## Вывод команд

Каждая команда имеет стандартизированный формат вывода:

```yaml
command_result:
  command: "[команда]"
  status: "success|partial|error"
  output: {...}
  signature: "[Agent] Agent"
```

---

*Реестр команд v1.1 | Aibolit AI — Claude Code Agent System*
