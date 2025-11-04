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

async def clear_chat_cron(bot: Bot, dp: Dispatcher):
    agronomists = read_collection("agronomists")
    
    firebase_config = get_config()
    tz = timezone(firebase_config['timezone'])
    time = datetime.now(tz=tz)
    for agronomist in agronomists:
        greating = None
        try:
            history = read_collection_with_composite_filter(
                collection = "history_message_id",
                filters=[
                {
                    "atribut": "tg_id",
                    "op": "==",
                    "value": agronomist["data"]["tg_id"],
                },
                {
                    "atribut": "bot",
                    "op": "==",
                    "value": "agrilink_review",
                },

                ],
                order=None
            )
        except:
            history = []
        menu = [f'View']
        buttons = ["View"]
        count_task =  len(download_information(agronomist["data"]["tg_id"]))
        if len(history) == 0:
            try:
                try:
                    greating = await bot.send_message(
                    text=text.view.format(count_task),
                    reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
                    parse_mode=ParseMode.MARKDOWN,
                    chat_id=agronomist["data"]["tg_id"]
                    )
                except TelegramForbiddenError:
                    print(f'''User blocked  {agronomist["data"]["tg_id"]}''')
                state_with = FSMContext(
                    storage=dp.storage, # dp - экземпляр диспатчера
                    key=StorageKey(
                    chat_id=agronomist["data"]["tg_id"], # если юзер в ЛС, то chat_id=user_id
                    user_id=agronomist["data"]["tg_id"],
                    bot_id=bot.id
                    )
                )

                await state_with.set_state(FSMStates.wait_menu_click)
                for i in range(greating.message_id - 1, 0, -1):
                    try:
                        await bot.delete_message(agronomist["data"]["tg_id"], i)
                    except:
                        print("All messages deleted")
                add_document(
                    {
                        "tg_id": agronomist["data"]["tg_id"],
                        "first_message_id": greating.message_id,
                        "bot": "agrilink_review"
                    },
                    collection = "history_message_id"
                )
            except:
                print(f'''Problem clear chat user_id: {agronomist["data"]["tg_id"]}''')
        elif len(history) == 1:
            try:
                try:
                    greating = await bot.send_message(
                    text=text.view.format(count_task),
                    reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
                    parse_mode=ParseMode.MARKDOWN,
                    chat_id=agronomist["data"]["tg_id"]
                    )
                except TelegramForbiddenError:
                    print(f'''User blocked  {agronomist["data"]["tg_id"]}''')
                state_with = FSMContext(
                    storage=dp.storage, # dp - экземпляр диспатчера
                    key=StorageKey(
                    chat_id=agronomist["data"]["tg_id"], # если юзер в ЛС, то chat_id=user_id
                    user_id=agronomist["data"]["tg_id"],
                    bot_id=bot.id
                    )
                )
                await state_with.set_state(FSMStates.wait_menu_click)
                for i in range(history[0]["data"]["first_message_id"], greating.message_id):
                    try:
                        await bot.delete_message(agronomist["data"]["tg_id"], i)
                    except:
                        print("All messages deleted")
                update_document(
                    history[0]["document_id"],
                    {
                        "tg_id": agronomist["data"]["tg_id"],
                        "first_message_id": greating.message_id,
                        "bot": "agrilink_review"
                    },
                    collection = "history_message_id"
                )
            except:
                print(f'''Problem clear chat user_id: {agronomist["data"]["tg_id"]}''')
        else:
            first_message_id = history[0]["data"]["first_message_id"]
            doc_id = history[0]["document_id"]
            for i in range(1, len(history)):
                if history[i]["data"]["first_message_id"] > first_message_id:
                    delete_document(doc_id, collection = "history_message_id")
                    doc_id = history[i]["document_id"]
                    first_message_id = history[i]["data"]["first_message_id"]
                else:
                    delete_document(history[i]["document_id"], collection = "history_message_id")
            try:
                greating =  await bot.send_message(
                    text=text.view.format(count_task),
                    reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
                    parse_mode=ParseMode.MARKDOWN,
                    chat_id=agronomist["data"]["tg_id"]
                )
                state_with = FSMContext(
                    storage=dp.storage, # dp - экземпляр диспатчера
                    key=StorageKey(
                    chat_id=agronomist["data"]["tg_id"], # если юзер в ЛС, то chat_id=user_id
                    user_id=agronomist["data"]["tg_id"],
                    bot_id=bot.id
                    )
                )

                await state_with.set_state(FSMStates.wait_menu_click)
                for i in range(first_message_id, greating.message_id):
                    try:
                        await bot.delete_message(agronomist["data"]["tg_id"], i)
                    except:
                        print("All messages deleted")
                update_document(
                    doc_id,
                    {
                        "tg_id": agronomist["data"]["tg_id"],
                        "first_message_id": greating.message_id,
                        "bot": "agrilink_review"
                    },
                    collection = "history_message_id"
                )
            except:
                print(f'''Problem clear chat user_id: {agronomist["data"]["tg_id"]}''')
                
