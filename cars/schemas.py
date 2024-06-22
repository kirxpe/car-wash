from pydantic import BaseModel


class CarBase(BaseModel):
    model: str
    brand_id: int


class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    model: str | None = None
    brand_id: int | None = None

class Car(CarBase):
    id: int
    brand_name: str

    class Config:
        orm_mode = True
        from_attributes = True

    @staticmethod
    def serialize_brand(brand):
        # Custom serializer for brand
        if brand:
            return brand.name
        return None
