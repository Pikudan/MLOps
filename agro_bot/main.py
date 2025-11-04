from aiogram import Bot, Dispatcher
import logging
from aiogram.enums.parse_mode import ParseMode
import asyncio
from datetime import datetime
from datetime import datetime
import pytz
from sulguk import AiogramSulgukMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware
from router import router
from unauthorized_handler import *
from chat_handler import *
from event_modifier import *
from event_registry import *
from notification import *
import config
from command_menu import set_main_menu
from handlers import *
from restart import *
from event_remover import *
from event_details import *

async def main():
    firebase_config = get_config()
    tz=pytz.timezone(firebase_config['timezone'])
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    bot.session.middleware(AiogramSulgukMiddleware())
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(ChatActionMiddleware())
    dp.include_router(router)
    await set_main_menu(bot)

    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(
        func=notify_problem,
        id="farmer_sent",
        trigger='interval',
        start_date=datetime(2024, 3, 1, 10, 15),
        minutes=5,
        timezone=tz,
        misfire_grace_time=60*5,
        kwargs={"bot": bot}
    )
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())