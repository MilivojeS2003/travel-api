from pydantic import BaseModel,Field


class ReviewsRequest(BaseModel):
    rating:int = Field(gt=0, lt=6)
    comment:str