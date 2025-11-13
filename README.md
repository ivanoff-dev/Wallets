# Wallet Service API

Микросервис для управления электронными кошельками и финансовыми операциями.

## Описание сервиса

Сервис предоставляет REST API для управления кошельками и проведения финансовых операций (пополнение и списание средств). Поддерживает параллельные операции с гарантией консистентности данных.

### Основные возможности:
- Получение баланса кошелька
- Проведение операций пополнения и списания

## Технологический стек

- **Backend**: Django + Django REST Framework
- **Database**: PostgreSQL
- **WSGI Server**: Gunicorn
- **Containerization**: Docker + Docker Compose
- **Testing**: Django Test Framework

## Методы API

### Кошельки (Wallets)

#### 1. Получить баланс кошелька
Метод позволяет получить баланс кошелька в минимальных единицах валюты
```http
GET /api/wallets/{wallet_id}/
```
###### HTTP 200 OK:
```json
{
    "balance": 1000
}
```

#### 2. Изменить баланс кошелька
Метод позволяет пополнить или списать с кошелька денежные средства в минимальных единицах валюты 
DEPOSIT - пополнение кошелька
WITHDRAW - списание с кошелька

```http
POST /api/wallets/{wallet_id}/operation
```

###### Тело запроса:
```json
{
    "operation_type": "DEPOSIT",
    "amount": "100"
}
```

###### HTTP 201 CREATED:
```json
{
    "operation_id": "uuid",
    "status": "SUCCESS",
    "operation_type": "DEPOSIT",
    "amount": "100",
    "new_balance": "1100"
}
```

##### Ошибки:

400 Bad Request - недостаточно средств для списания
404 Not Found - кошелек не найден
400 Bad Request - неверные данные запроса

## Быстрый запуск

### Клонируйте репозиторий:
```bash
git clone <repository-url>
cd wallets-service
```

### Создайте файл окружения:
```bash
cp .env.example .env
```

### Отредактируйте .env файл при необходимости:
```env
POSTGRES_DB=wallets_db
POSTGRES_USER=wallets_user
POSTGRES_PASSWORD=wallets_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Запустите сервис:
```bash
docker-compose up --build
Сервис будет доступен по адресу: http://localhost:8000
```

### Создайте суперпользователя:
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Откройте админ-панель в браузере:
```
http://127.0.0.1:8000/admin/
```

### Создайте кошелек и получите его идентификатор