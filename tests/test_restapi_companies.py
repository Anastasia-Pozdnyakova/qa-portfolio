"""Автотесты для API restapi.tech
Эндпоинт: /companies
Документация: https://restapi.tech
"""

import requests

BASE_URL = "https://restapi.tech/api"


def test_get_companies_returns_200():
    """Проверяет, что GET /companies возвращает статус 200"""
    response = requests.get(f"{BASE_URL}/companies")
    assert response.status_code == 200


def test_get_companies_returns_data_with_required_fields():
    """Проверяет, что ответ содержит поля data и meta"""
    response = requests.get(f"{BASE_URL}/companies")
    data = response.json()

    # Проверяем структуру ответа
    assert "data" in data, "Ответ должен содержать поле 'data'"
    assert "meta" in data, "Ответ должен содержать поле 'meta'"
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
