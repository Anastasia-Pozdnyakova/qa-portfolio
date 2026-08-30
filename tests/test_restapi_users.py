"""Автотесты для API restapi.tech
Эндпоинт: /users
Документация: https://restapi.tech
Тесты: TC-13 – TC-31
"""

import pytest
import allure

from api.users_api import UsersAPI
from data.users_data import USER_REQUIRED_FIELDS, USER_REQUIRED_FIELDS_AND_TYPES
from data.expected_status import EXPECTED_STATUS
from utils.helpers import (
    validate_content_type,
    get_validated_json,
    validate_response_structure,
    validate_meta,
    validate_422_error,
    validate_404_error,
    validate_400_error,
    get_active_company_id,
    get_inactive_company_id,
    validate_fields_presence_and_type,
)

api = UsersAPI()


# ========== Тесты ==========
@pytest.mark.smoke
@allure.feature("Users")
@allure.story("GET /users")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_all_users():
    """TC-13: Базовый GET-запрос на получение всех пользователей"""

    response = api.get_users_with_params()

    assert response.status_code == EXPECTED_STATUS["valid"]
    validate_content_type(response)
    data = get_validated_json(response)

    validate_response_structure(data, ["meta", "data"])
    validate_meta(data["meta"])

    users = data["data"]
    assert users, "Список пользователей пуст"

    first_user = users[0]
    validate_fields_presence_and_type(first_user, USER_REQUIRED_FIELDS_AND_TYPES)


@pytest.mark.parametrize(
    "limit_value, expected_status, expected_limit",
    [
        (5, EXPECTED_STATUS["valid"], 5),
        ("abc", EXPECTED_STATUS["validation_error"], None),
    ],
)
@allure.feature("Users")
@allure.story("GET /users")
@allure.severity(allure.severity_level.NORMAL)
def test_users_limit(limit_value, expected_status, expected_limit):
    """TC-14, TC-16: Параметризованный тест для limit"""

    response = api.get_users_with_params(limit=limit_value)

    assert (
        response.status_code == expected_status
    ), f"Ожидался статус {expected_status}, получен {response.status_code}"

    if expected_status == EXPECTED_STATUS["valid"]:
        data = get_validated_json(response)
        validate_response_structure(data, ["data", "meta"])
        validate_meta(data["meta"], expected_limit=expected_limit)
    else:
        error_data = get_validated_json(response)
        validate_422_error(error_data, expected_field="limit")


@allure.feature("Users")
@allure.story("GET /users")
@allure.severity(allure.severity_level.NORMAL)
def test_users_offset():
    """TC-15: Параметр offset сдвигает список пользователей"""

    offset_value = 2
    response = api.get_users_with_params(offset=offset_value)

    assert response.status_code == EXPECTED_STATUS["valid"]
    validate_content_type(response)
    data = get_validated_json(response)

    validate_response_structure(data, ["meta", "data"])
    assert data["meta"]["offset"] == offset_value

    users = data["data"]
    assert users, "Список пользователей пуст"


@pytest.mark.smoke
@allure.feature("Users")
@allure.story("POST /users")
@allure.severity(allure.severity_level.CRITICAL)
def test_create_user_valid(create_user):
    """TC-17: Создание юзера с валидаными данными"""

    user_data = create_user["data"]
    user = create_user["response"]

    # Проверка структуры и полей
    validate_response_structure(user, USER_REQUIRED_FIELDS)
    validate_fields_presence_and_type(user, USER_REQUIRED_FIELDS_AND_TYPES)

    # Проверка совпадения данных
    assert (
        user["last_name"] == user_data["last_name"]
    ), f"Ожидалось last_name={user_data['last_name']}, получено {user['last_name']}"


