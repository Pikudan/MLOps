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
@router.error()
async def error_handler(event: ErrorEvent):
    logging.critical("Critical error caused by %s", event.exception, exc_info=True)


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

@router.callback_query(StateFilter(FSMStates.waiting_for_confirmation), F.data.startswith('Refusal'))
async def process_refusal_press(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text="Confirm or refusal this answer.",
        reply_markup=None,
        parse_mode=ParseMode.MARKDOWN
    )
    await call.message.answer(
        text="Write comments and click 'submit'",
        reply_markup=create_title_menu(["Submit", "Back"], ["Submit", "Back"]),
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(FSMStates.waiting_for_end_comment)

@router.callback_query(StateFilter(FSMStates.waiting_for_end_comment), F.data.startswith('Submit'))
async def process_submit_press(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    try:
        data = await state.get_data()
        task = data.get(call.message.chat.id)
        print(task)
        if task["count_loading"] > 0:
            await call.message.answer("Wait for previous messages to finish loading")
            return
        document_id = task["id"]
        confirmation = read_document(document_id, collection = "agronomist_confirmation_buffer")
        
        if len(confirmation["messages_id"]) == 0:
            await call.message.answer("Write a comment about the refusal")
            return
        await state.set_state(FSMStates.waiting_for_end_loading_message)
        messages_id = confirmation["messages_id"]
        for message_id in messages_id:
            agronom_messages = read_collection_with_composite_filter(
                filters = [
                    {
                        "atribut": "user_telegram_id",
                        "op": "==",
                        "value": call.message.chat.id
                    },
                    {
                        "atribut": "message_id",
                        "op": "==",
                        "value": message_id
                    }
                ],
                collection = "message_agronomist_confirmation"
            )
            for agronom_message in agronom_messages:
                if agronom_message["data"]["type"] == "image":
                    path_local = agronom_message["data"]["path_on_cloud"].replace("/", "_")
                    if os.path.exists(path_local):
                        upload_file(path_local, agronom_message["data"]["path_on_cloud"])
                        os.remove(path_local)
    except:
        await state.set_state(FSMStates.waiting_for_confirmation)
    try:
        agronom_id = call.message.chat.id
        data = await state.get_data()
        info = data.get(agronom_id)
        bot_message = await call.message.answer("Wait delete messages")
        for i in range(info["start_id"], bot_message.message_id):
            try:
                await bot.delete_message(call.message.chat.id, i)
            except TelegramBadRequest as ex:
                if ex.message == "Bad Request: message to delete not found":
                    print("All messages deleted")
        page_number, document_id, confirm_id = info['page_number'], info['document_id'], info['id']
        firebase_config = get_config()
        tz = timezone(firebase_config['timezone'])
        time = datetime.now(tz=tz)
        confirmation = read_document(confirm_id, "agronomist_confirmation_buffer")
        delete_document(confirm_id, "agronomist_confirmation_buffer")
        update_document(document_id, {"status": "refused"}, "calendar_events")
        confirmation["timestamp_submit"] = time
        confirmation["status"] = "refused"
        add_document(confirmation, "agronomist_confirmation")
        if len(download_information(call.message.chat.id)) != 0:
            if page_number > len(download_information(agronom_id)) - 1:
                page_number = len(download_information(agronom_id)) - 1
            agronom_document = DataFramePaginator(download_information(agronom_id), page_number = page_number)
            msg = event_brief_information(agronom_document)
            await call.message.answer(
                text=msg,
                reply_markup=agronom_document.get_keyboard(
                [
                    agronom_id,
                    agronom_document.get_page_number()
                ]
                ),
                parse_mode=ParseMode.MARKDOWN
            )
            del info["start_id"]
            del info["count_loading"]
            del info["id"]
            info['page_number'] = agronom_document.get_page_number()
            info['document_id'] = agronom_document.get_document_id()
            await state.update_data({agronom_id: info})
            await state.set_state(FSMStates.waiting_for_start_comment)
        else:
            menu = [f'View']
            buttons = ["View"]
            count_task =  len(download_information(agronom_id))
            await call.message.answer(
                text=text.view.format(count_task),
                reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
                parse_mode=ParseMode.MARKDOWN
            )
            await state.set_state(FSMStates.wait_menu_click)
        try:
            await bot_message.delete()
        except:
            print("error delete message")
    except:
        menu = [f'View']
        buttons = ["View"]
        count_task =  len(download_information(call.message.chat.id))
        await call.message.answer(
            text=text.view.format(count_task),
            reply_markup=create_title_menu([name for name in menu], [button for button in buttons]),
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(FSMStates.wait_menu_click)

@router.message(StateFilter(FSMStates.waiting_for_end_comment), F.media_group_id, F.content_type.in_({'photo'}))
@media_group_handler
async def album_handler(messages: List[types.Message], bot: Bot, state: FSMContext):
    '''Save group of images with caption'''
    if True:
        data = await state.get_data()
        task = data.get(messages[0].from_user.id)
        task["count_loading"] += 1
        await state.update_data({messages[0].from_user.id: task})
        document_id = task["id"]
        messages_id = messages[0].message_id
        firebase_config = get_config()
        tz=timezone(firebase_config['timezone'])
        time = datetime.now(tz=tz)
        try:
            if messages[0].caption is not None:
                add_document(
                    {
                        "user_telegram_id": messages[0].from_user.id,
                        "message_id": messages_id,
                        "message_id_chat": messages_id,
                        "type": "text",
                        "time": time,
                        "text": messages[0].caption
                    }
                    ,
                    "message_agronomist_confirmation"
                )
        except:
            print("Add document on cloud error")
        for index, msg in enumerate(messages):
            path_local = '.'.join(('_'.join(("message_agronomist_confirmation", str(msg.from_user.id), str(messages_id), str(index), time.strftime("%Y-%m-%d_%H-%M-%S")
)), 'jpg'))
            path_on_cloud = '.'.join(('/'.join(("message_agronomist_confirmation", str(msg.from_user.id), str(messages_id), str(index), time.strftime("%Y-%m-%d_%H-%M-%S")
)), 'jpg'))
            await bot.download(
                msg.photo[-1],
                destination=path_local
            )
            try:
                add_document(
                    {
                        "user_telegram_id": msg.from_user.id,
                        "message_id": messages_id,
                        "message_id_chat": msg.message_id,
                        "image_group_index": index,
                        "type": "image",
                        "time": time,
                        "path_on_cloud": path_on_cloud
                    }
                    ,
                    "message_agronomist_confirmation"
                )
            except:
                print("Upload file on cloud error")
        data = await state.get_data()
        task = data.get(messages[0].from_user.id)
        task["count_loading"] -= 1
        await state.update_data({messages[0].from_user.id: task})
        update_document_array(
            document_id = document_id,
            array_name = "messages_id",
            collection = "agronomist_confirmation_buffer",
            value = [messages_id]
        )

@router.message(StateFilter(FSMStates.waiting_for_end_comment), F.text)
async def any_text_message(message: Message, state: FSMContext):
    '''Save text message'''
    if True:
        data = await state.get_data()
        task = data.get(message.from_user.id)
        task["count_loading"] += 1
        await state.update_data({message.from_user.id: task})
        document_id = task["id"]
        firebase_config = get_config()
        tz=timezone(firebase_config['timezone'])
        time = datetime.now(tz=tz)
        try:
            add_document(
                
                {
                    "user_telegram_id": message.from_user.id,
                    "message_id": message.message_id,
                    "message_id_chat": message.message_id,
                    "type": "text",
                    "time": time,
                    "text": message.text
                }
                ,
                "message_agronomist_confirmation"
            )
        except:
            print("Add document on cloud error")
        data = await state.get_data()
        task = data.get(message.from_user.id)
        task["count_loading"] -= 1
        await state.update_data({message.from_user.id: task})

        update_document_array(
            document_id = document_id,
            array_name = "messages_id",
            collection = "agronomist_confirmation_buffer",
            value = [message.message_id]
        )

@router.message(StateFilter(FSMStates.waiting_for_end_comment), F.photo)
async def any_image_message(message: Message, bot: Bot, state: FSMContext):
    '''Save one image with caption'''
    if True:
        data = await state.get_data()
        task = data.get(message.from_user.id)
        task["count_loading"] += 1
        await state.update_data({message.from_user.id: task})
        document_id = task["id"]
        firebase_config = get_config()
        tz=timezone(firebase_config['timezone'])
        time = datetime.now(tz=tz)
        path_local = '.'.join(('_'.join(("message_agronomist_confirmation", str(message.from_user.id), str(message.message_id), time.strftime("%Y-%m-%d_%H-%M-%S"))), 'jpg'))
        path_on_cloud = '.'.join(('/'.join(("message_agronomist_confirmation", str(message.from_user.id), str(message.message_id), time.strftime("%Y-%m-%d_%H-%M-%S"))), 'jpg'))
        await bot.download(
            message.photo[-1],
            destination=path_local
        )
        try:
            add_document(
            
                {
                    "user_telegram_id": message.from_user.id,
                    "message_id": message.message_id,
                    "message_id_chat": message.message_id,
                    "type": "image",
                    "time": time,
                    "path_on_cloud": path_on_cloud
                }
                ,
                "message_agronomist_confirmation"
            )
        except:
            print("Upload file on cloud error")
        try:
            if message.caption is not None:
                add_document(
                    {
                        "user_telegram_id": message.from_user.id,
                        "message_id": message.message_id,
                        "message_id_chat": message.message_id,
                        "type": "text",
                        "time": time,
                        "text": message.caption
                    }
                    ,
                    "message_agronomist_confirmation"
                )
        except:
            print("Add document on cloud error")
        data = await state.get_data()
        task = data.get(message.from_user.id)
        task["count_loading"] -= 1
        await state.update_data({message.from_user.id: task})
        document_id = task["id"]
        update_document_array(
            document_id = document_id,
            array_name = "messages_id",
            collection = "agronomist_confirmation_buffer",
            value = [message.message_id]
        )

