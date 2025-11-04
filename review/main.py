
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware
import config
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.state import State, StatesGroup, default_state
from datetime import datetime
from pytz import timezone
from router import router
from firebase.firebase import (
    get_config, add_document, \
    upload_file, read_collection, \
    read_document, download_file, \
    update_document, delete_document, \
    read_document_with_filter, delete_file, \
    read_collection_with_composite_filter
)
from aiogram.exceptions import TelegramForbiddenError
import text
from collection_editer import download_information
from states import FSMStates
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from datetime import datetime, timedelta
from kb_df import create_pagination_keyboard, create_title_menu
from command_menu import set_main_menu
from restart import *
from notification import *
from handlers import *
from calendar_swipe import *
from respond import *
from refusal import *
from confirm import *


            
async def main():
    firebase_config = get_config()
    tz=timezone(firebase_config['timezone'])
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.message.middleware(ChatActionMiddleware())
    dp.include_router(router)
    await set_main_menu(bot)
    scheduler = AsyncIOScheduler(timezone=tz)
    '''
    Send briefing every day at 1:00:00 am UTC+0. 5 minute delay if miss start
    '''
    scheduler.add_job(
        func=clear_chat_cron,
        id="clear chat",
        trigger='cron',
        hour=1,
        minute=0,
        misfire_grace_time=60*5,
        kwargs={"bot": bot, "dp": dp}
    )
    '''
    Send notification about response farmer every  30 minute. Start: 10:15 UTC+0. 5 minute delay if miss start
    '''
    scheduler.add_job(
        notification_for_agronomist,
        trigger='interval',
        start_date=datetime(2024, 3, 1, 10, 15),
        minutes=30,
        timezone=tz,
        misfire_grace_time=60*5,
        kwargs={"bot": bot}
    )
    '''
    Send briefing every day at 8:00:00 am UTC+0. 5 minute delay if miss start
    '''
    scheduler.add_job(
        briefing_for_agronom,
        id="briefing",
        trigger='cron',
        #seconds=5,
        hour=8,
        minute=0,
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
