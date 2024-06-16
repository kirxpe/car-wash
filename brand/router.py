from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status #noqa
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound


from database import get_async_session
from brand.models import Brand as brand_model
from brand.schemas import Brand, BrandCreate #noqa
from auth.dependencies import require_admin, require_admin_or_employee_or_client

#заменить query на stmt где не get операции. 
#добавить dependencies на put, delete, create операции.

router = APIRouter(prefix="/brands", tags=["Brands"])

@router.get("/", response_model=list[Brand], dependencies=[Depends(require_admin_or_employee_or_client)])
async def get_brands(skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_async_session)):
    try: 
        query = select(brand_model).offset(skip).limit(limit)
        result = await session.execute(query)
        brands = result.scalars().all()
        return brands
    except Exception:
        raise HTTPException(status_code=400, detail="Something went wrong") 

@router.get("/{brand_id}", response_model=Brand, dependencies=[Depends(require_admin_or_employee_or_client)])
async def get_brand_by_id(brand_id: int,  session: AsyncSession = Depends(get_async_session)):
    query = select(brand_model).where(brand_model.id == brand_id)
    result = await session.execute(query)
    db_brand = result.scalars().first()
    if not db_brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return db_brand

@router.post("/", response_model=Brand, dependencies=[Depends(require_admin)])
async def create_brand(brand: Annotated[BrandCreate, Depends()], session: AsyncSession = Depends(get_async_session)):
    stmt = select(brand_model).where(brand_model.name == brand.name)
    try:
        db_brand = await session.execute(stmt)
        db_brand = db_brand.scalar_one()
        raise HTTPException(status_code=400, detail="Brand already exists")
    except NoResultFound:
        db_brand = brand_model(name=brand.name.lower().capitalize())
        session.add(db_brand)
        await session.commit()
        await session.refresh(db_brand)
        return db_brand
    
@router.put("/{brand_id}", response_model=Brand, dependencies=[Depends(require_admin)]) #добавить exception при какой нибудь хуйне
async def update_brand(
    brand_id: int, brand_update: Annotated[BrandCreate, Depends()],
    session: AsyncSession = Depends(get_async_session)
):
    query = select(brand_model).where(brand_model.id == brand_id)
    result = await session.execute(query)
    db_brand = result.scalars().first()

    if not db_brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    for key, value in brand_update.dict(exclude_unset=True).items():
        setattr(db_brand, key, value)

    await session.commit()
    await session.refresh(db_brand)
    return db_brand

@router.delete("/by_name/{brand_name}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_brand_by_name(brand_name: str, session: AsyncSession = Depends(get_async_session)):
    query = select(brand_model).where(brand_model.name == brand_name)
    result = await session.execute(query)
    db_brand = result.scalars().first()

    if not db_brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    await session.delete(db_brand)
    await session.commit()
    
@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_brand(brand_id: int, session: AsyncSession = Depends(get_async_session)):
    query = select(brand_model).where(brand_model.id == brand_id)
    result = await session.execute(query)
    db_brand = result.scalars().first()

    if not db_brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    await session.delete(db_brand)
    await session.commit()    