# ExecutiveFinderBot — Telegram бот для поиска временных сотрудников

Telegram бот для размещения и поиска временных исполнителей на разовые задания.  
Аналог YouDo, но с управлением через Telegram и администрированием через бота.

## Функциональность

### Для исполнителей
- Автоматическая регистрация при первом запуске
- Просмотр доступных заданий
- Отклик на задания
- Просмотр своих откликов и статусов

### Для администраторов
- Публикация новых заданий
- Редактирование и удаление заданий
- Проверка откликов
- Пополнение баланса пользователей (команда администратора)
- Просмотр статистики

## Технологии

- **Python 3.10+**
- **aiogram 3.x** — асинхронная библиотека для Telegram Bot API
- **asyncpg** — асинхронный драйвер для PostgreSQL
- **PostgreSQL** — основная база данных
- **python-dotenv** — управление переменными окружения

## Установка и запуск

### 1. Клонировать репозиторий
git clone https://github.com/trythisenergy39/telegram-bot-project-employee.git
cd telegram-bot-project-employee

###2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows

###3. Установить зависимости
pip install -r requirements.txt

###4. Настроить переменные окружения
Создать файл secret.env (не добавлять в репозиторий!):

BOT_TOKEN=токен_бота_от_BotFather
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bot_db
DB_USER=postgres
DB_PASSWORD=ваш_пароль
ADMIN_IDS=123456789,987654321

###5. Настроить базу данных
Создать базу данных PostgreSQL и выполнить миграции (файлы в папке migrations/)

##6. Запустить бота
python bot.py

##Структура проекта
text
├── bot.py              # Точка входа
├── handlers/           # Обработчики команд и сообщений
├── keyboards/          # Клавиатуры (inline, reply)
├── database/           # Работа с БД (запросы, модели)
├── utils/              # Вспомогательные функции
├── config.py           # Конфигурация (чтение secret.env)
└── requirements.txt    # Зависимости
