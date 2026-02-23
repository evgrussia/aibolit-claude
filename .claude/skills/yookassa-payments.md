# Skill: YooKassa Payments

> Интеграция платежей через YooKassa

## Назначение

Приём платежей, возвраты, чеки через YooKassa (Яндекс.Касса).

## Уровень

**Senior / Lead** — продвинутый навык

## Credentials

- **Shop ID** — ID магазина в YooKassa
- **Secret Key** — секретный ключ API
- Получить в личном кабинете: https://yookassa.ru/my
- Хранить в переменных окружения: `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`

---

## Основы

### Тестовый режим

```yaml
Test credentials:
  - Shop ID: test_xxxxx
  - Secret Key: test_xxxxx

Test cards:
  - Успешный платёж: 5555 5555 5555 4444
  - Отклонение: 5555 5555 5555 4477
  - 3D-Secure: 5555 5555 5555 4501
```

### Типы платежей

```yaml
bank_card:
  - Банковские карты
  - Поддержка 3D-Secure

yoo_money:
  - Кошелёк ЮMoney

sbp:
  - Система быстрых платежей

sberbank:
  - SberPay

qiwi:
  - QIWI Кошелёк

tinkoff_bank:
  - Tinkoff Pay

mobile_balance:
  - Оплата с баланса телефона
```

---

## Python SDK

### Установка

```bash
pip install yookassa
```

### Конфигурация

```python
from yookassa import Configuration

Configuration.account_id = os.environ['YOOKASSA_SHOP_ID']
Configuration.secret_key = os.environ['YOOKASSA_SECRET_KEY']
```

---

## Создание платежа

### Базовый платёж

```python
from yookassa import Payment
import uuid

def create_payment(amount: float, description: str, return_url: str) -> dict:
    """Create a payment."""
    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "capture": True,  # Автоматическое подтверждение
        "description": description,
        "metadata": {
            "order_id": str(uuid.uuid4())
        }
    }, uuid.uuid4())

    return {
        "id": payment.id,
        "status": payment.status,
        "confirmation_url": payment.confirmation.confirmation_url
    }
```

### Платёж с указанием метода

```python
def create_card_payment(amount: float, return_url: str) -> dict:
    """Create card payment."""
    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "capture": True,
        "description": "Оплата заказа"
    })

    return payment
```

### Платёж через СБП

```python
def create_sbp_payment(amount: float, return_url: str) -> dict:
    """Create SBP payment."""
    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "sbp"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "capture": True
    })

    return payment
```

---

## Проверка статуса

```python
from yookassa import Payment

def check_payment_status(payment_id: str) -> dict:
    """Check payment status."""
    payment = Payment.find_one(payment_id)

    return {
        "id": payment.id,
        "status": payment.status,  # pending, waiting_for_capture, succeeded, canceled
        "paid": payment.paid,
        "amount": payment.amount.value,
        "created_at": payment.created_at
    }
```

### Статусы платежа

```yaml
pending:
  - Ожидает оплаты
  - Пользователь ещё не завершил

waiting_for_capture:
  - Деньги заблокированы
  - Требуется подтверждение (если capture=False)

succeeded:
  - Платёж успешен
  - Деньги списаны

canceled:
  - Платёж отменён
  - Деньги не списаны или возвращены
```

---

## Webhooks

### Настройка endpoint

```python
from flask import Flask, request, jsonify
from yookassa import Configuration
from yookassa.domain.notification import WebhookNotification

app = Flask(__name__)

@app.route('/webhook/yookassa', methods=['POST'])
def yookassa_webhook():
    # Проверка IP YooKassa (опционально, но рекомендуется)
    allowed_ips = ['185.71.76.0/27', '185.71.77.0/27', '77.75.153.0/25']

    # Парсинг уведомления
    notification = WebhookNotification(request.json)

    payment = notification.object

    if notification.event == 'payment.succeeded':
        # Платёж успешен
        handle_successful_payment(payment)

    elif notification.event == 'payment.canceled':
        # Платёж отменён
        handle_canceled_payment(payment)

    elif notification.event == 'refund.succeeded':
        # Возврат выполнен
        handle_refund(payment)

    return jsonify({"status": "ok"}), 200

def handle_successful_payment(payment):
    """Handle successful payment."""
    order_id = payment.metadata.get('order_id')
    amount = payment.amount.value
    # Обновить статус заказа в БД
    # Отправить уведомление пользователю
```

