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
    read_collection_with_composite_filter, update_document_array \
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
     
@router.callback_query(StateFilter(FSMStates.waiting_for_start_comment), F.data.startswith('forward'))
async def process_forward_press(call: types.CallbackQuery, state: FSMContext):
    agronom_id = call.message.chat.id
    data = await state.get_data()
    info = data.get(agronom_id)
    page_number, document_id =  info['page_number'], info['document_id']
    agronom_document = DataFramePaginator(download_information(agronom_id), page_number = page_number)
    agronom_document.increment_page()
    msg = event_brief_information(agronom_document)
    await call.message.edit_text(
        text=msg,
        reply_markup=agronom_document.get_keyboard(
            [
                agronom_id,
                agronom_document.get_page_number()
            ]
        ),
        parse_mode=ParseMode.MARKDOWN
    )
    info['page_number'] = agronom_document.get_page_number()
    info['document_id'] = agronom_document.get_document_id()
    await state.update_data({agronom_id: info})
    

@router.callback_query(StateFilter(FSMStates.waiting_for_start_comment), F.data.startswith('backward'))
async def process_backward_press(call: types.CallbackQuery, state: FSMContext):
    agronom_id = call.message.chat.id
    data = await state.get_data()
    info = data.get(agronom_id)
    page_number, document_id =  info['page_number'], info['document_id']
    agronom_document = DataFramePaginator(download_information(agronom_id), page_number = page_number)
    agronom_document.decrement_page()
    msg = event_brief_information(agronom_document)
    await call.message.edit_text(
        text=msg,
        reply_markup=agronom_document.get_keyboard(
            [
                agronom_id,
                agronom_document.get_page_number()
            ]
        ),
        parse_mode=ParseMode.MARKDOWN
    )
    info['page_number'] = agronom_document.get_page_number()
    info['document_id'] = agronom_document.get_document_id()
    await state.update_data({agronom_id: info})

@router.callback_query(StateFilter(FSMStates.waiting_for_start_comment), F.data.startswith('Back'))
async def process_back_press(call: types.CallbackQuery, state: FSMContext):
    menu = [f'View']
    buttons = ["View"]
    count_task =  len(download_information(call.message.chat.id))
    await call.message.edit_text(
        text=text.view.format(count_task),
        reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(FSMStates.wait_menu_click)
