from aiogram import types
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram import Bot, types
import logging
from firebase import delete_document, add_document, read_collection_with_composite_filter, update_document, increment_value
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import Command
from aiogram import F
from pagination_kb import create_title_menu
import pandas as pd
from available_farmers import count_message
from aiogram import Bot
from router import router
from aiogram.types.error_event import ErrorEvent


TITLE = pd.DataFrame({'name': []})


@router.error()
async def error_handler(event: ErrorEvent):
    logging.critical("Critical error caused by %s", event.exception, exc_info=True)

@router.callback_query(F.data.startswith('Got it!'))
async def briefing(call: types.CallbackQuery):
    await call.message.delete()

@router.message(Command("restart"))
async def restart(message: types.Message, bot: Bot, state: FSMContext):
    try:
        history = read_collection_with_composite_filter(
            collection = "history_message_id",
            filters=[
            {
                "atribut": "tg_id",
                "op": "==",
                "value": message.from_user.id,
            },
            {
                "atribut": "bot",
                "op": "==",
                "value": "agro",
            },
            ],
            order=None
        )
    except:
        history = []
    tracking = read_collection_with_composite_filter(
        collection = "tracking",
        filters=[
        {
            "atribut": "tg_id",
            "op": "==",
            "value": message.from_user.id,
        },
        {
            "atribut": "bot",
            "op": "==",
            "value": "agrilink_agronom",
        },
        ],
        order=None
    )
    if len(tracking):
        increment_value(tracking[0]["document_id"], "restart", 1, "tracking")
    else:
        add_document(
            {
                "tg_id": message.from_user.id,
                "bot": "agrilink_agronom",
                "start": 0,
                "restart": 1
            },
            collection="tracking"
        )
    cnt_new_message = count_message(message.from_user.id)
    message_text = (f"Hi {message.from_user.full_name}, I am a bot prepared by AgriLink serving you to assist farmers.\n\nPress *‘View’* to see farmers available to you, otherwise press *‘Contact us’* to address any questions to our team.")

    if len(history) == 0:
        try:
            greating = await message.answer(
                message_text,
                reply_markup=create_title_menu([f'View({cnt_new_message})', 'Contact us'], ['View', 'Contact us']),
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(default_state)
            for i in range(greating.message_id - 1, 0, -1):
                try:
                    await bot.delete_message(message.from_user.id, i)
                except:
                    print("All messages deleted")
            add_document(
                {
                    "tg_id": message.from_user.id,
                    "first_message_id": greating.message_id,
                    "bot": "agro"
                },
                collection = "history_message_id"
            )
        except:
            print(f'''Problem clear chat user_id: {message.from_user.id}''')
    elif len(history) == 1:
        try:
            greating = await message.answer(
                message_text,
                reply_markup=create_title_menu([f'View({cnt_new_message})', 'Contact us'], ['View', 'Contact us']),
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(default_state)
            for i in range(history[0]["data"]["first_message_id"], greating.message_id):
                try:
                    await bot.delete_message(message.from_user.id, i)
                except:
                    print("All messages deleted")
            update_document(
                history[0]["document_id"],
                {
                    "tg_id": message.from_user.id,
                    "first_message_id": greating.message_id,
                    "bot": "agro"
                },
                collection = "history_message_id"
            )
        except:
            print(f'''Problem clear chat user_id: {message.from_user.id}''')
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
            greating = await message.answer(
                message_text, 
                reply_markup=create_title_menu([f'View({cnt_new_message})', 'Contact us'], ['View', 'Contact us']), 
                parse_mode=ParseMode.MARKDOWN 
            )
            await state.set_state(default_state)
            for i in range(first_message_id, greating.message_id):
                try:
                    await bot.delete_message(message.from_user.id, i)
                except:
                    print("All messages deleted")
            update_document(
                doc_id,
                {
                    "tg_id": message.from_user.id,
                    "first_message_id": greating.message_id,
                    "bot": "agro"
                },
                collection = "history_message_id"
            )
        except:
            print(f'''Problem clear chat user_id: {message.from_user.id}''')