from pydantic import BaseModel, Field
from datetime import datetime

class CustomerCarBase(BaseModel):
    car_id: int
    user_id: int
    year: int = Field(..., ge=1920, le=datetime.now().year)
    number: str = Field(..., pattern=r"^[А-Я]\d{3}[А-Я]{2}\d{2,3}$")

    
    
class CustomerCarCreate(CustomerCarBase):
    pass

class CustomerCar(CustomerCarBase):
    id: int

    class Config:
        orm_mode = True
