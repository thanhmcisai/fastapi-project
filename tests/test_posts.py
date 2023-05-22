import pytest

from app import schemas
from .conftest import authorized_client, test_posts, client, test_user


def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")

    def validate(post):
        return schemas.PostReponse(**post)

    posts_map = map(validate, res.json())
    posts = list(posts_map)

    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200


def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthorized_user_get_one_post(client, test_posts):
    res = client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get("/posts/8888888888")
    assert res.status_code == 404


def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostReponse(**res.json())
    assert res.status_code == 200
    assert post.post.id == test_posts[0].id
    assert post.post.content == test_posts[0].content


@pytest.mark.parametrize("title, content, published", [
    ("awesome new title", "awesome new content", True),
    ("favorite pizza", "I love perperoni", False),
    ("tallest skyscrapers", "wahooo", True),
])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    res = authorized_client.post(f"/posts/", json={
        'title': title,
        'content': content,
        'published': published
    })

    create_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert create_post.title == title
    assert create_post.content == content
    assert create_post.published == published
    assert create_post.owner_id == test_user['id']


def test_create_post_default_published_true(authorized_client, test_user, test_posts):
    res = authorized_client.post(f"/posts/", json={
        'title': "awesome new title",
        'content': "awesome new content"
    })

    create_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert create_post.published == True
    assert create_post.owner_id == test_user['id']


def test_unauthorized_user_create_post(client, test_user, test_posts):
    res = client.post(f"/posts/", json={
        'title': "awesome new title",
        'content': "awesome new content"
    })
    assert res.status_code == 401


def test_unauthorized_user_delete_post(client, test_user, test_posts):
    res = client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 401


def test_delete_post_success(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == 204


def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/88888888")
    assert res.status_code == 404


def test_delete_other_user_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert res.status_code == 403


def test_update_post(authorized_client, test_user, test_posts):
    data = {
        'title': 'update title',
        'content': 'content title',
        'id': test_posts[0].id
    }
    res = authorized_client.put(f"/posts/{test_posts[0].id}", json=data)
    update_post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert update_post.title == data['title']
    assert update_post.content == data['content']


def test_update_other_user_post(authorized_client, test_user, test_second_user, test_posts):
    data = {
        'title': 'update title',
        'content': 'content title',
        'id': test_posts[3].id
    }
    res = authorized_client.put(f"/posts/{test_posts[3].id}", json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_post(client, test_user, test_posts):
    data = {
        'title': 'update title',
        'content': 'content title',
        'id': test_posts[0].id
    }
    res = client.put(f"/posts/{test_posts[0].id}", json=data)
    assert res.status_code == 401


def test_update_post_non_exist(authorized_client, test_user, test_posts):
    data = {
        'title': 'update title',
        'content': 'content title',
        'id': 8888888
    }
    res = authorized_client.put(f"/posts/8888888", json=data)
    assert res.status_code == 404
