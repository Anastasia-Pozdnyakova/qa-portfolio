"""Тестовые данные для /auth"""

# Базовые параметры для тестов
VALID_PASSWORD = "qwerty12345"
VALID_LOGIN_PREFIX = "user_"
TIMEOUT = 360  # время жизни токена

# Данные для негативных тестов
INVALID_PASSWORD = "qwerty1"
SHORT_LOGIN = "us"
INVALID_TOKEN = "invalid_token_123"

# Поля для /auth/me
AUTH_ME_REQUIRED_FIELDS = [
    "user_name",
    "email_address",
    "valid_till",
]
