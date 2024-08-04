from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from ..models.model_events import Event
from ..schemas.schema import EventRequest,EventResponse
from database import SessionLocal
from app.auth.routes.auth_entre import get_current_entre
from app.auth.routes.users import get_current_user

router = APIRouter(
    prefix='/event',
    tags=['event']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
entre_dependency = Annotated[dict, Depends(get_current_entre)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/")
async def read_all_event(db:db_dependency,user:user_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    event = db.query(Event).all()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Event is not faund')
    return event

@router.get("/{event_id}")
async def read_event_by_id(db:db_dependency,user:user_dependency,event_id:int):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    event = db.query(Event).filter(Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return event


@router.post("/", response_model=EventResponse)
async def create_event(db:db_dependency,user:user_dependency, event_request:EventRequest, entre:entre_dependency):
    if entre is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    if user.get("user_role") != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    elif entre:
        event = Event(**event_request.dict(), entre_id = entre.get(("id")), date = datetime.now())
    else:
        event = Event(**event_request.dict(), entre_id = user.get(("id")), date = datetime.now())
    db.add(event)
    db.commit()
    return event

@router.put("/{event_id}")
async def update_event(db:db_dependency,user:user_dependency, event_id:int, event_request: EventRequest, entre:entre_dependency):
    event = db.query(Event).filter(Event.id == event_id).first()

    if event.entre_id != entre.get("id") or event.entre_id != entre.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    event.title = event_request.title
    event.description = event_request.description
    event.destinacion = event_request.destinacion
    event.start_date = event_request.start_date
    event.end_date = event_request.end_date
    event.date = datetime.now()
    db.add(event)
    db.commit()
    raise HTTPException(status_code=status.HTTP_200_OK)

@router.delete("/")
async def delete_event(db:db_dependency,user:user_dependency, event_id:int, entre:entre_dependency): #mora user da se zamjeni sa entre!!!!
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    event = db.query(Event).filter(Event.id == event_id).first()

    if event.entre_id != entre.get("id") or event.entre_id != entre.get("id"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.query(Event).filter(Event.id == event_id).delete()
    db.commit()
    raise HTTPException(status_code=status.HTTP_204_NO_CONTENT)
