## 📅 `aiogram-datepicker` — Flexible Date Picker for Telegram Bots with aiogram

The `aiogram-datepicker` library provides a convenient and customizable date selection interface for Telegram bots built with **aiogram 3.x**. It supports two modes:  
- **inline**: a calendar displayed in a single message  
- **step-by-step**: guided selection (year → month → day)

---

## 📦 Installation

Simply copy `DatePicker.py` into your project directory:

```bash
cp DatePicker.py your_project/
```

### Requirements:
- Python ≥ 3.8  
- aiogram ≥ 3.0  
- Standard library modules: `calendar`, `datetime`

---

## 🚀 Quick Start

```python
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import date

from DatePicker import DatePicker

BOT_TOKEN = "YOUR_BOT_TOKEN"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def handle_selected_date(selected_date, callback):
    await callback.message.answer(f"You selected: {selected_date}")

# Inline mode (calendar in one message)
date_picker_inline = DatePicker(
    mode="inline",
    start_date=date(2025, 10, 1),
    end_date=date(2025, 12, 31),
    on_date_selected=handle_selected_date,
    prefix="dp1"
)

# Step-by-step mode (year → month → day)
date_picker_step = DatePicker(
    mode="step",
    start_date=date(2020, 1, 1),
    end_date=date(2030, 12, 31),
    on_date_selected=handle_selected_date,
    prefix="dp2"
)

dp.include_router(date_picker_inline.get_router())
dp.include_router(date_picker_step.get_router())

@dp.message(Command("date1"))
async def cmd_date1(message: Message, state: FSMContext):
    await date_picker_inline.start(message, state)

@dp.message(Command("date2"))
async def cmd_date2(message: Message, state: FSMContext):
    await date_picker_step.start(message, state)
```

---

## 📥 Registering the Router

```python
router = date_picker.get_router()
dp.include_router(router)
```

> ⚠️ **Important**: Without this, callback handlers won’t be registered, and the date picker won’t respond to user input.

---

## 📤 Handling the Selected Date

When a user picks a date:
- The `on_date_selected(result, callback)` function is called, where `result` is either a `date` object or a `str` (based on the `return_as` setting).
- The selected date is also stored in the FSM context:  
  ```python
  data = await state.get_data()  # → {"selected_date": ...}
  ```

---

## 🌍 Localization

Easily adapt the interface to any language:

```python
DatePicker(
    month_names=[
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ],
    day_names=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    prompt_select_date="📅 Pick a date:",
    prompt_select_year="📆 Choose a year:",
    prompt_select_month_fmt="Year: {year}. Pick a month:",
    prompt_select_day_fmt="Month: {year}-{month:02d}. Pick a day:",
    button_today="Today"
)
```

All prompts and labels are fully customizable.

---

## 📝 Notes

- In **inline mode**, the "Today" button is only shown if the current date falls within the `[start_date, end_date]` range.
- Dates outside the allowed range are displayed as disabled (`callback_data="noop"`).
- Month navigation in inline mode uses `callback.message.edit_reply_markup()` to avoid spamming the chat with new messages.

---

## ✅ Best Practices

- **Always use a unique `prefix`** for each `DatePicker` instance to prevent callback conflicts.
- Wrap your `on_date_selected` handler in a `try/except` block in production to avoid unhandled exceptions.
- Don’t forget to register the router with `dp.include_router()`.