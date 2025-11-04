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
from check_farmer import check_farmer

@router.error()
async def error_handler(event: ErrorEvent):
    logging.critical("Critical error caused by %s", event.exception, exc_info=True)

from aiogram.fsm.state import State, StatesGroup, default_state

@router.message(StateFilter(FSMStates.waiting_for_end_start))
@router.message(StateFilter(FSMStates.waiting_for_end_loading_message))
async def delete_message_in_this_state(message: types.Message, state: FSMContext):
    '''Do not respond until all messages from the farmer are sent'''
    try:
        await message.delete()
    except:
        print(f'Error clean {message.from_user.id} message_id: {message.message_id}')
        
@router.message(StateFilter(FSMStates.waiting_for_end_loading_message))
async def wait_loading(message: types.Message, state: FSMContext):
    await message.answer("Wait for messages to finish sending")
    try:
        await message.delete()
    except:
        print(f'Error clean {message.from_user.id} message_id: {message.message_id}')

@router.callback_query(F.data.startswith('Got it!'))
async def close_notification(call: types.CallbackQuery):
    await call.message.delete()
    
@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    logging.basicConfig(level=logging.DEBUG)
    if check_farmer(message.from_user.id):
        logging.basicConfig(level=logging.DEBUG)
        cnt_new_message = count_message(message.from_user.id)
        menu = [f'Crop Calendar', f'Add Record', f'Agronomics Support ({cnt_new_message})']
        buttons = ["Crop Calendar", "Add Record", "Support"]
        await message.answer(
            text=f'Hi, here are some things I can help with:',
            reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
            parse_mode=ParseMode.MARKDOWN
        )
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
                "value": "agrilink_farm",
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
                    "bot": "agrilink_farm",
                    "start": 1,
                    "restart": 0
                },
                collection="tracking"
            )
        



@router.callback_query(StateFilter(FSMStates.wait_menu_click), F.data.startswith('Support'))
async def support_menu(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.edit_text(
        text.support.format(call.from_user.full_name),
        reply_markup=create_menu(['Existing problems', 'New problem', 'Back'], count=2),
        parse_mode=ParseMode.MARKDOWN

    )
    await state.set_state(FSMStatus.support)
    await state.update_data(
        {
            call.message.chat.id: {"message": []}
        }
    )

@router.callback_query(StateFilter(FSMStatus.support), F.data.startswith('Back'))
async def back_to_start(call: types.CallbackQuery, state: FSMContext):
    cnt_new_message = count_message(call.from_user.id)
    menu = [f'Crop Calendar', f'Add Record', f'Agronomics Support ({cnt_new_message})']
    buttons = ["Crop Calendar", "Add Record", "Support"]
    await call.message.edit_text(
        text=f'Hi, here are some things I can help with:',
        reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(FSMStates.wait_menu_click)


