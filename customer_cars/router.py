from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from . import schemas
from database import get_async_session
from .customer_cars_service import CustomerCarService
from auth.dependencies import require_admin, require_admin_or_employee_or_client

router = APIRouter(prefix="/customer_cars", tags=["Customer Cars"])


def get_customer_car_service(
    session: AsyncSession = Depends(get_async_session),
): 
    return CustomerCarService(session)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.CustomerCar,
    dependencies=[Depends(require_admin)],
)
async def create_customer_car(
    customer_car: schemas.CustomerCarCreate,
    customer_car_service: CustomerCarService = Depends(get_customer_car_service),
):
    return await customer_car_service.create_customer_car(customer_car)


@router.get(
    "/",
    response_model=List[schemas.CustomerCar],
    dependencies=[Depends(require_admin_or_employee_or_client)],
)
async def read_customer_cars(
    skip: int = 0,
    limit: int = 100,
    customer_car_service: CustomerCarService = Depends(get_customer_car_service),
):
    return await customer_car_service.get_customer_cars(skip=skip, limit=limit)


@router.get(
    "/{customer_car_id}",
    response_model=schemas.CustomerCar,
    dependencies=[Depends(require_admin)],
)
async def read_customer_car_by_id(
    customer_car_id: int,
    customer_car_service: CustomerCarService = Depends(get_customer_car_service),
):
    return await customer_car_service.get_customer_car_by_id(customer_car_id)


@router.put(
    "/{customer_car_id}",
    response_model=schemas.CustomerCar,
    dependencies=[Depends(require_admin)],
)
async def update_customer_car(
    customer_car_id: int,
    customer_car_update: schemas.CustomerCarCreate,
    customer_car_service: CustomerCarService = Depends(get_customer_car_service),
):
    return await customer_car_service.update_customer_car(
        customer_car_id, customer_car_update
    )


@router.delete(
    "/{customer_car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_customer_car(
    customer_car_id: int,
    customer_car_service: CustomerCarService = Depends(get_customer_car_service),
):
    await customer_car_service.delete_customer_car(customer_car_id)
