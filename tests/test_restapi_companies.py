"""Автотесты для API restapi.tech
Эндпоинт: /companies
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
def test_tc01_get_all_companies():
    """TC-01: Базовый GET-запрос на получение всех компаний"""

    # Отправка GET-запроса
    try:
        response = requests.get(COMPANIES_ENDPOINT, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {COMPANIES_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {COMPANIES_ENDPOINT} вернул статус {response.status_code}. "
        f"Ожидался 200"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(data, ["data", "meta"])

    companies = data["data"]
    assert companies, "Массив 'data' пуст"

    # Валидация обязательных полей первой компании
    for field in constants.COMPANY_REQUIRED_FIELDS:
        assert field in companies[0], f"В компании отсутствует поле '{field}'"


def test_tc02_get_companies_with_limit():
    """ТС-02: Параметр limit ограничивает количество компаний"""

    # Подготовка данных
    limit_value = 5

    # Отправка GET-запроса с limit
    try:
        response = requests.get(
            COMPANIES_ENDPOINT, params={"limit": limit_value}, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {COMPANIES_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {COMPANIES_ENDPOINT} с параметрами {{'limit': {limit_value}}} "
        f"вернул статус {response.status_code}. Ожидался 200"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка, что meta.limit соответствует запросу
    assert data["meta"]["limit"] == limit_value

    # Проверка, что количество компаний в data не больше limit
    companies = data["data"]
    assert companies, "Массив 'data' пуст"
    assert len(companies) <= limit_value


def test_tc03_get_companies_with_offset():
    """ТС-03: Параметр offset сдвигает количество компаний"""

    # Подготовак данных
    offset_value = 2
    limit_value = 3  # по умолчанию limit=3 в API

    # Отправка GET-запроса с offset и limit=1 — получаем только одну компанию на позиции offset
    try:
        response = requests.get(
            COMPANIES_ENDPOINT,
            params={"offset": offset_value, "limit": limit_value},
            timeout=TIMEOUT,
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {COMPANIES_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {COMPANIES_ENDPOINT} с параметрами {{'offset': {offset_value}, 'limit': {limit_value}}} "
        f"вернул статус {response.status_code}. Ожидался 200"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(data, ["data", "meta"])

    companies = data["data"]
    meta = data["meta"]

    # Проверка полей meta
    assert (
        meta["offset"] == offset_value
    ), f"meta.offset={meta['offset']}, но ожидался {offset_value}"
    assert (
        meta["limit"] == limit_value
    ), f"meta.limit={meta['limit']}, но ожидался {limit_value}"

    # Если offset >= total, массив может быть пустым
    total_companies = meta["total"]
    if offset_value >= total_companies:
        assert not companies, (
            f"При offset={offset_value} (total={total_companies}) ожидался пустой массив, "
            f"но получен {len(companies)} компаний."
        )
        return

    # Проверка, что количество компаний не превышает limit
    assert (
        len(companies) <= limit_value
    ), f"Количество компаний ({len(companies)}) превышает limit={limit_value}"

    # Проверка наличия компаний (если offset в пределах total)
    if companies:
        # Валидация обязательных полей первой компании
        for field in constants.COMPANY_REQUIRED_FIELDS:
            assert field in companies[0], f"В компании отсутствует поле '{field}'"

    # Проверка соответствия ID компании позиции offset
    # В ответе API первая компания при offset=2 имеет company_id=3
    actual_company_id = companies[0]["company_id"]

    # Получаем ожидаемый ID из константы
    expected_company_id = offset_value + 1

    assert actual_company_id == expected_company_id, (
        f"Компания на позиции offset={offset_value} некорректна. "
        f"Ожидался ID {expected_company_id}, получен {actual_company_id}"
    )


def test_tc04_get_companies_filter_by_active_status():
    """TC-04: Фильтрация компаний по статусу ACTIVE"""

    # Подготовка данных
    status_value = "ACTIVE"

    # Отправка GET-запроса со статусом
    try:
        response = requests.get(
            COMPANIES_ENDPOINT, params={"status": status_value}, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {COMPANIES_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка + парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {COMPANIES_ENDPOINT} с параметрами {{'status': {status_value}}} "
        f"вернул статус {response.status_code}. Ожидался 200"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры ответа
    validate_response_structure(data, ["data", "meta"])

    companies = data["data"]
    assert companies, f"Массив 'data' пуст, нет компаний со статусом {status_value}"

    # Проверка, что у всех компаний статус соответствует запросу
    for company in companies:
        assert (
            company["company_status"] == status_value
        ), f"Ожидался статус {status_value}, получен {company['company_status']}"


def test_tc05_invalid_status_returns_422():
    """TC-05: Проверка корректности ошибки при невалидном статусе"""

    # Подготовка данных
    status_value = "INVALID"

    # Отправка GET-запроса
    try:
        response = requests.get(
            COMPANIES_ENDPOINT, params={"status": status_value}, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {COMPANIES_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса и заголовка
    assert response.status_code == 422, (
        f"Запрос к {COMPANIES_ENDPOINT} с параметрами {{'status': status_value}} "
        f"вернул статус {response.status_code}. Ожидался 422"
    )
    validate_content_type(response)

    # Парсинг JSON
    error_data = get_validated_json(response)

    # Проверка структуры detail
    assert "detail" in error_data, "В ответе отсутствует поле 'detail'"
    detail = error_data["detail"]
    assert isinstance(detail, list), "detail должен быть массивом"
    assert len(detail) > 0, "detail пуст"

    # Извлекаем первую ошибку
    first_error = detail[0]

    # Проверка обязательных полей ошибки
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"В ошибке отсутствует поле '{field}'"

    # Проверка, что сообщение об ошибке содержит упоминание допустимых статусов
    assert any(
        status in first_error["msg"] for status in constants.VALID_STATUSES
    ), f"Сообщение об ошибке не содержит ни одного из допустимых статусов: {constants.VALID_STATUSES}"


def test_tc06_limit_zero_returns_empty_data():
    """TC-06: limit=0 возвращает статус 200 и пустой массив data"""

    # Подготовка данных
    limit_value = 0

    # Отправка GET-запроса
    try:
        response = requests.get(
            COMPANIES_ENDPOINT, params={"limit": limit_value}, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {COMPANIES_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса, заголовка парсинг JSON
    assert response.status_code == 200, (
        f"Запрос к {COMPANIES_ENDPOINT} с параметром {{'limit': {limit_value}}} "
        f"вернул статус {response.status_code}. Ожидался 200"
    )
    validate_content_type(response)
    data = get_validated_json(response)

    # Проверка структуры data
    validate_response_structure(data, ["data", "meta"])

    # Проверка, что limit=0
    limit = data["meta"]["limit"]
    assert limit == limit_value, f"'limit' равен {limit}, а должно быть {limit_value}"

    # Проверка, что data пустой
    companies = data["data"]
    assert isinstance(companies, list), "'data' должен быть массивом"
    assert not companies, f"Массив 'data' не пустой"


def test_tc07_limit_abc_returns_422():
    """TC-07: limit=abc возвращает статус 422 и detail об ошибке"""

    # Подготовка данных
    limit_value = "abc"

    # Отправка GET-запроса
    try:
        response = requests.get(
            COMPANIES_ENDPOINT, params={"limit": limit_value}, timeout=TIMEOUT
        )
    except requests.exceptions.Timeout:
        assert False, f"Запрос к {COMPANIES_ENDPOINT} превысил таймаут {TIMEOUT} сек."

    # Проверка статуса и заголовка
    assert response.status_code == 422, (
        f"Запрос к {COMPANIES_ENDPOINT} с параметром {{'limit': {limit_value}}} "
        f"вернул статус {response.status_code}. Ожидался 422"
    )
    validate_content_type(response)

    # Парсинг JSON
    error_data = get_validated_json(response)

    # Проверка, что в ответе есть detail, массив и не пустой
    assert "detail" in error_data, "В ответе отсутствует поле 'detail'"
    detail = error_data["detail"]
    assert isinstance(detail, list), "detail должен быть массивом"
    assert len(detail) > 0, "detail пуст"

    # Извлекаем первую ошибку
    first_error = detail[0]

    # Проверка обязательных полей
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"В ошибке отсутствует {field}"

    # Проверка типа поля ошибки и содержание
    assert isinstance(first_error["msg"], str), "Поле 'msg' не строка"
    assert "integer" in first_error["msg"], "Сообщение об ошибке не содержит 'integer'"


def test_tc08_offset_negative_one_returns_no_shift():
    """TC-08: offset=-1 возвращает статус 200, компании без сдвига"""
