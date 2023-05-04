from fastapi import Body, FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_posts = [
    {"id": 1, "title": "aaaaaaaa", "content": "aaaaaaaaaaaaaaa"},
    {"id": 2, "title": "bbbbbbbb", "content": "aaaaaaaaaaaaaaa"},
    {"id": 3, "title": "cccccccc", "content": "aaaaaaaaaaaaaaa"},
]


def find_post(id):
    for post in my_posts:
        print(post["id"] == id, id)
        if post['id'] == id:
            return post


@app.get('/')
async def root():
    return {"message": "Change the Hello World"}


@app.get("/posts")
def get_posts():
    return {"data": my_posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = {
        "id": int(randrange(3, 1000000000000)),
        **post.dict()
    }
    my_posts.append(post_dict)
    return {"message": post_dict}


@app.get("/posts/latest")
def get_latest_post():
    return {"post_detail": my_posts[-1]}


@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found")
    return {"post_detail": find_post(id)}


@app.delete("/posts/{id}")
def delete_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} was not found")
    return {"post_detail": find_post(id)}
