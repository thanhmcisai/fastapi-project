from jose import JWTError, jwt
import pytest

from app import schemas
from app.config import settings
from .conftest import client, session, test_user


def test_root(client):
    res = client.get("/")
    assert res.json().get('message') == 'Change the Hello World'
    assert res.status_code == 200


def test_create_user(client):
    res = client.post(
        "/users/", json={"email": "test@gmail.com", "password": "123456"})
    assert res.status_code == 201
    new_user = schemas.User(**res.json())
    assert new_user.email == "test@gmail.com"


def test_login_user(test_user, client):
    res = client.post(
        "/login", data={"username": test_user["email"], "password": test_user["password"]})

    login_res = schemas.Token(**res.json())
    payload = jwt.decode(token=login_res.access_token,
                         key=settings.secret_key, algorithms=[settings.algorithm])

    id: str = payload.get("user_id")
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', '123456', 403),
    ('test@gmail.com', 'wrongPassword', 403),
    ('wrongemail@gmail.com', 'wrongPassword', 403),
    (None, '123456', 422),
    ('test@gmail.com', None, 422),
])
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post(
        "/login", data={"username": email, "password": password})

    assert res.status_code == status_code
