from pydantic import BaseModel


class CarBase(BaseModel):
    model: str
    brand_id: int


class CarCreate(CarBase):
    pass


class Car(CarBase):
    id: int
    # brand: Brand  # Include brand information in the response
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
