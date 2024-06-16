from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class OrderStatus(Enum):
    in_progress = 1
    completed = 2

class ServiceId(BaseModel):
    service_id: int

class OrderCreate(BaseModel):
    customer_car_id: int
    employee_id: int
    services: List[ServiceId]

class ServiceBase(BaseModel):
    id: int
    name: str
    min_value: int
    max_value: int
    format: str

    class Config:
        orm_mode = True
        from_attributes = True

class CustomerBase(BaseModel):
    id: int
    full_name: str
    email: str

    class Config:
        orm_mode = True

class CarBase(BaseModel):
    model: str
    brand: str

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    id: int
    full_name: str

    class Config:
        orm_mode = True
        from_attributes = True

class CustomerCarBase(BaseModel):
    id: int
    year: int
    number: str
    customer: CustomerBase
    car: CarBase

    class Config:
        orm_mode = True
        from_attributes = True

class OrderBase(BaseModel):
    id: int
    status: int
    start_date: datetime
    end_date: Optional[datetime]
    totalTime: int
    totalPrice: int
    administrator: UserBase
    employee: UserBase
    customerCar: CustomerCarBase

    class Config:
        orm_mode = True
        from_attributes = True