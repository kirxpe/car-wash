from typing import Annotated
from fastapi import Depends, FastAPI
from auth.dependencies import fastapi_users

from auth.base_config import auth_backend
from auth.schemas import UserCreate, UserRead

from cars.router import router as cars_router
from brand.router import router as brands_router
from auth.router import router as user_router
from service.router import router as service_router
from customer_cars.router import router as customer_cars_router
from orders.router import router as orders_router
from scheduler import scheduler

fastapi_users = fastapi_users

app = FastAPI(title="Car wash service")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth", #username = email.
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(
        UserRead, Annotated[UserCreate, Depends()]
    ),  
    prefix="/auth",
    tags=["Auth"],
)

@app.on_event("startup")
async def startup_event():
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

app.include_router(brands_router)
app.include_router(cars_router)
app.include_router(user_router)
app.include_router(service_router)
app.include_router(customer_cars_router)
app.include_router(orders_router)
