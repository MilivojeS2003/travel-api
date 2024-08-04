from typing import Annotated,List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from app.auth.models.model_auth import User
from app.auth.routes.users import get_current_user
from ..models.model_comment import Comment,CommentLike
from ..schemas.schema import CommentResponse,CommentRequest
from database import SessionLocal


router = APIRouter(
    prefix='/comment',
    tags=['comment']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/read_all_comments/{blog_id}", response_model=List[CommentResponse])
async def read_all_comments(blog_id: int, db: db_dependency):
    comments = (
        db.query(Comment, User.username)
        .join(User, Comment.owner_id == User.id)
        .filter(Comment.blog_id == blog_id)
        .all()
    )
    return [CommentResponse(
        id=comment.id,
        body=comment.body,
        username=username,
        like=comment.like,
        dislike=comment.dislike,
        blog_id=comment.blog_id,
        owner_id=comment.owner_id,
        created_at=comment.created_at) for comment, username in comments]

@router.get("/get_my_comment/")
async def read_my_comment(db:db_dependency,user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return db.query(Comment).filter(Comment.owner_id == user.get("id")).all()

@router.get("/sort_by_like/{blog_id}")
async def sort_by_like(db:db_dependency,user:user_dependency,blog_id,reverse:str):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    comment = db.query(Comment).filter(Comment.blog_id == blog_id).all()
    sorted_comments = sorted(comment, key=lambda x: x.like, reverse=reverse)
    return sorted_comments


@router.post("/{blog_id}")
async def create_comment(db:db_dependency,user:user_dependency, comment_request:CommentRequest, blog_id:int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    comment_model = Comment(**comment_request.dict(),like=0,blog_id=blog_id, owner_id=user["id"])
    db.add(comment_model)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK)

@router.put("/{comment_id}")
async def update_comment(
    comment_id: int,
    comment_request: CommentRequest,
    db: db_dependency,
    user: user_dependency
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment is None or comment.owner_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to edit this comment.")
    comment.body = comment_request.body
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK)


@router.delete("/{comment_id}")
async def delete_comment(comment_id: int, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment is None or comment.owner_id != user.get("id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this comment.")
    db.delete(comment)
    db.commit()
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/like/{comment_id}")
async def like_comment(comment_id: int, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Check if the user has already liked or disliked the comment
    existing_reaction = db.query(CommentLike).filter(CommentLike.user_id == user.get("id"), CommentLike.comment_id == comment_id).first()
    if existing_reaction:
        if existing_reaction.is_like:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already liked this comment")
        else:
            # Change dislike to like
            existing_reaction.is_like = True
            comment = db.query(Comment).filter(Comment.id == comment_id).first()
            comment.like = (comment.like or 0) + 1
            comment.dislike = max((comment.dislike or 0) - 1, 0)
            db.commit()
            return {"message": "Comment liked successfully!"}
    else:
        # Proceed to like the comment
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if comment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        comment.like = (comment.like or 0) + 1
        db.add(CommentLike(user_id=user.get("id"), comment_id=comment_id, is_like=True))
        db.commit()
        return {"message": "Comment liked successfully!"}

@router.post("/dislike/{comment_id}")
async def dislike_comment(comment_id: int, db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    # Check if the user has already liked or disliked the comment
    existing_reaction = db.query(CommentLike).filter(CommentLike.user_id == user.get("id"), CommentLike.comment_id == comment_id).first()
    if existing_reaction:
        if not existing_reaction.is_like:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already disliked this comment")
        else:
            # Change like to dislike
            existing_reaction.is_like = False
            comment = db.query(Comment).filter(Comment.id == comment_id).first()
            comment.dislike = (comment.dislike or 0) + 1
            comment.like = max((comment.like or 0) - 1, 0)
            db.commit()
            return {"message": "Comment disliked successfully!"}
    else:
        # Proceed to dislike the comment
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if comment is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        comment.dislike = (comment.dislike or 0) + 1
        db.add(CommentLike(user_id=user.get("id"), comment_id=comment_id, is_like=False))
        db.commit()
        return {"message": "Comment disliked successfully!"}

