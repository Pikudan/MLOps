from aiogram import Bot
from firebase import read_collection_with_composite_filter, update_document, get_config
from aiogram.enums.parse_mode import ParseMode
from datetime import datetime
from pagination_kb import create_title_menu
from datetime import datetime
import pytz

async def notify_problem(bot: Bot):
    
    notify_problems = read_collection_with_composite_filter(
        collection = "problems_for_support",
        filters = [
            {
                "atribut": "notify",
                "op": "==",
                "value": "agronom"
            },
            {
                "atribut": "status",
                "op": "==",
                "value": "open"
            }
        ]
    )
    
    notify_text =  '''Hi {0}, the farmer {1} has responded to you about *{2}*, *{3}*. Please, respond at your earliest convenience.\n\n⚠️ If you need more time, experience technical difficulties, or can no longer continue the conversation, contact us as soon as possible.'''
    firebase_config = get_config()
    tz = pytz.timezone(firebase_config['timezone'])
    time = datetime.now(tz=tz).strftime("%d %B %Y")
    for notify_problem in notify_problems:
        farmer_id = notify_problem["data"]["user_telegram_id"]
        problem_name = notify_problem["data"]["name"]
        farmer2agronomists = read_collection_with_composite_filter(
            collection = "agronomists",
            filters = [
                {
                    "atribut": "available_farmers",
                    "op": "array_contains",
                    "value": farmer_id
                },
            ]
        )
        for agronomist in farmer2agronomists:
            agronom_name = agronomist["data"]["personal_info"]["name"]
            try:
                await bot.send_message(text=notify_text.format(agronom_name, farmer_id, problem_name, time), reply_markup=create_title_menu(["Got it!"], ["Got it!"]), chat_id=agronomist["data"]["tg_id"], parse_mode=ParseMode.MARKDOWN)
                update_document(notify_problem["document_id"], {"notify": "nobody"}, "problems_for_support")
            except:
                print("Problem with chat. Telegram id: {}".format(agronomist["data"]["tg_id"]))