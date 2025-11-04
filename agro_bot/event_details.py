from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram import types
from collection_editer import to_DataFrame_information
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters import StateFilter
from aiogram import F
from pagination_kb import create_title_menu
from pagination_info import DataFramePaginator
from text_message import event_full_information
from checking_id import check_agronomist
from states import FSMStatus
from router import router

@router.callback_query(StateFilter(FSMStatus.selected_farmer), F.data.startswith('More'))
async def get_more_info_event(call: types.CallbackQuery, state: FSMContext):
    df = DataFramePaginator(to_DataFrame_information(check_agronomist(call.from_user.id)))
    df = df.get_DataFrame()
    data = await state.get_data()
    document_id = data.get('document_id')
    more_info = DataFramePaginator(df[df['document_id'] == document_id])
    msg = event_full_information(more_info)
    
    try:
        await call.message.edit_text(
        text=msg,
        reply_markup=create_title_menu(['Back'],['Return']),
        parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(FSMStatus.return_from_more_info)
    except:
        print(msg)
