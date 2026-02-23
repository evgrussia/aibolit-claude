# Skill: Telegram Bot API

> Разработка Telegram ботов

## Назначение

Создание и интеграция Telegram ботов с использованием Bot API.

## Уровень

**Senior / Lead** — продвинутый навык

## Credentials

- **Bot Token** — получить у @BotFather
- Хранить в переменных окружения: `TELEGRAM_BOT_TOKEN`

---

## Основы

### Создание бота

```yaml
1. Открыть @BotFather в Telegram
2. Отправить /newbot
3. Указать имя и username
4. Получить токен
5. Сохранить токен в .env
```

### Методы получения обновлений

```yaml
Long Polling:
  - Простая настройка
  - Для разработки и небольших ботов
  - Не требует HTTPS

Webhook:
  - Для production
  - Требует HTTPS
  - Более эффективен
  - Мгновенные обновления
```

---

## API Endpoints

### Основные методы

```yaml
getMe:
  - Информация о боте

sendMessage:
  - chat_id: ID чата
  - text: Текст сообщения
  - parse_mode: HTML | Markdown
  - reply_markup: Клавиатура

sendPhoto/sendDocument/sendVideo:
  - Отправка медиа

getUpdates:
  - Long polling
  - offset, limit, timeout

setWebhook:
  - url: HTTPS URL
  - certificate: Для self-signed
  - allowed_updates: Типы обновлений
```

### Inline Keyboards

```python
keyboard = {
    "inline_keyboard": [
        [
            {"text": "Button 1", "callback_data": "btn1"},
            {"text": "Button 2", "callback_data": "btn2"}
        ],
        [
            {"text": "URL Button", "url": "https://example.com"}
        ]
    ]
}
```

### Reply Keyboards

```python
keyboard = {
    "keyboard": [
        [{"text": "Button 1"}, {"text": "Button 2"}],
        [{"text": "Button 3"}]
    ],
    "resize_keyboard": True,
    "one_time_keyboard": True
}
```

---

## Python Implementation

### aiogram (рекомендуется)

```python
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

bot = Bot(token="YOUR_TOKEN")
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Привет! Я бот.",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(
                    text="Кнопка",
                    callback_data="action"
                )]
            ]
        )
    )

@dp.callback_query(lambda c: c.data == "action")
async def callback_handler(callback: types.CallbackQuery):
    await callback.answer("Обработано!")
    await callback.message.edit_text("Новый текст")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

### python-telegram-bot

```python
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет!")

app = Application.builder().token("YOUR_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
```

---

## Webhook Setup

### Nginx конфиг

```nginx
server {
    listen 443 ssl;
    server_name bot.example.com;

    ssl_certificate /etc/letsencrypt/live/bot.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bot.example.com/privkey.pem;

    location /webhook {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Установка webhook

```python
import requests

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}"

# Set webhook
response = requests.post(
    f"{TELEGRAM_API}/setWebhook",
    json={
        "url": "https://bot.example.com/webhook",
        "allowed_updates": ["message", "callback_query"]
    }
)

# Get webhook info
info = requests.get(f"{TELEGRAM_API}/getWebhookInfo").json()
```

---

## Telegram Login Widget

### HTML виджет

```html
<script async src="https://telegram.org/js/telegram-widget.js?22"
        data-telegram-login="YourBotUsername"
        data-size="large"
        data-onauth="onTelegramAuth(user)"
        data-request-access="write">
</script>

<script>
function onTelegramAuth(user) {
    // user содержит: id, first_name, last_name, username, photo_url, auth_date, hash
    fetch('/api/auth/telegram/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(user)
    });
}
</script>
```

### Верификация на backend

```python
import hashlib
import hmac

def verify_telegram_auth(data: dict, bot_token: str) -> bool:
    """Verify Telegram Login Widget data."""
    check_hash = data.pop('hash')
    data_check_string = '\n'.join(
        f"{k}={v}" for k, v in sorted(data.items())
    )
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return calculated_hash == check_hash
```

---

## Telegram Mini Apps (WebApp)

### Frontend

```javascript
const tg = window.Telegram.WebApp;

// Инициализация
tg.ready();
tg.expand();

// Данные пользователя
const initData = tg.initData;  // Для отправки на сервер
const user = tg.initDataUnsafe.user;

// Кнопки
tg.MainButton.setText('Отправить');
tg.MainButton.show();
tg.MainButton.onClick(() => {
    tg.sendData(JSON.stringify({action: 'submit'}));
});

// Закрыть
tg.close();
```

### Backend верификация

```python
import hashlib
import hmac
from urllib.parse import parse_qs

def verify_webapp_data(init_data: str, bot_token: str) -> bool:
    """Verify Telegram WebApp initData."""
    parsed = dict(parse_qs(init_data))
    parsed = {k: v[0] for k, v in parsed.items()}

    check_hash = parsed.pop('hash')

    data_check_string = '\n'.join(
        f"{k}={v}" for k, v in sorted(parsed.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        bot_token.encode(),
        hashlib.sha256
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()

    return calculated_hash == check_hash
```

---

## Best Practices

```yaml
Security:
  - Никогда не хардкодить токен
  - Верифицировать все входящие данные
  - Использовать HTTPS для webhook
  - Проверять auth_date (не старше 24h)

Performance:
  - Async handlers
  - Быстрые ответы (< 5 сек)
  - Отложенная обработка для тяжёлых задач

UX:
  - Понятные команды
  - Inline keyboards для действий
  - Обработка ошибок с понятными сообщениями
  - Loading indicators
```

---

## Формат вывода

```yaml
telegram_bot_implementation:
  bot_username: "@YourBotUsername"

  features:
    - "Command handlers"
    - "Inline keyboards"
    - "Callback queries"
    - "WebApp integration"

  update_method: "webhook|polling"

  handlers:
    commands: ["/start", "/help", "/settings"]
    callbacks: ["action_1", "action_2"]

  files:
    - "bot/main.py"
    - "bot/handlers/"
    - "bot/keyboards/"

  deployment:
    webhook_url: "https://bot.example.com/webhook"

  signature: "Coder Agent"
```

---

*Навык v1.0 | Claude Code Agent System*
