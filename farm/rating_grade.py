from aiogram import types, F, Router, flags, Bot, Dispatcher
from aiogram.types import (
    ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton, FSInputFile, \
    URLInputFile, BufferedInputFile, \
    Message, ReplyKeyboardRemove
)
from farmer2agronom import farmer2agronom
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_media_group import media_group_handler
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from typing import List
from aiogram.fsm.state import State, StatesGroup, default_state
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
import os
import logging
from firebase.firebase import (
    get_config, add_document, \
    upload_file, read_collection, \
    read_document, download_file, \
    update_document, delete_document, \
    read_document_with_filter, delete_file, \
    read_collection_with_composite_filter, update_document_array, \
    increment_value
)
from kb import create_menu
from bd_and_DataFrame import add_information, merge_and_sortes_message_about_problems
from sulguk import SULGUK_PARSE_MODE
from collection_editer import download_information
from aiogram.enums.parse_mode import ParseMode
import asyncio
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram import F
from datetime import datetime
from pytz import timezone
import requests
from kb import create_pagination_keyboard, create_title_menu
import kb, text
from pagination_info import DataFramePaginator
import pandas as pd
from text_message import event_brief_information, event_full_information, event_without_confirm, msg_for_support
from router import router
from states import FSMStates, FSMStatus
from aiogram.types.error_event import ErrorEvent
from count_message import count_message

@router.callback_query(StateFilter(FSMStates.set_grade), F.data.in_(['4', '5']))
async def good_grade(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    msg_clear = await call.message.edit_text('Thank you for your feedback!')
    data = await state.get_data()
    update_document(data.get('grade_document_id'), {"grade": int(call.data)}, "problems_for_support")
    await bot.delete_messages(call.from_user.id, [msg_clear.message_id])
    await state.set_state(FSMStates.wait_menu_click)

@router.callback_query(StateFilter(FSMStates.set_grade), F.data.in_(['1', '2', '3']))
async def bad_grade(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    msg_clear = await call.message.edit_text(text=text.bad_grade_text, reply_markup=kb.create_menu(['Submit', 'Skip'], count=2))
    update_document(data.get('grade_document_id'), {"grade": int(call.data)}, "problems_for_support")
    await state.update_data({'clear_messages': [msg_clear.message_id]})

@router.message(StateFilter(FSMStates.set_grade), F.text)
async def bad_grade_comment(msg: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    clear_messages = data.get('clear_messages')
    clear_messages.append(msg.message_id)
    update_document(data.get('grade_document_id'), {"comment": msg.text}, "problems_for_support")
    await state.update_data({'clear_messages': clear_messages})

@router.callback_query(StateFilter(FSMStates.set_grade), F.data.in_(['Submit', 'Skip']))
async def bad_grade_exit(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    message_for_delete = data.get('clear_messages')
    await bot.delete_messages(call.from_user.id, message_for_delete)
    await state.set_state(FSMStates.wait_menu_click)
