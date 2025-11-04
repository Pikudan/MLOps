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
    read_collection_with_composite_filter, update_document_array
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
from count_message import count_message



@router.callback_query(StateFilter(FSMStatus.support), F.data.startswith('Existing problems'))
async def process_exciting_problems_click(call: types.CallbackQuery, state: FSMContext):
    df = download_information(int(call.from_user.id), 'problems_for_support')
    buttons = []
    if df.empty:
         await call.message.edit_text(
             text="You have no existing problems ✅",
             reply_markup=create_menu(['Back'])
         )
    else:
        for index, row in df.iterrows():
            button = row.to_dict()
            buttons.append((button['name'], button['number_of_messages_from_agro']))
        await call.message.edit_text(
            text=f"Below you can find the list of your existing problems. The numbers in the bracket indicate how many new messages you received from our agronomists.\n\n*Click on the problem to continue the conversation.*",
            reply_markup=create_menu([f'{button[0]} ({button[1]})' for button in buttons] + ['Back'],
                                info=[button[0] for button in buttons] + ['Back']),
            parse_mode=ParseMode.MARKDOWN
        )

    await state.set_state(FSMStatus.start_chating)

@router.callback_query(StateFilter(FSMStatus.start_chating), F.data.startswith('Back'))
async def back_support_menu(call: types.CallbackQuery, bot: Bot, state: FSMContext):
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

