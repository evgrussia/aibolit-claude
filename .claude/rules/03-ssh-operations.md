# 03 - SSH операции на VPS

> Правила выполнения SSH операций на dev/production серверах

## Целевая платформа

**Ubuntu 24.04 LTS** (или совместимая)

---

## Агенты с SSH доступом

| Агент | Права | Задачи |
|-------|-------|--------|
| DevOps | Полные | Deployment, инфраструктура, CI/CD |
| SRE | Полные | Мониторинг, диагностика, incident response |
| QA | Deploy + Verify | Тестирование деплоя, smoke tests, логи |
| Coder | По запросу | Server debug, hotfix |

---

## Критические правила безопасности

### НИКОГДА:

```yaml
1. Хранить пароли/ключи в коде или логах
2. Выполнять деструктивные команды без подтверждения
3. Использовать пароли (только SSH ключи)
4. Запускать команды без верификации сервера
5. Менять production без approval пользователя
```

### ВСЕГДА:

```yaml
1. Использовать SSH ключи для аутентификации
2. Верифицировать сервер перед операциями
3. Логировать все действия
4. Запрашивать подтверждение для деструктивных операций
5. Иметь план отката
```

---

## Git-Only политика для файлов проекта

### Изменения файлов проекта — ТОЛЬКО через Git

```yaml
Правильно:
  Local:  git add → git commit → git push
  Server: git pull (или fetch + checkout)
  Затем:  build, migrate, restart

Неправильно:
  - Прямое редактирование файлов на сервере
  - Upload через SCP/SFTP
  - Копирование через MCP
```

### Исключения (можно через MCP/SCP):

```yaml
Можно скачивать:
  - Логи для анализа
  - Database dumps
  - Диагностические данные

Нельзя загружать:
  - Файлы проекта (код, конфиги)
  - Secrets (используй env vars)
```

---

## Стандартные пути

| Тип | Путь |
|-----|------|
| Приложения | `/var/www/` или `/opt/app/` |
| Логи | `/var/log/app/` |
| Nginx конфиги | `/etc/nginx/sites-available/` |
| Systemd сервисы | `/etc/systemd/system/` |
| SSL сертификаты | `/etc/letsencrypt/live/` |
| Docker volumes | `/var/lib/docker/volumes/` |
| Env файлы | `/opt/app/.env` или рядом с приложением |

---

## Workflow деплоя

### Стандартный деплой

```yaml
1. Pre-checks:
   - Проверить текущее состояние сервера
   - Проверить доступное место на диске
   - Проверить статус сервисов

2. Backup (если нужно):
   - Database dump
   - Копия конфигов

3. Deploy:
   - git pull origin main
   - docker compose pull (если Docker)
   - docker compose up -d --build
   - Или: pip install -r requirements.txt && systemctl restart app

4. Verify:
   - Health check endpoints
   - Логи на ошибки
   - Smoke tests

5. Post-deploy:
   - Очистка старых образов/артефактов
   - Уведомление о завершении
```

### Rollback

```yaml
1. Идентифицировать проблему
2. git checkout <previous-commit>
3. Rebuild/restart
4. Verify
5. Создать incident report
```

---

## Команды по категориям

### Диагностика

```bash
# Статус сервисов
systemctl status <service>
docker compose ps

# Логи
journalctl -u <service> -n 100 --no-pager
docker compose logs --tail=100 <service>
tail -f /var/log/app/error.log

# Ресурсы
df -h
free -m
top -bn1 | head -20
```

### Управление сервисами

```bash
# Systemd
sudo systemctl restart <service>
sudo systemctl reload nginx

# Docker
docker compose restart <service>
docker compose up -d --build <service>
```

### Nginx

```bash
# Проверка конфига
sudo nginx -t

# Reload
sudo systemctl reload nginx

# Логи
tail -f /var/log/nginx/error.log
```

### База данных

```bash
# PostgreSQL backup
pg_dump -U postgres dbname > backup.sql

# PostgreSQL restore (ОСТОРОЖНО!)
psql -U postgres dbname < backup.sql
```

---

## Уровни подтверждения

### Без подтверждения (информационные)

```yaml
- Просмотр логов
- Проверка статуса
- df, free, top
- git status, git log
```

### С подтверждением пользователя

```yaml
- Restart сервисов
- Deploy (git pull + rebuild)
- Изменение конфигов
- Database operations
```

### С ЯВНЫМ подтверждением + причина

```yaml
- Удаление данных
- Rollback
- Изменение production database
- Остановка сервисов
```

---

## Формат запроса SSH операции

```yaml
ssh_operation:
  server: "production|staging|development"
  agent: "[Agent Name]"

  operation:
    type: "diagnostic|deploy|restart|config|database"
    description: "[Что будем делать]"

  commands:
    - command: "[команда]"
      risk: "low|medium|high"
      rollback: "[команда отката]"

  requires_confirmation: true|false
  reason: "[Причина операции]"
```

---

## Формат отчёта об операции

```yaml
ssh_report:
  operation_id: "SSH-001"
  server: "[server]"
  agent: "[Agent Name]"
  timestamp: "YYYY-MM-DD HH:MM:SS"

  status: "success|partial|failed"

  commands_executed:
    - command: "[команда]"
      exit_code: 0
      output: "[краткий вывод]"

  changes_made:
    - "[Изменение 1]"
    - "[Изменение 2]"

  verification:
    health_check: "passed|failed"
    logs_checked: true
    smoke_test: "passed|failed"

  issues:
    - "[Проблема, если есть]"

  next_steps:
    - "[Следующий шаг]"

  signature: "[Agent Name] Agent"
```

---

## Incident Response

### При обнаружении проблемы

```yaml
1. Assess:
   - Определить severity (critical/high/medium/low)
   - Определить scope (что затронуто)
   - Собрать логи и метрики

2. Mitigate:
   - Временное решение (если возможно)
   - Уведомить пользователя

3. Investigate:
   - Root cause analysis
   - Собрать evidence

4. Resolve:
   - Применить fix
   - Verify fix

5. Document:
   - Incident report
   - Post-mortem (для critical)
```

### Severity определения

| Severity | Критерии | Время реакции |
|----------|----------|---------------|
| Critical | Сервис недоступен | Немедленно |
| High | Основная функциональность нарушена | < 1 час |
| Medium | Второстепенная функциональность | < 4 часа |
| Low | Минорные проблемы | Следующий рабочий день |

---

## Checklist перед SSH операцией

```yaml
Pre-operation:
  [ ] Сервер идентифицирован корректно
  [ ] Цель операции ясна
  [ ] Rollback план готов
  [ ] Backup создан (если нужно)
  [ ] Подтверждение получено (если требуется)

During operation:
  [ ] Команды выполняются по одной
  [ ] Вывод проверяется после каждой команды
  [ ] Ошибки обрабатываются немедленно

Post-operation:
  [ ] Health check пройден
  [ ] Логи проверены на ошибки
  [ ] Отчёт создан
```

---

*Правило версии 1.0 | Claude Code Agent System*
