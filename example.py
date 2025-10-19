import asyncio
import logging
from datetime import date

from aiogram import Bot, Dispatcher
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from aiogram_datepicker.DatePicker import DatePicker

BOT_TOKEN = ""
dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)


async def handle_selected_date(selected_date, callback: CallbackQuery):
    await callback.message.answer(f"выбрана дата {selected_date}")
    print(f"date: {selected_date}")


date_picker_inline = DatePicker(
    mode="inline",
    start_date=date(2025, 10, 1),
    end_date=date(2025, 12, 31),
    month_names=[
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ],
    day_names=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    prefix="dp1",
    prompt_select_date="📅 Pick a date:",
    prompt_select_year="📆 Choose year:",
    prompt_select_month_fmt="Pick month:",
    prompt_select_day_fmt="Pick day:",
    on_date_selected=handle_selected_date,
)
date_picker_step = DatePicker(
    mode="step",
    start_date=date(2020, 10, 1),
    end_date=date(2030, 12, 31),
    month_names=[
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ],
    day_names=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    prefix="dp2",
    prompt_select_date="📅 Pick a date:",
    prompt_select_year="📆 Choose year:",
    prompt_select_month_fmt="Pick month:",
    prompt_select_day_fmt="Pick day:",
    on_date_selected=handle_selected_date,
)

dp.include_router(date_picker_inline.get_router())
dp.include_router(date_picker_step.get_router())


@dp.message(Command("date1"))
async def cmd_date1(message: Message, state: FSMContext):
    await date_picker_inline.start(message, state)


@dp.message(Command("date2"))
async def cmd_date2(message: Message, state: FSMContext):
    await date_picker_step.start(message, state)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
