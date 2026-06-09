"""КОНСТАНТЫ"""

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
