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
from states import FSMStates, FSMStatus, FSMAddRecord
from count_message import count_message


@router.callback_query(StateFilter(FSMStatus.support), F.data.startswith('New problem'))
async def process_new_problem_click(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await call.message.edit_text(
        text='In one word (maximum two), what is the nature of your problem?\n*For example:* Irrigation failure',
        reply_markup=create_menu(['Back']),
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(FSMStatus.create_problem)
    await state.update_data({'message_for_delete': [call.message.message_id]})



@router.callback_query(StateFilter(FSMStatus.create_problem), F.data.startswith('Back'))
async def back_support_menu(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.answer(
        text.support.format(call.from_user.full_name),
        reply_markup=create_menu(['Existing problems', 'New problem', 'Back'], count=2),
        parse_mode=ParseMode.MARKDOWN
    )
    try:
        data = await state.get_data()
        message_for_delete = data.get('message_for_delete')
        await bot.delete_messages(call.from_user.id, message_for_delete)
    except:
        print("error back")
    await state.set_state(FSMStatus.support)
    await state.update_data(
        {
            call.message.chat.id: {"message": []}
        }
    )
    
@router.message(StateFilter(FSMStatus.create_problem), F.text)
async def create_problem(message: types.Message, state: FSMContext, bot: Bot):
    df = download_information(int(message.from_user.id), 'problems_for_support')
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    last_msg = ' '
    await state.update_data({'last_msg': last_msg})
    if len(df) and message.text in list(df["name"]):
        bot_message = await message.answer('''Enter another name, it's already taken''')
        message_for_delete.append(bot_message.message_id)
        message_for_delete.append(message.message_id)
        await state.update_data({'message_for_delete': message_for_delete})
        return
    doc_id = add_document({
        'user_telegram_id': message.from_user.id,
        'number_of_messages_from_agro': 0,
        'number_of_messages_from_farmer':0,
        'name': message.text,
        'time': message.date,
        'status': "create",
        'notify': "nobody"
        },
        collection='problems_for_support'
    )
    await state.set_state(FSMStatus.wait_describe)
    
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(message.message_id)

    message_date = message.date
    month_name = message_date.strftime("%B")
    day = message_date.day
    msg_for_delete = await message.answer(
        text= f'*{month_name} {day}, {message.text}*',
        parse_mode=ParseMode.MARKDOWN
    )
    bot_message = await message.answer(
        text=text.start_new_problem,
        reply_markup=create_title_menu(['Submit', 'Back'], ['Submit', 'Cancel']),
        parse_mode=ParseMode.MARKDOWN
    )
    await bot.delete_messages(message.from_user.id, message_for_delete)
    await state.update_data(
        {
            'document_id': doc_id,
            'problem': message.text,
            'message_for_delete': [msg_for_delete.message_id]
        }
    )

@router.callback_query(StateFilter(FSMStatus.wait_describe), F.data.startswith('Back'))
async def back_support_menu_from_describe(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.edit_text(
        text.support.format(call.from_user.full_name),
        reply_markup=create_menu(['Existing problems', 'New problem', 'Back'], count=2),
        parse_mode=ParseMode.MARKDOWN

    )
    
    try:
        data = await state.get_data()
        message_for_delete = data.get('message_for_delete')
        print(message_for_delete)
        await bot.delete_messages(call.from_user.id, message_for_delete)
    except:
        print("error back")
    await state.set_state(FSMStatus.support)
    await state.update_data(
        {
            call.message.chat.id: {"message": []}
        }
    )
    
@router.callback_query(StateFilter(FSMStatus.wait_describe), F.data.startswith('Cancel'))
async def back_from_describe(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    await call.message.edit_text(
        text.support.format(call.from_user.full_name),
        reply_markup=create_menu(['Existing problems', 'New problem', 'Back'], count=2),
        parse_mode=ParseMode.MARKDOWN

    )
    data = await state.get_data()
    task = data.get('problem')
    messages_task = read_collection_with_composite_filter(
        "telegram_message_from_farmer_for_support",
        [{'atribut': 'name', 'op': '==', 'value': task},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': call.from_user.id},
        {'atribut': 'status', 'op': '==', 'value': 'new'}]
    )
    for message_task in messages_task:
        delete_document(message_task["document_id"], collection="telegram_message_from_farmer_for_support")
        if message_task["data"]["type"] == "image":
            delete_file(message_task["data"]["path_on_cloud"])
    problem = read_collection_with_composite_filter(
        'problems_for_support',
        [{'atribut': 'name', 'op': '==', 'value': task},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': call.from_user.id},
        {'atribut': 'status', 'op': '==', 'value': 'create'}]
    )
    delete_document(problem[0]["document_id"], 'problems_for_support')

    try:
        data = await state.get_data()
        message_for_delete = data.get('message_for_delete')
        print(message_for_delete)
        await bot.delete_messages(call.from_user.id, message_for_delete)
    except:
        print("error back")
    await state.set_state(FSMStatus.support)
    await state.update_data(
        {
            call.message.chat.id: {"message": []}
        }
    )



@router.callback_query(StateFilter(FSMStatus.wait_describe), F.data.startswith('Submit'))
async def create_describe(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(call.message.message_id)
    last_msg = data.get('last_msg')
    if last_msg == ' ':
        msg_for_del = await call.message.answer(f'I didn’t quite catch the description of the problem. Please provide more details.')
        message_for_delete.append(msg_for_del.message_id)
    else:
        await call.message.answer(
            text=f"Thank you for your input!\nOur agronomists will get back to you as soon as they're free to process your request.",
            reply_markup=create_menu(['Back'])

        )
        task = data.get('problem')
        problem = read_collection_with_composite_filter(
            'problems_for_support',
            [{'atribut': 'name', 'op': '==', 'value': task},
            {'atribut': 'user_telegram_id', 'op': '==', 'value': call.from_user.id},
            {'atribut': 'status', 'op': '==', 'value': 'create'}]
        )
        document_id = problem[0]["document_id"]
        update_document(
            document_id,
            {"status": "open", "notify": "agronom"},
            "problems_for_support",
        )
        doc_id = add_document({
            'user_telegram_id': call.from_user.id,
            'name': data.get('problem'),
            'time_from_farmer': [call.message.date],
            'time_from_agronomist': [],
            'last_reply_from': 'farmer',
            'status': 'open',
            'notify': "nobody"
            },
            collection='record_message_support'
        )
        await bot.delete_messages(call.from_user.id, message_for_delete)
        await state.update_data(
            {
                'message_for_delete': []
            }
        )

@router.message(StateFilter(FSMStatus.wait_describe), F.text)
async def describe(msg: types.Message, state: FSMContext, bot: Bot):
    firebase_config = get_config()
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(msg.message_id)
    await state.update_data({'message_for_delete': message_for_delete, 'last_msg': msg.text})
    task = data.get('problem')
    problem = read_collection_with_composite_filter(
        'problems_for_support',
        [{'atribut': 'name', 'op': '==', 'value': task},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': msg.from_user.id},
        {'atribut': 'status', 'op': '==', 'value': 'create'}]
    )
    values = problem[0]['data']['number_of_messages_from_farmer']
    document_id = problem[0]["document_id"]
    increment_value(
        document_id,
        "number_of_messages_from_farmer",
        1,
        "problems_for_support",
    )
    try:
        add_document(
            {
                "user_telegram_id": msg.from_user.id,
                "message_id": msg.message_id,
                "message_id_chat": msg.message_id,
                "type": "text",
                "time": msg.date,
                "text": msg.text,
                "problem": task,
                "status": 'new'
            }
            ,
            "telegram_message_from_farmer_for_support"
        )
    except:
        print("Add document on cloud error")
        
@router.message(StateFilter(FSMStatus.wait_describe), F.photo)
async def any_image_message(msg: Message, bot: Bot, state: FSMContext):
    # Save one image with caption
    firebase_config = get_config()
    tz=timezone(firebase_config['timezone'])
    path_local = '.'.join(
        (
            '_'.join(
                (
                    "telegram_message_from_farmer_for_support",
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
                    "telegram_message_from_farmer_for_support",
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
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(msg.message_id)
    await state.update_data({'message_for_delete': message_for_delete})
    task = data.get('problem')
    problem = read_collection_with_composite_filter(
    'problems_for_support',
    [{'atribut': 'name', 'op': '==', 'value': task},
    {'atribut': 'user_telegram_id', 'op': '==', 'value': msg.from_user.id},
    {'atribut': 'status', 'op': '==', 'value': 'create'}]
    )
    values = problem[0]['data']['number_of_messages_from_farmer']
    document_id = problem[0]["document_id"]
        
    try:
        add_document(
            {
                "user_telegram_id": msg.from_user.id,
                "message_id": msg.message_id,
                "message_id_chat": msg.message_id,
                "type": "image",
                "time": msg.date,
                "path_on_cloud": path_on_cloud,
                "problem": task,
                "status": 'new'
            }
            ,
            "telegram_message_from_farmer_for_support"
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
                    "problem": task,
                    "status": 'new'
                }
                ,
                "telegram_message_from_farmer_for_support"
            )
    except:
        print("Add document on cloud error")
    count_new = 1 if msg.caption is None else 2
    increment_value(
        document_id,
        "number_of_messages_from_farmer",
        count_new,
        "problems_for_support",
    )
