from typing import Annotated, List
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from app.auth.models.model_auth import User
from ..models.model_blog import Blog,BlogLike
from ..models.model_comment import Comment
from ..schemas.schema import BlogResponse,BlogRequest
from database import SessionLocal
from app.auth.routes.users import get_current_user
router = APIRouter(
    prefix='/blog',
    tags=['blog']
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
async def get_blog_by_user(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Blog).filter(Blog.owner_id == user.get("id")).all()


@router.get("/all_blogs", response_model=List[BlogResponse])
async def get_all_blogs(db: db_dependency):
    query = db.query(Blog, User.username, func.count(Comment.id).label('comment_count')) \
        .join(User, Blog.owner_id == User.id) \
        .outerjoin(Comment, Comment.blog_id == Blog.id) \
        .group_by(Blog.id, User.username).all()

    blogs = []
    for blog, username, comment_count in query:
        blogs.append(BlogResponse(
            id=blog.id,
            title=blog.title,
            content=blog.content,
            like=blog.like,
            username=username,
            created_at=blog.created_at,
            destination=blog.destination,
            comment_count=comment_count
        ))
    return blogs


@router.get("/{destinacion}", response_model=List[BlogResponse])
async def get_blog_by_destinacion(destinacion: str, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    blogs = db.query(Blog).filter(func.lower(Blog.destination) == func.lower(destinacion)).all()
    if blogs is None:
        return {'respons': 'Dont have blogs on this destination'}
    return blogs


@router.get("/blog_info", response_model=BlogResponse)
async def user_info(db: db_dependency, user: user_dependency, blog_id: int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if blog is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return blog


@router.get("/sort_by_like")  # sortiranje za odredjenu destinaciju
async def sort_by_like(db: db_dependency, user: user_dependency, destination: str, reverse: str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    blog = db.query(Blog).filter(Blog.destination == destination).all()
    sorted_blogs = sorted(blog, key=lambda x: x.like, reverse=reverse)
    return sorted_blogs


@router.post("/create_blog")
async def create_blog(db: db_dependency, user: user_dependency, blog_model: BlogRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    blog = Blog(**blog_model.dict(), owner_id=user.get("id"))
    db.add(blog)
    db.commit()
    return HTTPException(status_code=status.HTTP_200_OK)


@router.delete("/{blog_id}")
async def delete_blog(db: db_dependency, user: user_dependency, blog_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if blog is None:
        raise HTTPException(status_code=404, detail='blog not found.')
    if blog.owner_id != user.get('id'):
        raise HTTPException(status_code=403, detail='Not authorized to delete this blog.')

    # Deleting the blog will also delete associated likes and comments due to cascade settings
    db.delete(blog)
    db.commit()
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{blog_id}")
async def update_blog(db: db_dependency, user: user_dependency, blog_id: int, blog_request: BlogRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if blog is None:
        raise HTTPException(status_code=404, detail='blog not found.')
    if blog.owner_id != user.get('id'):
        raise HTTPException(status_code=403, detail='Not authorized to edit this blog.')
    blog.title = blog_request.title
    blog.content = blog_request.content
    blog.destination = blog_request.destination
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK)

@router.post("/like/{blog_id}")
async def like_blog(blog_id: int, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Check if the user has already liked the blog
    already_liked = db.query(BlogLike).filter(BlogLike.user_id == user.get("id"), BlogLike.blog_id == blog_id).first()
    if already_liked:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already liked this blog")

    # Proceed to like the blog
    blog = db.query(Blog).filter(Blog.id == blog_id).first()
    if blog is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    blog.like = (blog.like or 0) + 1  # Ensure blog.like is not None before incrementing
    db.add(blog)

    # Record the like
    blog_like = BlogLike(user_id=user.get("id"), blog_id=blog_id)
    db.add(blog_like)

    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK)
