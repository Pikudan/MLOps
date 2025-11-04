from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    user_commands = [BotCommand(command="/restart",  description="restart")]
    await bot.set_my_commands(user_commands)
