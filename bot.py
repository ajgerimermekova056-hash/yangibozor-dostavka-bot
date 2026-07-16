import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("👋 Добро пожаловать в Yangibozor Dostavka!")

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
