import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

# Токен вашего бота от @BotFather
TOKEN = "8942590041:AAHw4DHaN8-0TU6qP8CUf2dSKC76rsA6eSw"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# Определение состояний для пошаговой формы (FSM)
class OrderSteps(StatesGroup):
    choosing_language = State()
    waiting_for_phone = State()
    waiting_for_name = State()
    waiting_for_location = State()
    browsing_menu = State()

# Тексты на двух языках
TEXTS = {
    'uz': {
        'welcome': "Xush kelibsiz! Tilni tanlang:",
        'ask_phone': "Telefon raqamingizni yuboring:",
        'btn_phone': "📞 Raqamni yuborish",
        'ask_name': "Ismingizni kiriting:",
        'ask_loc': "Joylashuvingizni (lokatsiya) yuboring:",
        'btn_loc': "📍 Lokatsiyani yuborish",
        'menu_welcome': "Katalogdan mahsulot tanlang:",
        'btn_veg': "🥦 Sabzavotlar",
        'btn_fruit': "🍎 Mevalar"
    },
    'ru': {
        'welcome': "Добро пожаловать! Выберите язык:",
        'ask_phone': "Отправьте ваш номер телефона:",
        'btn_phone': "📞 Отправить номер",
        'ask_name': "Введите ваше имя:",
        'ask_loc': "Отправьте вашу локацию:",
        'btn_loc': "📍 Отправить локацию",
        'menu_welcome': "Выберите категорию товаров:",
        'btn_veg': "🥦 Овощи",
        'btn_fruit': "🍎 Фрукты"
    }
}

# 1. Старт и выбор языка
@dp.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbekcha"), KeyboardButton(text="🇷🇺 Русский")]
        ],
        resize_keyboard=True
    )
    await message.answer(TEXTS['ru']['welcome'], reply_markup=kb)
    await state.set_state(OrderSteps.choosing_language)

# 2. Обработка выбора языка и запрос телефона
@dp.message(OrderSteps.choosing_language, F.text.in_({"🇺🇿 O'zbekcha", "🇷🇺 Русский"}))
async def process_language(message: Message, state: FSMContext):
    lang = 'uz' if "O'zbekcha" in message.text else 'ru'
    await state.update_data(lang=lang)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]['btn_phone'], request_contact=True)]],
        resize_keyboard=True
    )
    await message.answer(TEXTS[lang]['ask_phone'], reply_markup=kb)
    await state.set_state(OrderSteps.waiting_for_phone)

# 3. Получение телефона и запрос имени
@dp.message(OrderSteps.waiting_for_phone, F.contact)
async def process_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    await state.update_data(phone=message.contact.phone_number)
    
    await message.answer(TEXTS[lang]['ask_name'], reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderSteps.waiting_for_name)

# 4. Получение имени и запрос локации
@dp.message(OrderSteps.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    await state.update_data(name=message.text)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=TEXTS[lang]['btn_loc'], request_location=True)]],
        resize_keyboard=True
    )
    await message.answer(TEXTS[lang]['ask_loc'], reply_markup=kb)
    await state.set_state(OrderSteps.waiting_for_location)

# 5. Получение локации и переход в главное меню товаров
@dp.message(OrderSteps.waiting_for_location, F.location)
async def process_location(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    
    # Сохраняем координаты
    await state.update_data(lat=message.location.latitude, lon=message.location.longitude)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=TEXTS[lang]['btn_veg']), KeyboardButton(text=TEXTS[lang]['btn_fruit'])]
        ],
        resize_keyboard=True
    )
    await message.answer(TEXTS[lang]['menu_welcome'], reply_markup=kb)
    await state.set_state(OrderSteps.browsing_menu)

# 6. Обработка выбора категорий товаров
@dp.message(OrderSteps.browsing_menu)
async def process_menu(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data['lang']
    
    if message.text in [TEXTS['ru']['btn_veg'], TEXTS['uz']['btn_veg']]:
        await message.answer("Помидоры, Огурцы, Картошка..." if lang == 'ru' else "Pomidor, Bodring, Kartoshka...")
    elif message.text in [TEXTS['ru']['btn_fruit'], TEXTS['uz']['btn_fruit']]:
        await message.answer("Яблоки, Бананы, Урюк..." if lang == 'ru' else "Olma, Banan, O'rik...")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
