import pytest
import logging
import sqlite3
import os

from config import BASE_URL, TIMEOUT
from utils.helpers import get_validated_json, validate_content_type

from data.expected_status import EXPECTED_STATUS

# ========== Логирование ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== Фикстура: создание пользователя ==========
@pytest.fixture
def create_user():
    """Фикстура для создания нового юзера + очистка после теста"""
    from api.users_api import UsersAPI

    api = UsersAPI()
    user_data = api._generate_user_data()
    response = api.create_user(user_data)

    assert (
        response.status_code == EXPECTED_STATUS["created"]
    ), f"Ожидался статус {EXPECTED_STATUS['created']}, получен {response.status_code}"
    validate_content_type(response)
    full_user = get_validated_json(response)

    yield {"data": user_data, "response": full_user}

    # Очистка
    user_id = full_user["user_id"]
    api.delete_user(user_id)


# ========== Фикстура: токен авторизации ==========
@pytest.fixture(scope="session")
def auth_token():
    """Фикстура для получения токена"""
    from api.auth_api import AuthAPI

    api = AuthAPI()
    response = api.authorize()

    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"
    validate_content_type(response)
    data = get_validated_json(response)

    assert "token" in data, "В ответе отсутствует поле token"
    token = data["token"]
    assert isinstance(token, str), "token должен быть строкой"
    assert len(token) > 0, "token не должен быть пустым"

    return token


# ========== Фикстура: БД ==========
@pytest.fixture(scope="session")
def db_connection():
    """Создаёт БД, таблицы, возвращает соединение"""
    DB_NAME = "test_api.db"
    DEBUG_MODE = True

    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        logger.info(f"Удален старый файл БД: {DB_NAME}")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Таблица компаний
    cursor.execute(
        """CREATE TABLE companies (id INTEGER PRIMARY KEY, name TEXT, address TEXT, status TEXT)"""
    )

    # Таблица пользователей
    cursor.execute(
        """CREATE TABLE users (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, company_id INTEGER, FOREIGN KEY (company_id) REFERENCES companies(id))"""
    )

    conn.commit()
    logger.info("Таблицы companies и users созданы")

    yield conn

    conn.close()
    if not DEBUG_MODE and os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        logger.info(f"Файл {DB_NAME} удален")
    elif DEBUG_MODE:
        logger.info(f"Режим DEBUG: файл {DB_NAME} оставлен для анализа")
