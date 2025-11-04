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
from kb_df import create_pagination_keyboard, create_title_menu

@router.error()
async def error_handler(event: ErrorEvent):
    logging.critical("Critical error caused by %s", event.exception, exc_info=True)

from check_agronomist import check_agronomist

                
@router.message(StateFilter(FSMStates.waiting_for_end_start))
@router.message(StateFilter(FSMStates.waiting_for_end_cancel_comment))
@router.message(StateFilter(FSMStates.waiting_for_end_loading_message))
@router.message(StateFilter(FSMStates.waiting_for_end_get))
async def delete_message_in_this_state(message: types.Message, state: FSMContext):
    '''Do not respond until all messages from the farmer are sent'''
    try:
        await message.delete()
    except:
        print(f'Error clean {message.from_user.id} message_id: {message.message_id}')
    
@router.callback_query(F.data.startswith('Got it!'))
async def close_notification(call: types.CallbackQuery):
    await call.message.delete()



@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    '''Send how much data is available for confirmation
    Args:
        message:
            message from user
        pjjstate:
            state for bot
    Raises:
        Too much agronomists with the tg_id message.from_user.id in collection agronomists
    '''
    if check_agronomist(message.from_user.id):
        logging.basicConfig(level=logging.DEBUG)
        menu = [f'View']
        buttons = ["View"]
        count_task =  len(download_information(message.from_user.id))
        await message.answer(
            text=text.view.format(count_task),
            reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
            parse_mode=ParseMode.MARKDOWN
        )
        print(f'''{message.message_id} from {message.from_user.id}''')
        await state.set_state(FSMStates.wait_menu_click)
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
                "value": "agrilink_review",
            },
            ],
            order=None
        )
        if len(tracking):
            increment_value(tracking[0]["document_id"], "start", 1, "tracking")
        else:
            add_document(
                {
                    "tg_id": message.from_user.id,
                    "bot": "agrilink_review",
                    "start": 1,
                    "restart": 0
                },
                collection="tracking"
            )


@router.callback_query(StateFilter(FSMStates.wait_menu_click), F.data.startswith("View"))
async def agronom_menu(call: types.CallbackQuery, state: FSMContext):
    agronom_id = call.message.chat.id
    agronom_document = DataFramePaginator(download_information(agronom_id))
    if agronom_document.get_DataFrame().empty:
        try:
            msg = f'There are no tasks at the moment ✅'
            buttons = [f'View']
            names = ["View"]
            await call.message.edit_text(
                text=msg,
                reply_markup=create_title_menu([button for button in buttons], [name for name in names]),
                parse_mode=ParseMode.MARKDOWN
            )
        except TelegramBadRequest as ex:
            print(ex.message)
    else:
        msg =  event_brief_information(agronom_document)
        await call.message.edit_text(
            text=msg,
            reply_markup=agronom_document.get_keyboard(info=[agronom_document.get_page_number()]),
            parse_mode=ParseMode.MARKDOWN
        )
        await state.update_data(
            {
                agronom_id:
                {
                    "page_number": agronom_document.get_page_number(),
                    "document_id": agronom_document.get_document_id()
                }
            }
        )
        await state.set_state(FSMStates.waiting_for_start_comment)
