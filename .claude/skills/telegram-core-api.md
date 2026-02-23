# Skill: Telegram Core API (MTProto)

> Работа с Telegram Core API через MTProto

## Назначение

Создание кастомных Telegram клиентов, userbot'ов, работа с MTProto протоколом.

## Уровень

**Senior / Lead** — продвинутый навык

## Credentials

- **API ID** — получить на my.telegram.org
- **API Hash** — получить на my.telegram.org
- Хранить в переменных окружения: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`

---

## Отличия от Bot API

| Аспект | Bot API | Core API (MTProto) |
|--------|---------|-------------------|
| Кто использует | Боты | Пользователи, кастомные клиенты |
| Возможности | Ограничены | Полные (как приложение) |
| Авторизация | Токен бота | Телефон + код/2FA |
| Скорость | Через HTTP | Напрямую через MTProto |
| Лимиты | Жёсткие | Мягче |

---

## Получение credentials

```yaml
1. Открыть https://my.telegram.org
2. Войти по номеру телефона
3. Перейти в "API development tools"
4. Создать приложение
5. Получить api_id и api_hash
6. Сохранить в .env файл
```

---

## Python Libraries

### Telethon (рекомендуется)

```python
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import os

api_id = int(os.environ['TELEGRAM_API_ID'])
api_hash = os.environ['TELEGRAM_API_HASH']

# Создание клиента
client = TelegramClient('session_name', api_id, api_hash)

async def main():
    # Авторизация (интерактивно)
    await client.start()

    # Получение информации о себе
    me = await client.get_me()
    print(f"Logged in as {me.username}")

    # Отправка сообщения
    await client.send_message('username', 'Hello!')

    # Получение диалогов
    async for dialog in client.iter_dialogs():
        print(dialog.name, dialog.id)

with client:
    client.loop.run_until_complete(main())
```

### Pyrogram

```python
from pyrogram import Client, filters

api_id = int(os.environ['TELEGRAM_API_ID'])
api_hash = os.environ['TELEGRAM_API_HASH']

app = Client("my_account", api_id=api_id, api_hash=api_hash)

@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello!")

app.run()
```

---

## Основные операции

### Авторизация

```python
from telethon import TelegramClient

async def authorize():
    client = TelegramClient('session', api_id, api_hash)
    await client.start(phone='+7XXXXXXXXXX')

    # Если 2FA включён
    # await client.start(phone='+7XXXXXXXXXX', password='your_2fa')

    return client
```

### Session String (для serverless)

```python
from telethon.sessions import StringSession

# Создание session string
with TelegramClient(StringSession(), api_id, api_hash) as client:
    print(client.session.save())  # Сохранить эту строку

# Использование session string
session_string = os.environ['TELEGRAM_SESSION']
client = TelegramClient(StringSession(session_string), api_id, api_hash)
```

### Работа с сообщениями

```python
# Отправка сообщений
await client.send_message('username', 'Hello!')
await client.send_message(chat_id, 'Hello!')

# Отправка медиа
await client.send_file('username', 'photo.jpg', caption='Caption')

# Получение истории
async for message in client.iter_messages('channel_username', limit=100):
    print(message.text)

# Поиск сообщений
async for message in client.iter_messages('channel', search='keyword'):
    print(message.text)
```

### Работа с каналами и группами

```python
# Получение участников
async for user in client.iter_participants('group'):
    print(user.username)

# Присоединение к каналу
from telethon.tl.functions.channels import JoinChannelRequest
await client(JoinChannelRequest('channel_username'))

# Создание группы
from telethon.tl.functions.messages import CreateChatRequest
await client(CreateChatRequest(users=['user1', 'user2'], title='Group Name'))
```

### События (Events)

```python
from telethon import events

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply('Hello!')

@client.on(events.NewMessage(incoming=True, chats=['channel']))
async def channel_handler(event):
    print(f"New message in channel: {event.text}")

# Запуск
client.run_until_disconnected()
```

---

## Data Centers

```yaml
DC1: 149.154.175.50 (Miami)
DC2: 149.154.167.50 (Amsterdam) - основной для EU
DC3: 149.154.175.100 (Miami)
DC4: 149.154.167.91 (Amsterdam)
DC5: 91.108.56.130 (Singapore)

Test DCs:
  DC1: 149.154.175.10
  DC2: 149.154.167.40
```

---

## Rate Limits

```yaml
Messages:
  - 30 сообщений в секунду (примерно)
  - Flood wait при превышении

API calls:
  - Зависит от метода
  - Exponential backoff при ошибках

Best practices:
  - Добавлять delays между вызовами
  - Обрабатывать FloodWaitError
  - Использовать batch operations
```

### Обработка FloodWait

```python
from telethon.errors import FloodWaitError
import asyncio

async def safe_send(client, chat, message):
    try:
        await client.send_message(chat, message)
    except FloodWaitError as e:
        print(f"Flood wait: {e.seconds} seconds")
        await asyncio.sleep(e.seconds)
        await client.send_message(chat, message)
```

---

## Безопасность

```yaml
Критически важно:
  - Никогда не хардкодить api_id/api_hash
  - Никогда не коммитить session файлы
  - Использовать .gitignore для *.session
  - Хранить session string в secrets

Рекомендации:
  - Отдельный аккаунт для разработки
  - Ограничить IP для session
  - Мониторить активные сессии
  - Регулярно ревокать старые сессии
```

---

## Use Cases

```yaml
Разрешённые:
  - Кастомные клиенты
  - Автоматизация личных задач
  - Backup сообщений
  - Интеграции с разрешения участников

Запрещённые (нарушение ToS):
  - Спам
  - Scraping без разрешения
  - Массовые инвайты
  - Продажа userbot'ов
```

---

## Формат вывода

```yaml
telegram_core_implementation:
  library: "telethon|pyrogram"

  features:
    - "User authentication"
    - "Message handling"
    - "Channel operations"

  auth_method: "phone|session_string"

  handlers:
    - event: "NewMessage"
      pattern: "/command"

  files:
    - "client/main.py"
    - "client/handlers/"

  security:
    session_storage: "encrypted_env"
    rate_limiting: true

  signature: "Coder Agent"
```

---

*Навык v1.0 | Claude Code Agent System*
