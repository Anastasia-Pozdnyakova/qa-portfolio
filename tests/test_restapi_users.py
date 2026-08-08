"""Автотесты для API restapi.tech
Эндпоинт: /users
Документация: https://restapi.tech
"""

import requests
import constants
import pytest
import allure
from utils.helpers import (
    validate_content_type,
    get_validated_json,
    validate_response_structure,
)

# ========== Настройки ==========
BASE_URL = "https://restapi.tech/api"
TIMEOUT = 5
USERS_ENDPOINT = f"{BASE_URL}/users"
COMPANIES_ENDPOINT = f"{BASE_URL}/companies"


# ========== Тесты ==========
@pytest.mark.smoke
@allure.feature("Users")
@allure.story("GET /users")
@allure.severity(allure.severity_level.CRITICAL)
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


@allure.feature("Users")
@allure.story("GET /users")
@allure.severity(allure.severity_level.NORMAL)
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


@allure.feature("Users")
@allure.story("GET /users")
@allure.severity(allure.severity_level.NORMAL)
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


@allure.feature("Users")
@allure.story("GET /users")
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


@pytest.mark.smoke
@allure.feature("Users")
@allure.story("POST /users")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc17_create_user_valid(create_user):
    """TC-17: Создание юзера с валидаными данными"""

    # Подготовка данных (исходные данные и результат)
    user_data = create_user["data"]
    user = create_user["response"]

    validate_response_structure(user, constants.USER_REQUIRED_FIELDS)
    assert isinstance(user["user_id"], int), "Поле user_id не число"
    assert isinstance(user["last_name"], str), "Поле last_name не строка"

    assert user["last_name"] == user_data["last_name"], (
        f"Ожидалось в поле 'last_name' {user_data['last_name']}, "
        f"а получено {user['last_name']}"
    )


