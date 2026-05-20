# QA — Backend Autotests

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![pytest](https://img.shields.io/badge/pytest-passing-brightgreen.svg)](https://pytest.org)

Портфолио с автотестами для тестирования REST API (restapi.tech).  
Проверяются GET-запросы с параметрами `limit`, `offset`, `status`.  
Тесты написаны на pytest + requests, коллекция Postman прилагается.

---

## 🔧 Технологии

* **Python 3.10+** — основной язык программирования.
* **pytest** — фреймворк для написания и запуска тестов.
* **requests** — библиотека для выполнения HTTP‑запросов.
* **Postman** — инструмент для ручного и автоматизированного тестирования API (коллекция тестов на JavaScript).
* **GitHub** — платформа для хранения кода и демонстрации портфолио.

---

## 📁 Структура проекта

qa-portfolio/
├── tests/
│ └── test_restapi_companies.py
├── postman/
│ └── restapi-tech-collection.json
├── test-cases/
│ └── GET_companies.md
├── assets/
│ └── pytest_result.png
├── .gitignore
├── LICENSE
└── README.md

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

## 🧪 Тест‑кейсы для эндпоинта api/companies

TC-01 — Получение всех компаний

статус 200, структура data/meta, Content-Type, JSON

TC-02 — Ограничение количества (limit=5)

meta.limit = 5, длина data ≤ limit

TC-03 — Пагинация (offset=2)

meta.offset = 2, сдвиг списка

TC-04 — Фильтрация по статусу (status=ACTIVE)

возвращаются только компании со статусом ACTIVE

---

## 📊 Пример вывода тестов

collected 4 items

test_tc01_get_all_companies PASSED
test_tc02_get_companies_with_limit PASSED
test_tc03_get_companies_with_offset PASSED
test_tc04_get_companies_filter_by_active_status PASSED

============================== 4 passed in 0.35s ==============================

---

## 📝 Примечания

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

📫 Контакты
GitHub: [Anastasia-Pozdnyakova](https://github.com/Anastasia-Pozdnyakova)
Telegram: [@poznast](https://t.me/@poznast)
Email: poznast59@ya.ru
