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

# Поля пользователя (все)
USER_ALL_FIELDS = [
    "last_name",
    "user_id",
    "first_name",
    "company_id",
]

USER_ALL_FIELDS_AND_TYPES = [
    ("first_name", str),
    ("last_name", str),
    ("company_id", int),
    ("user_id", int),
]

# Тестовые данные
DEFAULT_COMPANY_ID = 3
INVALID_USER_ID = 99999
INVALID_USER_ID_STRING = "abc"
