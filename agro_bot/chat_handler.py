from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Bot, types
from firebase import upload_file, add_document, read_collection_with_composite_filter, update_document, get_config, download_file, update_document_array
from collection_editer import (download_information, merge_and_sortes_message_about_problems)
import os
from aiogram.types import FSInputFile, Message
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import StateFilter
from aiogram import F
from pagination_kb import create_title_menu, create_title_menu_resolved
import pandas as pd
from text_message import msg_for_support
import pytz
from available_farmers import count_messag_farmer
from router import router
from states import FSMStatus


@router.callback_query(F.data.startswith('Chat'))
async def chating_menu(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    df = download_information('problems_for_support', int(data.get('farmer_id')))
    print(df)
    if df.empty:
        await call.message.edit_text(
            text='You have no existing problems ✅',
            reply_markup=create_title_menu(['Back'], ['Return'])
        )
    else:
        buttons = []
        for index, row in df.iterrows():
            button = row.to_dict()
            buttons.append((button['name'], button['number_of_messages_from_farmer']))
        print(buttons)
        msg = "You have the following problems:"
        await call.message.edit_text(
            text= msg,
            reply_markup=create_title_menu_resolved([[f'{button[0]} ({button[1]})', f'Resolve'] for button in buttons],
                                        [[button[0], f'~{button[0]}'] for button in buttons]),
        )
        await state.set_state(FSMStatus.chating)

@router.callback_query(StateFilter(FSMStatus.chating), F.data.startswith('~'))
async def resolved_problem(call: types.CallbackQuery, state: FSMContext):
    name_problem = call.data[1:]
    data = await state.get_data()
    farmer_id = int(data.get('farmer_id'))
    info = read_collection_with_composite_filter(
        collection = "problems_for_support",
        filters = [
            {
                "atribut": "user_telegram_id",
                "op": "==",
                "value": farmer_id,
            },
            {
                "atribut": "name",
                "op": "==",
                "value": name_problem,
            }
        ]
    )
    update_document(document_id=info[0]["document_id"], new_data={"status": "resolved", "notify": "farmer"}, collection="problems_for_support")
    data = await state.get_data()
    df = download_information('problems_for_support', int(data.get('farmer_id')))
    
    record_msg = read_collection_with_composite_filter(
        'record_message_support',
        [{'atribut': 'name', 'op': '==', 'value': data.get('problem')},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': data.get('farmer_id')},
        {'atribut': 'status', 'op': '==', 'value': 'open'}]
        )
    update_document(
        record_msg[0]['document_id'],
        {'status': 'resolved'},
        'record_message_support'
    )

    if df.empty:
        await call.message.edit_text(
            text='You have no open problems',
            reply_markup=create_title_menu(['Back'], ['Return'])
        )
        await state.set_state(FSMStatus.selected_farmer)
    else:
        buttons = []
        max_length = 0
        for index, row in df.iterrows():
            button = row.to_dict()
            buttons.append((button['name'], button['number_of_messages_from_farmer']))
        msg = "You have the following problems:"
        await call.message.edit_text(
            text= msg,
            reply_markup=create_title_menu_resolved([[f'{button[0]} ({button[1]})', f'Resolved'] for button in buttons],
                                        [[button[0], f'~{button[0]}'] for button in buttons]),
        )
        await state.set_state(FSMStatus.chating)


@router.callback_query(StateFilter(FSMStatus.chating), F.data.startswith('Return'))
async def return_from_chating_list(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await call.message.edit_text("What can I help you with?", reply_markup=create_title_menu(['Crop Calendar', f"View the Conversation ({count_messag_farmer(data.get('farmer_id'))})", 'Back'], ['Calendar', 'Chat', 'Return']))
    await state.set_state(FSMStatus.selected_farmer)
        
@router.callback_query(StateFilter(FSMStatus.chating), ~F.data.startswith('Back'))
async def chating(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    farmer_id = int(data.get('farmer_id'))
    await state.update_data({'problem': call.data})
    problem = read_collection_with_composite_filter(
        'problems_for_support',
        [{'atribut': 'name', 'op': '==', 'value': call.data},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': farmer_id},
        {'atribut': 'status', 'op': '==', 'value': 'open'}]
    )
    task = call.data    
    message_chat = merge_and_sortes_message_about_problems(call.data, farmer_id, problem[0]["data"]["time"])
    msg_for_delete = await call.message.edit_text('Here is a message history for you', parse_mode=ParseMode.MARKDOWN)
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
            if doc['person'] == 'farmer' and doc['status'] == 'new':
                update_document(
                    doc['document_id'],
                    {'status': 'read'},
                    "telegram_message_from_farmer_for_support",
                )
                problem = read_collection_with_composite_filter(
                'problems_for_support',
                [{'atribut': 'name', 'op': '==', 'value': task},
                 {'atribut': 'user_telegram_id', 'op': '==', 'value': farmer_id},
                 {'atribut': 'status', 'op': '==', 'value': 'open'}]
                )
                values = problem[0]['data']['number_of_messages_from_farmer']
                document_id = problem[0]["document_id"]
                update_document(
                    document_id,
                    {"number_of_messages_from_farmer": values - 1},
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
                        "message_for_agronom",
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
    bot_message = await call.message.answer(text="*To continue this conversation, just type in a new a message.*", reply_markup=create_title_menu(['Back'], ['Back']), parse_mode=ParseMode.MARKDOWN)
    message_for_delete.append(bot_message.message_id)
    await state.update_data({'message_for_delete': message_for_delete})

@router.message(StateFilter(FSMStatus.chating), F.text)
async def any_text_message(message: types.Message, bot: Bot, state: FSMContext):
    '''Save text message'''
    if True:
        data = await state.get_data()
        message_for_delete = data.get('message_for_delete')
        message_for_delete.append(message.message_id)
        await state.update_data({'message_for_delete': message_for_delete, 'response': 'Yes'})
        task = data.get('problem')
        farmer_id = int(data.get('farmer_id'))
        problem = read_collection_with_composite_filter(
        'problems_for_support',
        [{'atribut': 'name', 'op': '==', 'value': task},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': farmer_id},
        {'atribut': 'status', 'op': '==', 'value': 'open'}]
        )
        values = problem[0]['data']['number_of_messages_from_agro']
        document_id = problem[0]["document_id"]
        update_document(
            document_id,
            {"number_of_messages_from_agro": values + 1},
            "problems_for_support",
        )
        try:
            add_document(
                {
                    "user_telegram_id": farmer_id,
                    "message_id": message.message_id,
                    "message_id_chat": message.message_id,
                    "type": "text",
                    "time": message.date,
                    "text": message.text,
                    "problem": task,
                    "status": 'new'
                }
                ,
                "telegram_message_from_support_for_farmer"
            )
        except:
            print("Add document on cloud error")
    
    
@router.message(StateFilter(FSMStatus.chating), F.photo)
async def any_image_message(msg: Message, bot: Bot, state: FSMContext):
    # Save one image with caption
    if True:
        firebase_config = get_config()
        tz=pytz.timezone(firebase_config['timezone'])
        path_local = '.'.join(
            (
                '_'.join(
                    (
                        "telegram_message_from_support_for_farmer",
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
                        "telegram_message_from_support_for_farmer",
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
        farmer_id = int(data.get('farmer_id'))
                
        try:
            add_document(
            
                {
                    "user_telegram_id": farmer_id,
                    "message_id": msg.message_id,
                    "message_id_chat": msg.message_id,
                    "type": "image",
                    "time": msg.date,
                    "path_on_cloud": path_on_cloud,
                    "problem": task,
                    "status": 'new'
                }
                ,
                "telegram_message_from_support_for_farmer"
            )
        except:
            print("Upload file on cloud error")
        try:
            if msg.caption is not None:
                add_document(
                    {
                        "user_telegram_id": farmer_id,
                        "message_id": msg.message_id,
                        "message_id_chat": msg.message_id,
                        "type": "text",
                        "time": msg.date,
                        "text": msg.caption,
                        "problem": task,
                        "status": 'new'
                    }
                    ,
                    "telegram_message_from_support_for_farmer"
                )
        except:
            print("Add document on cloud error")
        problem = read_collection_with_composite_filter(
        'problems_for_support',
        [{'atribut': 'name', 'op': '==', 'value': task},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': farmer_id},
        {'atribut': 'status', 'op': '==', 'value': 'open'}]
        )
        values = problem[0]['data']['number_of_messages_from_agro']
        document_id = problem[0]["document_id"]
        count_new = 1 if msg.caption is None else 2
        update_document(
            document_id,
            {"number_of_messages_from_agro": values + count_new},
            "problems_for_support",
         )

#ДОПИСЫВАЕМ
@router.callback_query(StateFilter(FSMStatus.chating), F.data.startswith('Back'))
async def return_from_chating_list(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    farmer_id = int(data.get('farmer_id'))
    
    if data.get('response') == 'Yes':
        record_msg = read_collection_with_composite_filter(
        'record_message_support',
        [{'atribut': 'name', 'op': '==', 'value': data.get('problem')},
        {'atribut': 'user_telegram_id', 'op': '==', 'value': farmer_id},
        {'atribut': 'status', 'op': '==', 'value': 'open'}]
        )
        if record_msg[0]['data']['last_reply_from'] == 'farmer':
            update_document_array(
                document_id = record_msg[0]['document_id'],
                array_name = 'time_from_agronomist',
                value = [call.message.date],
                collection = 'record_message_support'
            )
            update_document(
                record_msg[0]['document_id'],
                {'last_reply_from': 'agronomist'},
                'record_message_support'
            )
    
    task = data.get('problem')
    df = download_information('problems_for_support', farmer_id)
    problem = read_collection_with_composite_filter(
    'problems_for_support',
    [{'atribut': 'name', 'op': '==', 'value': task},
    {'atribut': 'user_telegram_id', 'op': '==', 'value': farmer_id},
    {'atribut': 'status', 'op': '==', 'value': 'open'}]
    )
    await state.update_data({'response': []})
    values = problem[0]['data']['number_of_messages_from_agro']
    document_id = problem[0]["document_id"]
    if values > 0:
        update_document(
            document_id,
            {"notify": "farmer"},
            "problems_for_support",
         )
    if df.empty:
        await call.message.answer(
            text='You have no open problems',
            reply_markup=create_title_menu(['Back'], ['Return'])
        )
        await state.set_state(FSMStatus.selected_farmer)
    else:
        buttons = []
        
        for index, row in df.iterrows():
            button = row.to_dict()
            buttons.append((button['name'], button['number_of_messages_from_farmer']))
        
        msg = "You have the following problems:"
        await call.message.answer(
            text= msg,
            reply_markup=create_title_menu_resolved([[f'{button[0]} ({button[1]})', f'Resolved'] for button in buttons],
                                        [[button[0], f'~{button[0]}'] for button in buttons]),
        )
        await state.set_state(FSMStatus.chating)
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    print(message_for_delete, call.from_user.id)
    try:
        await bot.delete_messages(call.from_user.id, message_for_delete)
    except:
        print(f'Error clean ')