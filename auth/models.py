from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database import Base


class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


# класс для библиотеки
class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey("roles.id"))
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    patronymic = Column(String, nullable=False, default="")
    hashed_password: str = Column(String(length=1024), nullable=False)
    role = relationship("Role", backref="users")
    is_send_notify = Column(Boolean, default=False, nullable=False)
    # поля для библиотеки
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
    employee_orders = relationship(
        "Order", foreign_keys="[Order.employee_id]", back_populates="employee"
    )
    admin_orders = relationship(
        "Order", foreign_keys="[Order.administrator_id]", back_populates="administrator"
    )
