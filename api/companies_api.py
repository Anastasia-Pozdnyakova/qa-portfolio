"""Методы для работы с API /companies"""

import requests
import pytest
from config import BASE_URL, TIMEOUT


class CompaniesAPI:
    """
    Клиент для работы с эндпоинтами /companies и /companies/{id}.

    Использует базовый URL и таймаут из config.
    Все методы возвращают объект Response из библиотеки requests.

    Методы:
        get_all_companies()
            Получить все компании.
        get_company_by_id(company_id)
            Получить компанию по ID.
        get_companies_with_params(**kwargs)
            Получить компании с параметрами (limit, offset, status).
    """

    def __init__(self):
        self.base_url = BASE_URL
        self.timeout = TIMEOUT

    def get_all_companies(self):
        """GET /companies"""
        try:
            url = f"{self.base_url}/companies"
            return requests.get(url, timeout=self.timeout)
        except requests.exceptions.Timeout:
            pytest.fail(f"Запрос к {url} превысил таймаут {self.timeout} сек.")

    def get_company_by_id(self, company_id, headers=None):
        """GET /companies/{id} с возможностью передать заголовки"""
        try:
            url = f"{self.base_url}/companies/{company_id}"
            return requests.get(url, headers=headers, timeout=self.timeout)
        except requests.exceptions.Timeout:
            pytest.fail(f"Запрос к {url} превысил таймаут {self.timeout} сек.")

    def get_companies_with_params(self, headers=None, **kwargs):
        """GET /companies с параметрами (limit, offset, status) и с возможностью передать заголовки"""
        try:
            url = f"{self.base_url}/companies"
            return requests.get(
                url, params=kwargs, headers=headers, timeout=self.timeout
            )
        except requests.exceptions.Timeout:
            pytest.fail(f"Запрос к {url} превысил таймаут {self.timeout} сек.")