### Типы событий

```yaml
payment.waiting_for_capture:
  - Платёж ожидает подтверждения

payment.succeeded:
  - Платёж успешен

payment.canceled:
  - Платёж отменён

refund.succeeded:
  - Возврат выполнен
```

---

## Возвраты

### Полный возврат

```python
from yookassa import Refund
import uuid

def create_refund(payment_id: str) -> dict:
    """Create full refund."""
    # Получить платёж
    payment = Payment.find_one(payment_id)

    refund = Refund.create({
        "payment_id": payment_id,
        "amount": {
            "value": payment.amount.value,
            "currency": "RUB"
        }
    }, uuid.uuid4())

    return {
        "id": refund.id,
        "status": refund.status,
        "amount": refund.amount.value
    }
```

### Частичный возврат

```python
def create_partial_refund(payment_id: str, amount: float) -> dict:
    """Create partial refund."""
    refund = Refund.create({
        "payment_id": payment_id,
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        }
    }, uuid.uuid4())

    return refund
```

---

## Чеки (54-ФЗ)

### Платёж с чеком

```python
def create_payment_with_receipt(
    amount: float,
    customer_email: str,
    items: list,
    return_url: str
) -> dict:
    """Create payment with receipt (54-FZ)."""

    receipt_items = [
        {
            "description": item["name"],
            "quantity": str(item["quantity"]),
            "amount": {
                "value": str(item["price"]),
                "currency": "RUB"
            },
            "vat_code": 1,  # НДС 20%
            "payment_mode": "full_payment",
            "payment_subject": "commodity"
        }
        for item in items
    ]

    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url
        },
        "capture": True,
        "receipt": {
            "customer": {
                "email": customer_email
            },
            "items": receipt_items
        }
    })

    return payment
```

### Коды НДС

```yaml
vat_code:
  1: НДС 20%
  2: НДС 10%
  3: НДС 0%
  4: Без НДС
  5: НДС 20/120
  6: НДС 10/110
```

---

## Best Practices

```yaml
Security:
  - HTTPS для webhook endpoint
  - Проверять IP YooKassa
  - Хранить credentials в env
  - Идемпотентные запросы (idempotency key)

Reliability:
  - Retry logic для API вызовов
  - Обрабатывать все статусы
  - Логировать все события
  - Webhook acknowledgment < 30 сек

UX:
  - Показывать сумму и описание
  - Редирект на страницу статуса
  - Email уведомления
  - Чёткие сообщения об ошибках
```

---

## Django Integration

```python
# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def yookassa_webhook(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        notification = WebhookNotification(data)

        if notification.event == 'payment.succeeded':
            payment = notification.object
            # Process payment
            Order.objects.filter(
                payment_id=payment.id
            ).update(status='paid')

        return JsonResponse({"status": "ok"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
```

---

## Формат вывода

```yaml
yookassa_implementation:
  mode: "test|production"

  features:
    - "Card payments"
    - "SBP payments"
    - "Webhooks"
    - "Refunds"
    - "Receipts (54-FZ)"

  payment_methods:
    - "bank_card"
    - "sbp"
    - "yoo_money"

  webhook_events:
    - "payment.succeeded"
    - "payment.canceled"
    - "refund.succeeded"

  files:
    - "payments/yookassa.py"
    - "payments/webhooks.py"

  compliance:
    - "54-FZ receipts"

  signature: "Coder Agent"
```

---

*Навык v1.0 | Claude Code Agent System*
