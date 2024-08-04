from pydantic import BaseModel,Field,field_validator
from datetime import datetime,date

class BookingRequest(BaseModel):
    start_date: date
    end_date: date
    num_people: int = Field(gt=0)

    @field_validator('start_date')
    def start_date_must_be_today_or_later(cls, v) -> date:
        if v < date.today():
            raise ValueError('start_date must be today or later')
        return v

    @field_validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values) -> date:
        if 'start_date' in values.data and v <= values.data['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class ResourceRequest(BaseModel):
    name:str = Field(min_length=3)
    description:str = Field(min_length=20)
    price:int = Field(gt=0)
    max_capacity:int = Field(gt=0)
    available:bool
    role:str