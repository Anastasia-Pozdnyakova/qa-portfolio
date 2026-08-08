import requests
import time
import pytest
import constants
from utils.helpers import get_validated_json, validate_content_type

# ========== Настройки ==========
BASE_URL = "https://restapi.tech/api"
TIMEOUT = 5
USERS_ENDPOINT = f"{BASE_URL}/users"
AUTH_ENDPOINT = f"{BASE_URL}/auth/authorize"
VALID_PASSWORD = "qwerty12345"


# ========== Фикстура: создание пользователя ==========
@pytest.fixture
def create_user():
    """Фикстура для создания нового юзера + получения данных + очистка БД после теста"""

    user_data = constants.create_unique_user()

    try:
        response = requests.post(USERS_ENDPOINT, json=user_data, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        pytest.fail(f"Запрос к {USERS_ENDPOINT} превысил таймаут {TIMEOUT} сек.")

    assert response.status_code == 201, f"Ожидался 201, получен {response.status_code}"
    full_user = get_validated_json(response)

    # Отдаём данные создания и результат (словарь)
    yield {"data": user_data, "response": full_user}

    # Очистка
    user_id = full_user["user_id"]
    # Чекаем, существует ли ещё пользователь и удаляем
    check = requests.get(f"{USERS_ENDPOINT}/{user_id}", timeout=TIMEOUT)
    if check.status_code == 200:
        requests.delete(f"{USERS_ENDPOINT}/{user_id}", timeout=TIMEOUT)


# ========== Фикстура: токен авторизации ==========
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
