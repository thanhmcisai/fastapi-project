from fastapi.testclient import TestClient
import pytest
from alembic.config import Config
from alembic import command

from app import models
from app.main import app
from app.database import get_db, Base
from app.oauth2 import create_access_token
from .database import engine, TestingSessionLocal


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "test@gmail.com", "password": "123456"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data["password"]
    return new_user


@pytest.fixture
def test_second_user(client):
    user_data = {"email": "test_second@gmail.com", "password": "789456123"}
    res = client.post("/users/", json=user_data)

    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client


@pytest.fixture
def test_posts(test_user, test_second_user, session):
    posts_data = [{
        "title": '1st title',
        "content": '1st content',
        "owner_id": test_user['id']
    }, {
        "title": '2nd title',
        "content": '2nd content',
        "owner_id": test_user['id']
    }, {
        "title": '3rd title',
        "content": '3rd content',
        "owner_id": test_user['id']
    }, {
        "title": '4th title',
        "content": '4th content',
        "owner_id": test_second_user['id']
    }]

    def create_post_model(post: dict):
        return models.Post(**post)

    posts_data_map = map(create_post_model, posts_data)
    posts = list(posts_data_map)

    session.add_all(posts)
    session.commit()

    posts = session.query(models.Post).all()
    return posts


@pytest.fixture
def test_vote(test_posts, session, test_user):
    new_vote = models.Vote(post_id=test_posts[3].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()
