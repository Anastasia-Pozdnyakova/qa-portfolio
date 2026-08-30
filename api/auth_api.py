"""Методы для работы с API /auth"""

import requests
import pytest
import time
from config import BASE_URL, TIMEOUT
from data.auth_data import VALID_PASSWORD, VALID_LOGIN_PREFIX


class AuthAPI:
    """
    Клиент для работы с эндпоинтами /auth/authorize и /auth/me.

    Использует базовый URL и таймаут из config.
    Все методы возвращают объект Response из библиотеки requests.

    Методы:
        authorize(login, password, timeout_sec)
            Получить токен (POST /auth/authorize).
        get_me(token)
            Получить данные текущего пользователя (GET /auth/me).
    """

    def __init__(self):
        self.base_url = BASE_URL
        self.timeout = TIMEOUT

    def authorize(self, login="default", password="default", timeout_sec=360):
        """
        POST /auth/authorize

        :param login:
            - "default" → генерируется
            - None → поле НЕ передаётся
            - "" → передаётся пустая строка
            - "text" → передаётся "text"
        :param password:
            - "default" → подставляется VALID_PASSWORD
            - None → поле НЕ передаётся
            - "" → передаётся пустая строка
            - "text" → передаётся "text"
        :param timeout_sec: время жизни токена
        """
        payload = {"timeout": timeout_sec}

        # Логин
        if login is None:
            pass  # поле не передаётся
        elif login == "default":
            payload["login"] = f"{VALID_LOGIN_PREFIX}{int(time.time())}"
        else:
            payload["login"] = login

        # Пароль
        if password is None:
            pass  # поле не передаётся
        elif password == "default":
            payload["password"] = VALID_PASSWORD
        else:
            payload["password"] = password

        try:
            url = f"{self.base_url}/auth/authorize"
            return requests.post(url, json=payload, timeout=self.timeout)
        except requests.exceptions.Timeout:
            pytest.fail(f"Запрос к {url} превысил таймаут {self.timeout} сек.")

    def get_me(self, token=None):
        """
        GET /auth/me — получить данные текущего пользователя.

        :param token: токен авторизации (если None — заголовок x-token не передаётся)
        :return: объект Response
        """
        try:
            url = f"{self.base_url}/auth/me"
            headers = {}
            if token is not None:
                headers["x-token"] = token
            return requests.get(url, headers=headers, timeout=self.timeout)
        except requests.exceptions.Timeout:
            pytest.fail(f"Запрос к {url} превысил таймаут {self.timeout} сек.")
