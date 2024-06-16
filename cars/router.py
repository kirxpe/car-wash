from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_async_session
from cars.schemas import CarCreate, Car
from cars.models import Car as Car_model
from brand.models import Brand as BrandModel
from auth.dependencies import require_admin, require_admin_or_employee_or_client

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Car, dependencies=[Depends(require_admin)])
async def create_car(
    car: Annotated[CarCreate, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    # Validate brand_id
    query = select(BrandModel).where(BrandModel.id == car.brand_id)
    result = await session.execute(query)
    brand = result.scalars().first()
    if not brand:
        raise HTTPException(
            status_code=400, detail="Invalid brand_id. Brand does not exist."
        )

    # Check if the car model already exists for the brand
    query = select(Car_model).where(
        (Car_model.brand_id == car.brand_id) & (Car_model.model == car.model)
    )
    result = await session.execute(query)
    existing_car = result.scalars().first()
    if existing_car:
        raise HTTPException(
            status_code=400, detail="Car model already exists for this brand."
        )

    db_car = Car_model(**car.dict())  # Pass the brand to the Car model
    session.add(db_car)
    await session.commit()
    await session.refresh(db_car)
    db_car.brand_name = brand.name
    # return db_car - выдает ошибку MissingGreenlet при этом все равно засовывает данные в табличку...
    return db_car


# @router.get("/", response_model=list[Car])
# async def get_cars(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_async_session)):
#     query = select(Car_model).options(joinedload(Car_model.brand)).offset(skip).limit(limit)
#     result = await session.execute(query)
#     cars = result.scalars().all()
#     return cars


@router.get("/", response_model=list[Car], dependencies=[Depends(require_admin_or_employee_or_client)])
async def get_cars(
    skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_async_session)
):
    query = (
        select(Car_model).options(joinedload(Car_model.brand)).offset(skip).limit(limit)
    )
    result = await session.execute(query)
    cars = result.scalars().all()

    # Serialize brand name
    for car in cars:
        car.brand_name = Car.serialize_brand(car.brand)

    return cars


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_car(car_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(Car_model).where(Car_model.id == car_id)
    result = await session.execute(query)
    db_car = result.scalars().first()

    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")

    await session.delete(db_car)
    await session.commit()


@router.put("/{car_id}", response_model=Car, dependencies=[Depends(require_admin)])
async def update_car(
    car_id: int,
    car_update: Annotated[CarCreate, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Car_model).where(Car_model.id == car_id)
    result = await session.execute(query)
    db_car = result.scalars().first()

    if not db_car:
        raise HTTPException(status_code=404, detail="Car not found")

    # Validate brand_id if it's included in the update
    if "brand_id" in car_update.dict(exclude_unset=True):
        brand_id = car_update.brand_id
        query = select(BrandModel).where(BrandModel.id == brand_id)
        result = await session.execute(query)
        brand = result.scalars().first()
        if not brand:
            raise HTTPException(
                status_code=400, detail="Invalid brand_id. Brand does not exist."
            )

    # Update car attributes
    for key, value in car_update.dict(exclude_unset=True).items():
        setattr(db_car, key, value)

    await session.commit()
    await session.refresh(db_car)

    # Serialize brand name
    db_car.brand_name = Car.serialize_brand(db_car.brand)
    return db_car
