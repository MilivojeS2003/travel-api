from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from  app.auth.models.model_auth import Entrepreneur
from ..models.model_review import Review
from ..schemas.schema import ReviewsRequest
from database import SessionLocal
from  app.auth.routes.auth_entre import get_current_entre
from app.auth.routes.users import get_current_user


router = APIRouter(
    prefix='/review',
    tags=['review']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
entre_dependency = Annotated[dict, Depends(get_current_entre)]

@router.get("/")
async def read_all_my_review(db:db_dependency, user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    reviews = db.query(Review).filter(Review.owner_id == user.get("id")).all()
    if reviews is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return reviews

@router.get("/{busniss_id}")
async def read_all_busniss_reviews(db:db_dependency, user:user_dependency,busniss_id):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    reviews = db.query(Review).filter(Review.business_id == busniss_id).all()
    if reviews is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return reviews


def convert_to_boolean(value: str) -> bool:
    return value.lower() in ('true', '1', 'yes')


@router.get("/sort_by_date/{busniss_id}")
async def sort_by_date(db:db_dependency,user:user_dependency,reverse:str, busniss_id:int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    reviews = db.query(Review).filter(Review.business_id == busniss_id).all()
    reverse = convert_to_boolean(reverse)
    sorted_reviews = sorted(reviews, key=lambda x: x.date, reverse=reverse)
    return sorted_reviews

@router.get("/sort_by_rating/{busniss_id}")
async def sort_by_rating(db:db_dependency,user:user_dependency, busniss_id:int, rating:int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    reviews = db.query(Review).filter(Review.rating > rating).all()
    return reviews

@router.post("/")
async def create_reviews(db:db_dependency,user:user_dependency, busniss_id:int, reviews_requets:ReviewsRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    busniss = db.query(Entrepreneur).filter(Entrepreneur.id == busniss_id).first()
    if busniss is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    review = Review(**reviews_requets.dict(), owner_id=user.get("id"), business_id = busniss_id, date=datetime.now())
    db.add(review)
    db.commit()

@router.put("/")
async def update_review(db:db_dependency, user:user_dependency, reviews_requets:ReviewsRequest, review_id:int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    review = db.query(Review).filter(Review.id == review_id).filter(Review.owner_id ==  user.get("id")).first()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    review.rating = reviews_requets.rating
    review.comment = reviews_requets.comment
    review.date = datetime.now()

    db.add(review)
    db.commit()

@router.delete("/")
async def delete_review(db:db_dependency, user:user_dependency, review_id:int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    review = db.query(Review).filter(Review.id == review_id).filter(Review.owner_id ==  user.get("id")).first()
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.query(Review).filter(Review.id == review_id).filter(Review.owner_id == user.get("id")).delete()
    db.commit()