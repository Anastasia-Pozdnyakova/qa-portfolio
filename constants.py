"""КОНСТАНТЫ"""

import time

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


# Поля пользователя (обязательные)
USER_REQUIRED_FIELDS = [
    "last_name",
    "user_id",
]

# Поля пользователя (опциональные)
USER_OPTIONAL_FIELDS = [
    "first_name",
    "company_id",
]


# Данные для создания /users
def create_unique_user():
    timestamp = int(time.time())
    return {
        "first_name": f"User_{timestamp}",
        "last_name": f"Test_{timestamp}",
        "company_id": 3,
    }
