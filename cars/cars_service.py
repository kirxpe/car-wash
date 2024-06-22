from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from cars import models, schemas
from brand.models import Brand as brand_model

class CarService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cars(self, skip: int = 0, limit: int = 10, filter_by: str = None, sort_by: str = None) -> list[models.Car]:
        query = select(models.Car).options(joinedload(models.Car.brand))
        if filter_by:
            query = query.where(models.Car.model.ilike(f"%{filter_by}%"))
        if sort_by:
            query = query.order_by(getattr(models.Car, sort_by))
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        cars = result.scalars().all()
        for car in cars:
            car.brand_name = schemas.Car.serialize_brand(car.brand)
        return cars

    async def create_car(self, car_data: schemas.CarCreate) -> models.Car:
        query = select(brand_model).where(brand_model.id == car_data.brand_id)
        result = await self.session.execute(query)
        brand = result.scalars().first()
        if not brand:
            raise HTTPException(status_code=400, detail="Invalid brand_id. Brand does not exist.")

        query = select(models.Car).where((models.Car.brand_id == car_data.brand_id) & (models.Car.model == car_data.model))
        result = await self.session.execute(query)
        existing_car = result.scalars().first()
        if existing_car:
            raise HTTPException(status_code=400, detail="Car model already exists for this brand.")

        db_car = models.Car(**car_data.dict())
        self.session.add(db_car)
        await self.session.commit()
        await self.session.refresh(db_car)
        db_car.brand_name = brand.name
        return db_car
    

    async def get_car_by_id(self, car_id: int) -> models.Car:
        query = select(models.Car).where(models.Car.id == car_id).options(joinedload(models.Car.brand))
        result = await self.session.execute(query)
        db_car = result.scalars().first()
        if not db_car:
            raise HTTPException(status_code=404, detail="Car not found")
        db_car.brand_name = schemas.Car.serialize_brand(db_car.brand)
        return db_car

    async def update_car(self, car_id: int, car_update: schemas.CarUpdate) -> models.Car:
        query = select(models.Car).where(models.Car.id == car_id)
        result = await self.session.execute(query)
        db_car = result.scalars().first()

        if not db_car:
            raise HTTPException(status_code=404, detail="Car not found")

        if car_update.brand_id is not None:
            query = select(brand_model).where(brand_model.id == car_update.brand_id)
            result = await self.session.execute(query)
            brand = result.scalars().first()
            if not brand:
                raise HTTPException(status_code=400, detail="Invalid brand_id. Brand does not exist.")

        for key, value in car_update.dict(exclude_unset=True).items():
            setattr(db_car, key, value)

        await self.session.commit()
        await self.session.refresh(db_car)
        db_car.brand_name = schemas.Car.serialize_brand(db_car.brand)
        return db_car

    async def delete_car(self, car_id: int) -> None:
        query = select(models.Car).where(models.Car.id == car_id)
        result = await self.session.execute(query)
        db_car = result.scalars().first()

        if not db_car:
            raise HTTPException(status_code=404, detail="Car not found")

        await self.session.delete(db_car)
        await self.session.commit()