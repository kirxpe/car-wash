from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas
from service.utils import convert_price_to_kopecks, convert_time_to_seconds


class ServiceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_service(
        self, service_data: schemas.ServiceCreate
    ) -> models.Service:
        db_service = models.Service(**service_data.dict())
        self.session.add(db_service)
        await self.session.commit()
        await self.session.refresh(db_service)
        return db_service

    async def get_services(
        self, skip: int = 0, limit: int = 100
    ) -> schemas.ServiceListResponse:
        query = select(models.Service).offset(skip).limit(limit)
        count_query = select(func.count()).select_from(models.Service)

        result = await self.session.execute(query)
        services = result.scalars().all()

        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()

        return schemas.ServiceListResponse(total_count=total_count, services=services)
    

    async def get_service_by_id(self, service_id: int) -> models.Service:
        query = select(models.Service).where(models.Service.id == service_id)
        result = await self.session.execute(query)
        service = result.scalars().first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service

    async def update_service(
        self, service_id: int, service_update: schemas.ServiceCreate
    ) -> models.Service:
        query = select(models.Service).where(models.Service.id == service_id)
        result = await self.session.execute(query)
        db_service = result.scalars().first()

        if not db_service:
            raise HTTPException(status_code=404, detail="Service not found")

        for key, value in service_update.dict(exclude_unset=True).items():
            if key == "price":
                db_service.price_kopecks = convert_price_to_kopecks(value)
            elif key == "time":
                db_service.time_seconds = convert_time_to_seconds(value)
            else:
                setattr(db_service, key, value)

        await self.session.commit()
        await self.session.refresh(db_service)
        return db_service

    async def delete_service(self, service_id: int) -> None:
        query = select(models.Service).where(models.Service.id == service_id)
        result = await self.session.execute(query)
        service = result.scalars().first()

        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        await self.session.delete(service)
        await self.session.commit()
