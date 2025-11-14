# API для вопросов и ответов

---
## Структура проекта
```
API_questions_answers/
├── alembic/                       # Миграции базы данных
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── src/                           # Основной код приложения
│   │
│   ├── api/                       # API эндпоинты
│   │   ├── __init__.py
│   │   ├── answers.py             # Эндпоинты ответов
│   │   └── questions.py           # Эндпоинты вопросов
│   │
│   ├── core/                      # Конфигурационные файлы
│   │   ├── __init__.py
│   │   ├── config.py              # Конфигурации сервиса
│   │   ├── db_config.py           # Конфигурации базы данных
│   │   ├── logging.py             # Конфигурации логирования
│   │
│   ├── logs/                      # Логи приложения (создается автоматически)
│   │   └── app.log
│   │
│   ├── models/                    # Модели данных SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py                # Базовая модель
│   │   └── questions_answers.py   # Модели вопросов и ответов
│   │
│   ├── schemas/                   # Схемы Pydantic
│   │   ├── __init__.py
│   │   └── questions_answers.py   # Схемы вопросов и ответов
│   │
│   ├── services/                  # Бизнес-логика
│   │   ├── __init__.py
│   │   └── questions_answers.py   # Логика работы с вопросами и ответами
│   │
│   └── main.py                    # Точка входа в приложение
│
├── tests/		                   # Тесты Pytest 
│   ├── __init.py__
│   ├── conftest.py	               # Фикстуры
│   ├── test_answers.py	           # Тесты эндопоинтов ответов
│   ├── test_questions.py	       # Тесты эндопоинтов вопросов
│   └── test_services.py	       # Тесты бизнес логики
│
├── .dockerignore                  # Игнорируемые файлы Docker
├── .env                           # Файл локального окружения
├── .env.docker                    # Файл Docker окружения
├── .gitignore                     # Игнорируемые файлы Git
├── alembic.ini                    # Конфигурация Alembic
├── docker-compose.yml             # Docker конфигурация
├── docker-entrypoint.sh           # Скрипт инициализации
├── Dockerfile                     # Сборка образа FastAPI
├── pyproject.toml                 # Конфигурация проекта
└── requirements.txt               # Список зависимостей
```
---
## Запуск проекта
### Локальный запуск
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/DiMiRka/API_questions_answers
   cd API_questions_answers
   ```
2. Создайте и активируйте виртуальное окружение:
    ```bash
    python -m venv venv
    source .venv/bin/activate # для Linux/MacOS
    venv\Scripts\activate     # для Windows
   ```
3. Установите зависимости:
    ```bash
    pip install -r requirements.txt
   ```
4. Настройте переменные окружения в .env
   ```
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=QuestionAnswer
   POSTGRES_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/QuestionAnswer
   HOST=localhost
   PORT=8000
   RELOAD=true
   DOCKER_MODE=0
   ```
5. Примените миграции alembic:
   ```bash
   alembic stamp head
   alembic revision --autogenerate -m "create tables"
   alembic upgrade head
   ```
6. Запустите сервис:
   ```bash
    python src/main.py
   ```
### Запуск через Docker
   ```bash
      docker-compose up --build -d
   ```
#### Система автоматически:
- Создаст и запустит контейнеры
- Применит все миграции
- Запустит FastAPI сервер
---
## Документация API
После запуска сервера доступны интерактивная документации:\
**Swagger UI**: `http://localhost:8000/api/openapi`

### Основные эндпоинты
GET / - Проверка работоспособности API
#### Questions
* GET /questions/ - Получение списка всех вопросов с ответами
* POST /questions/ - Создание нового вопроса
* GET /questions/{question_id} - Получение вопроса по ID с ответами на него
* DELETE /questions/{question_id} - Удаление вопроса и связанных ответов
#### Answers
* POST /answers/question/{question_id} - Добавление ответа к вопросу
* GET /answers/{answer_id} - Получение ответа по ID
* DELETE /answers/{answer_id} - Удаление ответа
