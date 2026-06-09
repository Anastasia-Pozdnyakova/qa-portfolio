"""Автотесты для API restapi.tech
Эндпоинт: /companies/{id}
Документация: https://restapi.tech
"""

import requests
import json
import constants

# ========== Настройки ==========
BASE_URL = "https://restapi.tech/api"
TIMEOUT = 5
COMPANIES_ENDPOINT = f"{BASE_URL}/companies"


# ========== Вспомогательные функции ==========
def validate_content_type(response, expected_type="application/json"):
    """Проверяет заголовок Content-Type"""
    content_type = response.headers.get("Content-Type", "")
    assert content_type.startswith(
        expected_type
    ), f"Content-Type некорректен: '{content_type}'. Ожидался '{expected_type}'"


def get_validated_json(response):
    """Проверяет, что ответ — валидный JSON, и возвращает распарсенные данные"""
    try:
        data = response.json()
        return data
    except json.JSONDecodeError:
        assert False, f"Ответ не является валидным JSON. Тело {response.text[:200]}"


def validate_response_structure(data, required_keys):
    """Проверяет наличие обязательных полей в ответе"""
    for key in required_keys:
        assert key in data, f"Отсутствует поле '{key}'"


# ========== Тесты ==========
def test_tc09_get_company_by_id_1():
    """TC-09: GET-запрос на получение компании по ID"""

    # Подготовка данных
    company_id = 1

    # GET-запрос
    try:
        response = requests.get(f"{COMPANIES_ENDPOINT}/{company_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {COMPANIES_ENDPOINT}/{company_id} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {COMPANIES_ENDPOINT}/{company_id} вернул статус "
        f"{response.status_code}. Ожидался 200"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка полей компании
    validate_response_structure(data, constants.COMPANY_REQUIRED_FIELDS)

    # Проверка, что ID компании в ответе равен запрашиваемому ID
    assert (
        data["company_id"] == company_id
    ), f"Запрошен {company_id}, получен {data['company_id']}"

    # Проверка полей переводов
    translation = data["description_lang"]
    assert translation, f"description_lang пуст"
    assert isinstance(translation, list), f"description_lang должен быть массивом"

    for item in translation:
        for field in constants.TRANSLATION_REQUIRED_FIELDS:
            assert field in item, f"В переводе отсутствует поле {field}"
        assert isinstance(
            item["translation_lang"], str
        ), f"translation_lang должен быть строкой"
        assert isinstance(item["translation"], str), f"translation должен быть строкой"


def test_tc10_get_company_by_id_1_with_accept_language_ru():
    """TC-10: GET-запрос на получение компании по ID с заголовком определяющим язык"""

    # Подготовка данных
    company_id = 1
    headers = {"Accept-Language": "RU"}

    # GET-запрос
    try:
        response = requests.get(
            f"{COMPANIES_ENDPOINT}/{company_id}", headers=headers, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {COMPANIES_ENDPOINT}/{company_id} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {COMPANIES_ENDPOINT}/{company_id} вернул статус "
        f"{response.status_code}. Ожидался 200"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка полей компании
    validate_response_structure(data, constants.COMPANY_REQUIRED_FIELDS)

    # Проверка, что ID компании в ответе равен запрашиваемому ID
    assert (
        data["company_id"] == company_id
    ), f"Запрошен {company_id}, получен {data['company_id']}"

    # Проверка, что description есть, что строка и не пустая
    assert "description" in data, "Поле description отсутствует"
    description = data["description"]
    assert isinstance(description, str), "Поле description не строка"
    assert description, "Поле description пустое"

    # Проверка, что description_lang отсутствует
    assert (
        "description_lang" not in data
    ), "Массив description_lang должен отсутствовать"


def test_tc11_get_company_by_id_9999_not_found():
    """TC-11: GET-запрос на получение компании по несуществующему ID"""

    # Подготовка данных
    company_id = 9999

    # GET-запрос
    try:
        response = requests.get(f"{COMPANIES_ENDPOINT}/{company_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {COMPANIES_ENDPOINT}/{company_id} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 404, (
        f"Запрос к {COMPANIES_ENDPOINT}/{company_id} вернул статус "
        f"{response.status_code}. Ожидался 404"
    )
    validate_content_type(response)
    error_data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in error_data, "Поле detail отсутствует"
    assert "reason" in error_data["detail"], "Поле reason отсутствует"
    reason = error_data["detail"]["reason"]
    assert isinstance(reason, str), "Поле reason не строка"
    assert reason, "Поле reason пустое"
    assert (
        str(company_id) in reason
    ), f"В тексте ошибки нет упоминания об id={company_id}"


def test_tc12_get_company_by_id_abc_invalid():
    """TC-12: GET-запрос на получение компании по невалидному ID"""

    # Подготовка данных
    company_id = "abc"

    # GET-запрос
    try:
        response = requests.get(f"{COMPANIES_ENDPOINT}/{company_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {COMPANIES_ENDPOINT}/{company_id} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 422, (
        f"Запрос к {COMPANIES_ENDPOINT}/{company_id} вернул статус "
        f"{response.status_code}. Ожидался 422"
    )
    validate_content_type(response)
    error_data = get_validated_json(response)

    # Проверка структуры detail
    assert "detail" in error_data, "В ответе отсутствует поле detail"
    detail = error_data["detail"]
    assert isinstance(detail, list), "detail должен быть массивом"
    assert len(detail) > 0, "detail пуст"

    # Извлекаем первую ошибку
    first_error = detail[0]

    # Проверка обязательных полей ошибки
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"В ошибке отсутствует поле '{field}'"

    # Проверка, что сообщение об ошибке содержит упоминание допустимого типа integer
    assert (
        "integer" in first_error["msg"]
    ), "Сообщение об ошибке не содержит упоминание об integer"
