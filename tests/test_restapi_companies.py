"""Автотесты для API restapi.tech
Эндпоинт: /companies
Документация: https://restapi.tech
Тесты: TC-1 – TC-12
"""

import pytest
import allure
from utils.helpers import (
    validate_content_type,
    get_validated_json,
    validate_response_structure,
    validate_meta,
    validate_422_error,
    validate_404_error,
    validate_fields_presence_and_type,
)
from data.expected_status import EXPECTED_STATUS
from api.companies_api import CompaniesAPI
from data.companies_data import (
    COMPANY_REQUIRED_FIELDS,
    COMPANY_REQUIRED_FIELDS_AND_TYPES,
    TRANSLATION_REQUIRED_FIELDS,
)

api = CompaniesAPI()


# ========== ТЕСТЫ ==========
@pytest.mark.smoke
@allure.feature("Companies")
@allure.story("GET /companies")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_all_companies():
    """TC-01: Базовый GET-запрос на получение всех компаний"""

    response = api.get_all_companies()

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    # Проверка заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(data, ["data", "meta"])

    companies = data["data"]

    # Валидация обязательных полей первой компании
    assert companies, "Список компаний пуст"
    validate_fields_presence_and_type(companies[0], COMPANY_REQUIRED_FIELDS_AND_TYPES)


@pytest.mark.parametrize(
    "limit_value, expected_status",
    [
        (5, EXPECTED_STATUS["valid"]),
        (0, EXPECTED_STATUS["valid"]),
        ("abc", EXPECTED_STATUS["validation_error"]),
    ],
)
@allure.feature("Companies")
@allure.story("GET /companies")
@allure.severity(allure.severity_level.NORMAL)
def test_companies_limit(limit_value, expected_status):
    """TC-02, TC-06, TC-07: Параметризованный тест для limit"""

    response = api.get_companies_with_params(limit=limit_value)

    # Проверка статуса
    assert (
        response.status_code == expected_status
    ), f"Ожидался статус {expected_status}, получен {response.status_code}"

    # Если статус валидный, парсим JSON, проверяем структуру
    if expected_status == EXPECTED_STATUS["valid"]:
        data = get_validated_json(response)
        validate_response_structure(data, ["data", "meta"])
        validate_meta(data["meta"], expected_limit=limit_value)

        if limit_value == 0:
            assert data["data"] == [], "При limit=0 data должен быть пустым"
        else:
            assert (
                len(data["data"]) <= limit_value
            ), "Количество компаний не должно превышать limit"

    else:
        # 422 — проверяем структуру ошибки
        error_data = get_validated_json(response)
        validate_422_error(error_data, "limit")


@pytest.mark.parametrize(
    "offset_value, expected_status, expected_first_id",
    [
        (2, EXPECTED_STATUS["valid"], 3),
        (-1, EXPECTED_STATUS["valid"], 1),
    ],
)
@allure.feature("Companies")
@allure.story("GET /companies")
@allure.severity(allure.severity_level.NORMAL)
def test_companies_offset(offset_value, expected_status, expected_first_id):
    """TC-03, TC-08: Параметризованный тест для offset"""

    response = api.get_companies_with_params(offset=offset_value, limit=3)

    # Проверка статуса
    assert (
        response.status_code == expected_status
    ), f"Ожидался статус {expected_status}, получен {response.status_code}"

    # Парсим JSON, проверяем структуру
    data = get_validated_json(response)
    validate_response_structure(data, ["data", "meta"])
    validate_meta(data["meta"], expected_offset=offset_value, expected_limit=3)

    companies = data["data"]
    assert companies, "data пустой"
    validate_response_structure(companies[0], COMPANY_REQUIRED_FIELDS)

    # Проверка сдвига: первая компания должна иметь ожидаемый ID
    assert (
        companies[0]["company_id"] == expected_first_id
    ), f"При offset={offset_value} ожидался ID {expected_first_id}, получен {companies[0]['company_id']}"