@router.callback_query(StateFilter(FSMStatus.chating), F.data.startswith('Back'))
async def back_from_chating(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    df = download_information(int(call.from_user.id), 'problems_for_support')
    data = await state.get_data()
    farmer_id  = int(call.from_user.id)
    task = data.get('problem')

    if data.get('response') == 'Yes':
        record_msg = read_collection_with_composite_filter(
        'record_message_support',
        [{'atribut': 'name', 'op': '==', 'value': task},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': farmer_id},
        {'atribut': 'status', 'op': '==', 'value': 'open'}]
        )
        if record_msg[0]['data']['last_reply_from'] == 'agronomist':
            update_document_array(
                document_id = record_msg[0]['document_id'],
                array_name = 'time_from_farmer',
                value = [call.message.date],
                collection = 'record_message_support'
            )
            update_document(
                record_msg[0]['document_id'],
                {'last_reply_from': 'farmer'},
                'record_message_support'
            )

    await state.update_data({'response': []})
    
    problem = read_collection_with_composite_filter(
    'problems_for_support',
    [{'atribut': 'name', 'op': '==', 'value': task},
    {'atribut': 'user_telegram_id', 'op': '==', 'value': farmer_id},
    {'atribut': 'status', 'op': '==', 'value': 'open'}]
    )
    values = problem[0]['data']['number_of_messages_from_farmer']
    document_id = problem[0]["document_id"]
    if values > 0:
        update_document(
            document_id,
            {"notify": "agronom"},
            "problems_for_support",
         )
    buttons = []
    for index, row in df.iterrows():
        button = row.to_dict()
        buttons.append((button['name'], button['number_of_messages_from_agro']))
    await call.message.answer(
        text=f"Below you can find the list of your existing problems. The numbers in the bracket indicate how many new messages you received from our agronomists.\n\n*Click on the problem to continue the conversation.*",
        reply_markup=create_menu([f'{button[0]} ({button[1]})' for button in buttons] + ['Back'],
                                 info=[button[0] for button in buttons] + ['Back']),
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(FSMStatus.start_chating)
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    #message_for_delete.append(call.message.message_id)
    await bot.delete_messages(call.from_user.id, message_for_delete)
    '''
    for message_id in task["message"]:
        try:
            await bot.delete_messages(call.from_user.id, message_for_delete)
        except:
            print(f'Error clean {call.message.chat.id} message_id: {message_id}')
    '''
    await state.update_data(
        {
            call.message.chat.id: {"message": []}
        }
    )

@router.callback_query(StateFilter(FSMStatus.start_chating))
async def chating(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(FSMStatus.chating)

    data = await state.get_data()
    problem = read_collection_with_composite_filter(
        'problems_for_support',
        [{'atribut': 'name', 'op': '==', 'value': call.data},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': call.from_user.id},
        {'atribut': 'status', 'op': '==', 'value': 'open'}]
    )
    task = call.data
    message_chat = merge_and_sortes_message_about_problems(call.data, int(call.from_user.id), problem[0]["data"]["time"])
    msg_for_delete =  await call.message.edit_text('Here is a message history for you', parse_mode=ParseMode.MARKDOWN)
    await state.update_data({'problem': call.data})
    message_for_delete = [msg_for_delete.message_id]
    if not message_chat.empty:
        text_messeges, days_messages = msg_for_support(message_chat)
        flag = True
        for index, row in message_chat.iterrows():
            if index in days_messages.keys():
                if flag:
                    date =  days_messages[index]
                    bot_message = await call.message.answer(text=', '.join((date, f'*{task}*')), parse_mode=ParseMode.MARKDOWN)
                    flag = False
                else:
                    bot_message = await call.message.answer(text=days_messages[index], parse_mode=ParseMode.MARKDOWN)
                message_for_delete.append(bot_message.message_id)
            doc = row.to_dict()
            if doc['person'] == 'agronomist' and doc['status'] == 'new':
                update_document(
                    doc['document_id'],
                    {'status': 'read'},
                    "telegram_message_from_support_for_farmer",
                )
                problem = read_collection_with_composite_filter(
                'problems_for_support',
                [{'atribut': 'name', 'op': '==', 'value': task},
                 {'atribut': 'user_telegram_id', 'op': '==', 'value': call.from_user.id},
                 {'atribut': 'status', 'op': '==', 'value': 'open'}]
                )
                values = problem[0]['data']['number_of_messages_from_agro']
                document_id = problem[0]["document_id"]
                update_document(
                    document_id,
                    {"number_of_messages_from_agro": values - 1},
                    "problems_for_support",
                )
            if doc["type"] == "text":
                bot_message = await call.message.answer(text=text_messeges[index], parse_mode=ParseMode.MARKDOWN)
                
            elif doc["type"] == "image":
                path_on_cloud = row["path_on_cloud"]
                path_local = '.'.join(
                (
                    '_'.join(
                        (
                        "message_for_farmer",
                        str(call.message.chat.id),
                        str(call.message.date.strftime("%Y-%m-%d_%H-%M-%S"))
                        )
                    ),
                    'jpg'
                )
                )
                download_file(path_on_cloud, path_local)
                image_from_pc = FSInputFile(path_local)
                bot_message = await call.message.answer_photo(image_from_pc, caption=text_messeges[index], parse_mode=ParseMode.MARKDOWN)
                if os.path.exists(path_local):
                    os.remove(path_local)
                
            message_for_delete.append(bot_message.message_id)
        bot_message = await call.message.answer(text="*To continue this conversation, just type in a new a message.*", reply_markup=create_menu(['Back'], count=1), parse_mode=ParseMode.MARKDOWN)
        message_for_delete.append(bot_message.message_id)
    await state.update_data({'message_for_delete': message_for_delete})


@router.message(StateFilter(FSMStatus.chating), F.text)
async def any_text_message(msg: Message, state: FSMContext, bot: Bot):
    firebase_config = get_config()
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(msg.message_id)
    await state.update_data({'message_for_delete': message_for_delete, 'response': 'Yes'})
    task = data.get('problem')
    problem = read_collection_with_composite_filter(
        'problems_for_support',
        [{'atribut': 'name', 'op': '==', 'value': task},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': msg.from_user.id},
        {'atribut': 'status', 'op': '==', 'value': 'open'}]
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
    
@router.message(StateFilter(FSMStatus.chating), F.photo)
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
    await state.update_data({'message_for_delete': message_for_delete, 'response': 'Yes'})
    task = data.get('problem')
    problem = read_collection_with_composite_filter(
    'problems_for_support',
    [{'atribut': 'name', 'op': '==', 'value': task},
    {'atribut': 'user_telegram_id', 'op': '==', 'value': msg.from_user.id},
    {'atribut': 'status', 'op': '==', 'value': 'open'}]
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
