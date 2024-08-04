from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text


class Event(Base):
    __tablename__ = 'event'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    destinacion = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime,nullable=True)
    date = Column(String)
    #entre_id = Column(Integer, ForeignKey("entrepreneurs.id")) -> OVAKO TREBA (ZAMJENITI SA LINIJOM ISPOD)
    entre_id = Column(Integer, ForeignKey("users.id"))