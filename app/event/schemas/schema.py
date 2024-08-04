from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class EventRequest(BaseModel):
    title: str
    description: str
    destinacion: str
    start_date:datetime
    end_date:Optional[datetime]


class EventResponse(BaseModel):
    title: str
    description: str
    destinacion: str
    start_date: datetime
    end_date:Optional[datetime]
    date:datetime

    class Config:
        orm_mode = True

