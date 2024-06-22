from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from database import async_session_maker
from orders.order_service import OrderService


scheduler = AsyncIOScheduler()


async def update_order_statuses_task():
    async with async_session_maker() as session:  
        order_service = OrderService(session)
        await order_service.update_order_statuses()

scheduler.add_job(update_order_statuses_task, IntervalTrigger(minutes=2))


