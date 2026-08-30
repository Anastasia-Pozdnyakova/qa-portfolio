"""Ожидаемые статусы для всех эндпоинтов"""

EXPECTED_STATUS = {
    "valid": 200,
    "created": 201,
    "deleted": 202,
    "bad_request": 400,
    "not_found": 404,
    "validation_error": 422,
    "unauthorized": 401,
    "forbidden": 403,
}
