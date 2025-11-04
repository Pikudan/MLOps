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
from kb import create_pagination_keyboard, create_title_menu, create_menu
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.fsm.state import State, StatesGroup, default_state
from states import FSMStates
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from collection_editer import download_information
from count_message import count_message

async def notify_problem(bot: Bot):
    notify_problems = read_collection_with_composite_filter(
        collection = "problems_for_support",
        filters = [
            {
                "atribut": "notify",
                "op": "==",
                "value": "farmer"
            },
            {
                "atribut": "status",
                "op": "==",
                "value": "open"
            }
        ]
    )
    firebase_config = get_config()
    tz = timezone(firebase_config['timezone'])
    time = datetime.now(tz=tz).strftime("%d %B %Y")
    for notify_problem in notify_problems:
        farmer_id = notify_problem["data"]["user_telegram_id"]
        problem_name = notify_problem["data"]["name"]
        farmer_doc = read_collection_with_composite_filter(
        collection = "farmers",
        filters = [
            {
                "atribut": "tg_id",
                "op": "==",
                "value": farmer_id
            }
        ]
        )
        farmer_name = farmer_doc[0]["data"]["personal_info"]["name"]
        try:
            await bot.send_message(text=text.notify_sent.format(farmer_name, problem_name, time), reply_markup=create_title_menu(["Got it!"], ["Got it!"]), chat_id=farmer_id, parse_mode=ParseMode.MARKDOWN)
            update_document(notify_problem["document_id"], {"notify": "nobody"}, "problems_for_support")
        except:
            #print("Problem with chat. Telegram id: {}".format(agronomist["data"]["tg_id"]))
            print("Problem with chat. Telegram id")

async def clear_chat_cron(bot: Bot, dp: Dispatcher):
    farmers = read_collection("farmers")
    firebase_config = get_config()
    tz = timezone(firebase_config['timezone'])
    time = datetime.now(tz=tz)
    for farmer in farmers:
        greating = None
        try:
            history = read_collection_with_composite_filter(
                collection = "history_message_id",
                filters = [
                {
                    "atribut": "tg_id",
                    "op": "==",
                    "value": farmer["data"]["tg_id"],
                },
                {
                    "atribut": "bot",
                    "op": "==",
                    "value": "farmer_task",
                }
                ])
        except:
            history = []
        cnt_new_message = count_message(farmer["data"]["tg_id"])
        menu = [f'Crop Calendar', f'Add Record', f'Agronomics Support ({cnt_new_message})']
        buttons = ["Crop Calendar", "Add Record", "Support"]
        if len(history) == 0:

            try:
                
                try:
                    greating = await bot.send_message(
                    text=f'Hi, here are some things I can help with:',
                    reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
                    parse_mode=ParseMode.MARKDOWN,
                    chat_id=farmer["data"]["tg_id"]
                    )
                except TelegramForbiddenError:
                    print(f'''User blocked  {farmer["data"]["tg_id"]}''')
               
                state_with = FSMContext(
                    storage=dp.storage, # dp - экземпляр диспатчера
                    key=StorageKey(
                    chat_id=farmer["data"]["tg_id"], # если юзер в ЛС, то chat_id=user_id
                    user_id=farmer["data"]["tg_id"],
                    bot_id=bot.id
                    )
                )

                await state_with.set_state(FSMStates.wait_menu_click)
                for i in range(greating.message_id - 1, 0, -1):
                    try:
                        await bot.delete_message(farmer["data"]["tg_id"], i)
                    except TelegramBadRequest as ex:
                        if ex.message == "Bad Request: message to delete not found":
                            print("All messages deleted")
                add_document(
                    {
                        "tg_id": farmer["data"]["tg_id"],
                        "first_message_id": greating.message_id,
                        "bot": "farmer_task"
                    
                    },
                    collection = "history_message_id"
                )
            except:
                print(f'''Problem clear chat user_id: {farmer["data"]["tg_id"]}''')
                
        elif len(history) == 1:
            try:
                try:
                    greating = await bot.send_message(
                    text=f'Hi, here are some things I can help with:',
                    reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
                    parse_mode=ParseMode.MARKDOWN,
                    chat_id=farmer["data"]["tg_id"]
                    )
                except TelegramForbiddenError:
                    print(f'''User blocked  {farmer["data"]["tg_id"]}''')
                state_with = FSMContext(
                    storage=dp.storage, # dp - экземпляр диспатчера
                    key=StorageKey(
                    chat_id=farmer["data"]["tg_id"], # если юзер в ЛС, то chat_id=user_id
                    user_id=farmer["data"]["tg_id"],
                    bot_id=bot.id
                    )
                )

                await state_with.set_state(FSMStates.wait_menu_click)
                for i in range(history[0]["data"]["first_message_id"], greating.message_id):
                    try:
                        await bot.delete_message(farmer["data"]["tg_id"], i)
                    except TelegramBadRequest as ex:
                        if ex.message == "Bad Request: message to delete not found":
                            print("All messages deleted")
                update_document(
                    history[0]["document_id"],
                    {
                        "tg_id": farmer["data"]["tg_id"],
                        "first_message_id": greating.message_id,
                        "bot": "farmer_task"
                    },
                    collection = "history_message_id"
                )
            except:
                print(f'''Problem clear chat user_id: {farmer["data"]["tg_id"]}''')
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
                try:
                    greating =  await bot.send_message(
                    text=f'Hi, here are some things I can help with:',
                    reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
                    parse_mode=ParseMode.MARKDOWN,
                    chat_id=farmer["data"]["tg_id"]
                    )
                except TelegramForbiddenError:
                    print(f'''User blocked  {farmer["data"]["tg_id"]}''')
                state_with = FSMContext(
                    storage=dp.storage, # dp - экземпляр диспатчера
                    key=StorageKey(
                    chat_id=farmer["data"]["tg_id"], # если юзер в ЛС, то chat_id=user_id
                    user_id=farmer["data"]["tg_id"],
                    bot_id=bot.id
                    )
                )

                await state_with.set_state(FSMStates.wait_menu_click)
                for i in range(first_message_id, greating.message_id):
                    try:
                        await bot.delete_message(farmer["data"]["tg_id"], i)
                    except TelegramBadRequest as ex:
                        if ex.message == "Bad Request: message to delete not found":
                            print("All messages deleted")
                update_document(
                    doc_id,
                    {
                        "tg_id": farmer["data"]["tg_id"],
                        "first_message_id": greating.message_id,
                        "bot": "farmer_task"
                    },
                    collection = "history_message_id"
                )
            except:
                print(f'''Problem clear chat user_id: {farmer["data"]["tg_id"]}''')
        
