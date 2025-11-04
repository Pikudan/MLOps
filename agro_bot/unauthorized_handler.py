from aiogram import types
from aiogram.filters import StateFilter
from pagination_kb import create_title_menu
from router import router
from states import FSMStatus

@router.message(StateFilter(FSMStatus.unauthorized_agronomist))
async def unauthorized_agronomist_bye(message: types.Message):
    await message.answer(
        text='Sorry, you are not on the list of authorized agronomists. Bye!',
        reply_markup=create_title_menu(['Back'],['Return']))