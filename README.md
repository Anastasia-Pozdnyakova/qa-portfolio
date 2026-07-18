# QA — Backend Autotests

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![pytest](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](https://pytest.org)

Портфолио с автотестами для тестирования REST API (restapi.tech).  
Тесты написаны на pytest + requests, коллекция Postman прилагается.

---

## 🔧 Технологии

- **Python 3.10+** — основной язык программирования
- **pytest** — фреймворк для написания и запуска тестов
- **requests** — библиотека для выполнения HTTP‑запросов
- **Postman** — инструмент для ручного и автоматизированного тестирования API
- **SQLite** — проверка данных через БД
- **GitHub** — платформа для хранения портфолио

---

## 🗂 Структура проекта

| Путь | Описание |
|------|----------|
| `tests/test_restapi_companies.py` | pytest автотесты для `/companies` |
| `tests/test_restapi_users.py` | pytest автотесты для `/users` |
| `tests/test_restapi_auth.py` | pytest автотесты для `/auth` |
| `tests/test_api_sql.py` | тесты интеграции API + SQLite |
| `postman/restapi-tech-collection.json` | Postman коллекция |
| `test-cases/companies.md` | Тест-кейсы для `/companies` |
| `test-cases/users.md` | Тест-кейсы для `/users` |
| `assets/pytest_results.png` | Скриншот результатов |
| `.gitignore` | Исключённые файлы |
| `LICENSE` | Лицензия MIT |
| `README.md` | Документация |

---

## 🚀 Запуск автотестов (pytest)

### 1. Установка зависимостей:

```bash
pip install pytest requests
```

### 2. Запуск всех тестов:

```bash
pytest tests/ -v
```

### 3. Запуск одного теста:

```bash
pytest tests/test_restapi_companies.py::test_tc01_get_all_companies -v
```

### 4. Запуск с подробным выводом и показом результатов для пройденных тестов:

```bash
pytest tests/ -v -s
```

### 5. Запуск тестов с генерацией отчёта в формате HTML:

```bash
pytest tests/ --html=report.html
```

### 6. Запуск Postman коллекции через Newman

```bash
newman run postman/restapi-tech-collection.json --environment postman/restapi-tech-environment.json
```
---

## 🚀 Запуск Postman коллекции через Newman

### 1. Установка Newman:

```bash
npm install -g newman
```

### 2. Запуск коллекции через Newman:

```bash
newman run postman/restapi-tech-collection.json --environment postman/restapi-tech-environment.json
```

---

## 📮 Postman коллекция

Как импортировать и настроить:

1. Откройте Postman.

2. Нажмите Import → выберите файл postman/restapi-tech-collection.json.

3. Создайте окружение (Environment) с переменной:
BASE_URL = https://restapi.tech/api

4. Запустите запросы и проверьте результаты тестов во вкладке Test Results.

Что содержит коллекция:

1. Запросы к эндпоинтам API.

2. Автоматизированные проверки на JavaScript.

---

## 🧪 Покрытие тестами

### GET /api/companies

| TC | Проверка | Ожидаемый статус | Статус |
|----|----------|------------------|--------|
| TC-01 | Базовый GET (структура, поля) | 200 | ✅ готов |
| TC-02 | Параметр `limit=5` | 200 | ✅ готов |
| TC-03 | Пагинация `offset=2` | 200 | ✅ готов |
| TC-04 | Фильтрация `status=ACTIVE` | 200 | ✅ готов |
| TC-05 | Невалидный `status=INVALID` | 422 | ✅ готов |
| TC-06 | Граничный `limit=0` | 200 | ✅ готов |
| TC-07 | Невалидный `limit=abc` | 422 | ✅ готов |
| TC-08 | Граничный `offset=-1` | 200 | ✅ готов |

### GET /api/companies/id

| TC | Проверка | Ожидаемый статус | Статус |
|----|----------|------------------|--------|
| TC-09 | Получение компании id=1 (без Accept-Language) | 200 | ✅ готов |
| TC-10 | Получение компании с заголовком Accept-Language: RU | 200 | ✅ готов |
| TC-11 | Несуществующий id=9999 | 404 | ✅ готов |
| TC-12 | Невалидный id=abc | 422 | ✅ готов |

### 🗄️ SQL + API интеграция

| Тест | Проверка | Статус |
|------|----------|--------|
| `test_sql_with_api_companies` | Сохранение одной компании в БД | ✅ готов |
| `test_sql_save_all_companies` | Сохранение всех компаний в БД | ✅ готов |
| `test_sql_filter_active_companies` | Фильтрация по статусу в SQL | ✅ готов |

### GET /api/users

| TC | Проверка | Ожидаемый статус | Статус |
|----|----------|------------------|--------|
| TC-13 | Базовый GET (структура, поля) | 200 | ✅ готов |
| TC-14 | Параметр `limit=5` | 200 | ✅ готов |
| TC-15 | Параметр `offset=2` | 200 | ✅ готов |
| TC-16 | Невалидный `limit=abc` | 422 | ✅ готов |

### POST /api/users

| TC | Проверка | Ожидаемый статус | Статус |
|----|----------|------------------|--------|
| TC-17 | POST-запрос на создание пользователя | 201 | ✅ готов |
| TC-18 | Без обязательного поля `last_name` | 422 | ✅ готов |
| TC-19 | На несуществующий `company_id` | 404 | ✅ готов |
| TC-20 | На невалидный `company_id` | 400 | ✅ готов |

### GET /api/users/{id}

| TC | Проверка | Ожидаемый статус | Статус |
|----|----------|------------------|--------|
| TC-21 | GET-запрос на получение юзера по ID| 200 | ✅ готов |
| TC-22 | На несуществующий `user_id=9999` | 404 | ✅ готов |
| TC-23 | На невалидный `user_id=abc` | 422 | ✅ готов |

### PUT /api/users/{user_id}

| TC | Проверка | Ожидаемый статус | Статус |
|----|----------|------------------|--------|
| TC-24 | Обновление существующего пользователя | 200 | ✅ готов |
| TC-25 | Обновление без обязательного поля `last_name` | 422 | ✅ готов |
| TC-26 | Обновление с несуществующей компанией | 404 | ✅ готов |
| TC-27 | Обновление с неактивной компанией | 400 | ✅ готов |

### DELETE /api/users/{user_id}

| TC | Проверка | Ожидаемый статус | Статус |
|----|----------|------------------|--------|
| TC-28 | Удаление существующего пользователя | 202 | ✅ готов |
| TC-29 | Удаление несуществующего пользователя | 404 | ✅ готов |
| TC-30 | Повторное удаление того же пользователя | 404 | ✅ готов |
| TC-31 | Удаление с невалидным ID | 422 | ✅ готов |

### 🔐 Auth

| TC | Проверка | Ожидаемый статус | Статус |
|----|----------|------------------|--------|
| TC-32 | Успешная регистрация | 200 | ✅ готов |
| TC-33 | Невалидный пароль | 403 | ✅ готов |
| TC-34 | Логин < 3 символов | 422 | ✅ готов |
| TC-35 | Без поля `password` | 422 | ✅ готов |
| TC-36 | /me с валидным токеном | 200 | ✅ готов |
| TC-37 | /me без токена | 401 | ✅ готов |
| TC-38 | /me с невалидным токеном | 403 | ✅ готов |
| TC-39 | Истечение токена | 403 | ✅ готов |

---

## 📸 Результаты тестов

![Результаты pytest](assets/pytest_results.png)

---

## 📋 Примечания

1. Перед запуском тестов убедитесь, что API доступно по указанному BASE_URL.

2. Для Postman тестов проверьте актуальность переменных окружения.

3. При изменении эндпоинтов обновите соответствующие тест‑кейсы в test-cases/.

---

## 📄 Лицензия

Проект распространяется под лицензией MIT.

---

## 🔗 Ссылка на портфолио

https://github.com/Anastasia-Pozdnyakova/qa-portfolio

---

📫 **Контакты:** GitHub [Anastasia-Pozdnyakova](https://github.com/Anastasia-Pozdnyakova) · Telegram [@nastyapoze](https://t.me/@nastyapoze) · Email poznast59@ya.ru