@pytest.mark.parametrize(
    "user_data, expected_status, expected_field",
    [
        # TC-18: без last_name
        (
            {"first_name": "Sydney", "company_id": "active"},
            EXPECTED_STATUS["validation_error"],
            "last_name",
        ),
        # TC-19: несуществующая компания
        (
            {"first_name": "Sydney", "last_name": "Sweeney", "company_id": 9999},
            EXPECTED_STATUS["not_found"],
            None,
        ),
        # TC-20: неактивная компания
        (
            {"first_name": "Sydney", "last_name": "Sweeney", "company_id": "inactive"},
            EXPECTED_STATUS["bad_request"],
            None,
        ),
    ],
)
@allure.feature("Users")
@allure.story("POST /users")
@allure.severity(allure.severity_level.MINOR)
def test_users_negative(user_data, expected_status, expected_field):
    """TC-18, TC-19, TC-20: Негативные сценарии POST /users"""

    # Получаем ID компании
    company_id = user_data.get("company_id")
    if company_id == "active":
        company_id = get_active_company_id()
    elif company_id == "inactive":
        company_id = get_inactive_company_id()
    user_data["company_id"] = company_id

    response = api.create_user(user_data)

    assert (
        response.status_code == expected_status
    ), f"Ожидался статус {expected_status}, получен {response.status_code}"

    validate_content_type(response)
    error_data = get_validated_json(response)

    if expected_status == EXPECTED_STATUS["validation_error"]:
        validate_422_error(error_data, expected_field)
    elif expected_status == EXPECTED_STATUS["not_found"]:
        validate_404_error(error_data, str(company_id))
    else:  # 400 Bad Request (неактивная компания)
        validate_400_error(error_data)


@pytest.mark.smoke
@allure.feature("Users")
@allure.story("GET /users/{id}")
@allure.severity(allure.severity_level.CRITICAL)
def test_user_by_id(create_user):
    """TC-21: GET-запрос на получение юзера по ID"""

    user_id = create_user["response"]["user_id"]
    expected_last_name = create_user["response"]["last_name"]

    response = api.get_user(user_id)

    assert response.status_code == EXPECTED_STATUS["valid"]
    validate_content_type(response)
    user = get_validated_json(response)

    validate_response_structure(user, USER_REQUIRED_FIELDS)
    validate_fields_presence_and_type(user, USER_REQUIRED_FIELDS_AND_TYPES)

    assert (
        user["user_id"] == user_id
    ), f"Ожидался ID {user_id}, получен {user['user_id']}"
    assert (
        user["last_name"] == expected_last_name
    ), f"Ожидался last_name {expected_last_name}, получен {user['last_name']}"


@pytest.mark.parametrize(
    "user_id, expected_status",
    [
        (99999, EXPECTED_STATUS["not_found"]),
        ("abc", EXPECTED_STATUS["validation_error"]),
    ],
)
@allure.feature("Users")
@allure.story("GET /users/{id}")
@allure.severity(allure.severity_level.MINOR)
def test_user_invalid_id(user_id, expected_status):
    """TC-22, TC-23: Параметризованный тест для невалидного ID"""

    response = api.get_user(user_id)

    assert (
        response.status_code == expected_status
    ), f"Ожидался статус {expected_status}, получен {response.status_code}"

    validate_content_type(response)
    data = get_validated_json(response)

    if expected_status == EXPECTED_STATUS["not_found"]:
        validate_404_error(data, str(user_id))
    else:
        validate_422_error(data, "user_id")


@pytest.mark.smoke
@allure.feature("Users")
@allure.story("PUT /users/{id}")
@allure.severity(allure.severity_level.CRITICAL)
def test_put_user_by_id(create_user):
    """TC-24: PUT-запрос на изменение данных юзера по ID"""

    user_id = create_user["response"]["user_id"]
    updated_data = api._generate_user_data()

    response = api.update_user(user_id, updated_data)

    assert response.status_code == EXPECTED_STATUS["valid"]
    validate_content_type(response)
    result = get_validated_json(response)

    validate_response_structure(result, USER_REQUIRED_FIELDS)
    validate_fields_presence_and_type(result, USER_REQUIRED_FIELDS_AND_TYPES)
    assert result["last_name"] == updated_data["last_name"]
    assert result["first_name"] == updated_data["first_name"]


