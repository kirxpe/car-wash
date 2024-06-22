from typing import Annotated
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from . import models, schemas


class CustomerCarService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_customer_car(
        self, customer_car_data: Annotated[schemas.CustomerCarCreate, Depends()]
    ) -> models.CustomerCar:
        db_customer_car = models.CustomerCar(**customer_car_data.dict())
        self.session.add(db_customer_car)
        await self.session.commit()
        await self.session.refresh(db_customer_car)
        return db_customer_car


    async def get_customer_cars(
        self, skip: int = 0, limit: int = 10
    ) -> list[models.CustomerCar]:
        query = select(models.CustomerCar).offset(skip).limit(limit)
        result = await self.session.execute(query)
        customer_cars = result.scalars().all()
        return customer_cars


    async def get_customer_car_by_id(self, customer_car_id: int) -> models.CustomerCar:
        query = select(models.CustomerCar).where(
            models.CustomerCar.id == customer_car_id
        )
        result = await self.session.execute(query)
        customer_car = result.scalars().first()
        if not customer_car:
            raise HTTPException(status_code=404, detail="CustomerCar not found")
        return customer_car

    async def update_customer_car(
        self, customer_car_id: int, customer_car_update: schemas.CustomerCarCreate
    ) -> models.CustomerCar:
        query = select(models.CustomerCar).where(
            models.CustomerCar.id == customer_car_id
        )
        result = await self.session.execute(query)
        db_customer_car = result.scalars().first()

        if not db_customer_car:
            raise HTTPException(status_code=404, detail="CustomerCar not found")

        
        for key, value in customer_car_update.dict(exclude_unset=True).items():
            setattr(db_customer_car, key, value)

        await self.session.commit()
        await self.session.refresh(db_customer_car)
        return db_customer_car

    async def delete_customer_car(self, customer_car_id: int) -> None:
        query = select(models.CustomerCar).where(
            models.CustomerCar.id == customer_car_id
        )
        result = await self.session.execute(query)
        customer_car = result.scalars().first()

        if not customer_car:
            raise HTTPException(status_code=404, detail="CustomerCar not found")

        await self.session.delete(customer_car)
        await self.session.commit()
