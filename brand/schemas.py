from pydantic import BaseModel, validator

class BrandBase(BaseModel):
    name: str

    @validator('name')
    def name_must_be_alpha(cls, v):
        if not v.isalpha():
            raise ValueError('Name can only contain letters')
        return v
    
class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int

    class Config:
        orm_mode = True