async def overdue_notify_farmer(bot: Bot):
    farmers = read_collection("farmers")
    firebase_config = get_config()
    tz = timezone(firebase_config['timezone'])
    time = datetime.now(tz=tz)
    for farmer in farmers:
        overdue_events = overdue(farmer["data"]["tg_id"])
        for calendar_event in overdue_events:
            time_before_begin = int((time - calendar_event["data"]["timestamp_end"]).total_seconds() / (60 * 60 * 24))
            title = calendar_event["data"]["title"]
            if  time_before_begin:
                try:
                    await bot.send_message(text=text.notify_overdue.format(title, time_before_begin), reply_markup=create_title_menu(["Got it!"], ["Got it!"]), chat_id=farmer["data"]["tg_id"], parse_mode=ParseMode.MARKDOWN)
                except:
                    print("Problem with chat. Telegram id: {}".format(farmer["data"]["tg_id"]))

async def outstanding_notify_farmer(bot: Bot):
    farmers = read_collection("farmers")
    firebase_config = get_config()
    tz = timezone(firebase_config['timezone'])
    time = datetime.now(tz=tz)
    for farmer in farmers:
        outstanding_events = outstanding(farmer["data"]["tg_id"])
        for calendar_event in outstanding_events:
            date_end = calendar_event["data"]["timestamp_end"].strftime("%d %B %Y")
            title = calendar_event["data"]["title"]
            type = calendar_event["data"]["type"]
            timing = {
                "Text only": 2,
                "Visual only": 2,
                "Text and Visual": 2,
                "Confirmation only": 1,
            }
            time_to_end = int((calendar_event["data"]["timestamp_end"] - time).total_seconds() / (60 * 60 * 24))
            if timing[type] == time_to_end:
                try:
                    await bot.send_message(text=text.notify_outstanding.format(title, date_end), reply_markup=create_title_menu(["Got it!"], ["Got it!"]), chat_id=farmer["data"]["tg_id"], parse_mode=ParseMode.MARKDOWN)
                except:
                    print("Problem with chat. Telegram id: {}".format(farmer["data"]["tg_id"]))

   

