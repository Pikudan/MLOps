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

from pytz import timezone
import requests
from kb import create_pagination_keyboard, create_title_menu
import kb, text
from pagination_info import DataFramePaginator
import pandas as pd
from text_message import event_brief_information, event_full_information, event_without_confirm, msg_for_support
from router import router
from states import FSMStates, FSMStatus, FSMAddRecord
from check_datetime import is_valid_datetime
from datetime import datetime
from count_message import count_message

@router.message(StateFilter(FSMAddRecord.wait_date), ~F.text)
@router.message(StateFilter(FSMAddRecord.wait_name), ~F.text)
async def wrong_change_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(message.message_id)
    bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
    message_for_delete.append(bot_message.message_id)
    await state.update_data({'message_for_delete': message_for_delete})


@router.callback_query(StateFilter(FSMStates.wait_menu_click), F.data.startswith('Add Record'))
async def process_add_record_click(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_text(
        text='In one word (maximum two), what is the nature of your record?\n*For example:* Irrigation failure',
        reply_markup=create_menu(['Back']),
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(FSMAddRecord.wait_name)
    await state.update_data({'message_for_delete': []})
    await state.update_data({'start_message': [call.message.message_id]})

@router.callback_query(StateFilter(FSMAddRecord.wait_describe), F.data.startswith('Back'))
@router.callback_query(StateFilter(FSMAddRecord.wait_name), F.data.startswith('Back'))
async def back_to_start_from_wait_name(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    cnt_new_message = count_message(call.from_user.id)
    menu = [f'Crop Calendar', f'Add Record', f'Agronomics Support ({cnt_new_message})']
    buttons = ["Crop Calendar", "Add Record", "Support"]
    data = await state.get_data()
    await call.message.edit_text(
        text=f'Hi, here are some things I can help with:',
        reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
        parse_mode=ParseMode.MARKDOWN
    )
    message_for_delete = data.get('message_for_delete')
    try:
        await bot.delete_messages(call.from_user.id, message_for_delete)
    except:
        print(f'Error clean')

    await state.set_state(FSMStates.wait_menu_click)
    
@router.callback_query(StateFilter(FSMAddRecord.wait_date), F.data.startswith('Back'))
async def back_to_start_from_wait_date(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    cnt_new_message = count_message(call.from_user.id)
    menu = [f'Crop Calendar', f'Add Record', f'Agronomics Support ({cnt_new_message})']
    buttons = ["Crop Calendar", "Add Record", "Support"]
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    await call.message.answer(
        text=f'Hi, here are some things I can help with:',
        reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
        parse_mode=ParseMode.MARKDOWN
    )
    try:
        await bot.delete_messages(call.from_user.id, message_for_delete)
    except:
        print(f'Error clean')
   
    await state.set_state(FSMStates.wait_menu_click)
    
@router.message(StateFilter(FSMAddRecord.wait_name), F.text)
async def create_record(message: types.Message, state: FSMContext, bot: Bot):
    df = download_information(int(message.from_user.id), 'records')
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    
    if len(df) and message.text in list(df["name"]):
        bot_message = await message.answer('''Enter another name, it's already taken''')
        message_for_delete.append(bot_message.message_id)
        message_for_delete.append(message.message_id)
        await state.update_data({'message_for_delete': message_for_delete})
        return
    await state.update_data({'name': message.text})
    
    bot_message = await message.answer(
        text=f'What time to set? Enter in the format of YYYY-MM-DD (example 2024-12-05)',
        reply_markup=create_menu(['Back']),
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(FSMAddRecord.wait_date)
    message_for_delete = data.get('message_for_delete')
    start_message = data.get('start_message')
    try:
        await bot.delete_messages(message.from_user.id, start_message)
    except:
        print(f'Error clean')
    try:
        await bot.delete_messages(message.from_user.id, message_for_delete)
    except:
        print(f'Error clean')
    try:
        await message.delete()
    except:
        print(f'Error clean')
    await state.update_data({'message_for_delete': [bot_message.message_id]})


@router.message(StateFilter(FSMAddRecord.wait_date), F.text)
async def enter_date(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    if is_valid_datetime(message.text):
        datetime_object = datetime.strptime(message.text, "%Y-%m-%d")
        message_for_delete = data.get('message_for_delete')
        bot_message = await message.answer(
            text=text.start_new_record,
            reply_markup=create_title_menu(['Submit', 'Back'], ['Submit', 'Cancel']),
            parse_mode=ParseMode.MARKDOWN
        )
        try:
            await bot.delete_messages(message.from_user.id, message_for_delete)
            await message.delete()
        except:
            print(f'Error clean')
        record_name = data.get('name')
        record_id = add_document(
            {
                "name": record_name,
                "timestamp_created": message.date,
                "time": datetime_object,
                "user_telegram_id": message.from_user.id
            },
            "records"
        )
        await state.update_data({'record_id': record_id})
        await state.update_data({'message_for_delete': []})
        await state.set_state(FSMAddRecord.wait_describe)
    else:
        bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
        message_for_delete = data.get('message_for_delete')
        message_for_delete.append(bot_message.message_id)
        message_for_delete.append(message.message_id)
        await state.update_data({'message_for_delete': message_for_delete})
     
    
@router.callback_query(StateFilter(FSMAddRecord.wait_describe), F.data.startswith('Cancel'))
async def back_from_describe(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    cnt_new_message = count_message(call.from_user.id)
    menu = [f'Crop Calendar', f'Add Record', f'Agronomics Support ({cnt_new_message})']
    buttons = ["Crop Calendar", "Add Record", "Support"]
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    try:
        await bot.delete_messages(call.from_user.id, message_for_delete)
    except:
        print(f'Error clean')
    await call.message.edit_text(
        text=f'Hi, here are some things I can help with:',
        reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(FSMStates.wait_menu_click)
    
    record_id= data.get('record_id')
    messages_record = read_collection_with_composite_filter(
        "telegram_message_from_farmer_for_record",
        [{'atribut': 'record_id', 'op': '==', 'value': record_id}]
    )
    for message_record in messages_record:
        delete_document(message_record["document_id"], collection="telegram_message_from_farmer_for_record")
        if message_record["data"]["type"] == "image":
            delete_file(message_record["data"]["path_on_cloud"])
    
    delete_document(record_id, 'records')
    await state.update_data({'message_for_delete': []})

@router.callback_query(StateFilter(FSMAddRecord.wait_describe), F.data.startswith('Submit'))
async def create_describe(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    
    record_id= data.get('record_id')
    messages_record = read_collection_with_composite_filter(
        "telegram_message_from_farmer_for_record",
        [{'atribut': 'record_id', 'op': '==', 'value': record_id}]
    )
    if len(messages_record) == 0:
        bot_message = await call.message.answer(f'I didn’t quite catch the description of the problem. Please provide more details.')
        message_for_delete = data.get('message_for_delete')
        message_for_delete.append(bot_message.message_id)
        await state.update_data({'message_for_delete': message_for_delete})
        return
        
    else:
        await call.message.edit_text(
            text=f"Thank you for your input!",
            reply_markup=create_menu(['Back'])
        )
        message_for_delete = data.get('message_for_delete')
        try:
            await bot.delete_messages(call.from_user.id, message_for_delete)
        except:
            print(f'Error clean')
        await state.update_data({'message_for_delete': []})

@router.message(StateFilter(FSMAddRecord.wait_describe), F.text)
async def describe(msg: types.Message, state: FSMContext, bot: Bot):
    firebase_config = get_config()
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(msg.message_id)
    await state.update_data({'message_for_delete': message_for_delete})
    record_id = data.get('record_id')
    try:
        add_document(
            {
                "user_telegram_id": msg.from_user.id,
                "message_id": msg.message_id,
                "message_id_chat": msg.message_id,
                "type": "text",
                "time": msg.date,
                "text": msg.text,
                "record_id": record_id,
            }
            ,
            "telegram_message_from_farmer_for_record"
        )
    except:
        print("Add document on cloud error")
        
@router.message(StateFilter(FSMAddRecord.wait_describe), F.photo)
async def any_image_message(msg: Message, bot: Bot, state: FSMContext):
    # Save one image with caption
    firebase_config = get_config()
    tz=timezone(firebase_config['timezone'])
    path_local = '.'.join(
        (
            '_'.join(
                (
                    "telegram_message_from_farmer_for_record",
                    str(msg.from_user.id),
                    str(msg.message_id),
                    str(msg.date)
                )
            ),
            'jpg'
        )
    )
    path_on_cloud = '.'.join(
        (
            '/'.join(
                (
                    "telegram_message_from_farmer_for_record",
                    str(msg.from_user.id),
                    str(msg.message_id),
                    str(msg.date.strftime("%Y-%m-%d_%H-%M-%S"))
                )
            ),
            'jpg'
        )
    )
    await bot.download(
        msg.photo[-1],
        destination=path_local
    )
    upload_file(path_local, path_on_cloud)
    if os.path.exists(path_local):
        os.remove(path_local)
    firebase_config = get_config()
    data = await state.get_data()
    record_id = data.get('record_id')
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(msg.message_id)
    await state.update_data({'message_for_delete': message_for_delete})
    try:
        add_document(
            {
                "user_telegram_id": msg.from_user.id,
                "message_id": msg.message_id,
                "message_id_chat": msg.message_id,
                "type": "image",
                "time": msg.date,
                "path_on_cloud": path_on_cloud,
                "record_id": record_id,
            }
            ,
            "telegram_message_from_farmer_for_record"
        )
    except:
        print("Upload file on cloud error")
    try:
        if msg.caption is not None:
            add_document(
                {
                    "user_telegram_id": msg.from_user.id,
                    "message_id": msg.message_id,
                    "message_id_chat": msg.message_id,
                    "type": "text",
                    "time": msg.date,
                    "text": msg.caption,
                    "record_id": record_id,
                }
                ,
                "telegram_message_from_farmer_for_record"
            )
    except:
        print("Add document on cloud error")
