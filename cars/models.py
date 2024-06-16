from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True)
    model = Column(String, unique=True, nullable=False)
    brand_id = Column(Integer, ForeignKey("brand.id"), nullable=False)

    brand = relationship("Brand", backref="cars")
    
    
    