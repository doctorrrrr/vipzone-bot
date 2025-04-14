import os
import asyncio
import logging
import random
import datetime
import pytz

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiohttp import ClientSession
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ForceReply
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from icmplib import ping
from icmplib import exceptions
from icmplib import traceroute
from functools import partial

from tabulate import tabulate

from config import BOT_TOKEN, WEATHER, PASSW

# Логування
logging.basicConfig(level=logging.INFO)

# Робимо об’єкт бота
bot = Bot(token=BOT_TOKEN)

# Диспетчер
dp = Dispatcher()

# Створення клавіатури з кнопками
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/start"), KeyboardButton(text="/help")],
        [KeyboardButton(text="Ping"), KeyboardButton(text="Traceroute")],
        [KeyboardButton(text="Weather")],
        [KeyboardButton(text="Write"), KeyboardButton(text="Read")],
        [KeyboardButton(text="Set Alarm")]
    ],
    resize_keyboard=True
)

# Словник для зберігання будильників
alarms = {}

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_handler(message: types.Message):
    user_name = message.from_user.first_name
    local_timezone = pytz.timezone('Europe/Kiev')
    current_time = datetime.datetime.now(local_timezone).strftime("%H:%M:%S")
    greeting_message = f'Вітаю, {user_name}! Це тестовий бот. Щоб переглянути доступні команди, скористайтесь /help. Поточний час: {current_time}'
    await message.answer(greeting_message, reply_markup=keyboard)

# Хэндлер на команду /help
@dp.message(Command("help"))
async def cmd_handler(message: types.Message):
    await message.answer(
        f"Типу допомога\n\n"
        f"/start старт\n"
        f"/help типу допомога\n"
        f"/ping пінг\n"
        f"/tr трасування\n"
        f"/weather погода\n"
        f"/write /read запис-читання файлу",
        reply_markup=keyboard
    )

# Хэндлер на команду Ping
@dp.message(lambda message: message.text == "Ping")
async def ask_ping_address(message: types.Message):
    await message.answer("Введіть адресу або IP для пінгу:", reply_markup=ForceReply())

# Хэндлер для відповіді на запит Ping
@dp.message(lambda message: message.reply_to_message and message.reply_to_message.text == "Введіть адресу або IP для пінгу:")
async def ping_handler(message: types.Message):
    host = message.text
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, partial(ping, host))
        await message.answer(f"Ping {host}: {response}", reply_markup=keyboard)
    except exceptions.NameLookupError:
        await message.answer(f"Не вдалося вирішити доменне ім'я {host}", reply_markup=keyboard)

# Хэндлер на команду Traceroute
@dp.message(lambda message: message.text == "Traceroute")
async def ask_traceroute_address(message: types.Message):
    await message.answer("Введіть адресу або IP для трасування:", reply_markup=ForceReply())

# Хэндлер для відповіді на запит Traceroute
@dp.message(lambda message: message.reply_to_message and message.reply_to_message.text == "Введіть адресу або IP для трасування:")
async def traceroute_handler(message: types.Message):
    host = message.text
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, partial(traceroute, host))
        table = tabulate(
            [
                [hop.distance, hop.address, hop.avg_rtt]
                for hop in response
            ],
            headers=["TTL", "IP", "Затримка (мс)"],
            tablefmt="pipe",
        )
        await message.answer(f"Трасування {host}:\n{table}", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"Не вдалося виконати трасування {host}: {e}", reply_markup=keyboard)

# Хэндлер на команду Weather
@dp.message(lambda message: message.text == "Weather")
async def ask_weather_city(message: types.Message):
    await message.answer("Введіть назву міста для отримання погоди:", reply_markup=ForceReply())

