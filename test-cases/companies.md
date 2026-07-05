# Тест-кейсы для api/companies

## Базовые данные
- **Документация:** `https://restapi.tech`
- **Эндпоинт:** `/companies`
- **Headers:** `Accept: application/json`

---

## GET /api/companies

### TC-01: Базовый запрос без параметров
- **Параметры:** (нет)
- **Ожидаемый статус:** 200
- **Ожидаемая структура ответа:**
  - `data` — тип: list (массив)
  - `meta` — тип: object
- **Ожидаемые поля в data[0]** (если массив не пуст):
  - `company_id` (integer)
  - `company_name` (string)
  - `company_address` (string)
  - `company_status` (string, одно из: ACTIVE, CLOSED, BANKRUPT)

### TC-02: Параметр limit
- **Параметры:** `limit=5`
- **Ожидаемый статус:** 200
- **Ожидаемая структура:** `meta.limit` == 5
- **Дополнительно:** длина `data` <= 5

### TC-03: Параметр offset
- **Параметры:** `offset=2`
- **Ожидаемый статус:** 200
- **Ожидаемая структура:** `meta.offset` == 2

### TC-04: Фильтрация по статусу
- **Параметры:** `status=ACTIVE`
- **Ожидаемый статус:** 200
- **Ожидаемая структура:** 
  - У всех элементов в `data` поле `company_status` == "ACTIVE"

### TC-05: Негатив — неверный статус
- **Параметры:** `status=INVALID`
- **Ожидаемый статус:** 422
- **Ожидаемая структура:** 
  - `detail` — массив с описанием ошибки

### TC-06: Негатив — limit меньше 1
- **Параметры:** `limit=0`
- **Ожидаемый статус:** 422

### TC-07: Негатив — limit не число
- **Параметры:** `limit=abc`
- **Ожидаемый статус:** 422

### TC-08: Негатив — offset отрицательный
- **Параметры:** `offset=-1`
- **Ожидаемый статус:** 422

### TC-09: Без заголовка Accept
- **Шаги:** GET `/companies` без заголовка Accept
- **Ожидаемый результат:** Статус 406 (Not Acceptable) или 200 с JSON по умолчанию

### TC-10: Неверный метод (POST вместо GET)
- **Шаги:** POST `/companies`
- **Ожидаемый результат:** Статус 405 (Method Not Allowed)

---

## GET /api/companies/{company_id}

### TC-09: Получение компании по существующему ID (без Accept-Language)
- **ID:** 1
- **Заголовки:** нет
- **Ожидаемый статус:** 200
- **Ожидаемые поля:**
  - `company_id` (integer)
  - `company_name` (string)
  - `company_address` (string)
  - `company_status` (string, одно из: ACTIVE, CLOSED, BANKRUPT)
  - `description_lang` (list)

### TC-10: Получение компании с Accept-Language: RU
- **ID:** 1
- **Заголовки:** `Accept-Language: RU`
- **Ожидаемый статус:** 200
- **Ожидаемые поля:** `company_id`, `company_name`, `company_address`, `company_status`, `description` (строка)
- **Дополнительно:** поле `description_lang` отсутствует

### TC-11: Несуществующий ID
- **ID:** 9999
- **Ожидаемый статус:** 404
- **Ожидаемая структура:** `detail.reason`

### TC-12: Невалидный ID (не число)
- **ID:** abc
- **Ожидаемый статус:** 422
- **Ожидаемая структура:** `detail` (массив ошибок)