from fastapi import HTTPException, status, Response, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/users", 
    tags=["Users"]
)

@router.get("/", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db), current_user: any = Depends(oauth2.get_current_user)):
    users = db.query(models.User).all()
    return users

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_users(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    user.password = utils.hash(user.password)
    
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}", response_model=schemas.User)
def get_user(id: int, db: Session = Depends(get_db), current_user: any = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter_by(id=id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id {id} was not found")
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), current_user: any = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter_by(id=id)
    if user_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} does not exist")
    user_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.User)
def update_user(id: int, user: schemas.UserCreate, db: Session = Depends(get_db), current_user: any = Depends(oauth2.get_current_user)):
    user_query = db.query(models.User).filter_by(id=id)
    if user_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user with id: {id} does not exist")
    user_query.update(user.dict(), synchronize_session=False)
    db.commit()

    return user_query.first()