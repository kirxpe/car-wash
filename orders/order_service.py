from typing import List
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from fastapi import HTTPException
from datetime import datetime, timedelta
from orders import models, schemas
from service.models import Service
from customer_cars.models import CustomerCar
from cars.models import Car
from auth.models import User
from .schemas import OrderBase, UserBase, CustomerBase, CustomerCarBase, CarBase, OrderListResponse
from .models import Order, OrderStatus
from notifications.email_service import notify_customer

class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_today_orders(self) -> list[schemas.OrderBase]:
        
            start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)

            result = await self.session.execute(
                select(Order)
                .options(
                    joinedload(models.Order.customer_car).joinedload(CustomerCar.user),
                    joinedload(Order.customer_car).joinedload(CustomerCar.car).joinedload(Car.brand),
                    joinedload(Order.employee),
                    joinedload(Order.administrator),
                )
                .where(Order.start_date >= start_of_day, Order.start_date < end_of_day)
            )
            orders = result.scalars().all()
            
            order_list = []
            for order in orders:
                total_time = await self.calculate_total_time(order.id)
                total_price = await self.calculate_total_price(order.id)

                order_data = OrderBase(
                    id=order.id,
                    status=order.status.value,
                    start_date=(order.start_date + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                    end_date=(order.end_date + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S') if order.end_date else None,
                    totalTime=total_time,
                    totalPrice=total_price,
                    administrator=UserBase(
                        id=order.administrator.id,
                        full_name=f"{order.administrator.first_name} {order.administrator.last_name} {order.administrator.patronymic}",
                    ),
                    employee=UserBase(
                        id=order.employee.id,
                        full_name=f"{order.employee.first_name} {order.employee.last_name} {order.employee.patronymic}",
                    ),
                    customerCar=CustomerCarBase(
                        id=order.customer_car.id,
                        year=order.customer_car.year,
                        number=order.customer_car.number,
                        customer=CustomerBase(
                            id=order.customer_car.user.id,
                            full_name=f"{order.customer_car.user.first_name} {order.customer_car.user.last_name} {order.customer_car.user.patronymic}",
                            email=order.customer_car.user.email,
                        ),
                        car=CarBase(
                            model=order.customer_car.car.model,
                            brand=order.customer_car.car.brand.name,
                        ),
                    ),
                )
                order_list.append(order_data)

            return order_list
    
    async def create_order(self, order_data: schemas.OrderCreate, administrator_id: int) -> dict:
        new_order = models.Order(
            status=models.OrderStatus.in_progress,
            customer_car_id=order_data.customer_car_id,
            employee_id=order_data.employee_id,
            administrator_id=administrator_id,
            start_date=datetime.utcnow(),
        )
        self.session.add(new_order)
        await self.session.commit()
        await self.session.refresh(new_order)

        for service in order_data.services:
            order_service = models.OrderService(order_id=new_order.id, service_id=service.service_id)
            self.session.add(order_service)

        await self.session.commit()
        await self.session.refresh(new_order)

        total_time = await self.calculate_total_time(new_order.id)
        new_order.end_date = new_order.start_date + timedelta(minutes=total_time)

        await self.session.commit()
        await self.session.refresh(new_order)

        return {"message": "Заказ создан"}

    async def calculate_total_time(self, order_id: int) -> int:
        result = await self.session.execute(select(models.OrderService).where(models.OrderService.order_id == order_id))
        order_services = result.scalars().all()
        total_time = 0
        for order_service in order_services:
            service_result = await self.session.execute(select(Service).where(Service.id == order_service.service_id))
            service = service_result.scalar_one_or_none()
            if service:
                total_time += service.time_seconds
        return total_time // 60

    async def calculate_total_price(self, order_id: int) -> int:
        result = await self.session.execute(select(models.OrderService).where(models.OrderService.order_id == order_id))
        order_services = result.scalars().all()
        total_price = 0
        for order_service in order_services:
            service_result = await self.session.execute(select(Service).where(Service.id == order_service.service_id))
            service = service_result.scalar_one_or_none()
            if service:
                total_price += service.price_kopecks
        return total_price // 100

    async def get_order_by_id_async(self, order_id: int) -> schemas.OrderBase:
        result = await self.session.execute(
            select(models.Order)
            .options(
                joinedload(models.Order.customer_car).joinedload(CustomerCar.user),
                joinedload(models.Order.customer_car).joinedload(CustomerCar.car).joinedload(Car.brand),
                joinedload(models.Order.employee),
                joinedload(models.Order.administrator),
            )
            .where(models.Order.id == order_id)
        )
        order = result.unique().scalars().one_or_none()
        
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")

        total_time = await self.calculate_total_time(order.id)
        total_price = await self.calculate_total_price(order.id)

        order_data = schemas.OrderBase(
            id=order.id,
            status=order.status.value,
            start_date=(order.start_date + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
            end_date=(order.end_date + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S') if order.end_date else None,
            totalTime=total_time,
            totalPrice=total_price,
            administrator=schemas.UserBase(
                id=order.administrator.id,
                full_name=f"{order.administrator.first_name} {order.administrator.last_name} {order.administrator.patronymic}",
            ),
            employee=schemas.UserBase(
                id=order.employee.id,
                full_name=f"{order.employee.first_name} {order.employee.last_name} {order.employee.patronymic}",
            ),
            customerCar=schemas.CustomerCarBase(
                id=order.customer_car.id,
                year=order.customer_car.year,
                number=order.customer_car.number,
                customer=schemas.CustomerBase(
                    id=order.customer_car.user.id,
                    full_name=f"{order.customer_car.user.first_name} {order.customer_car.user.last_name} {order.customer_car.user.patronymic}",
                    email=order.customer_car.user.email,
                ),
                car=schemas.CarBase(
                    model=order.customer_car.car.model,
                    brand=order.customer_car.car.brand.name,
                ),
            ),
        )

        return order_data

    async def get_orders(
            self, 
            user: User, 
            skip: int = 0, 
            limit: int = 10, 
            status: int = None,
            sort_by: list[str] = None,
            sort_order: str = "desc"
        ) -> OrderListResponse:
            query = select(models.Order).options(
                joinedload(models.Order.customer_car).joinedload(CustomerCar.user),
                joinedload(models.Order.customer_car).joinedload(CustomerCar.car).joinedload(Car.brand),
                joinedload(models.Order.employee),
                joinedload(models.Order.administrator),
            )

            if user.role_id == 2:
                query = query.where(models.Order.employee_id == user.id)
            elif user.role_id == 3:
                query = query.where(models.Order.customer_car.has(CustomerCar.user_id == user.id))

            if status is not None:
                query = query.where(models.Order.status == models.OrderStatus(status))

            count_query = select(func.count()).select_from(query.subquery())

            query = query.offset(skip).limit(limit)
            
            result = await self.session.execute(query)
            orders = result.scalars().all()
            count_result = await self.session.execute(count_query)
            total_count = count_result.scalar()
            order_list = []
            for order in orders:
                total_time = await self.calculate_total_time(order.id)
                total_price = await self.calculate_total_price(order.id)
                
                order_data = schemas.OrderBase(
                    id=order.id,
                    status=order.status.value,
                    start_date=(order.start_date + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                    end_date=(order.end_date + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S') if order.end_date else None,
                    totalTime=total_time,
                    totalPrice=total_price,
                    administrator=schemas.UserBase(
                        id=order.administrator.id,
                        full_name=f"{order.administrator.first_name} {order.administrator.last_name} {order.administrator.patronymic}",
                    ),
                    employee=schemas.UserBase(
                        id=order.employee.id,
                        full_name=f"{order.employee.first_name} {order.employee.last_name} {order.employee.patronymic}",
                    ),
                    customerCar=schemas.CustomerCarBase(
                        id=order.customer_car.id,
                        year=order.customer_car.year,
                        number=order.customer_car.number,
                        customer=schemas.CustomerBase(
                            id=order.customer_car.user.id,
                            full_name=f"{order.customer_car.user.first_name} {order.customer_car.user.last_name} {order.customer_car.user.patronymic}",
                            email=order.customer_car.user.email,
                        ),
                        car=schemas.CarBase(
                            model=order.customer_car.car.model,
                            brand=order.customer_car.car.brand.name,
                        ),
                    ),
                )
                order_list.append(order_data)

            if sort_by:
                reverse = sort_order == "desc"
                for field in reversed(sort_by):  
                    order_list.sort(key=lambda x: getattr(x, field, None), reverse=reverse) #magic

            return OrderListResponse(total_count=total_count, orders=order_list)

    async def delete_order_by_id(self, order_id: int) -> dict:
        result = await self.session.execute(select(models.Order).where(models.Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            await self.session.delete(order)
            await self.session.commit()
            return {"message": "Заказ успешно удален"}
        raise HTTPException(status_code=404, detail="Заказ не найден")

    async def add_services_to_order(self, order_id: int, services: list[schemas.ServiceId]) -> dict:
        result = await self.session.execute(select(models.Order).where(models.Order.id == order_id))
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")

        if order.status != models.OrderStatus.in_progress:
            raise HTTPException(
                status_code=400, detail="Нельзя добавлять услуги в уже выполненный заказ"
            )

        existing_services_result = await self.session.execute(
            select(models.OrderService.service_id).where(
                models.OrderService.order_id == order_id
            )
        )
        existing_services = {row[0] for row in existing_services_result.all()}

        additional_time_seconds = 0
        for service in services:
            if service.service_id in existing_services:
                service_name = await self._get_service_name(service.service_id)
                raise HTTPException(
                    status_code=400,
                    detail=f"Данная услуга '{service_name}' уже присутствует в заказе",
                )

            new_order_service = models.OrderService(
                order_id=order_id, service_id=service.service_id
            )
            self.session.add(new_order_service)

            service_result = await self.session.execute(
                select(Service).where(Service.id == service.service_id)
            )
            service_obj = service_result.scalar_one_or_none()
            if service_obj:
                additional_time_seconds += service_obj.time_seconds

        order.end_date = order.end_date + timedelta(seconds=additional_time_seconds)
        await self.session.commit()
        await self.session.refresh(order)

        return {"message": "Заказ добавлен"}

    async def _get_service_name(self, service_id: int) -> str:
        result = await self.session.execute(
            select(Service).where(Service.id == service_id)
        )
        service = result.scalar_one_or_none()
        return service.name if service else "Такой услуги нет"

    async def update_order_statuses(self):
        current_time = datetime.utcnow()
        result = await self.session.execute(
            select(models.Order)
            .options(joinedload(models.Order.customer_car).joinedload(CustomerCar.user))
            .where(models.Order.status == models.OrderStatus.in_progress)
        )
        orders = result.scalars().all()

        for order in orders:
            if order.end_date and current_time > order.end_date:
                order.status = models.OrderStatus.completed
                if order.customer_car.user.is_send_notify:
                    await self.notify_and_update_order(order)

        await self.session.commit()

    async def notify_and_update_order(self, order):
        await notify_customer(order.customer_car.user, order.id)
        self.session.add(order)
        await self.session.commit()
