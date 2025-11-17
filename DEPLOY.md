# Инструкция по развертыванию на сервере Beget

## Шаг 1: Подключение к серверу через SSH

Выполните в терминале:

```bash
ssh ваш_логин@ваш_домен.beget.com
```

Или если у вас есть IP адрес:

```bash
ssh ваш_логин@IP_АДРЕС
```

**Вопрос:** Подключились ли вы к серверу? (да/нет)

---

## Шаг 2: Проверка окружения на сервере

После подключения выполните команды для проверки:

```bash
python3 --version
git --version
which python3
pwd
```

**Вопрос:** Какие версии Python и Git установлены? Видите ли вы версии? (да/нет)

---

## Шаг 3: Клонирование проекта из Git

```bash
# Перейдите в нужную директорию (обычно /home/ваш_логин или /var/www)
cd ~
# Или если у вас есть специальная директория для проектов
# cd /var/www/ваш_домен

# Клонируйте репозиторий
git clone https://github.com/ВАШ_ПОЛЬЗОВАТЕЛЬ/GenData.git
# Или если используете SSH ключ:
# git clone git@github.com:ВАШ_ПОЛЬЗОВАТЕЛЬ/GenData.git

cd GenData
```

**Вопрос:** Проект склонирован? Видите ли вы файлы проекта (ls -la)? (да/нет)

---

## Шаг 4: Создание виртуального окружения

```bash
# Установите venv если нужно
sudo apt-get update
sudo apt-get install python3-venv -y

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate
```

**Вопрос:** Виртуальное окружение создано и активировано? Видите ли вы (venv) в начале строки? (да/нет)

---

## Шаг 5: Установка зависимостей

```bash
# Убедитесь что виртуальное окружение активировано
# Установите зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

**Вопрос:** Зависимости установлены без ошибок? (да/нет)

---

## Шаг 6: Настройка PostgreSQL

```bash
# Проверьте, установлен ли PostgreSQL
psql --version

# Если не установлен, установите:
sudo apt-get install postgresql postgresql-contrib -y

# Создайте базу данных и пользователя
sudo -u postgres psql
```

В psql выполните:

```sql
CREATE DATABASE gendata;
CREATE USER gendata_user WITH PASSWORD 'ваш_надежный_пароль';
ALTER ROLE gendata_user SET client_encoding TO 'utf8';
ALTER ROLE gendata_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE gendata_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE gendata TO gendata_user;
\q
```

**Вопрос:** База данных создана? (да/нет)

---

## Шаг 7: Настройка переменных окружения

```bash
# Создайте файл .env
nano .env
```

Добавьте в файл (замените значения на свои):

```env
DATABASE_URL=postgresql://gendata_user:ваш_надежный_пароль@localhost:5432/gendata
SECRET_KEY=сгенерируйте_случайную_строку_для_продакшена
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ADMIN_DEFAULT_PASSWORD=admin123
```

Сохраните: `Ctrl+O`, Enter, `Ctrl+X`

**Вопрос:** Файл .env создан и заполнен? (да/нет)

---

## Шаг 8: Инициализация базы данных

```bash
# Убедитесь что виртуальное окружение активировано
source venv/bin/activate

# Инициализируйте БД
python scripts/init_db.py
```

**Вопрос:** База данных инициализирована? Видите ли вы сообщение об успешном создании администратора? (да/нет)

---

## Шаг 9: Тестовый запуск сервера

```bash
# Убедитесь что виртуальное окружение активировано
source venv/bin/activate

# Запустите сервер
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Вопрос:** Сервер запустился? Видите ли вы сообщение "Uvicorn running on http://0.0.0.0:8000"? (да/нет)

---

## Шаг 10: Настройка systemd для автозапуска

Остановите тестовый сервер (Ctrl+C) и создайте systemd сервис:

```bash
sudo nano /etc/systemd/system/gendata.service
```

Добавьте содержимое (замените пути на ваши):

```ini
[Unit]
Description=GenData FastAPI Application
After=network.target postgresql.service

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

Сохраните и выполните:

```bash
# Перезагрузите systemd
sudo systemctl daemon-reload

# Включите автозапуск
sudo systemctl enable gendata

# Запустите сервис
sudo systemctl start gendata

# Проверьте статус
sudo systemctl status gendata
```

**Вопрос:** Сервис запущен и работает? (да/нет)

---

## Шаг 11: Настройка Nginx (опционально, для домена)

```bash
# Установите Nginx
sudo apt-get install nginx -y

# Создайте конфигурацию
sudo nano /etc/nginx/sites-available/gendata
```

Добавьте:

```nginx
server {
    listen 80;
    server_name ваш_домен.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активируйте:

```bash
sudo ln -s /etc/nginx/sites-available/gendata /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Вопрос:** Nginx настроен? (да/нет)

---

## Полезные команды для управления

```bash
# Проверить статус сервиса
sudo systemctl status gendata

# Остановить сервис
sudo systemctl stop gendata

# Запустить сервис
sudo systemctl start gendata

# Перезапустить сервис
sudo systemctl restart gendata

# Посмотреть логи
sudo journalctl -u gendata -f

# Обновить код из Git
cd ~/GenData
git pull
source venv/bin/activate
sudo systemctl restart gendata
```

