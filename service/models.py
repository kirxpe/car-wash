from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base
from service.utils import convert_price_to_kopecks, convert_time_to_seconds
from service.schemas import Price, Time

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price_kopecks = Column(Integer, nullable=False)  # Price in kopecks
    time_seconds = Column(Integer, nullable=False)  # Time in seconds
    orders = relationship("Order", secondary="order_service", back_populates="services")

    def __init__(self, name: str, price: int, time: int, *args, **kwargs):
        self.name = name
        self.price_kopecks = convert_price_to_kopecks(price) 
        self.time_seconds = convert_time_to_seconds(time)
        
    @property
    def price(self) -> Price:
        rubles = self.price_kopecks // 100
        kopecks = self.price_kopecks % 100
        return Price(min_value=self.price_kopecks, max_value=rubles, format=f"{rubles} руб. {kopecks:02d} коп.")

    @property
    def time(self) -> Time:
        minutes = self.time_seconds // 60
        return Time(seconds=self.time_seconds, minutes=minutes)    