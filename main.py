import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from handlers.profile_handler import register_profile_handlers
from handlers.help_handler import register_help_handlers
from utils.database import init_db
from utils.osu_api import OsuAPI

TELEGRAM_TOKEN = "insert_your_tg_token"
OSU_CLIENT_ID = "insert_your_osu_id"
OSU_CLIENT_SECRET = "insert_your_osu_secret"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

osu_api = OsuAPI(OSU_CLIENT_ID, OSU_CLIENT_SECRET)

async def main():
    init_db()
    
    register_profile_handlers(dp, osu_api)
    register_help_handlers(dp)
    
    print("[!] the bot was launched successfully without any problems.")
    print("[?] made with love, fourtech & notsordixs")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())