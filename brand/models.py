from sqlalchemy import Column, Integer, String

from database import Base


class Brand(Base):
    __tablename__ = "brand"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
