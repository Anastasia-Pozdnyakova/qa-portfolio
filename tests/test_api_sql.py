"""Тесты с SQLite для API restapi.tech — интеграция API + БД"""

import pytest
import allure
import json

from api.companies_api import CompaniesAPI
from api.users_api import UsersAPI
from data.expected_status import EXPECTED_STATUS
from data.companies_data import (
    COMPANY_REQUIRED_FIELDS,
    COMPANY_REQUIRED_FIELDS_AND_TYPES,
)
from data.users_data import USER_ALL_FIELDS_AND_TYPES
from conftest import logger
from utils.helpers import (
    get_validated_json,
    validate_content_type,
    validate_response_structure,
    validate_fields_presence_and_type,
    get_companies_ids,
)

companies_api = CompaniesAPI()
users_api = UsersAPI()


# ========== ТЕСТЫ ==========
@pytest.mark.parametrize("company_id", get_companies_ids())
@allure.feature("SQL + API")
@allure.story("Сохранение компаний в БД")
@allure.severity(allure.severity_level.NORMAL)
def test_sql_save_company_by_id(db_connection, company_id):
    """Проверяет, что данные компании из API корректно сохраняются в SQLite"""

    # Получаем данные компании через API-клиент
    response = companies_api.get_company_by_id(company_id)
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    # Парсим JSON через хелпер
    validate_content_type(response)
    company = get_validated_json(response)
    logger.info(
        f"Получены данные компании {company_id}:\n{json.dumps(company, indent=2, ensure_ascii=False)}"
    )

    # Проверяем структуру ответа (поля компании)
    validate_response_structure(company, COMPANY_REQUIRED_FIELDS)
    validate_fields_presence_and_type(company, COMPANY_REQUIRED_FIELDS_AND_TYPES)

    # Берем соединение из фикстуры
    cursor = db_connection.cursor()

    # Удаляем старую запись, если есть (на случай повторного запуска)
    cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))

    # Вставляем данные (4 поля)
    cursor.execute(
        "INSERT INTO companies (id, name, address, status) VALUES (?, ?, ?, ?)",
        (
            company["company_id"],
            company["company_name"],
            company["company_address"],
            company["company_status"],
        ),
    )
    db_connection.commit()

    # Проверяем, что данные сохранились
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    row = cursor.fetchone()

    assert row is not None, f"Компания с id={company_id} не найдена в БД"
    assert row == (
        company["company_id"],
        company["company_name"],
        company["company_address"],
        company["company_status"],
    ), f"Данные в БД не совпадают: {row}"

    logger.info(f"Тест для компании {company_id} пройден")


@allure.feature("SQL + API")
@allure.story("Фильтрация данных в БД")
@allure.severity(allure.severity_level.NORMAL)
def test_sql_save_all_companies(db_connection):
    """Сохраняем все компании из API в SQLite и проверяем количество"""

    # Получаем данные компании через API-клиент
    response = companies_api.get_companies_with_params(limit=100)
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    validate_content_type(response)
    data = get_validated_json(response)
    validate_response_structure(data, ["data", "meta"])

    total_companies_from_api = data["meta"]["total"]
    companies = data["data"]

    logger.info(
        f"Получено {len(companies)} компаний из API. Всего по данным API: {total_companies_from_api}"
    )

    # Берем соединение из фикстуры
    cursor = db_connection.cursor()

    # Удаляем старую запись, если есть (на случай повторного запуска)
    cursor.execute("DELETE FROM companies")

    # Список кортежей из данных компаний
    companies_data = [
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
        """INSERT INTO companies (id, name, address, status) VALUES (?, ?, ?, ?)""",
        companies_data,
    )
    db_connection.commit()

    # Проверяем, что сохранилось
    cursor.execute("SELECT COUNT(*) FROM companies")
    count_in_db = cursor.fetchone()[0]

    # Сравниваем количество
    assert (
        count_in_db == total_companies_from_api
    ), f"В БД {count_in_db} записей, в API {total_companies_from_api}"

    logger.info("Тест пройден: в БД {count_in_db} записей")


