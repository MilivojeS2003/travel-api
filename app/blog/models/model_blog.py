from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Blog(Base):
    __tablename__ = 'blogs'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    destination = Column(String, nullable=True)
    like = Column(Integer, default=0)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    likes = relationship("BlogLike", cascade="all, delete-orphan", backref="blog")
    comments = relationship("Comment", cascade="all, delete-orphan", backref="blog")

class BlogLike(Base):
    __tablename__ = 'blog_likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    blog_id = Column(Integer, ForeignKey("blogs.id"))



