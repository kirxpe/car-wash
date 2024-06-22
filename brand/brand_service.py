from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from brand import models, schemas


class BrandService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_brand(self, brand_data: schemas.BrandCreate) -> models.Brand:
        stmt = select(models.Brand).where(models.Brand.name == brand_data.name)
        result = await self.session.execute(stmt)
        db_brand = result.scalars().first()
        
        if db_brand:
            raise HTTPException(status_code=400, detail="Такой бренд уже существует")
        
        db_brand = models.Brand(name=brand_data.name.lower().capitalize())
        self.session.add(db_brand)
        
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=400, detail="Такой бренд уже существует")
        
        await self.session.refresh(db_brand)
        return db_brand

    async def get_brands(self, skip: int = 0, limit: int = 10, filter_by: str = None, sort_by: str = None) -> list[models.Brand]:
        query = select(models.Brand)
        if filter_by:
            query = query.where(models.Brand.name.ilike(f"%{filter_by}%"))
        if sort_by:
            query = query.order_by(getattr(models.Brand, sort_by))
        query = query.offset(skip).limit(limit)
        
        result = await self.session.execute(query)
        brands = result.scalars().all()
        return brands

    async def get_brand_by_id(self, brand_id: int) -> models.Brand:
        query = select(models.Brand).where(models.Brand.id == brand_id)
        result = await self.session.execute(query)
        db_brand = result.scalars().first()
        if not db_brand:
            raise HTTPException(status_code=404, detail="Бренд не найден")
        return db_brand

    async def get_brand_by_name(self, brand_name: str) -> models.Brand:
        stmt = select(models.Brand).where(models.Brand.name == brand_name.lower().capitalize())
        result = await self.session.execute(stmt)
        db_brand = result.scalars().first()
        
        if not db_brand:
            raise HTTPException(status_code=404, detail="Бренд не найден")
        
        return db_brand    

    async def update_brand(self, brand_id: int, brand_update: schemas.BrandCreate) -> models.Brand:
        query = select(models.Brand).where(models.Brand.id == brand_id)
        result = await self.session.execute(query)
        db_brand = result.scalars().first()

        if not db_brand:
            raise HTTPException(status_code=404, detail="Бренд не найден")

        for key, value in brand_update.dict(exclude_unset=True).items():
            setattr(db_brand, key, value)

        await self.session.commit()
        await self.session.refresh(db_brand)
        return db_brand

    async def delete_brand_by_name(self, brand_name: str) -> None:
        query = select(models.Brand).where(models.Brand.name == brand_name)
        result = await self.session.execute(query)
        db_brand = result.scalars().first()

        if not db_brand:
            raise HTTPException(status_code=404, detail="Бренд не найден")

        await self.session.delete(db_brand)
        await self.session.commit()

    async def delete_brand(self, brand_id: int) -> None:
        query = select(models.Brand).where(models.Brand.id == brand_id)
        result = await self.session.execute(query)
        db_brand = result.scalars().first()

        if not db_brand:
            raise HTTPException(status_code=404, detail="Бренд не найден")

        await self.session.delete(db_brand)
        await self.session.commit()
