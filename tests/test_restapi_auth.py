"""Автотесты для API restapi.tech
Эндпоинты: /auth/authorize, /auth/me
Документация: https://restapi.tech
"""

import requests
import json
import time
import pytest
import constants

# ========== Настройки ==========
BASE_URL = "https://restapi.tech/api"
TIMEOUT = 5
AUTH_ENDPOINT = f"{BASE_URL}/auth/authorize"
ME_ENDPOINT = f"{BASE_URL}/auth/me"
VALID_PASSWORD = "qwerty12345"


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


# ========== Фикстуры ==========
@pytest.fixture(scope="session")
def auth_token():
    """Фикстура для получения токена"""

    user_data = {
        "login": "user_" + str(int(time.time())),
        "password": VALID_PASSWORD,
        "timeout": 360,
    }

    try:
        auth_response = requests.post(AUTH_ENDPOINT, json=user_data, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pytest.fail(f"Запрос к {AUTH_ENDPOINT} превысил таймаут {TIMEOUT} сек.")

    assert (
        auth_response.status_code == 200
    ), f"Ожидался 200, получен {auth_response.status_code}"
    validate_content_type(auth_response)
    data = get_validated_json(auth_response)

    assert "token" in data, "В ответе отсутствует поле token"
    token = data["token"]
    assert isinstance(token, str), "token должен быть строкой"
    assert len(token) > 0, "token не должен быть пустым"

    return token


# ========== Тесты ==========
def test_tc32_auth_success(auth_token):
    """TC-32: Успешная регистрация пользователя"""

    print("🔑 Токен:", auth_token)
    assert auth_token is not None, f"Вместо токена – {auth_token}"
    assert isinstance(auth_token, str), "token должен быть строкой"
    assert len(auth_token) > 0, "token не должен быть пустым"


def test_tc33_auth_invalid_password():
    """TC-33: Регистрация с невалидным паролем"""

    # Подготовка данных
    user_data = {
        "login": "user_" + str(int(time.time())),
        "password": "qwerty1",
        "timeout": 360,
    }

    # Отправка POST-запроса
    try:
        response = requests.post(AUTH_ENDPOINT, json=user_data, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pytest.fail(f"Запрос к {AUTH_ENDPOINT} превысил таймаут {TIMEOUT} сек.")

    assert response.status_code == 403, f"Ожидался 403, получен {response.status_code}"
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"

    detail = data["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом (dict)"
    assert "reason" in detail, "В detail отсутствует поле reason"

    reason = detail["reason"].lower()
    assert isinstance(reason, str), "reason должен быть строкой"
    assert len(reason) > 0, "reason не должна быть пустой"
    assert (
        "login" in reason or "password" in reason
    ), f"reason не содержит ни 'login', ни 'password'. reason {reason}"


def test_tc34_auth_short_login():
    """TC-34: Регистрация с логином < 3 символов"""

    # Подготовка данных
    user_data = {
        "login": "us",
        "password": "qwerty12345",
        "timeout": 360,
    }

    # Отправка POST-запроса
    try:
        response = requests.post(AUTH_ENDPOINT, json=user_data, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pytest.fail(f"Запрос к {AUTH_ENDPOINT} превысил таймаут {TIMEOUT} сек.")

    assert response.status_code == 422, f"Ожидался 422, получен {response.status_code}"
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"
    detail = data["detail"]
    assert isinstance(detail, list), "detail должен быть массивом"
    assert len(detail) > 0, "detail пуст"

    # Парсим первую ошибку
    first_error = detail[0]

    # Проверка обязательных полей
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"В ошибке отсутствует поле '{field}'"

    # Проверка, loc (тип, размер, наполнение)
    loc = first_error["loc"]
    assert isinstance(loc, list), "loc не массив"
    assert len(loc) > 0, "loc пуст"
    assert "login" in loc, "loc не содержит упоминание о 'login'"

    # Проверка, msg (тип, размер, наполнение)
    msg = first_error["msg"].lower()
    assert isinstance(msg, str), "msg не строка"
    assert len(msg) > 0, "msg пуст"
    assert "3 characters" in msg, "msg не содержит упоминание о '3 characters'"


def test_tc35_auth_no_password():
    """TC-35: Регистрация без поля password"""

    # Подготовка данных
    user_data = {
        "login": "user_" + str(int(time.time())),
        "timeout": 360,
    }

    # Отправка POST-запроса
    try:
        response = requests.post(AUTH_ENDPOINT, json=user_data, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pytest.fail(f"Запрос к {AUTH_ENDPOINT} превысил таймаут {TIMEOUT} сек.")

    assert response.status_code == 422, f"Ожидался 422, получен {response.status_code}"
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"
    detail = data["detail"]
    assert isinstance(detail, list), "detail должен быть массивом"
    assert len(detail) > 0, "detail пуст"

    # Парсим первую ошибку
    first_error = detail[0]

    # Проверка обязательных полей
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"В ошибке отсутствует поле '{field}'"

    # Проверка, loc (тип, размер, наполнение)
    loc = first_error["loc"]
    assert isinstance(loc, list), "loc не массив"
    assert len(loc) > 0, "loc пуст"
    assert "password" in loc, "loc не содержит упоминание о 'password'"

    # Проверка, msg (тип, размер, наполнение)
    msg = first_error["msg"].lower()
    assert isinstance(msg, str), "msg не строка"
    assert len(msg) > 0, "msg пуст"
    assert "required" in msg, "msg не содержит упоминание о 'required'"


def test_tc36_me_success(auth_token):
    """TC-36: /me с валидным токеном"""

    # Подготовка данных
    headers = {"x-token": auth_token}

    # Отправка GET-запроса
    try:
        response = requests.get(ME_ENDPOINT, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pytest.fail(f"Запрос к {ME_ENDPOINT} превысил таймаут {TIMEOUT} сек.")

    assert response.status_code == 200, f"Ожидался 200, получен {response.status_code}"
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка наличия обязательных полей
    validate_response_structure(data, ["user_name", "email_address", "valid_till"])

    # Проверка типов полей
    assert isinstance(data["user_name"], str), f"user_name должен быть строкой"
    assert isinstance(data["email_address"], str), f"email_address должен быть строкой"
    assert isinstance(data["valid_till"], str), f"valid_till должен быть строкой"

    # Проверка, что поля не пустые
    assert len(data["user_name"]) > 0, "user_name пустой"
    assert len(data["email_address"]) > 0, "email_address пустой"
    assert len(data["valid_till"]) > 0, "valid_till пустой"


def test_tc37_me_no_token():
    """TC-37: /me без заголовка x-token"""

    # Отправка GET-запроса
    try:
        response = requests.get(ME_ENDPOINT, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pytest.fail(f"Запрос к {ME_ENDPOINT} превысил таймаут {TIMEOUT} сек.")

    assert response.status_code == 401, f"Ожидался 401, получен {response.status_code}"
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"

    detail = data["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом (dict)"
    assert "reason" in detail, "В detail отсутствует поле reason"

    reason = detail["reason"].lower()
    assert isinstance(reason, str), "reason должен быть строкой"
    assert len(reason) > 0, "reason не должен быть пустой"
    assert "auth" in reason, f"reason не содержит 'auth'. reason {reason}"


def test_tc38_me_invalid_token():
    """TC-38: /me с невалидным токеном"""

    # Подготовка данных
    headers = {"x-token": "invalid_token_123"}

    # Отправка GET-запроса
    try:
        response = requests.get(ME_ENDPOINT, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pytest.fail(f"Запрос к {ME_ENDPOINT} превысил таймаут {TIMEOUT} сек.")

    assert response.status_code == 403, f"Ожидался 403, получен {response.status_code}"
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"

    detail = data["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом (dict)"
    assert "reason" in detail, "В detail отсутствует поле reason"

    reason = detail["reason"].lower()
    assert isinstance(reason, str), "reason должен быть строкой"
    assert len(reason) > 0, "reason не должен быть пустой"
    assert "token" in reason, f"reason не содержит 'token'. reason {reason}"


def test_tc39_token_expires():
    """TC-39: Проверка истечения токена"""

    # Подготовка данных
    user_data = {
        "login": "user_" + str(int(time.time())),
        "password": "qwerty12345",
        "timeout": 1,
    }

    # Отправка POST-запроса
    try:
        auth_response = requests.post(AUTH_ENDPOINT, json=user_data, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pytest.fail(f"Запрос к {AUTH_ENDPOINT} превысил таймаут {TIMEOUT} сек.")

    assert (
        auth_response.status_code == 200
    ), f"Ожидался 200, получен {auth_response.status_code}"
    validate_content_type(auth_response)
    data = get_validated_json(auth_response)

    assert "token" in data, "В ответе отсутствует поле token"
    token = data["token"]
    assert isinstance(token, str), "token должен быть строкой"
    assert len(token) > 0, "token не должен быть пустым"

    # Подождать 2 секунды (чтобы токен истёк)
    time.sleep(2)

    # Попробовать получить /me с этим токеном
    headers = {"x-token": token}
    try:
        response = requests.get(ME_ENDPOINT, headers=headers, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pytest.fail(f"Запрос к {ME_ENDPOINT} превысил таймаут {TIMEOUT} сек.")

    assert response.status_code == 403, f"Ожидался 403, получен {response.status_code}"
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"

    detail = data["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом (dict)"
    assert "reason" in detail, "В detail отсутствует поле reason"

    reason = detail["reason"].lower()
    assert isinstance(reason, str), "reason должен быть строкой"
    assert len(reason) > 0, "reason не должен быть пустой"
    assert "token" in reason, f"reason не содержит 'token'. reason {reason}"
