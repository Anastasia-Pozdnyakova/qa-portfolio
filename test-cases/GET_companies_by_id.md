# Автотесты: GET /api/companies/{company_id}

## Базовые данные
- **Endpoint:** `GET {{BASE_URL}}/companies/{company_id}`
- **Headers:** `Accept: application/json`

---

## TC-09: Получение компании по существующему ID (без Accept-Language)
- **ID:** 1
- **Заголовки:** нет
- **Ожидаемый статус:** 200
- **Ожидаемые поля:**
  - `company_id` (integer)
  - `company_name` (string)
  - `company_address` (string)
  - `company_status` (string, одно из: ACTIVE, CLOSED, BANKRUPT)
  - `description_lang` (list)

---

## TC-10: Получение компании с Accept-Language: RU
- **ID:** 1
- **Заголовки:** `Accept-Language: RU`
- **Ожидаемый статус:** 200
- **Ожидаемые поля:** `company_id`, `company_name`, `company_address`, `company_status`, `description` (строка)
- **Дополнительно:** поле `description_lang` отсутствует

---

## TC-11: Несуществующий ID
- **ID:** 9999
- **Ожидаемый статус:** 404
- **Ожидаемая структура:** `detail.reason`

---

## TC-12: Невалидный ID (не число)
- **ID:** abc
- **Ожидаемый статус:** 422
- **Ожидаемая структура:** `detail` (массив ошибок)