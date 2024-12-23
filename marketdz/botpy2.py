from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio, logging
from dotenv import load_dotenv
import os

load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')

logging.basicConfig(level=logging.DEBUG)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

PRICE = {
    "фары": 5000,
    "стекло": 6500,
    "бампер": 9000,
    "дисплей": 2000,
    "батарея": 3000,
    "камера": 3500
}

orders = {}

user_state = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()

    builder.button(text="Мужской", callback_data="gender_male")
    builder.button(text="Женский", callback_data="gender_female")
    builder.adjust(2)

    await message.answer("ваш пол:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("gender_"))
async def choose_gender(callback: types.CallbackQuery):
    gender = callback.data.split("_")[1]
    user_state[callback.from_user.id] = {'gender': gender}

    builder = InlineKeyboardBuilder()
    builder.button(text="Автозапчасти", callback_data="category_auto_parts")
    builder.button(text="Мобильные запчасти", callback_data="category_mobile_parts")
    builder.adjust(2)

    await callback.message.answer("Категория товаров:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "category_auto_parts")
async def choose_auto_parts(callback: types.CallbackQuery):
    user_state[callback.from_user.id]['category'] = "auto_parts"

    builder = InlineKeyboardBuilder()
    builder.button(text="Фары", callback_data="item_фары")
    builder.button(text="Стекла", callback_data="item_стекло")
    builder.button(text="Бампер", callback_data="item_бампер")
    builder.adjust(3)

    await callback.message.answer("Выберите товар в категории 'Автозапчасти':", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "category_mobile_parts")
async def choose_mobile_parts(callback: types.CallbackQuery):
    user_state[callback.from_user.id]['category'] = "mobile_parts"

    builder = InlineKeyboardBuilder()
    builder.button(text="Дисплей", callback_data="item_дисплей")
    builder.button(text="Батарея", callback_data="item_батарея")
    builder.button(text="Камера", callback_data="item_камера")
    builder.adjust(3)

    await callback.message.answer("Выберите товар в категории 'Мобильные запчасти':", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("item_"))
async def choose_item(callback: types.CallbackQuery):
    item = callback.data.split("_")[1]
    user_id = callback.from_user.id
    category = user_state[user_id].get('category', 'unknown')

    price = PRICE.get(item, "Цена не найдена")

    orders[user_id] = {'item': item, 'price': price}

    if category == "auto_parts":
        await callback.message.answer(f"Вы выбрали товар: {item}, цена: {price} сомов")
    elif category == "mobile_parts":
        await callback.message.answer(f"Вы выбрали товар: {item}, цена: {price} сомов")
    else:
        await callback.message.answer("не выбрана категория товара")

    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить заказ", callback_data="confirm_order")
    builder.button(text="Отменить заказ", callback_data="cancel_order")
    builder.adjust(2)

    await callback.message.answer("Подтвердите заказ:", reply_markup=builder.as_markup())

@dp.callback_query(F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id in orders:
        item = orders[user_id]['item']
        price = orders[user_id]['price']
        await callback.message.answer(f"Вы заказали: {item}, цена: {price} сомов.")
        del orders[user_id]
    else:
        await callback.message.answer("нет заказов")

@dp.callback_query(F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id in orders:
        del orders[user_id]
        await callback.message.answer("вы отменили заказ")
    else:
        await callback.message.answer("нет заказов")

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