# Хэндлер для відповіді на запит Weather
@dp.message(lambda message: message.reply_to_message and message.reply_to_message.text == "Введіть назву міста для отримання погоди:")
async def weather_handler(message: types.Message):
    city = message.text
    try:
        async with ClientSession() as session:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER}&units=metric"
            async with session.get(url) as response:
                data = await response.json()

        if data["cod"] != 200:
            await message.answer(f"Помилка: {data['message']}")
            return

        weather = data["weather"][0]["main"]
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        pressure = data["main"]["pressure"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        wind_deg = data["wind"]["deg"]
        await message.answer(
            f"**Погода у {city}:**\n\n"
            f"• **Температура:** {temperature:.1f}°C\n"
            f"• **Відчувається як:** {feels_like:.1f}°C\n"
            f"• **Опади:** {weather}\n"
            f"• **Тиск:** {pressure} гПа\n"
            f"• **Вологість:** {humidity}%\n"
            f"• **Вітер:** {wind_speed:.1f} м/с, {wind_deg}°",
            reply_markup=keyboard
        )
    except Exception as e:
        await message.answer(f"Помилка: {e}", reply_markup=keyboard)

# Хэндлер на команду Write
@dp.message(lambda message: message.text == "Write")
async def ask_write_password(message: types.Message):
    await message.answer("Введіть пароль для запису інформації у файл:", reply_markup=ForceReply())

# Хэндлер для відповіді на запит Write
@dp.message(lambda message: message.reply_to_message and message.reply_to_message.text == "Введіть пароль для запису інформації у файл:")
async def check_password(message: types.Message):
    user_name = message.from_user.first_name
    password = message.text.strip()
    if password == PASSW:
        await message.answer("Пароль прийнято. Введіть текст для запису у файл:", reply_markup=ForceReply())
    else:
        await message.answer(f"Гарна спроба, {user_name}. Спробуйте ще раз.", reply_markup=keyboard)

# Хэндлер для відповіді на запит тексту для запису у файл
@dp.message(lambda message: message.reply_to_message and message.reply_to_message.text == "Пароль прийнято. Введіть текст для запису у файл:")
async def write_text(message: types.Message):
    text = message.text.strip()
    try:
        with open(os.path.join("/home/doctor/python/bot", "mem.txt"), "a") as f:
            f.write(f"{text}\n")
    except Exeption as e:
          await message.answer(f"Помилка запису у файл: {e}")
    await message.answer("Текст записано.", reply_markup=keyboard)

# Хэндлер на команду Read
@dp.message(lambda message: message.text == "Read")
async def read_text(message: types.Message):
    with open(os.path.join("/home/doctor/python/bot", "mem.txt"), "r") as f:
        text = f.read()
    await message.answer(text, reply_markup=keyboard)

# Функція очищення файлу
@dp.message(Command("clear"))
async def clear_file(message: types.Message):
    if not os.path.exists("/home/doctor/python/bot/mem.txt"):
        await message.answer("Файл не існує.")
        return

    # Очищення файлу
    with open("/home/doctor/python/bot/mem.txt", "w") as f:
        f.truncate(0)

    await message.answer("Файл успішно очищено.", reply_markup=keyboard)





# Функція для створення кнопок вибору дати та часу
def create_datetime_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # Підпис для вибору дня
        [InlineKeyboardButton(text="День:", callback_data="ignore")],
        # Кнопки для вибору дати (1-31)
        *[
            [InlineKeyboardButton(text=f"{day}", callback_data=f"day:{day}") for day in range(i, i + 7)]
            for i in range(1, 32, 7)
        ],
        # Підпис для вибору місяця
        [InlineKeyboardButton(text="Місяць:", callback_data="ignore")],
        # Кнопки для вибору місяця (1-12)
        *[
            [InlineKeyboardButton(text=f"{month}", callback_data=f"month:{month}") for month in range(i, i + 6)]
            for i in range(1, 13, 6)
        ],
        # Підпис для вибору року
        [InlineKeyboardButton(text="Рік:", callback_data="ignore")],
        # Кнопки для вибору року
        [InlineKeyboardButton(text=f"{year}", callback_data=f"year:{year}") for year in range(datetime.datetime.now().year, datetime.datetime.now().year + 3)],
        # Підпис для вибору години
        [InlineKeyboardButton(text="Година:", callback_data="ignore")],
        # Кнопки для вибору години (0-23)
        *[
            [InlineKeyboardButton(text=f"{hour:02d}", callback_data=f"hour:{hour}") for hour in range(i, i + 6)]
            for i in range(0, 24, 6)
        ],
        # Підпис для вибору хвилини
        [InlineKeyboardButton(text="Хвилини:", callback_data="ignore")],
        # Кнопки для вибору хвилини (0-59, кожні 5 хвилин)
        *[
            [InlineKeyboardButton(text=f"{minute:02d}", callback_data=f"minute:{minute}") for minute in range(i, i + 10, 5)]
            for i in range(0, 60, 10)
        ],
    ])
    return keyboard

