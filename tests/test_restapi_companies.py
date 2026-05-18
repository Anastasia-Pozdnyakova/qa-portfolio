"""Автотесты для API restapi.tech
Эндпоинт: /companies
Документация: https://restapi.tech
"""

import requests
import json

# ========== Константы ==========
BASE_URL = "https://restapi.tech/api"
COMPANY_REQUIRED_FIELDS = [
    "company_id",
    "company_name",
    "company_address",
    "company_status",
]


# ========== Вспомогательные функции ==========
def validate_content_type(response, expected_type="application/json"):
    """Проверяет заголовок Content-Type."""
    content_type = response.headers.get("Content-Type")
    assert (
        expected_type in content_type
    ), f"Content-Type некорректен: '{content_type}'. Ожидался '{expected_type}'"


def get_validated_json(response):
    """Проверяет, что ответ — валидный JSON, и возвращает распарсенные данные."""
    try:
        data = response.json()
        return data
    except json.JSONDecodeError:
        assert False, f"Ответ не является валидным JSON. Тело {response.text[:200]}"


def validate_response_structure(data, required_keys):
    """Проверяет наличие обязательных полей в ответе."""
    for key in required_keys:
        assert key in data, f"Отсутствует поле '{key}'"


def validate_company_fields(company, required_fields):
    """Проверяет обязательные поля у компании."""
    for field in required_fields:
        assert field in company, f"У компании нет поля '{field}'"


# ========== Тесты ==========
def test_tc01_get_all_companies():
    """TC-01: Базовый GET-запрос на получение всех компаний"""
    response = requests.get(f"{BASE_URL}/companies")

    assert (
        response.status_code == 200
    ), f"Ожидался статус 200, но получен {response.status_code}"

    # Проверка Content-Type
    validate_content_type(response)

    # Парсинг JSON
    data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(data, ["data", "meta"])

    # Если список не пуст, проверяем поля первой компании
    if len(data["data"]) > 0:
        validate_company_fields(data["data"][0], COMPANY_REQUIRED_FIELDS)


def test_tc02_get_companies_with_limit():
    """ТС-02: Параметр limit ограничивает количество компаний"""
    limit_value = 5
    response = requests.get(f"{BASE_URL}/companies", params={"limit": limit_value})

    assert (
        response.status_code == 200
    ), f"Ожидался статус 200, но получен {response.status_code}"

    # Проверка Content-Type
    validate_content_type(response)

    # Парсинг JSON
    data = get_validated_json(response)

    # Проверка meta.limit
    assert data["meta"]["limit"] == limit_value

    # Количество компаний в data не больше limit
    assert len(data["data"]) <= limit_value


def test_tc03_get_companies_with_offset():
    """ТС-03: Параметр offset сдвигает количество компаний"""
    offset_value = 2

    # Контрольный запрос без offset и парсинг JSON
    response_base = requests.get(f"{BASE_URL}/companies")
    base_data = get_validated_json(response_base)

    # ID компании, которая должна стать первой после сдвига
    expected_company_id = base_data["data"][offset_value]["company_id"]

    # Запрос с offset
    response = requests.get(f"{BASE_URL}/companies", params={"offset": offset_value})

    assert (
        response.status_code == 200
    ), f"Ожидался статус 200, но получен {response.status_code}"
    data = get_validated_json(response)
    assert data["meta"]["offset"] == offset_value
    assert len(data["data"]) > 0

    # Главная проверка пагинации
    actual_company_id = data["data"][0]["company_id"]
    assert expected_company_id == actual_company_id
