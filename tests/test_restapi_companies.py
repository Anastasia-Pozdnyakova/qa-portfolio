"""Автотесты для API restapi.tech
Эндпоинт: /companies
Документация: https://restapi.tech
"""

import requests

BASE_URL = "https://restapi.tech/api"


def test_tc01_get_companies_status():
    """TC-01: Базовый GET-запрос возвращает статус 200"""
    response = requests.get(f"{BASE_URL}/companies")
    assert response.status_code == 200


def test_tc01_get_companies_structure():
    """TC-01: Проверка структуры ответа (data, meta)"""
    response = requests.get(f"{BASE_URL}/companies")
    data = response.json()
    assert "data" in data, "Отсутствует поле data"
    assert "meta" in data, "Отсутствует поле meta"
    assert isinstance(data["data"], list), "data должен быть списком"

    # Если список не пуст, проверяем поля первой компании
    if len(data["data"]) > 0:
        first_company = data["data"][0]
        required_fields = [
            "company_id",
            "company_name",
            "company_address",
            "company_status",
        ]
        for field in required_fields:
            assert field in first_company, f"У компании нет поля {field}"


def test_tc02_get_companies_with_limit():
    """ТС-02: Параметр limit ограничивает количество компаний"""
    limit_value = 5
    response = requests.get(f"{BASE_URL}/companies", params={"limit": limit_value})

    # Проверка 1: статус 200
    assert response.status_code == 200

    # Проверка 2: в meta.limit пришло то, что запросили
    data = response.json()
    assert data["meta"]["limit"] == limit_value

    # Проверка 3: количество компаний в data не больше limit
    assert len(data["data"]) <= limit_value
