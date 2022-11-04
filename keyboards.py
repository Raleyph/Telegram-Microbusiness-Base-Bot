from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="Клиенты 🙎‍♀"))
    kb.add(types.KeyboardButton(text="Записи 📃"))
    kb.add(types.KeyboardButton(text="Аналитика 📊"))
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Главное меню")


def get_clients_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="Добавить клиента"))
    kb.add(types.KeyboardButton(text="Редактировать клиента"))
    kb.add(types.KeyboardButton(text="Список клиентов"))
    kb.add(types.KeyboardButton(text="Назад"))
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Меню клиентов")


def get_records_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="Добавить запись"))
    kb.add(types.KeyboardButton(text="Удалить запись"))
    kb.add(types.KeyboardButton(text="Текущие записи"))
    kb.add(types.KeyboardButton(text="Завершить запись"))
    kb.add(types.KeyboardButton(text="Назад"))
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Меню записей")


def get_analytics_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="График доходов 💶"))
    kb.add(types.KeyboardButton(text="График времени ⏳"))
    kb.add(types.KeyboardButton(text="Общие данные 🗄"))
    kb.add(types.KeyboardButton(text="Завершенные записи ✅"))
    kb.add(types.KeyboardButton(text="Назад"))
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Меню аналитики")


def get_time_period_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="За неделю"))
    kb.add(types.KeyboardButton(text="За месяц"))
    kb.add(types.KeyboardButton(text="За все время"))
    kb.add(types.KeyboardButton(text="Назад"))
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Меню аналитики")


def get_general_data_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="Доходы 💰"))
    kb.add(types.KeyboardButton(text="Расходы 💸"))
    kb.add(types.KeyboardButton(text="Рентабельность 📈"))
    kb.add(types.KeyboardButton(text="Назад"))
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Меню аналитики")


def get_expenses_keyboard():
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="Добавить расход"))
    kb.add(types.KeyboardButton(text="Удалить расход"))
    kb.add(types.KeyboardButton(text="Список расходов"))
    kb.add(types.KeyboardButton(text="Назад"))
    kb.adjust(3)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Меню аналитики")


def get_skip_button():
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="Пропустить"))
    return kb.as_markup(resize_keyboard=True)


def get_confirm_keyboard():
    kb = InlineKeyboardBuilder()
    kb.add(types.InlineKeyboardButton(text="Да ✅", callback_data="yes"))
    kb.add(types.InlineKeyboardButton(text="Нет ❌", callback_data="no"))
    return kb.as_markup(row_width=2)


def get_expenses_type_keyboard():
    kb = InlineKeyboardBuilder()
    kb.add(types.InlineKeyboardButton(text="Материал 🧱", callback_data="material"))
    kb.add(types.InlineKeyboardButton(text="Зарплата 💳", callback_data="salary"))
    kb.add(types.InlineKeyboardButton(text="Перевозка 🚛", callback_data="transportation"))
    kb.add(types.InlineKeyboardButton(text="Налог ⚖", callback_data="tax"))
    return kb.as_markup(row_width=1)


def get_clients_choose_keyboard(data):
    kb = InlineKeyboardBuilder()
    for i in data:
        kb.row(types.InlineKeyboardButton(text=f"{i[1]} {'' if i[3] is None else str(i[3])}", callback_data=i[0]))
    return kb.as_markup(row_width=1)


def get_current_records_choose_keyboard(data):
    kb = InlineKeyboardBuilder()
    for i in data:
        kb.row(types.InlineKeyboardButton(text=f"{i[1]} {i[2]}", callback_data=i[0]))
    return kb.as_markup(row_width=1)


def get_expenses_for_remove_keyboard(data):
    kb = InlineKeyboardBuilder()
    for i in data:
        kb.row(types.InlineKeyboardButton(text=f"{i[3]} {i[4] if i[1] == 'Материал' else i[8]}", callback_data=i[0]))
    return kb.as_markup(row_width=1)
