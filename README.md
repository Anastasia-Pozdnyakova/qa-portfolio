# QA Portfolio — Backend Autotests

Портфолио с автотестами для тестирования REST API.  
Навыки автоматизации тестирования бэкенда на Python + pytest, а также работу с Postman и GitHub.


## 🔧 Технологии

- Python 3.10+
- pytest — фреймворк для тестирования
- requests — HTTP-запросы
- Postman — коллекция тестов (JS)
- GitHub — хранение портфолио


## 📁 Структура проекта

qa-portfolio/
├── tests/
│ └── test_restapi_companies.py # pytest автотесты
├── postman/
│ └── restapi-tech-collection.json # коллекция Postman
├── test-cases/
│ └── GET_companies.md # тест-кейсы документация
├── .gitignore
└── README.md


## 🚀 Запуск автотестов (pytest)

### 1. Установка зависимостей

```bash
pip install pytest requests

### 2. Запуск всех тестов

pytest tests/ -v

### 3. Запуск одного теста

pytest tests/test_restapi_companies.py::test_tc01_get_all_companies -v
```

## 📮 Postman коллекция

1. Откройте Postman  
2. Нажмите Import → выберите файл `postman/restapi-tech-collection.json`  
3. Создайте окружение с переменной:  
   `BASE_URL = https://restapi.tech/api`

Коллекция содержит 4 запроса с автотестами на JS.

## 🧪 Тест-кейсы (покрытие)

TC-01 — Получение всех компаний
статус 200, структура data/meta, Content-Type, JSON

TC-02 — Ограничение количества (limit=5)
meta.limit = 5, длина data ≤ limit

TC-03 — Пагинация (offset=2)
meta.offset = 2, сдвиг списка (первая компания после сдвига = третья без сдвига)

TC-04 — Фильтрация по статусу (status=ACTIVE)
возвращаются только компании со статусом ACTIVE


## 📊 Пример вывода тестов
```bash
collected 4 items

test_tc01_get_all_companies PASSED
test_tc02_get_companies_with_limit PASSED
test_tc03_get_companies_with_offset PASSED
test_tc04_get_companies_filter_by_active_status PASSED

============================== 4 passed in 0.35s ==============================
```

## 🔗 Ссылка на портфолио

[Anastasia Pozdnyakova](https://github.com/Anastasia-Pozdnyakova/qa-portfolio)
---

📫 Контакты
GitHub: [Anastasia-Pozdnyakova](https://github.com/Anastasia-Pozdnyakova)
Email: poznast59@ya.ru
Telegram: @poznast
