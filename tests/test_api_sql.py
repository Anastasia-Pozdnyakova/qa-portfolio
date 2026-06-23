"""Тесты с SQLite для API restapi.tech — интеграция API + БД"""

import pytest
import requests
import sqlite3
import logging
import os

# ========== Настройки ==========
BASE_URL = "https://restapi.tech/api"
COMPANIES_ENDPOINT = f"{BASE_URL}/companies"
TIMEOUT = 5

# Режим отладки: True — старый файл удаляется, новый остается, False — старый и новый удаляются
DEBUG_MODE = True

# Имя файла БД
DB_NAME = "test_companies.db"

# ========== Логирование ==========
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== Вспомогательные функции ==========
def get_company_ids():
    """Получает список ID компаний из /companies (берётся из data[])"""
    response = requests.get(
        f"{COMPANIES_ENDPOINT}", params={"limit": 100}, timeout=TIMEOUT
    )
    assert response.status_code == 200, f"API вернул статус {response.status_code}"

    data = response.json()
    assert "data" in data, f"Ожидался ключ 'data', но пришёл ответ: {list(data.keys())}"

    companies = data["data"]
    assert isinstance(companies, list), "Поле 'data' должно быть списком"
    return [company["company_id"] for company in companies[:3]]  # Первые 3 ID


# ========== Фикстура: БД и таблица ========
@pytest.fixture(scope="session")
def db_connection():
    """Создаёт БД, таблицу, возвращает соединение"""

    # Удаяет старый файл, если есть
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        logger.info(f"Удален сарый файл БД: {DB_NAME}")

    # Подключается
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Создает таблицу
    cursor.execute(
        """CREATE TABLE companies (id INTEGER PRIMARY KEY, name TEXT, address TEXT, status TEXT)"""
    )
    conn.commit()

    logger.info("Таблица companies создана")

    yield conn  # передаёт соединение в тесты

    # После всех тестов
    conn.close()
    if not DEBUG_MODE and os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        logger.info(f"Файл {DB_NAME} удален")
    elif DEBUG_MODE:
        logger.info(f"Режим DEBUG: файл {DB_NAME} оставлен для анализа")


# ========== Тесты ==========
@pytest.mark.parametrize("company_id", get_company_ids())
def test_sql_with_api_companies(db_connection, company_id):
    """Проверяет, что данные компании из API корректно сохраняются в SQLite"""

    # Получаем данные компании по ID
    response = requests.get(f"{COMPANIES_ENDPOINT}/{company_id}", timeout=TIMEOUT)
    assert response.status_code == 200, f"API вернул {response.status_code}"

    # Парсинг JSON
    data = response.json()
    logger.info(f"Получены данные компании {company_id}: {data}")

    # Проверяем структуру ответа
    required_fields = [
        "company_id",
        "company_name",
        "company_address",
        "company_status",
    ]
    for field in required_fields:
        assert field in data, f"Поле {field} отсутствует в ответе"

    # Берем соединение из фикстуры
    cursor = db_connection.cursor()

    # Удаляем старую запись, если есть (на случай повторного запуска)
    cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))

    # Вставляем данные (4 поля)
    cursor.execute(
        "INSERT INTO companies (id, name, address, status) VALUES (?, ?, ?, ?)",
        (
            data["company_id"],
            data["company_name"],
            data["company_address"],
            data["company_status"],
        ),
    )
    db_connection.commit()

    # Проверяем, что сохранилось
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    row = cursor.fetchone()

    assert row is not None, f"Компания с id={company_id} не найдена в БД"
    assert row == (
        data["company_id"],
        data["company_name"],
        data["company_address"],
        data["company_status"],
    )

    logger.info(f"Тест для компании {company_id} пройден")


def test_sql_save_all_companies(db_connection):
    """Сохраняем все компании из API в SQLite и проверяем количество"""

    # Получаем список всех компаний из API
    response = requests.get(
        f"{COMPANIES_ENDPOINT}", params={"limit": 100}, timeout=TIMEOUT
    )
    assert response.status_code == 200, f"API вернул {response.status_code}"

    # Парсинг JSON
    data = response.json()

    # Берём общее количество компаний из meta.total
    total_companies_from_api = data["meta"]["total"]

    # Проверка структуры ответа
    companies = data["data"]
    assert len(companies) > 0, "Список компаний пуст"

    # Берем соединение из фикстуры
    cursor = db_connection.cursor()

    # Удаляем старую запись
    cursor.execute("DELETE FROM companies")

    # Собираем список кортежей из данных компаний
    data_for_insert = [
        (
            company["company_id"],
            company["company_name"],
            company["company_address"],
            company["company_status"],
        )
        for company in companies
    ]

    # Вставляем данные (4 поля)
    cursor.executemany(
        """
        INSERT INTO companies (id, name, address, status) 
        VALUES (?, ?, ?, ?)
        """,
        data_for_insert,
    )
    db_connection.commit()

    # Проверяем, что сохранилось
    cursor.execute("SELECT COUNT(*) FROM companies")
    count_in_db = cursor.fetchone()[0]

    # Сравниваем количество компаний из API и БД
    assert (
        count_in_db == total_companies_from_api
    ), f"В БД {count_in_db} записей, в API {total_companies_from_api}"


def test_sql_filter_active_companies(db_connection):
    """Проверяем SQL-запрос с фильтрацией по статусу"""

    # Получаем список всех компаний из API
    response_all = requests.get(
        f"{COMPANIES_ENDPOINT}", params={"limit": 100}, timeout=TIMEOUT
    )
    assert response_all.status_code == 200, f"API вернул {response_all.status_code}"

    # Парсинг JSON
    data_all = response_all.json()

    # Сохраняем список всех компаний
    companies = data_all["data"]

    # Получаем только ACTIVE
    response_active = requests.get(
        f"{COMPANIES_ENDPOINT}",
        params={"limit": 100, "status": "ACTIVE"},
        timeout=TIMEOUT,
    )
    assert (
        response_active.status_code == 200
    ), f"API вернул {response_active.status_code}"

    # Парсинг JSON
    data_active = response_active.json()

    # Сохраняем список компаний со статусом
    companies_active = data_active["data"]

    # Сохраняем количество компаний со статусом
    count_api_active = len(companies_active)

    # Берем соединение из фикстуры
    cursor = db_connection.cursor()

    # Удаляем старую запись
    cursor.execute("DELETE FROM companies")

    # Собираем список кортежей из данных компаний
    data_for_insert = [
        (
            company["company_id"],
            company["company_name"],
            company["company_address"],
            company["company_status"],
        )
        for company in companies
    ]

    # Вставляем данные (4 поля)
    cursor.executemany(
        """
        INSERT INTO companies (id, name, address, status) 
        VALUES (?, ?, ?, ?)
        """,
        data_for_insert,
    )
    db_connection.commit()

    # Проверяем, что сохранилось
    cursor.execute("SELECT * FROM companies WHERE status = 'ACTIVE'")
    sql_active_rows = cursor.fetchall()

    logger.debug(f"SQL результат: {sql_active_rows}")

    # Сравниваем количество
    assert len(sql_active_rows) == count_api_active, (
        f"В БД {len(sql_active_rows)} записей со статусом ACTIVE, "
        f"в API {count_api_active}"
    )

    # Проверить статус каждой записи
    for row in sql_active_rows:
        assert row[3] == "ACTIVE", f"Ожидался статус ACTIVE, получен {row[3]}"
