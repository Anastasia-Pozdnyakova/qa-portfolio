"""Автотесты для API restapi.tech
Эндпоинты: /auth/authorize, /auth/me
Документация: https://restapi.tech
Тесты: TC-32 – TC-139
"""

import requests
import time
import pytest
import allure
from api.auth_api import AuthAPI
from data.expected_status import EXPECTED_STATUS
from data.auth_data import (
    INVALID_PASSWORD,
    SHORT_LOGIN,
    AUTH_ME_REQUIRED_FIELDS,
    INVALID_TOKEN,
)

from utils.helpers import (
    validate_content_type,
    get_validated_json,
    validate_response_structure,
    validate_fields_presence_and_type,
    validate_403_error,
    validate_422_error,
    validate_401_error,
)

api = AuthAPI()


# ========== ТЕСТЫ ==========
@pytest.mark.smoke
@allure.feature("Auth")
@allure.story("POST /auth/authorize")
@allure.severity(allure.severity_level.CRITICAL)
def test_auth_success():
    """TC-32: Успешная авторизация"""

    response = api.authorize()

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    # Проверка  заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # token — обязательное поле, строка, не пустая
    validate_fields_presence_and_type(data, ("token", str))


@allure.feature("Auth")
@allure.story("POST /auth/authorize")
@allure.severity(allure.severity_level.NORMAL)
def test_auth_invalid_password():
    """TC-33: Авторизация с невалидным паролем"""

    response = api.authorize(password=INVALID_PASSWORD)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["forbidden"]
    ), f"Ожидался статус {EXPECTED_STATUS['forbidden']}, получен {response.status_code}"

    # Проверка  заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    validate_403_error(data, "invalid")


@allure.feature("Auth")
@allure.story("POST /auth/authorize")
@allure.severity(allure.severity_level.MINOR)
def test_auth_short_login():
    """TC-34: Авторизация с логином < 3 символов"""

    response = api.authorize(login=SHORT_LOGIN)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["validation_error"]
    ), f"Ожидался статус {EXPECTED_STATUS['validation_error']}, получен {response.status_code}"

    # Проверка  заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    validate_422_error(data, "login")


@allure.feature("Auth")
@allure.story("POST /auth/authorize")
@allure.severity(allure.severity_level.NORMAL)
def test_auth_no_password():
    """TC-35: Авторизация без поля password"""

    response = api.authorize(password=None)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["validation_error"]
    ), f"Ожидался статус {EXPECTED_STATUS['validation_error']}, получен {response.status_code}"

    # Проверка  заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    validate_422_error(data, "password")


@pytest.mark.smoke
@allure.feature("Auth")
@allure.story("GET /auth/me")
@allure.severity(allure.severity_level.CRITICAL)
def test_me_success(auth_token):
    """TC-36: /me с валидным токеном"""

    response = api.get_me(auth_token)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    # Проверка  заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка наличия обязательных полей
    validate_response_structure(data, AUTH_ME_REQUIRED_FIELDS)
    fields = [
        ("user_name", str),
        ("email_address", str),
        ("valid_till", str),
    ]
    validate_fields_presence_and_type(data, fields)


@allure.feature("Auth")
@allure.story("GET /auth/me")
@allure.severity(allure.severity_level.MINOR)
def test_me_no_token():
    """TC-37: /me без заголовка x-token"""

    response = api.get_me()

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["unauthorized"]
    ), f"Ожидался статус {EXPECTED_STATUS['unauthorized']}, получен {response.status_code}"

    # Проверка  заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    validate_401_error(data, "auth")


@allure.feature("Auth")
@allure.story("GET /auth/me")
@allure.severity(allure.severity_level.MINOR)
def test_me_invalid_token():
    """TC-38: /me с невалидным токеном"""

    response = api.get_me(INVALID_TOKEN)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["forbidden"]
    ), f"Ожидался статус {EXPECTED_STATUS['forbidden']}, получен {response.status_code}"

    # Проверка  заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    validate_403_error(data, "token")


@allure.feature("Auth")
@allure.story("GET /auth/me")
@allure.severity(allure.severity_level.MINOR)
def test_token_expires():
    """TC-39: Проверка истечения токена"""

    response = api.authorize(timeout_sec=2)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    # Проверка  заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # token — обязательное поле, строка, не пустая
    validate_fields_presence_and_type(data, ("token", str))
    token = data["token"]

    # Подождать 2 секунды (чтобы токен истёк)
    time.sleep(2)

    # Попробовать получить /me с этим токеном
    response = api.get_me(token)

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["forbidden"]
    ), f"Ожидался статус {EXPECTED_STATUS['forbidden']}, получен {response.status_code}"

    # Проверка  заголовка + парсинг JSON
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    validate_403_error(data, "token")
