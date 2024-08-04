from typing import Annotated
from ..schemas.schemas import BookingRequest
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from ..models.model_booking import Resource,Booking
from database import SessionLocal
from app.auth.routes.users import get_current_user
from ..fun_booking import checking_date,checking_num_people

router = APIRouter(
    prefix='/booking',
    tags=['booking']
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
async def read_my_booking(user:user_dependency,db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_bookings = db.query(Booking).filter(Booking.user_id == user.get("id")).all()
    return user_bookings

@router.get("/{booking_id}")
async def read_booking(user:user_dependency,db:db_dependency,booking_id:int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    user_booking = db.query(Booking).filter(Booking.id == booking_id).first()
    return user_booking

@router.post("/create_booking/{resource_id}")
async def create_booking(db:db_dependency,user:user_dependency,resource_id:int, booking_request:BookingRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    resource = db.query(Resource).filter(Resource.id == resource_id).first()

    if checking_date(db,booking_request.start_date,booking_request.end_date,resource_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The requested dates are not available")

    if not checking_num_people(db, booking_request.num_people, resource_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Number of people exceeds the allowed limit")

    days = (booking_request.end_date - booking_request.start_date).days
    role = resource.role.lower()

    if role == 'apartmani':
        price = resource.price * days
    elif role in ['hotel', 'bad']:
        price = resource.price * booking_request.num_people * days
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resource role")

    booking_model =  Booking(
        user_id = user.get("id"),
        resource_id = resource_id,
        start_date = booking_request.start_date,
        end_date = booking_request.end_date,
        num_people = booking_request.num_people,
        total_price = price
    )
    db.add(booking_model)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK)


@router.put("/{booking_id}")
async def update_booking(db: db_dependency, user: user_dependency, booking_request: BookingRequest, booking_id: int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated")

    booking_model = db.query(Booking).filter(Booking.id == booking_id).first()

    if booking_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="booking not found")

    resource_id = booking_model.resource_id

    if checking_date(db, booking_request.start_date, booking_request.end_date, resource_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The requested dates are not available")

    if not checking_num_people(db, booking_request.num_people, resource_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Number of people exceeds the allowed limit")


    # Ažuriraj atribute rezervacije
    booking_model.start_date = booking_request.start_date
    booking_model.end_date = booking_request.end_date
    booking_model.num_people = booking_request.num_people

    # Pronađi resurs za izračunavanje cene
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if resource is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")

    # Izračunaj ukupnu cenu
    days = (booking_request.end_date - booking_request.start_date).days
    role = resource.role.lower()

    if role == 'apartmani':
        price = resource.price * days
    elif role in ['hotel', 'bed']:
        price = resource.price * booking_request.num_people * days
    else:
        price = resource.price  # Podrazumevana cena ako nije ni jedno od navedenih

    booking_model.total_price = price

    # Spremi izmene u bazi
    db.add(booking_model)
    db.commit()

    raise HTTPException(status_code=status.HTTP_200_OK)


@router.delete("/delete_booking/{booking_id}")
async def delete_booking(db:db_dependency,user:user_dependency,booking_id:int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if booking is None :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if booking.user_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    db.query(Booking).filter(Booking.id == booking_id).delete()
    db.commit()
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)