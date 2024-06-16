from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from fastapi import HTTPException

from service.models import Service
from customer_cars.models import CustomerCar
from .models import Order, OrderStatus, OrderService as OrderServiceModel
from .schemas import OrderBase, OrderCreate, CustomerCarBase, ServiceId, UserBase, CustomerBase, CarBase
from cars.models import Car
from notifications.email_service import notify_customer



class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order: OrderCreate, administrator_id: int):
        await self.update_order_statuses()

        new_order = Order(
            status=OrderStatus.in_progress,  # Статус по умолчанию
            customer_car_id=order.customer_car_id,
            employee_id=order.employee_id,
            administrator_id=administrator_id,
            start_date=datetime.utcnow()
        )
        self.session.add(new_order)
        await self.session.commit()
        await self.session.refresh(new_order)

        for service in order.services:
            order_service = OrderServiceModel(order_id=new_order.id, service_id=service.service_id)
            self.session.add(order_service)

        await self.session.commit()
        await self.session.refresh(new_order)

        # Calculate end_date
        total_time = await self.calculate_total_time(new_order.id)
        new_order.end_date = new_order.start_date + timedelta(minutes=total_time)

        await self.session.commit()
        await self.session.refresh(new_order)

        return {"message": "Order created successfully"}

    async def calculate_total_time(self, order_id: int) -> int:
        result = await self.session.execute(
            select(OrderServiceModel).where(OrderServiceModel.order_id == order_id)
        )
        order_services = result.scalars().all()
        total_time = 0
        for order_service in order_services:
            service_result = await self.session.execute(
                select(Service).where(Service.id == order_service.service_id)
            )
            service = service_result.scalar_one_or_none()
            if service:
                total_time += service.time_seconds
        return total_time // 60
    
    async def calculate_total_price(self, order_id: int) -> int:
        result = await self.session.execute(
            select(OrderServiceModel).where(OrderServiceModel.order_id == order_id)
        )
        order_services = result.scalars().all()
        total_price = 0
        for order_service in order_services:
            service_result = await self.session.execute(
                select(Service).where(Service.id == order_service.service_id)
            )
            service = service_result.scalar_one_or_none()
            if service:
                total_price += service.price_kopecks
        return total_price // 100

    async def get_order_by_id_async(self, order_id: int):
        result = await self.session.execute(
        select(Order)
        .options(
            joinedload(Order.customer_car).joinedload(CustomerCar.user),
            joinedload(Order.customer_car).joinedload(CustomerCar.car).joinedload(Car.brand),
            joinedload(Order.employee),
            joinedload(Order.administrator)
        )
        .where(Order.id == order_id)
    )
        order = result.unique().scalars().one()


        total_time = await self.calculate_total_time(order.id)
        total_price = await self.calculate_total_price(order.id)

        order_data = OrderBase(
            id=order.id,
            status=order.status.value,  
            start_date=order.start_date,
            end_date=order.end_date,
            totalTime=total_time,
            totalPrice=total_price,
            administrator=UserBase(
                id=order.administrator.id,
                full_name=f"{order.administrator.first_name} {order.administrator.last_name} {order.administrator.patronymic}"
            ),
            employee=UserBase(
                id=order.employee.id,
                full_name=f"{order.employee.first_name} {order.employee.last_name} {order.employee.patronymic}"
            ),
            customerCar=CustomerCarBase(
                id=order.customer_car.id,
                year=order.customer_car.year,
                number=order.customer_car.number,
                customer=CustomerBase(
                    id=order.customer_car.user.id,
                    full_name=f"{order.customer_car.user.first_name} {order.customer_car.user.last_name} {order.customer_car.user.patronymic}",
                    email=order.customer_car.user.email
                ),
                car=CarBase(
                    model=order.customer_car.car.model,
                    brand=order.customer_car.car.brand.name
                )
            )
        )

        return order_data
    

    async def delete_order_by_id(self, order_id: int):
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        if order:
            await self.session.delete(order)
            await self.session.commit()
            return {"message": "Order deleted successfully"}
        raise HTTPException(status_code=404, detail="Order not found")


    async def add_services_to_order(self, order_id: int, services: List[ServiceId]):
        result = await self.session.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status != OrderStatus.in_progress:
            raise HTTPException(status_code=400, detail="Cannot add services to a completed order")

        existing_services_result = await self.session.execute(
            select(OrderServiceModel.service_id).where(OrderServiceModel.order_id == order_id)
        )
        existing_services = {row[0] for row in existing_services_result.all()}

        additional_time_seconds = 0
        for service in services:
            if service.service_id in existing_services:
                service_name = await self._get_service_name(service.service_id)
                raise HTTPException(status_code=400, detail=f"Service '{service_name}' already exists in the order")

            new_order_service = OrderServiceModel(order_id=order_id, service_id=service.service_id)
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

        return {"message": "Services added successfully"}

    async def _get_service_name(self, service_id: int) -> str:
        result = await self.session.execute(select(Service).where(Service.id == service_id))
        service = result.scalar_one_or_none()
        return service.name if service else "Unknown Service"

    async def update_order_statuses(self):
        current_time = datetime.utcnow()
        result = await self.session.execute(
            select(Order)
            .options(
                joinedload(Order.customer_car).joinedload(CustomerCar.user)
            )
            .where(Order.status == OrderStatus.in_progress)
        )
        orders = result.scalars().all()

        for order in orders:
            if order.end_date and current_time > order.end_date:
                order.status = OrderStatus.completed
                if order.customer_car.user.is_send_notify:
                    await self.notify_and_update_order(order)

        await self.session.commit()

    async def notify_and_update_order(self, order):
        # Вызов уведомления
        await notify_customer(order.customer_car.user, order.id)
        # Сохранение изменений в базе данных
        self.session.add(order)
        await self.session.commit()