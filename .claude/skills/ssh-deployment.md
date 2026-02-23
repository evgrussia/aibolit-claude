# Skill: SSH Deployment

> SSH операции на VPS серверах

## Назначение

Выполнение операций на удалённых серверах через SSH: деплой, диагностика, управление сервисами.

## Уровень

**Senior / Lead** — продвинутый навык

## Целевая платформа

**Ubuntu 24.04 LTS** (или совместимая)

---

## Агенты с доступом

| Агент | Права | Задачи |
|-------|-------|--------|
| DevOps | Полные | Deployment, инфраструктура, CI/CD |
| SRE | Полные | Мониторинг, диагностика, incidents |
| QA | Deploy + Verify | Deployment testing, smoke tests |
| Coder | По запросу | Server debug, hotfix |

---

## Критические правила безопасности

### НИКОГДА

```yaml
- Хранить пароли/ключи в коде или логах
- Выполнять деструктивные команды без подтверждения
- Использовать пароли (только SSH ключи)
- Запускать команды без верификации сервера
- Менять production без approval пользователя
```

### ВСЕГДА

```yaml
- Использовать SSH ключи для аутентификации
- Верифицировать сервер перед операциями
- Логировать все действия
- Запрашивать подтверждение для деструктивных операций
- Иметь план отката
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
| Env файлы | `/opt/app/.env` |

---

## Операции

### Диагностика

```bash
# Статус сервиса
systemctl status app
docker compose ps

# Логи
journalctl -u app -n 100 --no-pager
docker compose logs --tail=100 app
tail -f /var/log/app/error.log

# Ресурсы
df -h          # Диск
free -m        # Память
top -bn1       # CPU/процессы
```

### Управление сервисами

```bash
# Systemd
sudo systemctl restart app
sudo systemctl reload nginx
sudo systemctl status app

# Docker
docker compose restart app
docker compose up -d --build app
docker compose logs -f app
```

### Deployment

```bash
# Git-based deployment
cd /var/www/app
git fetch origin
git checkout main
git pull origin main

# Docker rebuild
docker compose pull
docker compose up -d --build
docker compose exec -T app python manage.py migrate

# Verify
curl -f http://localhost:8000/health/
docker compose ps
```

### Nginx

```bash
# Проверка конфига
sudo nginx -t

# Reload
sudo systemctl reload nginx

# Логи
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log
```

### База данных

```bash
# PostgreSQL backup
pg_dump -U postgres dbname > backup_$(date +%Y%m%d).sql

# PostgreSQL restore (ОСТОРОЖНО!)
psql -U postgres dbname < backup.sql

# Check connections
psql -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## Workflow деплоя

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
   - docker compose pull
   - docker compose up -d --build
   - Run migrations

4. Verify:
   - Health check endpoints
   - Логи на ошибки
   - Smoke tests

5. Post-deploy:
   - Очистка старых образов
   - Уведомление о завершении
```

---

## Уровни подтверждения

### Без подтверждения

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

## Формат запроса

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

## Формат отчёта

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

## Checklist

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

## Git-Only Policy

```yaml
Изменения файлов проекта — ТОЛЬКО через Git:
  Local:  git add → git commit → git push
  Server: git pull (или fetch + checkout)
  Затем:  build, migrate, restart

Можно через SSH:
  - Скачивать логи
  - Скачивать database dumps
  - Диагностика

Нельзя через SSH:
  - Загружать файлы проекта
  - Редактировать код напрямую
```

---

*Навык v1.0 | Claude Code Agent System*
