# Инструкция по развертыванию на Beget

## Параметры базы данных Beget

- **Имя БД:** y90814l8_users
- **Пароль:** 12345678
- **Пользователь:** y90814l8_users (совпадает с именем БД)
- **Сервер для сайтов:** localhost
- **Сервер для внешних подключений:** y90814l8.beget.tech
- **Версия:** MySQL 8.0

---

## Шаг 1: Подключение к серверу через SSH

```bash
ssh ваш_логин@y90814l8.beget.tech
```

Или через IP адрес, если он у вас есть.

**Вопрос:** Подключились? (да/нет)

---

## Шаг 2: Проверка окружения

```bash
python3 --version
git --version
pwd
```

**Вопрос:** Видите версии Python и Git? (да/нет)

---

## Шаг 3: Клонирование проекта

```bash
cd ~
git clone https://github.com/ВАШ_ПОЛЬЗОВАТЕЛЬ/GenData.git
cd GenData
```

**Вопрос:** Проект склонирован? (да/нет)

---

## Шаг 4: Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

**Вопрос:** Виртуальное окружение активировано? Видите (venv) в начале строки? (да/нет)

---

## Шаг 5: Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Вопрос:** Зависимости установлены? (да/нет)

---

## Шаг 6: Настройка .env файла

```bash
# Скопируйте пример для Beget
cp .env.beget.example .env

# Отредактируйте файл
nano .env
```

Убедитесь что в файле указано:

```env
DATABASE_URL=mysql+pymysql://y90814l8_users:12345678@localhost:3306/y90814l8_users
SECRET_KEY=сгенерируйте_случайную_строку_минимум_32_символа
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_DEFAULT_PASSWORD=admin123
```

**Вопрос:** Файл .env создан и заполнен? (да/нет)

---

## Шаг 7: Инициализация базы данных

```bash
# Убедитесь что виртуальное окружение активировано
source venv/bin/activate

# Инициализируйте БД
python scripts/init_db.py
```

**Вопрос:** База данных инициализирована? Видите сообщение об успешном создании администратора? (да/нет)

---

## Шаг 8: Тестовый запуск

```bash
# Убедитесь что виртуальное окружение активировано
source venv/bin/activate

# Запустите сервер
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Вопрос:** Сервер запустился? Видите "Uvicorn running on http://0.0.0.0:8000"? (да/нет)

---

## Шаг 9: Настройка systemd для автозапуска

Остановите тестовый сервер (Ctrl+C) и создайте сервис:

```bash
# Узнайте ваш домашний каталог
echo $HOME

# Создайте файл сервиса (замените /home/ваш_логин на ваш путь)
sudo nano /etc/systemd/system/gendata.service
```

Добавьте содержимое (замените пути):

```ini
[Unit]
Description=GenData FastAPI Application
After=network.target mysql.service

[Service]
Type=simple
User=ваш_логин
Group=ваш_логин
WorkingDirectory=/home/ваш_логин/GenData
Environment="PATH=/home/ваш_логин/GenData/venv/bin"
ExecStart=/home/ваш_логин/GenData/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:

```bash
sudo systemctl daemon-reload
sudo systemctl enable gendata
sudo systemctl start gendata
sudo systemctl status gendata
```

**Вопрос:** Сервис запущен? (да/нет)

---

## Шаг 10: Настройка Nginx (если нужен домен)

Если у вас есть домен на Beget, настройте Nginx через панель управления Beget или создайте конфигурацию вручную.

---

## Полезные команды

```bash
# Статус сервиса
sudo systemctl status gendata

# Логи
sudo journalctl -u gendata -f

# Перезапуск
sudo systemctl restart gendata

# Обновление кода
cd ~/GenData
git pull
source venv/bin/activate
sudo systemctl restart gendata
```

---

## Проверка работы API

После запуска сервера проверьте:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

Или откройте в браузере:
- http://ваш_домен:8000/docs - Swagger документация
- http://ваш_домен:8000/redoc - ReDoc документация

