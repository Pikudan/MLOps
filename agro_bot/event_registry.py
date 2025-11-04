from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from firebase import add_document, get_config
from collection_editer import to_DataFrame_information, is_valid_datetime
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import StateFilter
from aiogram import F
from datetime import datetime
from pagination_kb import create_title_menu
from pagination_info import DataFramePaginator
from text_message import event_brief_information
from checking_id import check_agronomist
from agronomist_selection_list import TYPE
from datetime import datetime, timedelta
import pytz
from router import router
from states import FSMStatus

@router.callback_query(StateFilter(FSMStatus.add_event), F.data.startswith('Return'))
@router.callback_query(StateFilter(FSMStatus.add_type), F.data.startswith('Return'))
@router.callback_query(StateFilter(FSMStatus.add_info), F.data.startswith('Return'))
@router.callback_query(StateFilter(FSMStatus.add_notify), F.data.startswith('Return'))
@router.callback_query(StateFilter(FSMStatus.add_begin_date), F.data.startswith('Return'))
@router.callback_query(StateFilter(FSMStatus.add_begin_date), F.data.startswith('Return'))
@router.callback_query(StateFilter(FSMStatus.add_end_date), F.data.startswith('Return'))
async def back_from_add_event(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    try:
        await bot.delete_messages(call.from_user.id, message_for_delete)
    except:
        print(f'Error clean')
    
    df = DataFramePaginator(to_DataFrame_information(check_agronomist(call.from_user.id)))
    farmer_id, page_number = data.get('farmer_id'), data.get('page_number')
    farmer_document = DataFramePaginator(df[farmer_id], page_number = page_number)
    if farmer_document.get_DataFrame().empty:
        
        msg = "There are no events here yet. Don't want to add an event?"
        await call.message.edit_text(
            text=msg,
            reply_markup=create_title_menu(['Back', 'Add'],['Return', 'Add']),
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(FSMStatus.return_from_empty_file)

    else:
        msg = event_brief_information(farmer_document)
        await call.message.edit_text(
            text=msg,
            reply_markup=farmer_document.get_keyboard(info=[farmer_id, farmer_document.get_page_number()]),
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(FSMStatus.selected_farmer)
        await state.update_data({'page_number': farmer_document.get_page_number(), 'document_id':farmer_document.get_document_id()})




@router.callback_query(StateFilter(FSMStatus.selected_farmer), F.data.startswith('Add'))
@router.callback_query(StateFilter(FSMStatus.return_from_empty_file), F.data.startswith('Add'))
async def add_event(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    await call.message.edit_text(
        text=f'Of course! I will need more details from you to add the task to the farmer’s calendar.\n\n*Please follow the instructions below.*',
        reply_markup=create_title_menu(['Back'],['Return']),
        parse_mode=ParseMode.MARKDOWN
    )
   
    bot_message = await call.message.answer(
        text=f'What’s the title of the new event? (use a maximum of three words)'
    )
    message_for_delete = data.get('message_for_delete')
    try:
        await bot.delete_messages(call.from_user.id, message_for_delete)
    except:
        print(f'Error clean')
    await state.update_data({'message_add_event_delete': [call.message.message_id]})
    await state.update_data({'message_for_delete': [bot_message.message_id]})
    await state.set_state(FSMStatus.add_event)

@router.message(StateFilter(FSMStatus.add_event), F.text)
async def enter_title(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await state.update_data({'title': message.text.strip()})
    message_for_delete = data.get('message_for_delete')
    bot_message = await message.answer(
        text='What level of confirmation would you like to set?',
        reply_markup=create_title_menu(TYPE, TYPE)
    )
    try:
        await bot.delete_messages(message.from_user.id, message_for_delete)
        await message.delete()
    except:
        print(f'Error clean ')
    await state.update_data({'message_for_delete': [bot_message.message_id]})
    await state.set_state(FSMStatus.add_type)
    
@router.callback_query(StateFilter(FSMStatus.add_type), F.data.in_(TYPE))
async def enter_type(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await state.update_data({'type': call.data})
    await state.set_state(FSMStatus.add_info)
    await call.message.edit_text(
        text=f'Please provide more information about the nature of the task.\n\nTry and include things like a) preferred time of the day during which the farmer should be performing the task b) area of the farm the task should be performed on c) if it requires inputs (seeds, pesticides), how much should be used per square meter or what input to use',
        reply_markup=None
    )
    
@router.message(StateFilter(FSMStatus.add_info), F.text)
async def enter_info(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    await state.set_state(FSMStatus.add_notify)
    message_for_delete = data.get('message_for_delete')
    await state.update_data({'info': message.text.strip()})
    bot_message = await message.answer(
        text=f'How many days in advance would you like us to notify the farmer before starting the task? Provide a number (example 4)',
    )
    try:
        await bot.delete_messages(message.from_user.id, message_for_delete)
        await message.delete()
    except:
        print(f'Error clean ')
    await state.update_data({'message_for_delete': [bot_message.message_id]})
    
@router.message(StateFilter(FSMStatus.add_notify), F.text)
async def enter_notify(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    if message.text.strip().isdigit():
        await state.set_state(FSMStatus.add_begin_date)
        await state.update_data({'notify_for_days':int(message.text.strip())})
        bot_message = await message.answer(
            text=f'When would you like the farmer to start? Enter in the format of YYYY-MM-DD (example 2024-12-05)',
            parse_mode=ParseMode.MARKDOWN
        )
        message_for_delete = data.get('message_for_delete')
        try:
            await bot.delete_messages(message.from_user.id, message_for_delete)
            await message.delete()
        except:
            print(f'Error clean ')
        await state.update_data({'message_for_delete': [bot_message.message_id]})
    else:
        bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
        message_for_delete = data.get('message_for_delete')
        message_for_delete.append(bot_message.message_id)
        message_for_delete.append(message.message_id)
        await state.update_data({'message_for_delete': message_for_delete})
    
@router.message(StateFilter(FSMStatus.add_begin_date), F.text)
async def enter_begin_date(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    if is_valid_datetime(message.text):
        await state.set_state(FSMStatus.add_end_date)
        datetime_object = datetime.strptime(message.text, "%Y-%m-%d")
        await state.update_data({'timestamp_begin': datetime_object})
        bot_message = await message.answer(
            text='By what date is it important for the farmer to complete the task? Enter in the YYYY-MM-DD format (example 2024-12-05)',
            parse_mode=ParseMode.MARKDOWN
        )
        message_for_delete = data.get('message_for_delete')
        try:
            await bot.delete_messages(message.from_user.id, message_for_delete)
            await message.delete()
        except:
            print(f'Error clean')
        await state.update_data({'message_for_delete': [bot_message.message_id]})
    else:
        bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
        message_for_delete = data.get('message_for_delete')
        message_for_delete.append(bot_message.message_id)
        message_for_delete.append(message.message_id)
        await state.update_data({'message_for_delete': message_for_delete})

@router.message(StateFilter(FSMStatus.add_end_date), F.text)
async def enter_end_date(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    if is_valid_datetime(message.text):
        datetime_object = datetime.strptime(message.text, "%Y-%m-%d")
        firebase_config = get_config()
        tz=pytz.timezone(firebase_config['timezone'])
        datetime_object = tz.localize(datetime_object)
        time_begin = data.get('timestamp_begin')
        time_begin = tz.localize(time_begin)
        if datetime_object < time_begin + timedelta(days=3):
            bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
            message_for_delete = data.get('message_for_delete')
            message_for_delete.append(bot_message.message_id)
            await state.update_data({'message_for_delete': message_for_delete})
        else:
            date_begin = data.get('timestamp_begin')
            date_begin = date_begin.replace(hour=10, minute=0)
            datetime_object = datetime_object.replace(hour=20, minute=0)
            doc = {
                'title': data.get('title'),
                'agronomist_tg_id': message.from_user.id, 
                'farmer_tg_id': data.get('farmer_id'),
                'info': data.get('info'),
                'notify_for_days': data.get('notify_for_days'),
                'status': 'creation',
                'timestamp_begin': date_begin,
                'timestamp_creates': message.date,
                'timestamp_end': datetime_object,
                'type': data.get('type')
            }
            doc_id = add_document(doc, collection='calendar_events')
            await state.update_data({'doc_add_id': doc_id})
            await message.answer(
                text=f'The task was created successfully! We will notify the farmer about your changes. Press *Back* to return to the farmer’s calendar. ',
                reply_markup=create_title_menu(['Back'],['Return']),
                parse_mode=ParseMode.MARKDOWN)
            message_for_delete = data.get('message_for_delete')
            message_add_event = data.get('message_add_event_delete')
            try:
                await bot.delete_messages(message.from_user.id, message_add_event)
                await bot.delete_messages(message.from_user.id, message_for_delete)
                await message.delete()
            except:
                print(f'Error clean')
            await state.set_state(FSMStatus.back_from_add_event)
    else:
        bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
        message_for_delete = data.get('message_for_delete')
        message_for_delete.append(bot_message.message_id)
        message_for_delete.append(message.message_id)
        await state.update_data({'message_for_delete': message_for_delete})
        await state.set_state(FSMStatus.add_end_date)



@router.callback_query(StateFilter(FSMStatus.back_from_add_event),F.data.startswith('Return'))
async def chating_menu(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    df = DataFramePaginator(to_DataFrame_information(check_agronomist(call.from_user.id)))
    farmer_id, doc_id = data.get('farmer_id'), data.get('doc_add_id')
    df = df[farmer_id]
    if df.empty:
        msg = "There are no events here yet. Don't want to add an event?"
        await call.message.edit_text(
            text=msg,
            reply_markup=create_title_menu(['Back', 'Add'],['Return', 'Add']),
            parse_mode=ParseMode.MARKDOWN
        )
        
    else:
        doc_ids = list(df["document_id"])
        if doc_id not in doc_ids:
            farmer_document = DataFramePaginator(df, page_number = 0)
        else:
            farmer_document = DataFramePaginator(df, page_number = doc_ids.index(doc_id))
        msg = event_brief_information(farmer_document)
        await call.message.edit_text(
            text=msg,
            reply_markup=farmer_document.get_keyboard(info=[farmer_id, farmer_document.get_page_number()]),
            parse_mode=ParseMode.MARKDOWN
        )
        await state.update_data({'page_number': farmer_document.get_page_number(), 'document_id':farmer_document.get_document_id()})
    await state.set_state(FSMStatus.selected_farmer)