@allure.feature("Users")
@allure.story("POST /users")
@allure.severity(allure.severity_level.TRIVIAL)
def test_tc18_create_user_no_last_name():
    """TC-18: Создание юзера без обязательного поля last_name возвращает статус 422"""

    # Подготовка данных
    invalid_user = {"first_name": "Sydney", "company_id": 3}

    # Отправка POST-запроса
    try:
        response = requests.post(USERS_ENDPOINT, json=invalid_user, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 422, (
        f"Запрос к {USERS_ENDPOINT} вернул статус {response.status_code}. "
        f"Ожидался 422"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"
    assert isinstance(data["detail"], list), "detail не массив"
    assert len(data["detail"]) > 0, "Массив detail пуст"

    # Берем первую ошибку
    first_error = data["detail"][0]

    # Проверка обязательных полей
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"Нет поля {field} в ответе"

    # Проверка типа поля ошибки и содержание
    assert isinstance(first_error["loc"], list), "loc не массив"
    assert isinstance(first_error["msg"], str), "msg не строка"

    assert (
        "last_name" in first_error["loc"]
    ), "loc не содержит упоминание о месте ошибки – поле last_name"
    assert (
        "required" in first_error["msg"]
    ), "msg не содержит упоминание об обязательности поля – required"


@allure.feature("Users")
@allure.story("POST /users")
@allure.severity(allure.severity_level.TRIVIAL)
def test_tc19_create_user_invalid_company():
    """TC-19: Создание юзера на несуществующую компанию возвращает статус 404"""

    # Подготовка данных
    invalid_company_id = 9999
    user = {
        "first_name": "Sydney",
        "last_name": "Sweeney",
        "company_id": invalid_company_id,
    }

    # Отправка POST-запроса
    try:
        response = requests.post(USERS_ENDPOINT, json=user, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 404, (
        f"Запрос к {USERS_ENDPOINT} вернул статус {response.status_code}. "
        f"Ожидался 404"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"
    detail = data["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом (dict)"

    assert "reason" in detail, "В detail отсутствует поле reason"
    reason = detail["reason"]
    assert isinstance(reason, str), "reason должен быть строкой"
    assert len(reason) > 0, "reason не должна быть пустой"
    assert (
        str(invalid_company_id) in reason
    ), f"reason не содержит упоминание о невалидном ID {invalid_company_id}"


@allure.feature("Users")
@allure.story("POST /users")
def test_tc20_create_user_inactive_company():
    """TC-20: Создание юзера на неактивную компанию возвращает статус 400"""

    # Подготовка данных
    status_value = "CLOSED"

    # Отправка GET-запроса на получение компании со статусом CLOSED
    try:
        response_companies = requests.get(
            COMPANIES_ENDPOINT, params={"status": status_value}, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {COMPANIES_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON первого запроса
    assert response_companies.status_code == 200, (
        f"Запрос к {COMPANIES_ENDPOINT} с параметрами status={status_value} "
        f"вернул статус {response_companies.status_code}. Ожидался 200"
    )
    validate_content_type(response_companies)
    data_companies = get_validated_json(response_companies)

    companies = data_companies["data"]

    # Если нет CLOSED компаний — пропускаем тест
    if not companies:
        pytest.skip("Нет компаний со статусом CLOSED")

    # Берем id первой компании
    first_company_id = companies[0]["company_id"]

    # Подготовка данных для второго запроса
    user = {
        "first_name": "Sydney",
        "last_name": "Sweeney",
        "company_id": first_company_id,
    }

    # Отправка POST-запроса
    try:
        response_user = requests.post(USERS_ENDPOINT, json=user, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response_user.status_code == 400, (
        f"Запрос к {USERS_ENDPOINT} вернул статус {response_user.status_code}. "
        f"Ожидался 400"
    )
    validate_content_type(response_user)
    data = get_validated_json(response_user)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"
    detail = data["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом (dict)"

    assert "reason" in detail, "В detail отсутствует поле reason"
    reason = detail["reason"]
    assert isinstance(reason, str), "reason должен быть строкой"
    assert len(reason) > 0, "reason не должна быть пустой"
    assert (
        "active" in reason.lower()
    ), f"reason не содержит упоминание о валидном статусе ACTIVE"


@pytest.mark.smoke
@allure.feature("Users")
@allure.story("GET /users/{id}")
@allure.severity(allure.severity_level.CRITICAL)
def test_tc21_get_user_by_id(create_user):
    """TC-21: GET-запрос на получение юзера по ID"""

    # Берём данные из фикстуры по созданию юзера
    created_user_id = create_user["response"]["user_id"]
    created_last_name = create_user["response"]["last_name"]

    # Отправляем GET-запрос с ID из фикстуры
    try:
        response = requests.get(f"{USERS_ENDPOINT}/{created_user_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {USERS_ENDPOINT} вернул статус {response.status_code}. "
        f"Ожидался 200"
    )
    validate_content_type(response)
    fetched_user = get_validated_json(response)

    # Проверка обязательных полей
    validate_response_structure(fetched_user, constants.USER_REQUIRED_FIELDS)

    fetched_user_id = fetched_user["user_id"]
    fetched_last_name = fetched_user["last_name"]

    assert isinstance(fetched_user_id, int), "ID должен быть числом"
    assert isinstance(fetched_last_name, str), "last_name должен быть строкой"

    # Сравниваем
    assert (
        created_user_id == fetched_user_id
    ), f"user_id={created_user_id} из url не совпал с user_id={fetched_user_id} из ответа"
    assert (
        created_last_name == fetched_last_name
    ), f"last_name={created_last_name} из фикстуры не совпал с last_name={fetched_last_name} из ответа"


@allure.feature("Users")
@allure.story("GET /users/{id}")
@allure.severity(allure.severity_level.TRIVIAL)
def test_tc22_invalid_id_returns_404():
    """TC-22: Получение юзера по несуществующему ID возвращает статус 404"""

    # Подготовка данных
    user_id = 99999

    # Отправка GET-запроса
    try:
        response = requests.get(f"{USERS_ENDPOINT}/{user_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 404, (
        f"Запрос к {USERS_ENDPOINT}/{user_id} (несуществуюший ID) вернул статус {response.status_code}. "
        f"Ожидался 404"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"
    detail = data["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом (dict)"

    assert "reason" in detail, "В detail отсутствует поле reason"
    reason = detail["reason"]
    assert isinstance(reason, str), "reason должен быть строкой"
    assert len(reason) > 0, "reason не должна быть пустой"
    assert str(user_id) in reason, f"reason не содержит упоминание об id={user_id}"


@allure.feature("Users")
@allure.story("GET /users/{id}")
def test_tc23_id_abc_returns_422():
    """TC-23: Получение юзера на невалидный ID возвращает статус 422"""

    # Подготовка данных
    user_id = "abc"

    # Отправка GET-запроса
    try:
        response = requests.get(f"{USERS_ENDPOINT}/{user_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 422, (
        f"Запрос к {USERS_ENDPOINT}/{user_id} (невалидный ID) вернул статус {response.status_code}. "
        f"Ожидался 422"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"
    assert isinstance(data["detail"], list), "detail не массив"
    assert len(data["detail"]) > 0, "Массив detail пуст"

    # Берем первую ошибку
    first_error = data["detail"][0]

    # Проверка обязательных полей
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"Нет поля {field} в ответе"

    assert isinstance(first_error["loc"], list), "loc не массив"
    assert isinstance(first_error["msg"], str), "msg не строка"

    assert (
        "user_id" in first_error["loc"]
    ), "loc не содержит упоминание о месте ошибки – поле user_id"
    assert (
        "integer" in first_error["msg"]
    ), "msg не содержит упоминание о валидном типе – integer"


@pytest.mark.smoke
@allure.feature("Users")
@allure.story("PUT /users/{id}")
@allure.severity(allure.severity_level.CRITICAL)
def test_tc24_update_user_by_id(create_user):
    """TC-24: PUT-запрос на изменение данных юзера по ID"""

    # Берем данные из фикстуры
    created_user_id = create_user["response"]["user_id"]
    user_update_data = constants.create_unique_user()

    # Отправка PUT-запроса
    try:
        response = requests.put(
            f"{USERS_ENDPOINT}/{created_user_id}",
            json=user_update_data,
            timeout=TIMEOUT,
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {USERS_ENDPOINT}/{created_user_id} вернул статус {response.status_code}. "
        f"Ожидался 200"
    )
    validate_content_type(response)
    fresh_user_data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(fresh_user_data, constants.USER_REQUIRED_FIELDS)
    assert isinstance(fresh_user_data["user_id"], int), "Поле user_id не число"
    assert isinstance(fresh_user_data["last_name"], str), "Поле last_name не строка"

    assert fresh_user_data["last_name"] == user_update_data["last_name"], (
        f"Ожидалось в поле 'last_name' {user_update_data['last_name']}, "
        f"а получено {fresh_user_data['last_name']}"
    )

    assert fresh_user_data["first_name"] == user_update_data["first_name"], (
        f"Ожидалось в поле 'first_name' {user_update_data['first_name']}, "
        f"а получено {fresh_user_data['first_name']}"
    )


@allure.feature("Users")
@allure.story("PUT /users/{id}")
@allure.severity(allure.severity_level.TRIVIAL)
def test_tc25_update_user_no_last_name(create_user):
    """TC-25: PUT без обязательного поля last_name возвращает 422"""

    # Берем ID юзера из фикстуры
    created_user_id = create_user["response"]["user_id"]

    # Подготовка данных без обязательного поля
    user_data = {"first_name": "Sydney", "company_id": 3}

    # Отправка PUT-запроса
    try:
        response = requests.put(
            f"{USERS_ENDPOINT}/{created_user_id}",
            json=user_data,
            timeout=TIMEOUT,
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 422, (
        f"Запрос к {USERS_ENDPOINT}/{created_user_id} (невалидный ID) вернул статус {response.status_code}. "
        f"Ожидался 422"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"
    assert isinstance(data["detail"], list), "detail не массив"
    assert len(data["detail"]) > 0, "Массив detail пуст"

    # Берем первую ошибку
    first_error = data["detail"][0]

    # Проверка обязательных полей
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"Нет поля {field} в ответе"

    assert isinstance(first_error["loc"], list), "loc не массив"
    assert isinstance(first_error["msg"], str), "msg не строка"

    assert (
        "last_name" in first_error["loc"]
    ), "loc не содержит упоминание о месте ошибки – поле last_name"
    assert (
        "required" in first_error["msg"]
    ), "msg не содержит упоминание об обязательности поля – required"


@allure.feature("Users")
@allure.story("PUT /users/{id}")
def test_tc26_update_user_invalid_company(create_user):
    """TC-26: Изменение юзера на несуществующую компанию возвращает статус 404"""

    # Берем ID юзера из фикстуры
    created_user_id = create_user["response"]["user_id"]

    # Подготовка данных без обязательного поля
    invalid_company_id = 9999
    user_data = {
        "first_name": "Sydney",
        "last_name": "Sweeney",
        "company_id": invalid_company_id,
    }

    # Отправка PUT-запроса
    try:
        response = requests.put(
            f"{USERS_ENDPOINT}/{created_user_id}",
            json=user_data,
            timeout=TIMEOUT,
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 404, (
        f"Запрос к {USERS_ENDPOINT}/{created_user_id} вернул статус {response.status_code}. "
        f"Ожидался 404"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"
    detail = data["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом (dict)"

    assert "reason" in detail, "В detail отсутствует поле reason"
    reason = detail["reason"]
    assert isinstance(reason, str), "reason должен быть строкой"
    assert len(reason) > 0, "reason не должна быть пустой"
    assert (
        str(invalid_company_id) in reason
    ), f"reason не содержит упоминание о несуществующем ID компании = {invalid_company_id}"


@allure.feature("Users")
@allure.story("PUT /users/{id}")
def test_tc27_update_user_inactive_company(create_user):
    """TC-27: Изменение юзера на неактивную компанию возвращает статус 400"""

    # Подготовка данных
    inactive_status = "CLOSED"

    # Отправка GET-запроса со статусом
    try:
        response_companies = requests.get(
            COMPANIES_ENDPOINT, params={"status": inactive_status}, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {COMPANIES_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response_companies.status_code == 200, (
        f"Запрос к {COMPANIES_ENDPOINT} с параметром 'status'={inactive_status} "
        f"вернул статус {response_companies.status_code}. Ожидался 200"
    )
    validate_content_type(response_companies)
    data_companies = get_validated_json(response_companies)

    companies = data_companies["data"]

    if not companies:
        pytest.skip("Нет компаний со статусом CLOSED")

    inactive_company_id = companies[0]["company_id"]

    # Берем ID юзера из фикстуры
    created_user_id = create_user["response"]["user_id"]

    # Подготовка данных с неактивной компанией
    user_data = {
        "first_name": "Sydney",
        "last_name": "Sweeney",
        "company_id": inactive_company_id,
    }

    # Отправка PUT-запроса
    try:
        response = requests.put(
            f"{USERS_ENDPOINT}/{created_user_id}",
            json=user_data,
            timeout=TIMEOUT,
        )
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {USERS_ENDPOINT}/{created_user_id} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 400, (
        f"Запрос к {USERS_ENDPOINT}/{created_user_id} вернул статус {response.status_code}. "
        f"Ожидался 400"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ошибки
    assert "detail" in data, "В ответе отсутствует поле detail"
    detail = data["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом (dict)"

    assert "reason" in detail, "В detail отсутствует поле reason"
    reason = detail["reason"]
    assert isinstance(reason, str), "reason должен быть строкой"
    assert len(reason) > 0, "reason не должна быть пустой"
    assert (
        "active" in reason.lower()
    ), f"reason не содержит упоминание о валидном статусе ACTIVE"


@pytest.mark.smoke
@allure.feature("Users")
@allure.story("DELETE /users/{id}")
@allure.severity(allure.severity_level.BLOCKER)
def test_tc28_delete_user_by_id(create_user):
    """TC-28: DELETE-запрос на удаление юзера по ID"""

    user_id = create_user["response"]["user_id"]

    try:
        response = requests.delete(f"{USERS_ENDPOINT}/{user_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {USERS_ENDPOINT}/{user_id} превысил таймаут {TIMEOUT} сек."

    assert response.status_code == 202, (
        f"Запрос к {USERS_ENDPOINT}/{user_id} вернул статус {response.status_code}. "
        f"Ожидался 202"
    )
    validate_content_type(response)

    # Проверка, что пользователь удалён
    try:
        response_get = requests.get(f"{USERS_ENDPOINT}/{user_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {USERS_ENDPOINT}/{user_id} превысил таймаут {TIMEOUT} сек."

    assert (
        response_get.status_code == 404
    ), f"Пользователь {user_id} всё ещё существует. Статус {response_get.status_code}"


@allure.feature("Users")
@allure.story("DELETE /users/{id}")
def test_tc29_delete_user_not_found():
    """TC-29: DELETE-запрос на удаление несуществующего юзера"""

    user_id = 851987

    try:
        response = requests.delete(f"{USERS_ENDPOINT}/{user_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {USERS_ENDPOINT}/{user_id} превысил таймаут {TIMEOUT} сек."

    assert response.status_code == 404, (
        f"Запрос к {USERS_ENDPOINT}/{user_id} вернул статус {response.status_code}. "
        f"Ожидался 404"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    assert "detail" in data, "В ответе отсутствует поле detail"
    detail = data["detail"]
    assert isinstance(detail, dict), "detail должен быть объектом (dict)"
    assert "reason" in detail, "В detail отсутствует поле reason"

    reason = detail["reason"]
    assert isinstance(reason, str), "reason должен быть строкой"
    assert len(reason) > 0, "reason не должна быть пустой"
    assert str(user_id) in reason, f"reason не содержит упоминание об id={user_id}"


@allure.feature("Users")
@allure.story("DELETE /users/{id}")
def test_tc30_delete_user_twice(create_user):
    """TC-30: Повторное удаление одного и того же юзера"""

    user_id = create_user["response"]["user_id"]

    # Первое удаление → 202
    try:
        response1 = requests.delete(f"{USERS_ENDPOINT}/{user_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {USERS_ENDPOINT}/{user_id} превысил таймаут {TIMEOUT} сек."

    assert response1.status_code == 202

    # Второе удаление → 404
    try:
        response2 = requests.delete(f"{USERS_ENDPOINT}/{user_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {USERS_ENDPOINT}/{user_id} превысил таймаут {TIMEOUT} сек."

    assert response2.status_code == 404


@allure.feature("Users")
@allure.story("DELETE /users/{id}")
def test_tc31_delete_user_invalid_id():
    """TC-31: DELETE-запрос на удаление юзера по невалидному ID"""

    user_id = "abc"

    try:
        response = requests.delete(f"{USERS_ENDPOINT}/{user_id}", timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert (
            False
        ), f"Запрос к {USERS_ENDPOINT}/{user_id} превысил таймаут {TIMEOUT} сек."

    assert response.status_code == 422, (
        f"Запрос к {USERS_ENDPOINT}/{user_id} вернул статус {response.status_code}. "
        f"Ожидался 422"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    assert "detail" in data, "В ответе отсутствует поле detail"
    detail = data["detail"]
    assert isinstance(detail, list), "detail должен быть массивом"
    assert len(detail) > 0, "detail пуст"

    first_error = detail[0]
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"В ошибке отсутствует поле '{field}'"

    assert "user_id" in str(first_error["loc"]), "loc не содержит упоминание о user_id"
    assert (
        "integer" in first_error["msg"].lower()
    ), "msg не содержит упоминание об integer"
