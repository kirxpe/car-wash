from pydantic import BaseModel


class Price(BaseModel):
    min_value: int  # Value in kopecks
    max_value: int  # Value in rubles
    format: str  # Formatted string representation (e.g., "1 руб.")

class Time(BaseModel):
    seconds: int
    minutes: int



class ServiceBase(BaseModel):
    name: str

class ServiceCreate(ServiceBase):
    price: int  # Price in rubles (for input)
    time: int  # Time in minutes (for input)


class Service(ServiceBase):
    id: int
    price: Price
    time: Time

    class Config:
        orm_mode = True