from typing import List
from pydantic import BaseModel


class Price(BaseModel): #Eto Value Object
    min_value: int  # Копейки
    max_value: int  # Рубли
    format: str  


class Time(BaseModel): #Eto toje Value Object
    seconds: int
    minutes: int


class ServiceBase(BaseModel):
    name: str


class ServiceCreate(ServiceBase):
    price: float  
    time: int  


class Service(ServiceBase): #a eto uje DTO 
    id: int 
    price: Price
    time: Time

    class Config:
        orm_mode = True
        from_attributes = True


class ServiceListResponse(BaseModel):
    total_count: int
    services: List[Service]

    class Config:
        orm_mode = True