@allure.feature("SQL + API")
@allure.story("Сохранение одной компании")
@allure.severity(allure.severity_level.MINOR)
def test_sql_filter_companies_by_status(db_connection):
    """Проверяем SQL-запрос с фильтрацией по статусу"""

    response = companies_api.get_companies_with_params(limit=100)
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    validate_content_type(response)
    all_data = get_validated_json(response)
    validate_response_structure(all_data, ["data", "meta"])

    all_companies = all_data["data"]

    logger.info(f"Получено всего – {len(all_companies)} компаний из API.")

    response = companies_api.get_companies_with_params(limit=100, status="ACTIVE")
    assert (
        response.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response.status_code}"

    validate_content_type(response)
    data = get_validated_json(response)
    validate_response_structure(data, ["data", "meta"])

    active_companies = data["data"]

    logger.info(
        f"Получено компаний со статусом ACTIVE – {len(active_companies)} из API."
    )

    # Берем соединение из фикстуры
    cursor = db_connection.cursor()

    # Удаляем старую запись
    cursor.execute("DELETE FROM companies")

    # Список кортежей из данных компаний
    companies_data = [
        (
            company["company_id"],
            company["company_name"],
            company["company_address"],
            company["company_status"],
        )
        for company in all_companies
    ]

    # Вставляем данные (4 поля)
    cursor.executemany(
        """
        INSERT INTO companies (id, name, address, status) 
        VALUES (?, ?, ?, ?)
        """,
        companies_data,
    )
    db_connection.commit()

    # Проверяем, что сохранилось
    cursor.execute("SELECT * FROM companies WHERE status = 'ACTIVE'")
    sql_active_rows = cursor.fetchall()

    logger.debug(f"SQL результат: {sql_active_rows}")

    # Сравниваем количество
    assert len(sql_active_rows) == len(active_companies), (
        f"В БД {len(sql_active_rows)} записей со статусом ACTIVE, "
        f"в API {len(active_companies)}"
    )

    # Проверить статус каждой записи
    for row in sql_active_rows:
        assert row[3] == "ACTIVE", f"Ожидался статус ACTIVE, получен {row[3]}"

    logger.info(f"Тест пройден: в БД {len(sql_active_rows)} записей")


@allure.feature("SQL + API")
@allure.story("Сохранение пользователей и компаний")
@allure.severity(allure.severity_level.NORMAL)
def test_sql_join_users_with_companies(db_connection):
    """Проверяем JOIN между пользователями и компаниями"""

    # Получаем компании
    response_companies = companies_api.get_companies_with_params(limit=10)
    assert (
        response_companies.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response_companies.status_code}"
    validate_content_type(response_companies)
    companies_data = get_validated_json(response_companies)
    validate_response_structure(companies_data, ["data", "meta"])
    companies = companies_data["data"]
    validate_fields_presence_and_type(companies[0], COMPANY_REQUIRED_FIELDS_AND_TYPES)

    logger.info(f"Получено {len(companies)} компаний")

    # Получаем пользователей
    response_users = users_api.get_users_with_params(limit=10)
    assert (
        response_users.status_code == EXPECTED_STATUS["valid"]
    ), f"Ожидался статус {EXPECTED_STATUS['valid']}, получен {response_users.status_code}"
    validate_content_type(response_users)
    users_data = get_validated_json(response_users)
    validate_response_structure(users_data, ["data", "meta"])
    users = users_data["data"]
    validate_fields_presence_and_type(users[0], USER_ALL_FIELDS_AND_TYPES)

    logger.info(f"Получено {len(users)} пользователей")

    # Берем соединение из фикстуры
    cursor = db_connection.cursor()

    # Удаляем старую запись, если есть (на случай повторного запуска)
    cursor.execute("DELETE FROM companies")
    cursor.execute("DELETE FROM users")

    # Список кортежей из данных компаний
    companies_row = [
        (
            company["company_id"],
            company["company_name"],
            company["company_address"],
            company["company_status"],
        )
        for company in companies
    ]

    # Список кортежей из данных пользователей
    users_row = [
        (user["user_id"], user["first_name"], user["last_name"], user["company_id"])
        for user in users
    ]

    # Вставляем данные компаний
    cursor.executemany(
        """INSERT INTO companies (id, name, address, status) VALUES (?, ?, ?, ?)""",
        companies_row,
    )
    db_connection.commit()

    # Вставляем данные пользователей
    cursor.executemany(
        """INSERT INTO users (id, first_name, last_name, company_id) VALUES (?, ?, ?, ?)""",
        users_row,
    )
    db_connection.commit()

    # JOIN
    cursor.execute("""
        SELECT u.id, u.first_name, u.last_name, c.name 
        FROM users u 
        JOIN companies c ON u.company_id = c.id
    """)
    join_result = cursor.fetchall()

    logger.info(f"Результат JOIN: {len(join_result)} записей")

    # Проверяем количество
    assert len(join_result) == len(
        users
    ), f"Количество записей в JOIN-результате ({len(join_result)}) "
    f"не совпадает с количеством пользователей ({len(users)}). "
    f"Значит, у некоторых пользователей указан несуществующий company_id, "
    f"и они не связались с таблицей companies."

    # Проверяем, что у каждого есть компания
    for row in join_result:
        assert row[3] is not None, "У пользователя нет компании"

    # Проверить, что компания не пустая
    for row in join_result:
        assert len(row[3]) > 0, "Название компании пустое"


# ========== БУДУЩИЕ ТЕСТЫ (план) ==========

# def test_sql_count_users_per_company():
#     """Количество пользователей в каждой компании (GROUP BY)"""
#     pass

# def test_sql_users_without_company():
#     """Пользователи, у которых нет компании (LEFT JOIN)"""
#     pass

# def test_sql_aggregate_active_companies():
#     """Агрегация: активные компании и пользователи в них"""
#     pass
