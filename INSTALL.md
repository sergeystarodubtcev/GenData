# Инструкция по установке и запуску GenData

## Требования

- Python 3.9+
- PostgreSQL 12+
- pip

## Установка

### 1. Клонирование репозитория

```bash
git clone <ваш-репозиторий>
cd GenData
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных

#### Для локальной разработки (PostgreSQL):
Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE gendata;
```

#### Для Beget (MySQL):
Используйте существующую базу данных MySQL на Beget. Параметры подключения:
- Имя БД: y90814l8_users
- Пользователь: y90814l8_users
- Пароль: 12345678
- Хост: localhost

### 5. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Отредактируйте `.env` и укажите свои настройки:

#### Для PostgreSQL (локально):
```env
DATABASE_URL=postgresql://user:password@localhost:5432/gendata
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_DEFAULT_PASSWORD=admin123
```

#### Для MySQL (Beget):
```env
DATABASE_URL=mysql+pymysql://y90814l8_users:12345678@localhost:3306/y90814l8_users
SECRET_KEY=your-secret-key-here-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_DEFAULT_PASSWORD=admin123
```

**Важно:** Измените `SECRET_KEY` на случайную строку для продакшена!

### 6. Инициализация базы данных

#### Вариант 1: Использование скрипта (рекомендуется для начала)

```bash
python scripts/init_db.py
```

Этот скрипт создаст таблицы и первого администратора.

#### Вариант 2: Использование Alembic (рекомендуется для продакшена)

```bash
# Создание первой миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

После применения миграций создайте первого администратора:

```bash
python scripts/init_db.py
```

### 7. Запуск приложения

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Приложение будет доступно по адресу: `http://localhost:8000`

## Использование API

### Документация API

После запуска приложения доступна интерактивная документация:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Первый вход

1. Используйте логин и пароль администратора:
   - Логин: `admin`
   - Пароль: `admin123` (или тот, что указан в `.env`)

2. Получите токен через эндпоинт `POST /auth/token`:

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"login": "admin", "password": "admin123"}'
```

Ответ:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

3. Используйте токен для доступа к защищенным эндпоинтам:

```bash
curl -X GET "http://localhost:8000/admin/users/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Импорт пользователей

Создайте CSV или XLSX файл со следующими колонками:

**Обязательные:**
- `login` - логин пользователя

**Опциональные:**
- `full_name` - полное имя
- `company_name` - название компании
- `role` - роль (client, employee, investor, admin)
- Любые другие колонки будут сохранены в `metadata`

Пример CSV:
```csv
login,full_name,company_name,role
user1,Иван Иванов,ООО "Ромашка",client
user2,Петр Петров,ИП "Василек",employee
```

Загрузите файл через эндпоинт `POST /admin/users/import`:

```bash
curl -X POST "http://localhost:8000/admin/users/import" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -F "file=@users.csv"
```

## Структура проекта

```
GenData/
├── app/
│   ├── __init__.py
│   ├── main.py              # Главный файл приложения
│   ├── config.py            # Настройки приложения
│   ├── database.py          # Подключение к БД
│   ├── models.py            # SQLAlchemy модели
│   ├── schemas.py           # Pydantic схемы
│   ├── auth.py              # Аутентификация и авторизация
│   ├── crud.py              # CRUD операции
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # Роутер аутентификации
│       └── users.py         # Роутер пользователей
├── alembic/                 # Миграции БД
├── scripts/
│   └── init_db.py          # Скрипт инициализации БД
├── requirements.txt         # Зависимости Python
├── alembic.ini             # Конфигурация Alembic
├── .env.example            # Пример файла с переменными окружения
└── README.md               # Документация проекта
```

## Решение проблем

### Ошибка подключения к БД

Проверьте:
1. PostgreSQL запущен
2. База данных создана
3. Правильность `DATABASE_URL` в `.env`
4. Права доступа пользователя БД

### Ошибка импорта модулей

Убедитесь, что виртуальное окружение активировано и все зависимости установлены:

```bash
pip install -r requirements.txt
```

### Ошибка миграций

Если миграции не применяются, попробуйте:

```bash
# Удалить все миграции (осторожно!)
rm -rf alembic/versions/*

# Создать новую миграцию
alembic revision --autogenerate -m "Initial migration"

# Применить
alembic upgrade head
```

## Следующие шаги

После успешного запуска первого этапа вы можете:

1. Протестировать API через Swagger UI (`/docs`)
2. Импортировать пользователей из CSV/XLSX
3. Создать пользователей вручную через API
4. Перейти к реализации второго этапа (Конструктор форм)

