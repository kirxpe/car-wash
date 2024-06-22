from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class CustomerCar(Base):
    __tablename__ = "customer_cars"

    id = Column(Integer, primary_key=True)
    year = Column(Integer, nullable=False)
    number = Column(String, nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    car = relationship("Car", backref="customer_cars")
    user = relationship("User", backref="customer_cars")
    orders = relationship("Order", back_populates="customer_car")
