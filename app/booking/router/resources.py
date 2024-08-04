from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from ..models.model_booking import Resource
from database import SessionLocal
from app.auth.routes.users import get_current_user
from ..schemas.schemas import ResourceRequest


router = APIRouter(
    prefix='/resource',
    tags=['resource']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



@router.get("/")
async def read_resource(db:db_dependency, user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Resource).all()

@router.get("/{owner_id}")
async def read_resource_by_id(db:db_dependency, user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Resource).filter(Resource.owner_id == user.get("id")).first()

@router.post("/")
async def create_resource(db:db_dependency,user:user_dependency,resource_request:ResourceRequest):
    if user is None or user.get('user_role') != 'admin': #treba dodati i entre
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    resource_model = Resource(**resource_request.dict(), owner_id = user.get("id"))
    db.add(resource_model)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK)

@router.put("/{resource_id}")
async def update_resource(db:db_dependency, user:user_dependency, resource_request:ResourceRequest, resource_id:int):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if user is None or user.get('user_role') != 'admin' or resource.owner_id != user.get("id"): #treba dodati i entre
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    resource.name = resource_request.name
    resource.description = resource_request.description
    resource.role = resource_request.role
    resource.max_capacity = resource_request.max_capacity
    resource.available = resource_request.available
    resource.price = resource_request.price

    db.add(resource)
    db.commit()
    db.refresh(resource)
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)