# Хэндлер на команду "Set Alarm"
@dp.message(lambda message: message.text == "Set Alarm")
async def ask_alarm_datetime(message: types.Message):
    await message.answer("Виберіть дату і час для встановлення будильника:", reply_markup=create_datetime_keyboard())

# Словник для зберігання проміжних даних вибору дати та часу
user_data = {}

# Хэндлер для обробки вибору дати та часу
@dp.callback_query(lambda call: call.data.startswith(("day:", "month:", "year:", "hour:", "minute:")))
async def handle_datetime_selection(callback_query: types.CallbackQuery):
    data_type, value = callback_query.data.split(":")
    user_id = callback_query.from_user.id

    if user_id not in user_data:
        user_data[user_id] = {}

    user_data[user_id][data_type] = int(value)

    # Перевіряємо, чи всі дані обрані
    if all(key in user_data[user_id] for key in ("day", "month", "year", "hour", "minute")):
        day = user_data[user_id]["day"]
        month = user_data[user_id]["month"]
        year = user_data[user_id]["year"]
        hour = user_data[user_id]["hour"]
        minute = user_data[user_id]["minute"]

        try:
            local_timezone = pytz.timezone('Europe/Kiev')
            alarm_datetime = datetime.datetime(year, month, day, hour, minute)
            alarm_datetime = local_timezone.localize(alarm_datetime)
            alarms[user_id] = {"datetime": alarm_datetime, "message": None}
            await callback_query.message.answer("Введіть повідомлення для будильника:", reply_markup=ForceReply())
        except ValueError:
            await callback_query.message.answer("Неправильний формат дати і часу. Спробуйте ще раз.")
            return

        del user_data[user_id]  # Очищаємо проміжні дані

    await callback_query.answer()

# Залишаємо без змін хэндлер для введення повідомлення
@dp.message(lambda message: message.reply_to_message and message.reply_to_message.text == "Введіть повідомлення для будильника:")
async def set_alarm_message(message: types.Message):
    if message.from_user.id in alarms:
        alarms[message.from_user.id]["message"] = message.text.strip()
        await message.answer(f"Будильник встановлено на {alarms[message.from_user.id]['datetime']} з повідомленням: {message.text.strip()}")

        # Встановлення таймера
        asyncio.create_task(alarm_timer(message.from_user.id, alarms[message.from_user.id]["datetime"], alarms[message.from_user.id]["message"]))

# Функція для таймера будильника
async def alarm_timer(user_id, alarm_datetime, alarm_message):
    now = datetime.datetime.now(pytz.timezone('Europe/Kiev'))
    delay = (alarm_datetime - now).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)
        await bot.send_message(user_id, f"🔔 Нагадування: {alarm_message}")
    else:
        await bot.send_message(user_id, "Неможливо встановити будильник у минулому. Будь ласка, спробуйте знову.")

@dp.message(Command("cancel_alarm"))
async def cancel_alarm(message: types.Message):
    user_id = message.from_user.id
    if user_id in alarms:
        del alarms[user_id]
        await message.answer("Будильник скасовано.")
    else:
        await message.answer("У вас немає активних будильників.")




# main
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
