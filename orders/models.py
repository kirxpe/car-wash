from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class OrderStatus(enum.Enum):
    in_progress = 1
    completed = 2

class OrderService(Base):
    __tablename__ = "order_service"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    service_id = Column(Integer, ForeignKey("services.id"))

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.in_progress)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    customer_car_id = Column(Integer, ForeignKey("customer_cars.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    administrator_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    customer_car = relationship("CustomerCar", back_populates="orders")
    employee = relationship("User", foreign_keys="[Order.employee_id]", back_populates="employee_orders")
    administrator = relationship("User", foreign_keys="[Order.administrator_id]", back_populates="admin_orders")
    services = relationship("Service", secondary="order_service", back_populates="orders")

    @property
    def total_time(self):
        return sum(service.time_seconds for service in self.services) // 60

    @property
    def total_price(self):
        return sum(service.price_kopecks for service in self.services) // 100
