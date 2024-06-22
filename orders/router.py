from typing import List
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas
from .order_service import OrderService
from database import get_async_session
from auth.dependencies import require_admin, get_current_user, require_admin_or_employee_or_client
from auth.models import User
from auth.schemas import UserRead

router = APIRouter(prefix="/orders", tags=["Orders"])

def get_order_service(session: AsyncSession = Depends(get_async_session)):
    return OrderService(session)

@router.get("/today", response_model=List[schemas.OrderBase], dependencies=[Depends(require_admin_or_employee_or_client)])
async def get_today_orders(order_service: OrderService = Depends(get_order_service)):
    return await order_service.get_today_orders()

@router.get("/", response_model=schemas.OrderListResponse, dependencies=[Depends(require_admin_or_employee_or_client)])
async def get_orders(
    skip: int = 0, 
    limit: int = 10,
    status: int = None,
    sort_by: List[str] = Query(None),
    sort_order: str = Query("desc"),
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    return await order_service.get_orders(user=current_user, skip=skip, limit=limit, status=status, sort_by=sort_by, sort_order=sort_order)

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_order(
    order: schemas.OrderCreate, 
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user)
):
    return await order_service.create_order(order, administrator_id=current_user.id)

@router.get("/{order_id}", response_model=schemas.OrderBase, dependencies=[Depends(require_admin)])
async def get_order(order_id: int, order_service: OrderService = Depends(get_order_service)):
    return await order_service.get_order_by_id_async(order_id)

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_order(order_id: int, order_service: OrderService = Depends(get_order_service)):
    return await order_service.delete_order_by_id(order_id)

@router.put("/{order_id}/services", status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def add_services_to_order(order_id: int, services: List[schemas.ServiceId], order_service: OrderService = Depends(get_order_service)):
    return await order_service.add_services_to_order(order_id, services)

@router.put("/update-statuses", status_code=status.HTTP_200_OK, dependencies=[Depends(require_admin)])
async def update_order_statuses(order_service: OrderService = Depends(get_order_service)):
    await order_service.update_order_statuses()
    return {"message": "Order statuses updated successfully"}