@pytest.mark.parametrize(
    "status_value, expected_status",
    [
        ("ACTIVE", EXPECTED_STATUS["valid"]),
        ("INVALID", EXPECTED_STATUS["validation_error"]),
    ],
)
@allure.feature("Companies")
@allure.story("GET /companies")
@allure.severity(allure.severity_level.NORMAL)
def test_companies_status(status_value, expected_status):
    """TC-04, TC-05: Параметризованный тест для status"""

    response = api.get_companies_with_params(status=status_value)

    # Проверка статуса + заголовка
    assert (
        response.status_code == expected_status
    ), f"Ожидался статус {expected_status}, получен {response.status_code}"
    validate_content_type(response)

    if expected_status == EXPECTED_STATUS["valid"]:
        data = get_validated_json(response)
        validate_response_structure(data, ["data", "meta"])

        companies = data["data"]

        # Валидация обязательных полей первой компании
        assert companies, "Список компаний пуст"
        validate_fields_presence_and_type(
            companies[0], COMPANY_REQUIRED_FIELDS_AND_TYPES
        )

        # Проверка, что у всех компаний статус соответствует запросу
        for company in companies:
            assert (
                company["company_status"] == status_value
            ), f"Ожидался статус {status_value}, получен {company['company_status']}"
    else:
        # 422 — проверяем структуру ошибки
        error_data = get_validated_json(response)
        validate_422_error(error_data, "status")


@pytest.mark.smoke
@allure.feature("Companies")
@allure.story("GET /companies/{id}")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_company_by_id():
    """TC-09: GET-запрос на получение компании по ID"""

    company_id = 1
    response = api.get_company_by_id(company_id)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    # Проверка заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(data, COMPANY_REQUIRED_FIELDS)

    # ID компании в ответе равен запрашиваемому ID
    assert (
        data["company_id"] == company_id
    ), f"Запрошен {company_id}, получен {data['company_id']}"

    # description_lang — обязательное поле, список, не пустой
    validate_fields_presence_and_type(data, ("description_lang", list))

    # Проверка полей переводов
    for item in data["description_lang"]:
        for field in TRANSLATION_REQUIRED_FIELDS:
            assert field in item, f"В переводе отсутствует поле {field}"
        assert isinstance(
            item["translation_lang"], str
        ), f"translation_lang должен быть строкой"
        assert isinstance(item["translation"], str), f"translation должен быть строкой"


@allure.feature("Companies")
@allure.story("GET /companies/{id}")
@allure.severity(allure.severity_level.MINOR)
def test_get_company_by_id_with_language():
    """TC-10: GET-запрос на получение компании по ID с заголовком определяющим язык"""

    company_id = 1
    headers = {"Accept-Language": "RU"}
    response = api.get_company_by_id(company_id, headers=headers)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    # Проверка заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(data, COMPANY_REQUIRED_FIELDS)

    # ID компании в ответе равен запрашиваемому ID
    assert (
        data["company_id"] == company_id
    ), f"Запрошен {company_id}, получен {data['company_id']}"

    # Проверяем, что API вернул перевод на русском языке
    validate_fields_presence_and_type(data, ("description", str))
    assert (
        "description_lang" not in data
    ), "Массив description_lang должен отсутствовать"


@allure.feature("Companies")
@allure.story("GET /companies/{id}")
@allure.severity(allure.severity_level.MINOR)
def test_get_company_by_id_not_found():
    """TC-11: GET-запрос на получение компании по несуществующему ID"""

    company_id = 9999
    response = api.get_company_by_id(company_id)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["not_found"]
    ), f"Ожидался статус {EXPECTED_STATUS['not_found']}, получен {response.status_code}"

    # Проверка заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    validate_404_error(data, str(company_id))


@allure.feature("Companies")
@allure.story("GET /companies/{id}")
@allure.severity(allure.severity_level.MINOR)
def test_get_company_by_id_invalid():
    """TC-12: GET-запрос на получение компании по невалидному ID"""

    company_id = "abc"
    response = api.get_company_by_id(company_id)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["validation_error"]
    ), f"Ожидался статус {EXPECTED_STATUS['validation_error']}, получен {response.status_code}"

    # Проверка заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    validate_422_error(data, "company_id")
