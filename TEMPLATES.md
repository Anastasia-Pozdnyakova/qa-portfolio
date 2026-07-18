АЛГОРИТМЫ

1. Успешный GET-запрос | 200

def test_get_resource_success():
    # 1. Отправить GET-запрос
    response = requests.get(ENDPOINT, timeout=TIMEOUT)
    
    # 2. Проверить статус 200
    assert response.status_code == 200
    
    # 3. Проверить Content-Type
    validate_content_type(response)
    
    # 4. Распарсить JSON
    data = get_validated_json(response)
    
    # 5. Проверить структуру (обязательные поля)
    validate_response_structure(data, ["id", "name"])
    
    # 6. Проверить, что данные не пустые
    assert len(data) > 0

2. Успешный POST-запрос (создание) | 200, 201

def test_create_resource_success():
    # 1. Подготовить данные
    payload = {"name": "Test", "status": "active"}
    
    # 2. Отправить POST-запрос
    response = requests.post(ENDPOINT, json=payload, timeout=TIMEOUT)
    
    # 3. Проверить статус 201
    assert response.status_code == 201
    
    # 4. Проверить Content-Type
    validate_content_type(response)
    
    # 5. Распарсить JSON
    data = get_validated_json(response)
    
    # 6. Проверить, что ID создан
    assert "id" in data
    assert data["id"] > 0
    
    # 7. Проверить, что данные совпадают
    assert data["name"] == payload["name"]

3. Ошибка валидации | 422

def test_invalid_data_returns_422():
    # 1. Подготовить невалидные данные
    invalid_payload = {"name": ""}  # обязательное поле пустое
    
    # 2. Отправить запрос
    response = requests.post(ENDPOINT, json=invalid_payload, timeout=TIMEOUT)
    
    # 3. Проверить статус 422
    assert response.status_code == 422
    
    # 4. Проверить Content-Type
    validate_content_type(response)
    
    # 5. Распарсить JSON
    error_data = get_validated_json(response)
    
    # 6. Проверить, что detail — массив, не пустой
    assert "detail" in error_data
    assert isinstance(error_data["detail"], list)
    assert len(error_data["detail"]) > 0
    
    # 7. Проверить, что в detail есть loc и msg
    first_error = error_data["detail"][0]
    assert "loc" in first_error
    assert "msg" in first_error
    
    # 8. Проверить, что msg содержит ожидаемую подстроку
    assert "required" in first_error["msg"].lower()

4. Ресурс не найден | 400, 404

def test_resource_not_found():
    # 1. Отправить запрос с несуществующим ID
    response = requests.get(f"{ENDPOINT}/99999", timeout=TIMEOUT)
    
    # 2. Проверить статус 404
    assert response.status_code == 404
    
    # 3. Проверить Content-Type
    validate_content_type(response)
    
    # 4. Распарсить JSON
    error_data = get_validated_json(response)
    
    # 5. Проверить, что detail — объект с reason
    assert "detail" in error_data
    assert isinstance(error_data["detail"], dict)
    assert "reason" in error_data["detail"]
    assert isinstance(error_data["detail"]["reason"], str)
    assert len(error_data["detail"]["reason"]) > 0

5. Невалидный токен / авторизация | 401, 403

def test_invalid_token():
    # 1. Подготовить невалидный токен
    invalid_token = "invalid_token_123"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    
    # 2. Отправить запрос
    response = requests.get(ENDPOINT, headers=headers, timeout=TIMEOUT)
    
    # 3. Проверить статус 401 или 403
    assert response.status_code in [401, 403]
    
    # 4. Проверить Content-Type
    validate_content_type(response)
    
    # 5. Распарсить JSON
    error_data = get_validated_json(response)
    
    # 6. Проверить структуру ошибки
    assert "detail" in error_data
    assert "reason" in error_data["detail"]

6. Проверка истечения токена

def test_token_expires():
    # 1. Получить токен с коротким timeout
    payload = {"username": "test", "password": "pass", "timeout": 1}
    auth_response = requests.post(AUTH_ENDPOINT, json=payload)
    token = auth_response.json()["token"]
    
    # 2. Подождать (таймаут + запас)
    time.sleep(2)
    
    # 3. Попробовать использовать истёкший токен
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(ENDPOINT, headers=headers)
    
    # 4. Проверить, что доступ запрещён
    assert response.status_code == 403
