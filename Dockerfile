FROM python:3.10

WORKDIR /app

# Зависимости для Allure
RUN apt-get update && apt-get install -y wget unzip default-jre

# Скачиваем и распаковываем Allure
RUN wget https://github.com/allure-framework/allure2/releases/download/2.32.0/allure-2.32.0.zip && \
    unzip allure-2.32.0.zip && \
    mv allure-2.32.0 /opt/allure && \
    ln -s /opt/allure/bin/allure /usr/local/bin/allure

# Установка Python-библиотеки
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копия проекта
COPY . .