"""Методы для работы с API /users"""

import requests
import pytest
import time
from config import BASE_URL, TIMEOUT
from data.users_data import DEFAULT_COMPANY_ID


class UsersAPI:
    """
    Клиент для работы с эндпоинтами /users.

    Использует базовый URL и таймаут из config.
    Все методы возвращают объект Response из библиотеки requests.

    Методы:
        create_user(user_data)
            Создать пользователя (POST /users).
        get_user(user_id)
            Получить пользователя по ID (GET /users/{id}).
        update_user(user_id, user_data)
            Обновить пользователя (PUT /users/{id}).
        delete_user(user_id)
            Удалить пользователя (DELETE /users/{id}).
        _generate_user_data()
            Сгенерировать уникальные данные для пользователя (внутренний метод).
    """

    def __init__(self):
        self.base_url = BASE_URL
        self.timeout = TIMEOUT

    def create_user(self, user_data=None):
        """POST /users"""
        if user_data is None:
            user_data = self._generate_user_data()

        try:
            url = f"{self.base_url}/users"
            return requests.post(url, json=user_data, timeout=self.timeout)
        except requests.exceptions.Timeout:
            pytest.fail(f"Таймаут {self.timeout} сек. при запросе к {url}")

    def get_user(self, user_id):
        """GET /users/{id}"""
        try:
            url = f"{self.base_url}/users/{user_id}"
            return requests.get(url, timeout=self.timeout)
        except requests.exceptions.Timeout:
            pytest.fail(f"Таймаут {self.timeout} сек. при запросе к {url}")

    def update_user(self, user_id, user_data):
        """PUT /users/{id}"""
        try:
            url = f"{self.base_url}/users/{user_id}"
            return requests.put(url, json=user_data, timeout=self.timeout)
        except requests.exceptions.Timeout:
            pytest.fail(f"Таймаут {self.timeout} сек. при запросе к {url}")

    def delete_user(self, user_id):
        """DELETE /users/{id}"""
        try:
            url = f"{self.base_url}/users/{user_id}"
            return requests.delete(url, timeout=self.timeout)
        except requests.exceptions.Timeout:
            pytest.fail(f"Таймаут {self.timeout} сек. при запросе к {url}")

    def _generate_user_data(self):
        """Генерирует уникальные данные для пользователя"""
        timestamp = int(time.time())
        return {
            "first_name": f"User_{timestamp}",
            "last_name": f"Test_{timestamp}",
            "company_id": DEFAULT_COMPANY_ID,
        }

    def get_users_with_params(self, **kwargs):
        """GET /users с параметрами (limit, offset)"""
        try:
            url = f"{self.base_url}/users"
            return requests.get(url, params=kwargs, timeout=self.timeout)
        except requests.exceptions.Timeout:
            pytest.fail(f"Запрос к {url} превысил таймаут {self.timeout} сек.")
