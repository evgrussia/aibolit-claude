# Команда: /deploy-vps

> Деплой на VPS сервер

## Синтаксис

```
/deploy-vps [environment]
```

## Параметры

- `[environment]` — `production`, `staging`, `development` (по умолчанию: `production`)

---

## Описание

Выполняет деплой приложения на VPS сервер через SSH.

---

## Требования

```yaml
Перед деплоем:
  - SSH ключи настроены
  - Сервер доступен
  - Git репозиторий актуален
  - Все тесты проходят
  - Code review завершён

Environment variables:
  - SSH_HOST
  - SSH_USER
  - SSH_KEY_PATH (или SSH-agent)
```

---

## Процесс

### Step 1: Pre-flight checks

```yaml
Действия:
  - Проверить доступность сервера
  - Проверить текущий статус сервисов
  - Проверить свободное место на диске
  - Получить текущую версию
```

### Step 2: Backup (если production)

```yaml
Действия:
  - Database dump
  - Сохранить текущий commit hash
  - Зафиксировать rollback point
```

### Step 3: Deploy

```yaml
Действия:
  - git fetch origin
  - git checkout main
  - git pull origin main
  - docker compose pull
  - docker compose up -d --build
  - Run migrations
```

### Step 4: Verify

```yaml
Действия:
  - Health check endpoints
  - Smoke tests
  - Проверка логов на ошибки
  - Verify services running
```

### Step 5: Report

```yaml
Действия:
  - Сформировать отчёт
  - Зафиксировать deployment
  - Уведомить о завершении
```

---

## Пример использования

### Ввод

```
/deploy-vps staging
```

### Вывод

```
🚀 Deployment to staging

📋 Pre-flight checks:
  ✅ Server reachable: staging.example.com
  ✅ Services running: backend, frontend, db
  ✅ Disk space: 45GB free
  ✅ Current version: abc1234

📦 Deploying...
  ✅ git pull origin main
  ✅ docker compose pull
  ✅ docker compose up -d --build
  ✅ Migrations applied

🔍 Verification:
  ✅ Health check: /health/ → 200 OK
  ✅ API: /api/ → 200 OK
  ✅ Frontend: / → 200 OK
  ✅ Logs: No errors

📊 Deployment Summary:
  Environment: staging
  Previous version: abc1234
  New version: def5678
  Duration: 2m 15s
  Status: ✅ SUCCESS

📁 Rollback command (if needed):
  git checkout abc1234 && docker compose up -d --build

---
✍️ **DevOps Agent**
```

---

## Rollback

При проблемах после деплоя:

```yaml
Автоматический rollback (если critical error):
  1. Остановить деплой
  2. git checkout {previous_commit}
  3. docker compose up -d --build
  4. Verify services
  5. Create incident report

Ручной rollback:
  /deploy-vps rollback {commit_hash}
```

---

## Deployment Checklist

```yaml
Pre-deployment:
  [ ] Все тесты проходят
  [ ] Code review approved
  [ ] Staging протестирован (для production)
  [ ] Backup создан
  [ ] Rollback plan готов

Deployment:
  [ ] Pull latest code
  [ ] Build containers
  [ ] Run migrations
  [ ] Restart services

Post-deployment:
  [ ] Health checks passed
  [ ] Smoke tests passed
  [ ] Logs clean
  [ ] Monitoring OK
```

---

## Формат отчёта

```yaml
deployment_report:
  id: "DEPLOY-001"
  environment: "staging"
  timestamp: "2024-01-15 14:30:00"

  status: "success|partial|failed"

  versions:
    previous: "abc1234"
    current: "def5678"
    changes: 5  # commits

  duration: "2m 15s"

  steps:
    - step: "git pull"
      status: "success"
      duration: "5s"
    - step: "docker compose build"
      status: "success"
      duration: "1m 30s"
    - step: "migrations"
      status: "success"
      duration: "10s"

  verification:
    health_check: "passed"
    api_check: "passed"
    smoke_tests: "passed"

  rollback:
    command: "git checkout abc1234 && docker compose up -d --build"
    tested: false

  signature: "DevOps Agent"
```

---

## Environments

### Production

```yaml
Server: production.example.com
Path: /var/www/app
Требует:
  - Explicit approval
  - Backup before deploy
  - Smoke tests after
```

### Staging

```yaml
Server: staging.example.com
Path: /var/www/app
Требует:
  - Tests passed
  - Smoke tests after
```

### Development

```yaml
Server: dev.example.com
Path: /var/www/app
Требует:
  - Build successful
```

---

## Безопасность

```yaml
НИКОГДА:
  - Деплой без подтверждения на production
  - Деплой с failing tests
  - Хардкод credentials в логах

ВСЕГДА:
  - Backup перед production deploy
  - Verify после deploy
  - Rollback plan готов
```

---

*Команда v1.0 | Claude Code Agent System*
