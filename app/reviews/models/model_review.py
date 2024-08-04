from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer)
    comment = Column(String)
    date = Column(DateTime)
    business_id = Column(Integer, ForeignKey("entrepreneurs.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))