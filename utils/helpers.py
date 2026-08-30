"""Вспомогательные функции"""

import json
from data.expected_status import EXPECTED_STATUS
from data.companies_data import COMPANY_REQUIRED_FIELDS
from api.companies_api import CompaniesAPI

companies_api = CompaniesAPI()


def validate_content_type(response, expected_type="application/json"):
    """
    Проверяет, что заголовок Content-Type соответствует ожидаемому.

    :param response: объект ответа requests
    :param expected_type: ожидаемый MIME-тип (по умолчанию application/json)
    """
    content_type = response.headers.get("Content-Type", "")
    assert content_type.startswith(
        expected_type
    ), f"Content-Type некорректен: '{content_type}'. Ожидался '{expected_type}'"


def get_validated_json(response):
    """
    Извлекает и проверяет JSON из ответа.

    :param response: объект ответа requests
    :return: распарсенный JSON (dict/list)
    """
    try:
        data = response.json()
        return data
    except json.JSONDecodeError:
        assert False, f"Ответ не является валидным JSON. Тело {response.text[:200]}"


def validate_response_structure(data, required_keys):
    """
    Проверяет, что в ответе присутствуют все обязательные поля.

    :param data: распарсенный JSON (dict)
    :param required_keys: список обязательных полей (list)
    """
    for key in required_keys:
        assert key in data, f"Отсутствует поле '{key}'"


def validate_meta(meta, expected_offset=None, expected_limit=None):
    """
    Универсальная проверка полей meta (limit и offset).

    :param meta: словарь с полями meta из ответа API
    :param expected_offset: ожидаемое значение offset (если None — проверка пропускается)
    :param expected_limit: ожидаемое значение limit (если None — проверка пропускается)
    """
    if expected_offset is not None:
        assert (
            meta["offset"] == expected_offset
        ), f"Ожидался offset={expected_offset}, получен meta.offset={meta['offset']}"
    if expected_limit is not None:
        assert (
            meta["limit"] == expected_limit
        ), f"Ожидался limit={expected_limit}, получен meta.limit={meta['limit']}"


def validate_companies_list(companies, required_fields):
    """
    Проверяет, что список компаний не пустой и у первой компании есть обязательные поля.

    :param companies: список компаний из ответа API (data['data'])
    :param required_fields: список обязательных полей (например, COMPANY_REQUIRED_FIELDS)
    """
    assert companies, "Список компаний пуст"
    validate_response_structure(companies[0], required_fields)


def validate_fields_presence_and_type(data, fields_with_types, allow_empty=False):
    """
    Проверяет, что поле есть в ответе, имеет нужный тип.

    Проверяет наличие и тип одного или нескольких полей.

    :param data: распарсенный JSON (dict)
    :param fields_with_types:
        - кортеж (field, expected_type: str, int, list, dict, bool) для одного поля
        - список кортежей для нескольких полей
          Пример: [("user_name", str), ("user_id", int)]
    :param allow_empty: разрешать ли пустые значения для str/list (по умолчанию False)
    """
    if isinstance(fields_with_types, tuple):
        fields_with_types = [fields_with_types]

    for field, expected_type in fields_with_types:
        assert field in data, f"Поле '{field}' отсутствует"
        value = data[field]

        assert isinstance(value, expected_type), (
            f"Поле '{field}' должно быть типа {expected_type.__name__}, "
            f"получено {type(value).__name__}"
        )

        if expected_type in (str, list) and not allow_empty:
            assert value, f"Поле '{field}' не должно быть пустым"


def get_active_company_id():
    """Возвращает ID первой активной компании (status=ACTIVE)"""
    response = companies_api.get_companies_with_params(status="ACTIVE")

    # Проверка статуса
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    # Парсим JSON, проверяем структуру
    data = get_validated_json(response)
    validate_response_structure(data, ["data", "meta"])

    companies = data["data"]
    assert companies, "Нет активных компаний"
    validate_response_structure(companies[0], COMPANY_REQUIRED_FIELDS)

    return companies[0]["company_id"]


