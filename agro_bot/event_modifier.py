from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import Bot
from firebase import get_config
from collection_editer import get_information_to_agronomist, update_information, to_DataFrame_information, is_valid_datetime
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import StateFilter
from aiogram import F
from datetime import datetime
from pagination_kb import create_title_menu
from pagination_info import DataFramePaginator
from checking_id import check_agronomist
from agronomist_selection_list import TYPE
from datetime import datetime, timedelta
import pytz
from router import router
from states import FSMStatus


@router.callback_query(StateFilter(FSMStatus.selected_farmer), F.data.startswith('Change'))
async def change_event(call: types.CallbackQuery, state: FSMContext):
    df = DataFramePaginator(to_DataFrame_information(check_agronomist(call.from_user.id)))
    df = df.get_DataFrame()
    data = get_information_to_agronomist(df)
    names = data + ['RETURN']
    buttons = data + ['Back']
    data = await state.get_data()
    await call.message.edit_text(
        text=f'Select what you would like to change',
        reply_markup=create_title_menu(buttons, names)
        )
    await state.set_state(FSMStatus.change_event)

@router.callback_query(StateFilter(FSMStatus.change_event), F.data.startswith('type'))
async def select_change_type(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text=f'Select what type of task you want to install',
        reply_markup=create_title_menu(TYPE + ['Back'], TYPE + ['RETURN'])
    )

@router.callback_query(StateFilter(FSMStatus.change_event), F.data.in_(TYPE))
async def change_type(call: types.CallbackQuery, state: FSMContext):
    df = DataFramePaginator(to_DataFrame_information(check_agronomist(call.from_user.id)))
    data = await state.get_data()
    document_id = data.get('document_id')
    new_data = {'type': call.data}
    df = update_information(df.get_DataFrame(), document_id, new_data)
    await call.message.edit_text(
        text="Type changed! Click on the *Back* button to return to the list",
        reply_markup=create_title_menu(['Back'],['Return']),
        parse_mode=ParseMode.MARKDOWN)
    await state.set_state(FSMStatus.selected_farmer)

@router.callback_query(StateFilter(FSMStatus.change_event), F.data.startswith('title'))
async def wait_change_title(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text='Enter new title',
        reply_markup=create_title_menu(['Back'],['Return']))
    data = await state.get_data()
    await state.set_state(FSMStatus.change_title)
    await state.update_data({'message_for_delete': [call.message.message_id]})

@router.message(StateFilter(FSMStatus.change_title), F.text)
async def title_change(message: types.Message, bot: Bot, state: FSMContext):
    data = await state.get_data()
    document_id = data.get('document_id')
    new_data = {'title': message.text}
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(message.message_id)
    df = DataFramePaginator(to_DataFrame_information(check_agronomist(message.from_user.id)))
    
    await message.answer(
        text="Title changed! Click on the *Back* button to return to the list",
        reply_markup=create_title_menu(['Back'],['Return']),
        parse_mode=ParseMode.MARKDOWN)
    try:
        await bot.delete_messages(message.from_user.id, message_for_delete)
    except:
        print(f'Error clean')
    df = update_information(df.get_DataFrame(), document_id, new_data)
    await state.set_state(FSMStatus.selected_farmer)
    await state.update_data({'farmer_id': data.get('farmer_id'), 'page_number': data.get('page_number'), 'document_id':data.get('document_id')})

@router.message(StateFilter(FSMStatus.change_title), ~F.text)
@router.message(StateFilter(FSMStatus.change_info), ~F.text)
@router.message(StateFilter(FSMStatus.change_begin_date), ~F.text)
@router.message(StateFilter(FSMStatus.change_end_date), ~F.text)
@router.message(StateFilter(FSMStatus.add_event), ~F.text)
@router.message(StateFilter(FSMStatus.change_notify_about_begin_before_days), ~F.text)
@router.message(StateFilter(FSMStatus.add_begin_date), ~F.text)
@router.message(StateFilter(FSMStatus.add_end_date), ~F.text)
@router.message(StateFilter(FSMStatus.add_info), ~F.text)
async def wrong_change_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(message.message_id)
    bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
    message_for_delete.append(bot_message.message_id)
    await state.update_data({'message_for_delete': message_for_delete})

@router.callback_query(StateFilter(FSMStatus.change_event), F.data.startswith('info'))
async def wait_change_title(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text='Enter new info',
        reply_markup=create_title_menu(['Back'],['Return']))
    data = await state.get_data()
    await state.set_state(FSMStatus.change_info)
    await state.update_data({'message_for_delete': [call.message.message_id]})

@router.message(StateFilter(FSMStatus.change_info), F.text)
async def info_change(message: types.Message, bot: Bot, state: FSMContext):
    df = DataFramePaginator(to_DataFrame_information(check_agronomist(message.from_user.id)))
    data = await state.get_data()
    document_id = data.get('document_id')
    new_data = {'info': message.text}
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(message.message_id)

    df = update_information(df.get_DataFrame(), document_id, new_data)
    await message.answer(
        text="Info changed! Click on the *Back* button to return to the list",
        reply_markup=create_title_menu(['Back'],['Return']),
        parse_mode=ParseMode.MARKDOWN)
    try:
        await bot.delete_messages(message.from_user.id, message_for_delete)
    except:
        print(f'Error clean')
    await state.set_state(FSMStatus.selected_farmer)