@pytest.mark.parametrize(
    "user_data, expected_status, expected_field",
    [
        # TC-25: без last_name
        (
            {"first_name": "Sydney", "company_id": "active"},
            EXPECTED_STATUS["validation_error"],
            "last_name",
        ),
        # TC-26: несуществующая компания
        (
            {"first_name": "Sydney", "last_name": "Sweeney", "company_id": 9999},
            EXPECTED_STATUS["not_found"],
            None,
        ),
        # TC-27: неактивная компания
        (
            {"first_name": "Sydney", "last_name": "Sweeney", "company_id": "inactive"},
            EXPECTED_STATUS["bad_request"],
            None,
        ),
    ],
)
@allure.feature("Users")
@allure.story("PUT /users/{id}")
@allure.severity(allure.severity_level.MINOR)
def test_put_users_negative(create_user, user_data, expected_status, expected_field):
    """TC-25, TC-26, TC-27: Негативные сценарии PUT /users"""

    user_id = create_user["response"]["user_id"]

    # Получаем ID компании
    company_id = user_data.get("company_id")
    if company_id == "active":
        company_id = get_active_company_id()
    elif company_id == "inactive":
        company_id = get_inactive_company_id()
    user_data["company_id"] = company_id

    response = api.update_user(user_id, user_data)

    assert (
        response.status_code == expected_status
    ), f"Ожидался статус {expected_status}, получен {response.status_code}"

    validate_content_type(response)
    error_data = get_validated_json(response)

    if expected_status == EXPECTED_STATUS["validation_error"]:
        validate_422_error(error_data, expected_field)
    elif expected_status == EXPECTED_STATUS["not_found"]:
        validate_404_error(error_data, str(company_id))
    else:  # 400 Bad Request (неактивная компания)
        validate_400_error(error_data)


@pytest.mark.smoke
@allure.feature("Users")
@allure.story("DELETE /users/{id}")
@allure.severity(allure.severity_level.CRITICAL)
def test_delete_user_by_id(create_user):
    """TC-28: DELETE-запрос на удаление юзера по ID"""

    user_id = create_user["response"]["user_id"]

    response = api.delete_user(user_id)

    assert (
        response.status_code == EXPECTED_STATUS["deleted"]
    ), f"Ожидался статус {EXPECTED_STATUS['deleted']}, получен {response.status_code}"

    # Проверяем, что пользователь удалён
    get_response = api.get_user(user_id)
    assert (
        get_response.status_code == EXPECTED_STATUS["not_found"]
    ), f"Пользователь {user_id} всё ещё существует"


@pytest.mark.parametrize(
    "user_id, expected_status",
    [
        (851987, EXPECTED_STATUS["not_found"]),
        ("abc", EXPECTED_STATUS["validation_error"]),
    ],
)
@allure.feature("Users")
@allure.story("DELETE /users/{id}")
@allure.severity(allure.severity_level.MINOR)
def test_delete_user_invalid(user_id, expected_status):
    """TC-29, TC-31: DELETE с несуществующим / невалидным ID"""

    response = api.delete_user(user_id)

    assert (
        response.status_code == expected_status
    ), f"Ожидался статус {expected_status}, получен {response.status_code}"

    validate_content_type(response)
    data = get_validated_json(response)

    if expected_status == EXPECTED_STATUS["not_found"]:
        validate_404_error(data, str(user_id))
    else:
        validate_422_error(data, "user_id")


@allure.feature("Users")
@allure.story("DELETE /users/{id}")
@allure.severity(allure.severity_level.MINOR)
def test_delete_user_twice(create_user):
    """TC-30: Повторное удаление одного и того же юзера"""

    user_id = create_user["response"]["user_id"]

    # Первое удаление
    response1 = api.delete_user(user_id)
    assert response1.status_code == EXPECTED_STATUS["deleted"]

    # Второе удаление (уже удалён)
    response2 = api.delete_user(user_id)
    assert response2.status_code == EXPECTED_STATUS["not_found"]
