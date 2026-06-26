"""Автотесты для API restapi.tech
Эндпоинт: /users
Документация: https://restapi.tech
"""

import requests
import json
import constants

# ========== Настройки ==========
BASE_URL = "https://restapi.tech/api"
TIMEOUT = 5
USERS_ENDPOINT = f"{BASE_URL}/users"


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
def test_tc13_get_all_users():
    """TC-13: Базовый GET-запрос на получение всех пользователей"""

    # Отправка GET-запроса
    try:
        response = requests.get(USERS_ENDPOINT, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {USERS_ENDPOINT} вернул статус {response.status_code}. "
        f"Ожидался 200"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(data, ["meta", "data"])

    meta = data["meta"]
    assert isinstance(meta["total"], int), "Поле total не число"
    assert isinstance(meta["limit"], int), "Поле limit не число"
    assert isinstance(meta["offset"], int), "Поле offset не число"

    users = data["data"]
    assert isinstance(users, list), "Поле data не массив"
    assert len(users) > 0, "Массив data пустой"

    first_user = users[0]
    validate_response_structure(first_user, constants.USER_REQUIRED_FIELDS)
    assert isinstance(first_user["last_name"], str), "last_name должен быть строкой"
    assert isinstance(first_user["user_id"], int), "user_id должен быть числом"


def test_tc14_get_users_with_limit():
    """ТС-14: Параметр limit ограничивает количество пользователей"""

    # Подготовка данных
    limit_value = 5

    # Отправка GET-запроса с limit
    try:
        response = requests.get(
            USERS_ENDPOINT, params={"limit": limit_value}, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {USERS_ENDPOINT} вернул статус {response.status_code}. "
        f"Ожидался 200"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(data, ["meta", "data"])

    # Проверка, что meta.limit соответствует запросу
    assert data["meta"]["limit"] == limit_value

    # Проверка, что кол-во пользователей не больше limit
    assert len(data["data"]) <= data["meta"]["limit"]


def test_tc15_get_users_with_offset():
    """TC-15: Параметр offset сдвигает список пользователей"""

    # Подготовка данных
    offset_value = 2

    # Отправка GET-запроса
    try:
        response = requests.get(
            USERS_ENDPOINT, params={"offset": offset_value}, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {USERS_ENDPOINT} вернул статус {response.status_code}. "
        f"Ожидался 200"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(data, ["meta", "data"])

    # Проверка, что meta.offset соответствует запросу
    assert data["meta"]["offset"] == offset_value

    # Проверка, что data.data массив и не пустой
    users = data["data"]
    assert isinstance(users, list), "Поле data не массив"
    assert len(users) > 0, "Массив data пустой"


def test_tc16_limit_abc_returns_422():
    """TC-16: limit=abc возвращает статус 422 и detail об ошибке"""

    # Подготовка данных
    limit_value = "abc"

    # Отправка GET-запроса
    try:
        response = requests.get(
            USERS_ENDPOINT, params={"limit": limit_value}, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 422, (
        f"Запрос к {USERS_ENDPOINT} вернул статус {response.status_code}. "
        f"Ожидался 422"
    )
    validate_content_type(response)
    error_data = get_validated_json(response)

    # Проверка, что в ответе есть detail - массив, не пустой
    assert "detail" in error_data, "Поле detail отсутствует"
    detail = error_data["detail"]
    assert isinstance(detail, list), "detail не массив"
    assert len(detail) > 0, "Массив detail пустой"

    # Извлекаем первую ошибку
    first_error = detail[0]

    # Проверка обязательных полей
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"В ошибке отсутствует {field}"

    # Проверка типа поля ошибки и содержание
    error_msg = first_error["msg"]
    assert isinstance(error_msg, str), "Поле 'msg' не строка"
    assert "integer" in error_msg, "Сообщение об ошибке не содержит 'integer'"
