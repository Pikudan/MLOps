from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List


LEXICON = {'backward': '<<',
           'forward': '>>'}
EDITOR_BUTTONS =['Delete', 'More info', 'Change']
RETURN_BUTTON = ['Return']

def create_pagination_keyboard(buttons: List, editor_buttons = True, info = None) -> InlineKeyboardMarkup:
    kb_builder = InlineKeyboardBuilder()
    if info is None:
        kb_builder.row(*[InlineKeyboardButton(
            text=LEXICON[button] if button in LEXICON else button,
            callback_data=button) for button in buttons]
        )
        if editor_buttons:
            kb_builder.row(*[InlineKeyboardButton(
                text=button,
                callback_data=button) for button in EDITOR_BUTTONS]
            )
            kb_builder.row(*[InlineKeyboardButton(
                text="Back",
                callback_data=button) for button in RETURN_BUTTON]
            )
    else:
        kb_builder.row(*[InlineKeyboardButton(
            text=LEXICON[button] if button in LEXICON else button,
            callback_data=f"{button} {info}") for button in buttons]
        )
        if editor_buttons:
            kb_builder.row(*[InlineKeyboardButton(
                text=button,
                callback_data=f"{button} {info}") for button in EDITOR_BUTTONS]
            )
            kb_builder.row(*[InlineKeyboardButton(
                text="Back",
                callback_data=f"{button} {info}") for button in RETURN_BUTTON]
            )
    return kb_builder.as_markup(resize_keyboard=True)

#МЕНЮ С КНОПКАМИ ФЕРМЕРОВ, ДОБАВИТЬ УВЕДОМЛЕНИЯ
def create_title_menu(buttons: List, info: List, count = 1):
    kb_builder = InlineKeyboardBuilder()
    for button, inf in zip(buttons, info):
        kb_builder.button(text=button, callback_data=inf)
    kb_builder.adjust(count)
    return kb_builder.as_markup(resize_keyboard=True)

def create_title_menu_resolved(buttons: List, info: List):
    kb_builder = InlineKeyboardBuilder()
    for button, inf in zip(buttons, info):
        kb_builder.row(*[InlineKeyboardButton(
            text=button[i],
            callback_data=f"{inf[i]}") for i in range(len(button))]
        )
    kb_builder.row(*[InlineKeyboardButton(
        text="Back",
        callback_data="Return")])
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=False)
