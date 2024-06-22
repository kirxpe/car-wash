from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
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
    start_date: str
    end_date: Optional[str]
    totalTime: int
    totalPrice: int
    administrator: UserBase
    employee: UserBase
    customerCar: CustomerCarBase

    class Config:
        orm_mode = True
        from_attributes = True

    @staticmethod
    def format_time(dt: datetime) -> str:
        if dt:
            dt += timedelta(hours=7)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        return None

    @classmethod
    def from_orm(cls, obj):
        obj.start_date = cls.format_time(obj.start_date)
        obj.end_date = cls.format_time(obj.end_date) if obj.end_date else None
        return super().from_orm(obj)


class Order(BaseModel):
    id: int
    status: int
    start_date: str
    end_date: Optional[str]
    customer_car_id: int
    employee_id: int
    administrator_id: int

    class Config:
        orm_mode = True
        from_attributes = True

    @staticmethod
    def format_time(dt: datetime) -> str:
        if dt:
            dt += timedelta(hours=7)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        return None

    @classmethod
    def from_orm(cls, obj):
        obj.start_date = cls.format_time(obj.start_date)
        obj.end_date = cls.format_time(obj.end_date) if obj.end_date else None
        return super().from_orm(obj)
    

class OrderListResponse(BaseModel):
    total_count: int
    orders: List[OrderBase]

    class Config:
        orm_mode = True    