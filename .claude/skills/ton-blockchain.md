# Skill: TON Blockchain

> Разработка на TON Blockchain

## Назначение

Интеграция с TON Blockchain: кошельки, платежи, Jettons, NFT.

## Уровень

**Senior / Lead** — продвинутый навык

## Credentials

- **TON API Key** — получить на TonConsole (https://tonconsole.com)
- Хранить в переменных окружения: `TON_API_KEY`

---

## Основы TON

### Сеть

```yaml
Mainnet:
  - Основная сеть
  - Реальные средства

Testnet:
  - Тестовая сеть
  - Бесплатные тестовые монеты
  - Для разработки
```

### Типы адресов

```yaml
Raw address:
  - Формат: workchain:hex
  - Пример: 0:123abc...

User-friendly:
  - Формат: EQ... или UQ...
  - EQ = bounceable (для контрактов)
  - UQ = non-bounceable (для кошельков)
```

---

## Python SDK

### tonutils

```python
from tonutils.client import TonapiClient
from tonutils.wallet import WalletV4R2
import os

# Инициализация клиента
client = TonapiClient(api_key=os.environ['TON_API_KEY'])

# Создание кошелька
wallet = WalletV4R2.create(client)
print(f"Address: {wallet.address}")
print(f"Mnemonic: {wallet.mnemonic}")

# Из существующей мнемоники
wallet = WalletV4R2.from_mnemonic(client, mnemonic_list)
```

### pytoniq

```python
from pytoniq import LiteClient, WalletV4R2

# Подключение к сети
client = await LiteClient.connect(
    config='https://ton.org/global-config.json',
    trust_level=2
)

# Получение баланса
balance = await client.get_balance("EQAddress...")
print(f"Balance: {balance / 10**9} TON")
```

---

## Основные операции

### Проверка баланса

```python
from tonutils.client import TonapiClient

async def get_balance(address: str) -> float:
    client = TonapiClient(api_key=os.environ['TON_API_KEY'])
    account = await client.accounts.get_info(address)
    return account.balance / 10**9  # nanoTON to TON
```

### Отправка TON

```python
from tonutils.wallet import WalletV4R2
from tonutils.client import TonapiClient

async def send_ton(mnemonic: list, to_address: str, amount: float, comment: str = ""):
    client = TonapiClient(api_key=os.environ['TON_API_KEY'])
    wallet = WalletV4R2.from_mnemonic(client, mnemonic)

    # amount в TON, конвертируем в nanoTON
    await wallet.transfer(
        destination=to_address,
        amount=int(amount * 10**9),
        body=comment
    )
```

### Проверка транзакции

```python
async def check_transaction(tx_hash: str):
    client = TonapiClient(api_key=os.environ['TON_API_KEY'])
    tx = await client.blockchain.get_transaction(tx_hash)
    return {
        "success": tx.success,
        "amount": tx.in_msg.value / 10**9,
        "from": tx.in_msg.source,
        "to": tx.in_msg.destination
    }
```

---

## Jettons (Токены)

### Получение баланса Jetton

```python
async def get_jetton_balance(wallet_address: str, jetton_master: str):
    client = TonapiClient(api_key=os.environ['TON_API_KEY'])

    # Получить Jetton wallet address
    jetton_wallet = await client.jettons.get_jetton_wallet(
        account_id=wallet_address,
        jetton_id=jetton_master
    )

    return jetton_wallet.balance
```

### Отправка Jettons

```python
from tonutils.jetton import JettonWallet

async def send_jetton(
    mnemonic: list,
    jetton_wallet_address: str,
    to_address: str,
    amount: int,
    decimals: int = 9
):
    client = TonapiClient(api_key=os.environ['TON_API_KEY'])
    wallet = WalletV4R2.from_mnemonic(client, mnemonic)

    jetton_wallet = JettonWallet(client, jetton_wallet_address)

    await jetton_wallet.transfer(
        wallet=wallet,
        destination=to_address,
        amount=amount * (10 ** decimals),
        forward_amount=int(0.05 * 10**9)  # для уведомления
    )
```

---

## NFT

### Получение NFT коллекции

```python
async def get_nfts(owner_address: str):
    client = TonapiClient(api_key=os.environ['TON_API_KEY'])
    nfts = await client.nft.get_items_by_owner(owner_address)

    return [{
        "address": nft.address,
        "name": nft.metadata.get("name"),
        "image": nft.metadata.get("image"),
        "collection": nft.collection.address if nft.collection else None
    } for nft in nfts.nft_items]
```

### Передача NFT

```python
from tonutils.nft import NFTItem

async def transfer_nft(mnemonic: list, nft_address: str, new_owner: str):
    client = TonapiClient(api_key=os.environ['TON_API_KEY'])
    wallet = WalletV4R2.from_mnemonic(client, mnemonic)

    nft = NFTItem(client, nft_address)
    await nft.transfer(wallet, new_owner)
```

---

## TON Connect

### Интеграция в приложение

```javascript
// Frontend (React)
import { TonConnectButton, useTonWallet } from '@tonconnect/ui-react';

function App() {
    const wallet = useTonWallet();

    return (
        <div>
            <TonConnectButton />
            {wallet && (
                <p>Connected: {wallet.account.address}</p>
            )}
        </div>
    );
}
```

### Верификация подписи

```python
from nacl.signing import VerifyKey
import base64

def verify_ton_proof(
    address: str,
    proof: dict,
    payload: str
) -> bool:
    """Verify TON Connect proof."""
    # Реконструировать сообщение
    message = f"ton-proof-item-v2/{address}/{proof['domain']}/{proof['timestamp']}/{payload}"

    # Верифицировать подпись
    public_key = base64.b64decode(proof['public_key'])
    signature = base64.b64decode(proof['signature'])

    try:
        verify_key = VerifyKey(public_key)
        verify_key.verify(message.encode(), signature)
        return True
    except Exception:
        return False
```

---

## Telegram Mini App + TON

```javascript
// Интеграция TON Connect в Telegram Mini App
import { TonConnectUI } from '@tonconnect/ui';

const tonConnectUI = new TonConnectUI({
    manifestUrl: 'https://app.example.com/tonconnect-manifest.json',
    buttonRootId: 'ton-connect-button'
});

// Отправка транзакции
async function sendPayment(amount, toAddress) {
    const transaction = {
        validUntil: Math.floor(Date.now() / 1000) + 360,
        messages: [
            {
                address: toAddress,
                amount: (amount * 1e9).toString(), // в nanoTON
            }
        ]
    };

    const result = await tonConnectUI.sendTransaction(transaction);
    return result.boc;
}
```

---

## Best Practices

```yaml
Security:
  - Никогда не хранить мнемонику в коде
  - Использовать hardware wallets для production
  - Проверять адреса перед отправкой
  - Использовать testnet для разработки

Performance:
  - Кэшировать балансы
  - Batch запросы где возможно
  - Обрабатывать rate limits

UX:
  - Показывать комиссии перед транзакцией
  - Подтверждение от пользователя
  - Понятные сообщения об ошибках
```

---

## Формат вывода

```yaml
ton_implementation:
  network: "mainnet|testnet"

  features:
    - "Wallet integration"
    - "TON transfers"
    - "Jetton support"
    - "NFT support"
    - "TON Connect"

  sdk: "tonutils|pytoniq"

  operations:
    - "get_balance"
    - "send_ton"
    - "send_jetton"
    - "get_nfts"

  files:
    - "ton/client.py"
    - "ton/wallet.py"
    - "ton/jettons.py"

  signature: "Coder Agent"
```

---

*Навык v1.0 | Claude Code Agent System*
