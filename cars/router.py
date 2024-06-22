from typing import Annotated
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from cars.schemas import CarCreate, Car
from auth.dependencies import require_admin, require_admin_or_employee_or_client
from .cars_service import CarService

router = APIRouter(prefix="/cars", tags=["Cars"])

def get_car_service(session: AsyncSession = Depends(get_async_session)):
    return CarService(session)

@router.get("/", response_model=List[Car], dependencies=[Depends(require_admin_or_employee_or_client)])
async def get_cars(
    skip: int = 0, 
    limit: int = 10, 
    filter_by: str = Query(None, alias="filter"),
    sort_by: str = Query(None, alias="sort"),
    car_service: CarService = Depends(get_car_service)
):
    return await car_service.get_cars(skip=skip, limit=limit, filter_by=filter_by, sort_by=sort_by)

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=Car,
    dependencies=[Depends(require_admin)],
)
async def create_car(
    car: Annotated[CarCreate, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    service = CarService(session)
    return await service.create_car(car)

@router.get(
    "/{car_id}",
    response_model=list[Car],
    dependencies=[Depends(require_admin_or_employee_or_client)],
)
async def get_car_by_id(car_id: int, session: AsyncSession = Depends(get_async_session)):
    service = CarService(session)
    await service.get_car_by_id(car_id)

@router.delete(
    "/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_car(car_id: int, session: AsyncSession = Depends(get_async_session)):
    service = CarService(session)
    await service.delete_car(car_id)

@router.put("/{car_id}", response_model=Car, dependencies=[Depends(require_admin)])
async def update_car(
    car_id: int,
    car_update: Annotated[CarCreate, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    service = CarService(session)
    return await service.update_car(car_id, car_update)
