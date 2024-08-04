from pydantic import BaseModel,Field
from datetime import datetime
from typing import Optional


class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    like: Optional[int]
    username: str
    created_at: datetime
    destination: Optional[str] = None
    comment_count: int

    class Config:
        orm_mode = True


class BlogRequest(BaseModel):
    title: str = Field(min_length=3, max_length=30)
    content: str = Field(min_length=20, max_length=5000)
    destination: Optional[str] = None

class CommentResponse(BaseModel):
    id: int
    body: str
    username: str
    like: int
    dislike: int
    blog_id: int
    owner_id: int
    created_at: datetime


    class Config:
        orm_mode = True

class CommentRequest(BaseModel):
    body:str = Field(min_length=3)