async def notification_for_agronomist(bot: Bot):
    agronomists = read_collection("agronomists")
    for agronomist in agronomists:
        calendar_events = read_collection_with_composite_filter(
                collection = "calendar_events",
                filters = [
                    {
                        "atribut": "agronomist_tg_id",
                        "op": "==",
                        "value": agronomist["data"]["tg_id"]
                    },
                    {
                        "atribut": "type",
                        "op": "in",
                        "value": ["Text only", "Visual only", "Text and Visual"]
                    },
                    {
                        "atribut": "status",
                        "op": "in",
                        "value": ["farmer_response"]
                    }
                ]
            )
        for calendar_event in calendar_events:
            update_document(
                calendar_event["document_id"],
                {
                    "status": "notified_agronomist"
                },
                collection = "calendar_events"
            )
            try:
                await bot.send_message(text=text.notify_task.format(agronomist["data"]["personal_info"]["name"]), reply_markup=create_title_menu(["Got it!"], ["Got it!"]), chat_id=agronomist["data"]["tg_id"], parse_mode=ParseMode.MARKDOWN)
            except:
                print("Problem with chat. Telegram id: {}".format(agronomist["data"]["tg_id"]))

async def briefing_for_agronom(bot: Bot):
    agronomists = read_collection("agronomists")
    firebase_config = get_config()
    tz = timezone(firebase_config['timezone'])
    time = datetime.now(tz=tz)
    for agronomist in agronomists:
        calendar_events = read_collection_with_composite_filter(
                collection = "calendar_events",
                filters = [
                    {
                        "atribut": "agronomist_tg_id",
                        "op": "==",
                        "value": agronomist["data"]["tg_id"]
                    },
                    {
                        "atribut": "type",
                        "op": "in",
                        "value": ["Text only", "Visual only", "Text and Visual"]
                    },
                    {
                        "atribut": "status",
                        "op": "in",
                        "value": ["notified_agronomist", "farmer_response"]
                    }
                ]
            )
        try:
            if len(calendar_events) > 0:
                await bot.send_message(text=text.notify_briefing.format(agronomist["data"]["personal_info"]["name"], time.strftime("%d %B %Y"), len(calendar_events)), reply_markup=create_title_menu(["Got it!"], ["Got it!"]), chat_id=agronomist["data"]["tg_id"], parse_mode=ParseMode.MARKDOWN)
            else:
                await bot.send_message(text=text.notify_empty.format(agronomist["data"]["personal_info"]["name"], time.strftime("%d %B %Y")), reply_markup=create_title_menu(["Got it!"], ["Got it!"]), chat_id=agronomist["data"]["tg_id"], parse_mode=ParseMode.MARKDOWN)
        except:
            print("Problem with chat. Telegram id: {}".format(agronomist["data"]["tg_id"]))
