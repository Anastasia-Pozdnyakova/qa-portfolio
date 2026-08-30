"""Тестовые данные для /users"""

# Поля пользователя (обязательные)
USER_REQUIRED_FIELDS = [
    "last_name",
    "user_id",
]

USER_REQUIRED_FIELDS_AND_TYPES = [
    ("last_name", str),
    ("user_id", int),
]

# Поля пользователя (опциональные)
USER_OPTIONAL_FIELDS = [
    "first_name",
    "company_id",
]

# Тестовые данные
DEFAULT_COMPANY_ID = 3
INVALID_USER_ID = 99999
INVALID_USER_ID_STRING = "abc"
