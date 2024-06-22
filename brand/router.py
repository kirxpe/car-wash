from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from brand.schemas import Brand, BrandCreate
from auth.dependencies import require_admin, require_admin_or_employee_or_client
from brand.brand_service import BrandService

router = APIRouter(prefix="/brands", tags=["Brands"])

def get_brand_service(session: AsyncSession = Depends(get_async_session)):
    return BrandService(session)

@router.get(
    "/",
    response_model=list[Brand],
    dependencies=[Depends(require_admin_or_employee_or_client)],
)
@router.get("/", response_model=List[Brand], dependencies=[Depends(require_admin_or_employee_or_client)])
async def get_brands(
    skip: int = 0, 
    limit: int = 10, 
    filter_by: str = Query(None, alias="filter"),
    sort_by: str = Query(None, alias="sort"),
    brand_service: BrandService = Depends(get_brand_service)
):
    return await brand_service.get_brands(skip=skip, limit=limit, filter_by=filter_by, sort_by=sort_by)

@router.get("/{brand_name}", response_model=Brand, dependencies=[Depends(require_admin_or_employee_or_client)])
async def get_brand_by_name(
    brand_name: str, 
    brand_service: BrandService = Depends(get_brand_service)
):
    return await brand_service.get_brand_by_name(brand_name)

@router.get(
    "/{brand_id}",
    response_model=Brand,
    dependencies=[Depends(require_admin_or_employee_or_client)],
)
async def get_brand_by_id(
    brand_id: int, session: AsyncSession = Depends(get_async_session)
):
    service = BrandService(session)
    return await service.get_brand_by_id(brand_id)

@router.post("/", response_model=Brand, dependencies=[Depends(require_admin)])
async def create_brand(
    brand: Annotated[BrandCreate, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    service = BrandService(session)
    return await service.create_brand(brand)

@router.put(
    "/{brand_id}", response_model=Brand, dependencies=[Depends(require_admin)]
)
async def update_brand(
    brand_id: int,
    brand_update: Annotated[BrandCreate, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    service = BrandService(session)
    return await service.update_brand(brand_id, brand_update)

@router.delete(
    "/by_name/{brand_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_brand_by_name(
    brand_name: str, session: AsyncSession = Depends(get_async_session)
):
    service = BrandService(session)
    await service.delete_brand_by_name(brand_name)

@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_brand(
    brand_id: int, session: AsyncSession = Depends(get_async_session)
):
    service = BrandService(session)
    await service.delete_brand(brand_id)