@router.callback_query(StateFilter(FSMStatus.change_event), F.data.startswith('timestamp_begin'))
async def wait_change_title(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text='Enter new date and time like YYYY-MM-DD\n(*Example*: 2024-02-11)',
        reply_markup=create_title_menu(['Back'],['Return']),
        parse_mode=ParseMode.MARKDOWN)
    data = await state.get_data()
    await state.set_state(FSMStatus.change_begin_date)
    await state.update_data({'message_for_delete': [call.message.message_id]})

@router.message(StateFilter(FSMStatus.change_begin_date), F.text)
async def begin_date_change(message: types.Message, bot: Bot, state: FSMContext):
    df = DataFramePaginator(to_DataFrame_information(check_agronomist(message.from_user.id)))
    data = await state.get_data()
    document_id = data.get('document_id')
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(message.message_id)
    if is_valid_datetime(message.text):

        datetime_object = datetime.strptime(message.text, "%Y-%m-%d")
        timestamp_obj = datetime_object.replace(hour=10, minute=0)
        new_data = {'timestamp_begin': timestamp_obj}
        new_information = update_information(df.get_DataFrame(), document_id, new_data)
        await message.answer(
            text="Info changed! Click on the *Back* button to return to the list",
            reply_markup=create_title_menu(['Back'],['Return']),
            parse_mode=ParseMode.MARKDOWN)
        try:
            await bot.delete_messages(message.from_user.id, message_for_delete)
        except:
            print(f'Error clean')
        await state.set_state(FSMStatus.selected_farmer)
    else:
        bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
        message_for_delete.append(bot_message.message_id)
        await state.update_data({'message_for_delete': message_for_delete})

@router.callback_query(StateFilter(FSMStatus.change_event), F.data.startswith('timestamp_end'))
async def wait_change_title(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text='Enter new date and time like YYYY-MM-DD\n(*Example*: 2024-02-11)',
        reply_markup=create_title_menu(['Back'],['Return']),
        parse_mode=ParseMode.MARKDOWN)
    data = await state.get_data()
    await state.set_state(FSMStatus.change_end_date)
    await state.update_data({'message_for_delete': [call.message.message_id]})

@router.message(StateFilter(FSMStatus.change_end_date), F.text)
async def end_date_change(message: types.Message, bot: Bot, state: FSMContext):
    df = DataFramePaginator(to_DataFrame_information(check_agronomist(message.from_user.id)))
    data = await state.get_data()
    document_id = data.get('document_id')
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(message.message_id)
    if is_valid_datetime(message.text):
        firebase_config = get_config()
        tz=pytz.timezone(firebase_config['timezone'])
        datetime_object = datetime.strptime(message.text, "%Y-%m-%d")
        datetime_object = tz.localize(datetime_object)
        timestamp_obj = datetime_object.replace(hour=20, minute=0)
        new_data = {'timestamp_end': timestamp_obj}
        data = df.get_DataFrame()
        time_begin = data[data['document_id'] == document_id].loc[:, 'timestamp_begin'].iloc[0]
        if datetime_object < time_begin + timedelta(days=3):
            bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
            message_for_delete.append(bot_message.message_id)
        else:

            new_data = update_information(df.get_DataFrame(), document_id, new_data)

            await message.answer(
                text="Info changed! Click on the *Back* button to return to the list",
                reply_markup=create_title_menu(['Back'],['Return']),
                parse_mode=ParseMode.MARKDOWN)
            try:
                await bot.delete_messages(message.from_user.id, message_for_delete)
            except:
                print(f'Error clean')
            await state.set_state(FSMStatus.selected_farmer)
    else:
        bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
        message_for_delete.append(bot_message.message_id)
        await state.update_data({'message_for_delete': message_for_delete})

@router.callback_query(StateFilter(FSMStatus.change_event), F.data.startswith('notify_for_days'))
async def wait_notify_about_begin_before_days(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Enter new days')
    data = await state.get_data()
    await state.set_state(FSMStatus.change_notify_about_begin_before_days)
    await state.update_data({'message_for_delete': [call.message.message_id]})

@router.message(StateFilter(FSMStatus.change_notify_about_begin_before_days), F.text)
async def notify_about_begin_before_days_change(message: types.Message, bot: Bot, state: FSMContext):
    df = DataFramePaginator(to_DataFrame_information(check_agronomist(message.from_user.id)))
    data = await state.get_data()
    document_id = data.get('document_id')
    message_for_delete = data.get('message_for_delete')
    message_for_delete.append(message.message_id)
    if message.text.isdigit():

        new_data = {'notify_for_days':int(message.text)}
        df = update_information(df.get_DataFrame(), document_id, new_data)
        await message.answer(
            text="Notify changed! Click on the *Back* button to return to the list",
            reply_markup=create_title_menu(['Back'],['Return']),
            parse_mode=ParseMode.MARKDOWN)
        
        try:
            await bot.delete_messages(message.from_user.id, message_for_delete)
        except:
            print(f'Error clean')
        await state.set_state(FSMStatus.selected_farmer)
    else:
        bot_message = await message.answer(text='Sorry, you entered something wrong. Try again')
        message_for_delete.append(bot_message.message_id)
        await state.update_data({'message_for_delete': message_for_delete})