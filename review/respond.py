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


@router.callback_query(StateFilter(FSMStates.waiting_for_start_comment), F.data.startswith('Respond'))
async def process_respond_press(call: types.CallbackQuery, state: FSMContext):
    '''The event with the closest end time is selected. Send data from one event for confirmation.
    Args:
        message:
            message from user
        state:
            state for bot
    Raises:
        Too much agronomists with the tg_id message.from_user.id in collection agronomists
    '''
    try:
        agronom_id = call.message.chat.id
        call_id = call.message.message_id
        data = await state.get_data()
        info = data.get(agronom_id)
        page_number, document_id =  info['page_number'], info['document_id']
        agronom_document = DataFramePaginator(download_information(agronom_id), page_number = page_number)
        task = read_document(document_id=document_id, collection="calendar_events")
        content = as_list(
            as_marked_section(
                Bold("Information:"),
                task["info"],
                ),
            as_marked_section(
                Bold("Title:"),
                task["title"]
                ),
        )
        await call.message.answer(**content.as_kwargs())
        await call.message.delete()
        farmer_response = read_collection_with_composite_filter(
            collection = "farmer_response",
            filters = [
                {
                    "atribut": "calendar_event_id",
                    "op": "==",
                    "value": document_id
                }
            ],
            order = {
                "atribut": "timestamp_submit",
                "desc": True
                }
        )
        if len(farmer_response) == 0:
            farmer_messages = []
            await call.message.answer("The farmer didn't send messages")
        else:
            bot_message = await call.message.answer("wait a moment messages are sent from the farmer")
            farmer_messages_id_on_task = farmer_response[0]["data"]["messages_id"]
            farmer_messages = read_collection_with_composite_filter(
                collection = "message_farmer_response",
                filters = [
                    {
                        "atribut": "user_telegram_id",
                        "op": "==",
                        "value": task["farmer_tg_id"]
                    },
                    {
                        "atribut": "message_id",
                        "op": "in",
                        "value": farmer_messages_id_on_task
                    }
                ]
            )
            farmer_messages_data = [message["data"] for message in farmer_messages]
            df = pd.DataFrame.from_dict(farmer_messages_data)
            farmer_messages_id = sorted(list(set(df["message_id"])))
            for farmer_message_id in farmer_messages_id:
                farmer_message = df[df["message_id"] == farmer_message_id]
                try:
                    farmer_message = farmer_message.sort_values(["message_id", "image_group_index"], na_position='first')
                    local_paths = []
                    if (farmer_message[0: 1]["type"] == "text").all():
                        album_builder = MediaGroupBuilder(
                            caption=farmer_message[0: 1]['text'].item()
                        )
                        for i in range(1, len(farmer_message)):
                            path_on_cloud = farmer_message[i: i + 1]["path_on_cloud"]
                            path_local = '.'.join(('_'.join(("message_for_agronomist", str(call.message.chat.id), str(call.message.date.strftime("%Y-%m-%d_%H-%M-%S")), str(i))), 'jpg'))
                            try:
                                download_file(path_on_cloud.item(), path_local)
                                album_builder.add(
                                    type="photo",
                                    media=FSInputFile(path_local)
                                )
                                local_paths.append(path_local)
                            except:
                                print("Error send to {call.message.chat.id}: {path_on_cloud.item()}")
                    else:
                        album_builder = MediaGroupBuilder()
                        for i in range(len(farmer_message)):
                            path_on_cloud = farmer_message[i: i + 1]["path_on_cloud"]
                            path_local = '.'.join(
                                (
                                    '_'.join(
                                        (
                                            "message_for_agronomist",
                                            str(call.message.chat.id),
                                            str(call.message.date.strftime("%Y-%m-%d_%H-%M-%S")),
                                            str(i)
                                        )
                                    ),
                                    'jpg'
                                )
                            )
                            try:
                                download_file(path_on_cloud.item(), path_local)
                                album_builder.add(
                                    type="photo",
                                    media=FSInputFile(path_local)
                                )
                                local_paths.append(path_local)
                            except:
                                print("Error send to {call.message.chat.id}: {path_on_cloud.item()}")
                    await call.message.answer_media_group(media=album_builder.build())
                    for path_local in local_paths:
                        if os.path.exists(path_local):
                            os.remove(path_local)
                except:
                    if len(farmer_message) == 1:
                        if (farmer_message[0: 1]["type"] == "text").all():
                            await call.message.answer(farmer_message[0: 1]["text"].item())
                        elif (farmer_message[0: 1]["type"] == "image").all():
                            path_on_cloud = farmer_message[0: 1]["path_on_cloud"]
                            path_local = '.'.join(
                                (
                                    '_'.join(
                                        (
                                            "message_for_agronomist",
                                            str(call.message.chat.id),
                                            str(call.message.date.strftime("%Y-%m-%d_%H-%M-%S"))
                                        )
                                    ),
                                    'jpg'
                                )
                            )
                            try:
                                download_file(path_on_cloud.item(), path_local)
                                image_from_pc = FSInputFile(path_local)
                                result = await call.message.answer_photo(image_from_pc)
                                if os.path.exists(path_local):
                                    os.remove(path_local)
                            except:
                                print("Error send message to {call.message.from_user.id}: {path_on_cloud.item()}")
                    elif len(farmer_message) == 2:
                        if (farmer_message[0: 1]["type"] == "text").all():
                            text = farmer_message[0: 1]["text"].item()
                            path_on_cloud = farmer_message[1: 2]["path_on_cloud"]
                        elif (farmer_message[0: 1]["type"] == "image").all():
                            text = farmer_message[1: 2]["text"].item()
                            path_on_cloud = farmer_message[0: 1]["path_on_cloud"]
                        
                            path_local = '.'.join(
                                (
                                    '_'.join(
                                        (
                                            "message_for_agronomist",
                                            str(call.message.chat.id),
                                            str(call.message.date.strftime("%Y-%m-%d_%H-%M-%S"))
                                        )
                                    ),
                                    'jpg'
                                )
                            )
                        try:
                            download_file(path_on_cloud.item(), path_local)
                            image_from_pc = FSInputFile(path_local)
                            await call.message.answer_photo(image_from_pc, caption=text)
                            if os.path.exists(path_local):
                                os.remove(path_local)
                        except:
                            print("Error send message to {message.from_user.id}: {path_on_cloud.item()}")
            try:
                bot_message.delete()
            except:
                print(f'Error clean {call.message.chat.id} message_id: {bot_message.message.message_id}')
        firebase_config = get_config()
        tz=timezone(firebase_config['timezone'])
        time = datetime.now(tz=tz)
        add_document(
            {
                "calendar_event_id": document_id,
                "agronomist_tg_id": task["agronomist_tg_id"],
                "farmer_tg_id": task["farmer_tg_id"],
                "timestamp_creates": time,
                "messages_id": [],
            },
            "agronomist_confirmation_buffer"
        )
        confirmations = read_collection_with_composite_filter(
            collection = "agronomist_confirmation_buffer",
            filters = [
                {
                    "atribut": "calendar_event_id",
                    "op": "==",
                    "value": document_id
                }
            ],
            order = {
                "atribut": "timestamp_creates",
                "desc": True
                }
        )
        info["count_loading"] = 0
        info["id"] = confirmations[0]["document_id"]
        info["start_id"] = call_id
        await state.update_data({agronom_id: info})
        type_message = await call.message.answer(
            text=f"Is evidence provided sufficient to confirm the completion of the task?\n\nOtherwise, reject the submission and specify what actions are needed to meet the criteria for this task.",
            reply_markup=create_title_menu(["Confirm", "Refusal", "Back"], ["Confirm", "Refusal", "Back"]),
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(FSMStates.waiting_for_confirmation)
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


@router.callback_query(StateFilter(FSMStates.waiting_for_end_comment), F.data.startswith('Back'))
@router.callback_query(StateFilter(FSMStates.waiting_for_confirmation), F.data.startswith('Back'))
async def go_to_calendar(call: types.CallbackQuery,  bot: Bot, state: FSMContext):
    '''Go to start. Cancel comment and confirmation.
    Args:
        message:
            message from user
        state:
            state for bot
    '''
    data = await state.get_data()
    try:
        task = data.get(call.message.chat.id)
        if task["count_loading"] > 0:
            await call.message.answer("Wait for previous messages to finish loading")
            return
    except:
        print(f'state no contain {message.from_user.id}')
    bot_message = await call.message.answer("Wait delete messages")
    try:
        await state.set_state(FSMStates.waiting_for_end_cancel_comment)
        confirmations = read_collection_with_composite_filter(
            collection = "agronomist_confirmation_buffer",
            filters = [
                {
                    "atribut": "agronomist_tg_id",
                    "op": "==",
                    "value": call.message.chat.id
                }
            ],
            order = {
                "atribut": "timestamp_creates",
                "desc": True
            }
        )
        
        for confirmation in confirmations:
            messages_id = confirmation["data"]["messages_id"]
            
            for message_id in messages_id:
                agronom_messages = read_collection_with_composite_filter(
                    filters = [
                        {
                            "atribut": "user_telegram_id",
                            "op": "==",
                            "value": confirmation["data"]["farmer_tg_id"]
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
                        path_local = agronom_message["path_on_cloud"].replace("/", "_")
                        if os.path.exists(path_local):
                            os.remove(path_local)
                        delete_document(agronom_message["document_id"], collection = "message_agronomist_confirmation")
                    elif agronom_message["data"]["type"] == "text":
                        delete_document(agronom_message["document_id"], collection = "message_agronomist_confirmation")
            delete_document(confirmation["document_id"], collection = "agronomist_confirmation_buffer")
    except:
        print("Error delete confirmation agronom {call.message.chat.id}")
        await state.set_state(FSMStates.waiting_for_confirmation)
    data = await state.get_data()
    info = data.get(call.message.chat.id)
    
    for i in range(info["start_id"], bot_message.message_id):
        try:
            await bot.delete_message(call.message.chat.id, i)
        except TelegramBadRequest as ex:
            if ex.message == "Bad Request: message to delete not found":
                print("All messages deleted")
    agronom_id = call.message.chat.id
    page_number, document_id =  info['page_number'], info['document_id']
    try:
        if len(download_information(agronom_id)) != 0:
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
            try:
                await bot_message.delete()
            except:
                print("error delete message")
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
            try:
                await bot_message.delete()
            except:
                print("error delete message")
            await state.set_state(FSMStates.wait_menu_click)
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
        try:
            await call.message.delete()
        except:
            print("error delete message")
