from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Booking(Base):
    __tablename__ = 'booking'

    id = Column(Integer,primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resource_id = Column(Integer, ForeignKey("resource.id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    num_people = Column(Integer)
    total_price = Column(Integer)


class Resource(Base):
    __tablename__ = 'resource'

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    max_capacity = Column(Integer)
    available = Column(Boolean, default=True)
    role = Column(String)  #Concert, Apartman, Bed, Ticket, Hotel

