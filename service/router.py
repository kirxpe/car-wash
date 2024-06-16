# ... (existing imports)
from fastapi import APIRouter, Depends
from service.service import ServiceService
from . import schemas
from database import AsyncSession, get_async_session
from auth.dependencies import require_admin_or_employee_or_client, require_admin
from fastapi import status

router = APIRouter(prefix="/services", tags=["Services"])

# ... (other dependencies)

# Dependency to inject ServiceService
def get_service_service(session: AsyncSession = Depends(get_async_session)):
    return ServiceService(session)

# Create Service
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Service, dependencies=[Depends(require_admin)])
async def create_service(service: schemas.ServiceCreate, service_service: ServiceService = Depends(get_service_service)):
    return await service_service.create_service(service)

# Read All Services
@router.get("/", response_model=list[schemas.Service], dependencies=[Depends(require_admin_or_employee_or_client)])
async def get_services(skip: int = 0, limit: int = 5, service_service: ServiceService = Depends(get_service_service)):
    return await service_service.get_services(skip=skip, limit=limit)

# Read Service by ID
@router.get("/{service_id}", response_model=schemas.Service, dependencies=[Depends(require_admin_or_employee_or_client)])
async def get_service_by_id(service_id: int, service_service: ServiceService = Depends(get_service_service)):
    return await service_service.get_service_by_id(service_id)

# Update Service (Admin only)
@router.put("/{service_id}", response_model=schemas.Service, dependencies=[Depends(require_admin)])
async def update_service(service_id: int, service_update: schemas.ServiceCreate, service_service: ServiceService = Depends(get_service_service)):
    return await service_service.update_service(service_id, service_update)

# Delete Service (Admin only)
@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def delete_service(service_id: int, service_service: ServiceService = Depends(get_service_service)):
    await service_service.delete_service(service_id)