import calendar
from datetime import date, timedelta
from typing import Callable, Literal, Optional

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)


class DatePicker:
    def __init__(
        self,
        *,
        mode: Literal["inline", "step"] = "inline",
        date_format: str = "%Y-%m-%d",
        return_as: Literal["date", "str"] = "date",
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        on_date_selected: Optional[Callable] = None,
        prefix: str = "dp",
        month_names: Optional[list[str]] = None,
        day_names: Optional[list[str]] = None,
        prompt_select_date: str = "Выберите дату:",
        prompt_select_year: str = "Выберите год:",
        prompt_select_month_fmt: str = "Год: {year}. Выберите месяц:",
        prompt_select_day_fmt: str = "Месяц: {year}-{month:02d}. Выберите день:",
        button_today: str = "Сегодня",
    ):
        """A flexible date picker for Telegram bots built with aiogram.

    Supports two interaction modes:
      - **inline**: Displays an interactive calendar in a single message with
        month navigation.
      - **step**: Guides the user through a step-by-step selection:
        year → month → day.

    Each instance must use a unique `prefix` to avoid callback data conflicts
    when multiple date pickers are used in the same bot.

    Args:
        mode (Literal["inline", "step"], optional): Interaction mode.
            Defaults to "inline".
        date_format (str, optional): Date string format used when
            `return_as="str"`. Defaults to "%Y-%m-%d".
        return_as (Literal["date", "str"], optional): Type of the selected
            value passed to the handler—either a `datetime.date` object or a
            formatted string. Defaults to "date".
        start_date (Optional[date], optional): Minimum allowed date (inclusive).
            Defaults to today.
        end_date (Optional[date], optional): Maximum allowed date (inclusive).
            Defaults to `start_date + 365 days`.
        on_date_selected (Optional[Callable], optional): Async callback function
            invoked when a date is selected. It receives two arguments:
            `(selected_value: date | str, callback: CallbackQuery)`.
            Defaults to None.
        prefix (str, optional): Unique prefix for callback data.
            Required when using multiple pickers. Defaults to "dp".
        month_names (Optional[list[str]], optional): List of 12 month names.
            Defaults to Russian month names.
        day_names (Optional[list[str]], optional): List of 7 weekday abbreviations
            (starting from Monday). Defaults to Russian short names ("Пн", "Вт", etc.).
        prompt_select_date (str, optional): Prompt text for inline mode.
            Defaults to "Выберите дату:".
        prompt_select_year (str, optional): Prompt when selecting a year in step mode.
            Defaults to "Выберите год:".
        prompt_select_month_fmt (str, optional): Prompt format when selecting a month.
            Supports `{year}` placeholder. Defaults to "Год: {year}. Выберите месяц:".
        prompt_select_day_fmt (str, optional): Prompt format when selecting a day.
            Supports `{year}` and `{month}` placeholders.
            Defaults to "Месяц: {year}-{month:02d}. Выберите день:".
        button_today (str, optional): Label for the "Today" button in inline mode.
            Defaults to "Сегодня".

    Example:
         async def handle_date(selected, callback):
             await callback.message.answer(f"Selected: {selected}")
        
         picker = DatePicker(
             mode="inline",
             start_date=date(2025, 1, 1),
             end_date=date(2025, 12, 31),
             on_date_selected=handle_date,
             prefix="my_picker"
         )
        dp.include_router(picker.get_router())
        """
        self.mode = mode
        self.date_format = date_format
        self.return_as = return_as
        self.start_date = start_date or date.today()
        self.end_date = end_date or (self.start_date + timedelta(days=365))
        self.on_date_selected = on_date_selected
        self.prefix = prefix
        self._callback_prefix = f"{prefix}:"
        self.months = month_names or [
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь",
        ]
        self.days = day_names or ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        self.prompt_select_date = prompt_select_date
        self.prompt_select_year = prompt_select_year
        self.prompt_select_month_fmt = prompt_select_month_fmt
        self.prompt_select_day_fmt = prompt_select_day_fmt
        self.button_today = button_today

        self.router = Router()
        self.router.callback_query.register(
            self._handle_callback, F.data.startswith(self._callback_prefix)
        )

    def _encode(self, action: str, value: str = "") -> str:
        return f"{self.prefix}:{action}:{value}"

    def get_router(self) -> Router:
        return self.router

    async def start(self, message: Message, state: FSMContext) -> None:
        if self.mode == "inline":
            markup = self._build_inline_calendar(self.start_date)
            await message.answer(self.prompt_select_date, reply_markup=markup)
        elif self.mode == "step":
            markup = self._build_year_keyboard()
            await message.answer(self.prompt_select_year, reply_markup=markup)

    def _build_inline_calendar(self, current: date) -> InlineKeyboardMarkup:
        kb = []
        kb.append(
            [InlineKeyboardButton(text=current.strftime("%B %Y"), callback_data="noop")]
        )
        kb.append(
            [InlineKeyboardButton(text=d, callback_data="noop") for d in self.days]
        )

        first_day = current.replace(day=1)
        start_offset = first_day.weekday()
        days_in_month = calendar.monthrange(current.year, current.month)[1]

        week = []
        for _ in range(start_offset):
            week.append(InlineKeyboardButton(text=" ", callback_data="noop"))

        for day in range(1, days_in_month + 1):
            d = current.replace(day=day)
            if self.start_date <= d <= self.end_date:
                week.append(
                    InlineKeyboardButton(
                        text=str(day),
                        callback_data=self._encode("select", d.isoformat()),
                    )
                )
            else:
                week.append(InlineKeyboardButton(text=str(day), callback_data="noop"))
            if len(week) == 7:
                kb.append(week)
                week = []

        if week:
            while len(week) < 7:
                week.append(InlineKeyboardButton(text=" ", callback_data="noop"))
            kb.append(week)

        prev_month = (first_day - timedelta(days=1)).replace(day=1)
        next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        nav = []
        if prev_month >= self.start_date.replace(day=1):
            nav.append(
                InlineKeyboardButton(
                    text="◀️", callback_data=self._encode("nav", prev_month.isoformat())
                )
            )
        else:
            nav.append(InlineKeyboardButton(text=" ", callback_data="noop"))

        today = date.today()
        if self.start_date <= today <= self.end_date:
            print(str(date.today()))
            nav.append(
                InlineKeyboardButton(
                    text=str(date.today()),
                    callback_data=self._encode("select", today.isoformat()),
                )
            )
        else:
            nav.append(InlineKeyboardButton(text=" ", callback_data="noop"))

        if next_month <= self.end_date.replace(day=1):
            nav.append(
                InlineKeyboardButton(
                    text="▶️", callback_data=self._encode("nav", next_month.isoformat())
                )
            )
        else:
            nav.append(InlineKeyboardButton(text=" ", callback_data="noop"))

        kb.append(nav)
        return InlineKeyboardMarkup(inline_keyboard=kb)

    def _build_year_keyboard(self) -> InlineKeyboardMarkup:
        min_year = self.start_date.year
        max_year = self.end_date.year
        actual_start = max(self.start_date.year, min_year)
        actual_end = min(self.end_date.year, max_year)
        years = list(range(actual_start, actual_end + 1))
        if not years:
            years = [date.today().year]

        buttons = []
        for i in range(0, len(years), 3):
            row = []
            for y in years[i : i + 3]:
                row.append(
                    InlineKeyboardButton(
                        text=str(y), callback_data=self._encode("select_year", str(y))
                    )
                )
            buttons.append(row)
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    def _build_month_keyboard(self, year: int) -> InlineKeyboardMarkup:
        buttons = []
        for i in range(0, 12, 3):
            row = []
            for m in range(i, min(i + 3, 12)):
                month_num = m + 1
                first_day = date(year, month_num, 1)
                last_day = date(
                    year, month_num, calendar.monthrange(year, month_num)[1]
                )
                if not (self.start_date <= last_day and first_day <= self.end_date):
                    row.append(
                        InlineKeyboardButton(text=self.months[m], callback_data="noop")
                    )
                else:
                    row.append(
                        InlineKeyboardButton(
                            text=self.months[m],
                            callback_data=self._encode(
                                "select_month", f"{year}-{month_num}"
                            ),
                        )
                    )
            buttons.append(row)
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    def _build_day_keyboard(self, year: int, month: int) -> InlineKeyboardMarkup:
        days_in_month = calendar.monthrange(year, month)[1]
        buttons = []
        header = f"{year}-{month:02d}"
        buttons.append([InlineKeyboardButton(text=header, callback_data="noop")])
        buttons.append(
            [InlineKeyboardButton(text=d, callback_data="noop") for d in self.days]
        )

        first_weekday = calendar.monthrange(year, month)[0]
        week = [
            InlineKeyboardButton(text=" ", callback_data="noop")
            for _ in range(first_weekday)
        ]

        for day in range(1, days_in_month + 1):
            d = date(year, month, day)
            if self.start_date <= d <= self.end_date:
                week.append(
                    InlineKeyboardButton(
                        text=str(day),
                        callback_data=self._encode("select", d.isoformat()),
                    )
                )
            else:
                week.append(InlineKeyboardButton(text=str(day), callback_data="noop"))
            if len(week) == 7:
                buttons.append(week)
                week = []

        if week:
            while len(week) < 7:
                week.append(InlineKeyboardButton(text=" ", callback_data="noop"))
            buttons.append(week)

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def _handle_callback(self, callback: CallbackQuery, state: FSMContext):
        await callback.answer()
        data = callback.data

        if not data.startswith(self._callback_prefix):
            return
        payload = data[len(self._callback_prefix) :]
        parts = payload.split(":", 1)
        action = parts[0]
        value = parts[1] if len(parts) > 1 else ""

        if self.mode == "inline":
            if action == "nav":
                new_date = date.fromisoformat(value)
                markup = self._build_inline_calendar(new_date)
                await callback.message.edit_reply_markup(reply_markup=markup)
            elif action == "select":
                await self._finalize_selection(callback, state, value)

        elif self.mode == "step":
            if action == "select_year":
                year = int(value)
                markup = self._build_month_keyboard(year)
                await callback.message.edit_text(
                    self.prompt_select_month_fmt, reply_markup=markup
                )
            elif action == "select_month":
                year, month = map(int, value.split("-"))
                markup = self._build_day_keyboard(year, month)
                await callback.message.edit_text(
                    self.prompt_select_day_fmt, reply_markup=markup
                )
            elif action == "select":
                await self._finalize_selection(callback, state, value)

    async def _finalize_selection(
        self, callback: CallbackQuery, state: FSMContext, iso_date: str
    ):
        selected = date.fromisoformat(iso_date)
        result = (
            selected
            if self.return_as == "date"
            else selected.strftime(self.date_format)
        )
        await callback.message.delete()
        await state.update_data(selected_date=result)
        if self.on_date_selected:
            await self.on_date_selected(result, callback)
