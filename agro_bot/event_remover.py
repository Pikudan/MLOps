from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import types
from firebase import delete_document
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import StateFilter
from aiogram import F
from pagination_kb import create_title_menu
from states import FSMStatus
from router import router
from handlers import calendar

@router.callback_query(StateFilter(FSMStatus.selected_farmer), F.data.startswith('Delete'))
async def deletion_confirmation(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    farmer_id, page_number, document_id = data.get('farmer_id'), data.get('page_number'), data.get('document_id')
    await call.message.edit_text(
        text='Are you sure you want to delete the event?',
        reply_markup=create_title_menu(['Yes', 'No'],['Yes', 'No']),
        parse_mode=ParseMode.MARKDOWN)
    await state.set_state(FSMStatus.delete_event)
    await state.update_data({'farmer_id': data.get('farmer_id'), 'page_number': data.get('page_number'), 'document_id':data.get('document_id')})

@router.callback_query(StateFilter(FSMStatus.delete_event), F.data.startswith('Yes'))
async def event_delete(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    document_id = data.get('document_id')
    delete_document(document_id, 'calendar_events')
    await call.message.edit_text(
        text="Document deleted. Click on the *Back* button to return to the list",
        reply_markup=create_title_menu(['Back'],['Return']),
        parse_mode=ParseMode.MARKDOWN)
    await state.set_state(FSMStatus.selected_farmer)
    await state.update_data({'farmer_id': data.get('farmer_id'), 'page_number': data.get('page_number'), 'document_id':data.get('document_id')})

@router.callback_query(StateFilter(FSMStatus.delete_event), F.data.startswith('No'))
async def Return_from_delete_event(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(FSMStatus.selected_farmer)
    data = await state.get_data()
    await state.update_data({'farmer_id': data.get('farmer_id'), 'page_number': data.get('page_number'), 'document_id':data.get('document_id')})
    return await calendar(call, state)
