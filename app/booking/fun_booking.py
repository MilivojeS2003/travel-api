from datetime import datetime,date
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .models.model_booking import Booking,Resource

def checking_date(db: Session, start_date: date, end_date: date, resource_id: int) -> bool:
    stmt = select(Booking).filter(Booking.resource_id == resource_id)
    result = db.execute(stmt)
    existing_bookings = result.scalars().all()

    for booking in existing_bookings:
        if isinstance(booking.start_date, datetime) and isinstance(booking.end_date, datetime):
            booking_start_date = booking.start_date.date()
            booking_end_date = booking.end_date.date()

            if booking_start_date < end_date and start_date < booking_end_date:
                return True
        else:
            if booking.start_date < end_date and start_date < booking.end_date:
                return True

    return False

def checking_num_people(db:Session, num_people:int, recource_id:int) -> bool:
    recource = db.query(Resource).filter(Resource.id == recource_id).first()
    if recource.max_capacity < num_people:
        return False
    return True