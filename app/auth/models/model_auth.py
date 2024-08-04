from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)

class Entrepreneur(Base):
    __tablename__ = 'entrepreneurs'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    hashed_password = Column(String)
    business_id = (Integer,ForeignKey("business.id"))
    destination = Column(String)
    description = Column(String)


class Business(Base):
    __tablename__ = 'business'

    id = Column(Integer,primary_key=True, index=True)
    name = Column(String)