def get_inactive_company_id():
    """Возвращает ID первой неактивной компании (status=CLOSED)"""
    response = companies_api.get_companies_with_params(status="CLOSED")

    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    data = get_validated_json(response)
    validate_response_structure(data, ["data", "meta"])

    companies = data["data"]
    assert companies, "Нет неактивных компаний"
    validate_response_structure(companies[0], COMPANY_REQUIRED_FIELDS)

    return companies[0]["company_id"]


def validate_422_error(error_data, expected_field):
    """
    Проверяет ошибку 422 (Validation Error).

    :param error_data: распарсенный JSON ответа
    :param expected_field: ожидаемое поле в 'loc' (например, 'last_name')
    """
    # Проверяем структуру ошибки
    assert "detail" in error_data, "В ответе отсутствует поле detail"
    detail = error_data["detail"]

    assert isinstance(detail, list), "detail должен быть массивом"
    assert len(detail) > 0, "detail не должен быть пустым"

    # Берём первую ошибку
    first_error = detail[0]

    # Проверяем, что есть поля type, loc, msg
    for field in ["type", "loc", "msg"]:
        assert field in first_error, f"В ошибке отсутствует поле '{field}'"

    # Проверяем, что loc содержит нужное поле
    assert (
        expected_field in first_error["loc"]
    ), f"Ожидалось поле '{expected_field}' в loc, получено {first_error['loc']}"


def validate_404_error(error_data, expected_substr=None):
    """
    Проверяет ошибку 404 (Not Found).

    :param error_data: распарсенный JSON ответа
    :param expected_substr: ожидаемая подстрока в 'reason' (опционально)
    """
    assert "detail" in error_data, "В ответе отсутствует поле detail"
    detail = error_data["detail"]
    assert "reason" in detail, "Поле reason отсутствует"

    reason = detail["reason"]
    assert isinstance(reason, str), "Поле reason не строка"
    assert reason, "Поле reason пустое"

    # Если передана подстрока — проверяем (опционально)
    if expected_substr:
        assert (
            expected_substr in reason.lower()
        ), f"В тексте ошибки нет упоминания об '{expected_substr}'. Получено: {reason}"


def validate_401_error(error_data, expected_substr=None):
    """
    Проверяет ошибку 401 (Unauthorized).

    :param error_data: распарсенный JSON ответа
    :param expected_substr: ожидаемая подстрока в 'reason' (опционально)
    """
    assert "detail" in error_data, "В ответе отсутствует поле detail"
    detail = error_data["detail"]
    assert "reason" in detail, "Поле reason отсутствует"

    reason = detail["reason"]
    assert isinstance(reason, str), "Поле reason не строка"
    assert reason, "Поле reason пустое"

    if expected_substr:
        assert (
            expected_substr in reason.lower()
        ), f"В тексте ошибки нет упоминания об '{expected_substr}'. Получено: {reason}"


def validate_403_error(error_data, expected_substr=None):
    """
    Проверяет ошибку 403 (Forbidden).

    :param error_data: распарсенный JSON ответа
    :param expected_substr: ожидаемая подстрока в 'reason' (опционально)
    """
    assert "detail" in error_data, "В ответе отсутствует поле detail"
    detail = error_data["detail"]
    assert "reason" in detail, "Поле reason отсутствует"

    reason = detail["reason"]
    assert isinstance(reason, str), "Поле reason не строка"
    assert reason, "Поле reason пустое"

    if expected_substr:
        assert (
            expected_substr in reason.lower()
        ), f"В тексте ошибки нет упоминания об '{expected_substr}'. Получено: {reason}"


def validate_400_error(error_data, expected_substr=None):
    """
    Проверяет ошибку 400 (Bad Request).

    :param error_data: распарсенный JSON ответа
    :param expected_substr: ожидаемая подстрока в 'reason' (опционально)
    """
    assert "detail" in error_data, "В ответе отсутствует поле detail"
    detail = error_data["detail"]
    assert "reason" in detail, "Поле reason отсутствует"

    reason = detail["reason"]
    assert isinstance(reason, str), "Поле reason не строка"
    assert reason, "Поле reason пустое"

    if expected_substr:
        assert (
            expected_substr in reason.lower()
        ), f"В тексте ошибки нет упоминания об '{expected_substr}'. Получено: {reason}"
