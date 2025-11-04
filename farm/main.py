
import asyncio
import logging
from sulguk import AiogramSulgukMiddleware
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware
import config
from datetime import datetime
from pytz import timezone
from router import router
import text
from firebase.firebase import (
    get_config, add_document, \
    upload_file, read_collection, \
    read_document, download_file, \
    update_document, delete_document, \
    read_document_with_filter, delete_file, \
    read_collection_with_composite_filter
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from collection_editer import outstanding, upcoming, overdue
from kb import create_pagination_keyboard, create_title_menu
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from collection_editer import download_information
from restart import restart
from handlers import *
from notification import *
from new_problem import *
from exciting_problem import *
from add_record import *
from crop_calendar import *
from command_menu import set_main_menu
from rating_grade import *

async def main():
    firebase_config = get_config()
    tz=timezone(firebase_config['timezone'])
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    bot.session.middleware(AiogramSulgukMiddleware())
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(ChatActionMiddleware())
    dp.include_router(router)
    await set_main_menu(bot)

    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(
        func=clear_chat_cron,
        id="clear chat",
        trigger='interval',
        start_date=datetime(2024, 2, 27, 23, 20, 0),
        #minutes=60,
        #seconds=20,
        hours=24,
        misfire_grace_time=60*5,
        kwargs={"bot": bot, "dp": dp}
    )
    scheduler.add_job(
        upcoming_notify_farmer,
        trigger='interval',
        start_date=datetime(2024, 2, 27, 10, 0, 0),
        #minutes=60,
        #seconds=20,
        hours=24,
        timezone=tz,
        misfire_grace_time=60*5,
        kwargs={"bot": bot}
    )
    scheduler.add_job(
        outstanding_notify_farmer,
        trigger='interval',
        start_date=datetime(2024, 2, 27, 10, 30, 0),
        #minutes=60,
        #seconds=20,
        hours=24,
        timezone=tz,
        misfire_grace_time=60*5,
        kwargs={"bot": bot}
    )
    scheduler.add_job(
        overdue_notify_farmer,
        trigger='interval',
        start_date=datetime(2024, 2, 27, 11, 0, 0),
        #minutes=60,
        #seconds=20,
        hours=24,
        timezone=tz,
        misfire_grace_time=60*5,
        kwargs={"bot": bot}
    )
    scheduler.add_job(
        briefing_for_farmer,
        trigger='interval',
        start_date=datetime(2024, 2, 27, 8, 0, 0),
        #minutes=5,
        #seconds=20,
        hours=24,
        timezone=tz,
        misfire_grace_time=60*5,
        kwargs={"bot": bot}
    )
    scheduler.add_job(
        notify_problem,
        trigger='interval',
        start_date=datetime(2024, 2, 27, 8, 0, 0),
        minutes=10,
        #seconds=20,
        #hours=24,
        timezone=tz,
        misfire_grace_time=60*5,
        kwargs={"bot": bot}
    )
    scheduler.add_job(
        quality_control,
        trigger='interval',
        start_date=datetime(2024, 2, 27, 8, 15, 0),
        #minutes=10,
        #seconds=20,
        hours=1,
        timezone=tz,
        misfire_grace_time=60*5,
        kwargs={"bot": bot, "dp": dp}
    )
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())