async def upcoming_notify_farmer(bot: Bot):
    farmers = read_collection("farmers")
    firebase_config = get_config()
    tz = timezone(firebase_config['timezone'])
    time = datetime.now(tz=tz)
    
    for farmer in farmers:
        calendar_events = read_collection_with_composite_filter(
        "calendar_events",
        [
            {
                "atribut": "farmer_tg_id",
                "op": "==",
                "value": farmer["data"]["tg_id"],
            },
            {
                "atribut": "status",
                "op": "==",
                "value": "creation",
            },

        ],
        {
            "atribut": "timestamp_begin",
            "desc": False
        }
        )
        notify_id = []
        for calendar_event in calendar_events:
            minuts_before = calendar_event["data"]["notify_for_days"] * 24 * 60
            time_before_begin = (time - calendar_event["data"]["timestamp_begin"]).total_seconds() / 60
            if calendar_event["data"]["status"] == "creation" and  time_before_begin > -minuts_before and time_before_begin < 0:
                notify_id.append(calendar_event["document_id"])
        for event_id in notify_id:
            update_document(
                event_id,
                {
                    "status": "notified_farmer"
                },
                collection = "calendar_events"
            )
            event = read_document(event_id, "calendar_events")
            title = event["title"]
            date_begin = event["timestamp_begin"].strftime("%d %B %Y")
            try:
                await bot.send_message(text=text.notify_upcoming.format(title, date_begin), reply_markup=create_title_menu(["Got it!"], ["Got it!"]), chat_id=farmer["data"]["tg_id"], parse_mode=ParseMode.MARKDOWN)
            except:
                print("Problem with chat. Telegram id: {}".format(farmer["data"]["tg_id"]))

async def briefing_for_farmer(bot: Bot):
    farmers = read_collection("farmers")
    firebase_config = get_config()
    tz = timezone(firebase_config['timezone'])
    time = datetime.now(tz=tz)
    
    for farmer in farmers:
       
        calendar_events = read_document_with_filter(
            atribut = "farmer_tg_id",
            op = "==",
            value = farmer["data"]["tg_id"],
            collection = "calendar_events"
        )
        calendar_name = ["Upcoming", "Outstanding", "Overdue"]
        upcoming_events = upcoming(farmer["data"]["tg_id"])
        outstanding_events = outstanding(farmer["data"]["tg_id"])
        overdue_events = overdue(farmer["data"]["tg_id"])
        msg = ""
        if len(upcoming_events) > 0:
            msg = ''.join((msg, f'✅ ({len(upcoming_events)}) Upcoming\n\n'))
        if len(outstanding_events) > 0:
            msg = ''.join((msg, f'⚠️ ({len(outstanding_events)}) Outstanding\n\n'))
        if len(overdue_events) > 0:
            msg = ''.join((msg, f'❗️ ({len(overdue_events)}) Overdue\n\n'))
        try:
            if len(msg) > 0:
                await bot.send_message(text=text.notify_briefing.format(farmer["data"]["personal_info"]["name"], time.strftime("%d %B %Y"), msg), reply_markup=create_title_menu(["Got it!"], ["Got it!"]), chat_id=farmer["data"]["tg_id"], parse_mode=ParseMode.MARKDOWN)
            else:
                await bot.send_message(text=text.notify_empty.format(farmer["data"]["personal_info"]["name"], time.strftime("%d %B %Y")), reply_markup=create_title_menu(["Got it!"], ["Got it!"]), chat_id=farmer["data"]["tg_id"], parse_mode=ParseMode.MARKDOWN)
                
        except:
            print("Problem with chat. Telegram id: {}".format(farmer["data"]["tg_id"]))

async def quality_control(bot: Bot, dp: Dispatcher):
    notify_problems = read_collection_with_composite_filter(
        collection = "problems_for_support",
        filters = [
            {
                "atribut": "notify",
                "op": "==",
                "value": "farmer"
            },
            {
                "atribut": "status",
                "op": "==",
                "value": "resolved"
            }
        ]
    )
    firebase_config = get_config()
    tz = timezone(firebase_config['timezone'])
    time = datetime.now(tz=tz).strftime("%d %B %Y")
    for notify_problem in notify_problems:
        farmer_id = notify_problem["data"]["user_telegram_id"]
        problem_name = notify_problem["data"]["name"]
        farmer_doc = read_collection_with_composite_filter(
        collection = "farmers",
        filters = [
            {
                "atribut": "tg_id",
                "op": "==",
                "value": farmer_id
            }
        ]
        )
        farmer_name = farmer_doc[0]["data"]["personal_info"]["name"]
        state_with = FSMContext(
                    storage=dp.storage, # dp - экземпляр диспатчера
                    key=StorageKey(
                    chat_id=farmer_id, # если юзер в ЛС, то chat_id=user_id
                    user_id=farmer_id,
                    bot_id=bot.id
                    )
                )
        try:
            await bot.send_message(text=text.solved_problem.format(farmer_name, problem_name, time), reply_markup=create_menu(['1', '2', '3', '4', '5'], count=5), chat_id=farmer_id, parse_mode=ParseMode.MARKDOWN)
            update_document(notify_problem["document_id"], {"notify": "nobody"}, "problems_for_support")
            await state_with.set_state(FSMStates.set_grade)
            await state_with.update_data({'grade_farm_id': farmer_id, 'grade_document_id': notify_problem["document_id"]})
            
        except:
            #print("Problem with chat. Telegram id: {}".format(agronomist["data"]["tg_id"]))
            print("Problem with chat. Telegram id")
