"""Тестовые данные для /companies"""

# Базовые параметры для тестов
COMPANY_IDS = [1, 2, 3]
INVALID_COMPANY_ID = 9999
INVALID_COMPANY_ID_STRING = "abc"

# Параметры для запросов
LIMIT_VALUES = [5, 0, "abc"]
OFFSET_VALUES = [2, -1]
STATUS_VALUES = ["ACTIVE", "INVALID"]

# Поля компании
COMPANY_REQUIRED_FIELDS = [
    "company_id",
    "company_name",
    "company_address",
    "company_status",
]

# Допустимые статусы
VALID_STATUSES = ["ACTIVE", "CLOSED", "BANKRUPT"]

# Поля переводов в description_lang
TRANSLATION_REQUIRED_FIELDS = [
    "translation_lang",
    "translation",
]

# Поля компании (для SQL)
COMPANY_SQL_FIELDS = ["id", "name", "address", "status"]
