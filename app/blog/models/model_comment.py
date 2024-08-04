from database import Base
from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Comment(Base):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text)
    like = Column(Integer, default=0)
    dislike = Column(Integer, default=0)
    blog_id = Column(Integer, ForeignKey("blogs.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, server_default=func.now())
    likes = relationship("CommentLike", cascade="all, delete-orphan", backref="comment")

class CommentLike(Base):
    __tablename__ = 'comment_likes'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    comment_id = Column(Integer, ForeignKey("comment.id"))
    is_like = Column(Boolean)