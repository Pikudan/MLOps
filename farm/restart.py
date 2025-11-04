
from aiogram import types, F, Router, flags, Bot, Dispatcher
from aiogram.utils.formatting import (
    Bold, as_list, as_marked_section, \
    as_key_value, HashTag
)
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_media_group import media_group_handler
from aiogram.fsm.context import FSMContext
from firebase.firebase import (
    get_config, add_document, \
    upload_file, read_collection, \
    read_document, download_file, \
    update_document, delete_document, \
    read_document_with_filter, delete_file, \
    read_collection_with_composite_filter, update_document_array, \
    increment_value
)
from datetime import datetime
from pytz import timezone
import numpy as np
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.filters import Command, StateFilter, CommandStart
import pandas as pd

import os
from typing import List
from aiogram.types import (
    ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton, FSInputFile, \
    URLInputFile, BufferedInputFile, \
    Message, ReplyKeyboardRemove
)
import logging

from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
import text
from states import FSMStates
from collection_editer import download_information
from router import router
from aiogram.types.error_event import ErrorEvent
from text_message import event_brief_information
from pagination_info import DataFramePaginator
from kb import create_pagination_keyboard, create_title_menu



def count_message(farmer_id: int):
    df = download_information(int(farmer_id), 'problems_for_support')
    buttons = []
    count = 0
    if df.empty:
        return count
    else:
        for index, row in df.iterrows():
            button = row.to_dict()
            count += button['number_of_messages_from_agro']
    return count
    
    
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
                "value": "farmer_task",
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
            "value": "agrilink_farm",
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
                "bot": "agrilink_farm",
                "start": 0,
                "restart": 1
            },
            collection="tracking"
        )
    cnt_new_message = count_message(message.from_user.id)
    menu = [f'Crop Calendar', f'Add Record', f'Agronomics Support ({cnt_new_message})']
    buttons = ["Crop Calendar", "Add Record", "Support"]
    if len(history) == 0:
        try:
            greating = await message.answer(
                text=f'Hi, here are some things I can help with:',
                reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(FSMStates.wait_menu_click)
            for i in range(greating.message_id - 1, 0, -1):
                try:
                    await bot.delete_message(message.from_user.id, i)
                except:
                    print("All messages deleted")
            add_document(
                {
                    "tg_id": message.from_user.id,
                    "first_message_id": greating.message_id,
                    "bot": "farmer_task"
                },
                collection = "history_message_id"
            )
        except:
            print(f'''Problem clear chat user_id: {message.from_user.id}''')
    elif len(history) == 1:
        try:
            greating = await message.answer(
                text=f'Hi, here are some things I can help with:',
                reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(FSMStates.wait_menu_click)
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
                    "bot": "farmer_task"
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
            greating =  await message.answer(
                text=f'Hi, here are some things I can help with:',
                reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(FSMStates.wait_menu_click)
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
                    "bot": "farmer_task"
                },
                collection = "history_message_id"
            )
        except:
            print(f'''Problem clear chat user_id: {message.from_user.id}''')
