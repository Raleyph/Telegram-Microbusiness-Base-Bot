from aiogram import Router
from aiogram import types
from aiogram.filters import Text
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import database as db
import config as cfg
import keyboards as kb

router = Router()


class MenuStates(StatesGroup):
    menu = State()
    general_data_menu = State()
    expenses_menu = State()
    set_time_period = State()


# commands
@router.message(Command(commands=["start"]))
async def start_bot(message: types.Message, state: FSMContext):
    await state.clear()

    if message.chat.id in cfg.whitelist:
        if not db.user_check(message.chat.id):
            us_id = message.from_user.id
            us_name = message.from_user.first_name
            username = message.from_user.username

            db.user_login(user_id=us_id, user_name=us_name, username=username)

        await message.answer(cfg.start_message, reply_markup=kb.get_main_keyboard(), parse_mode='html', disable_web_page_preview=True)
        db.check_dirs()


@router.message(Command(commands=["cancel"]))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Отмена!", reply_markup=kb.get_main_keyboard())


# client menu
@router.message(Text(text="Клиенты 🙎‍♀"))
async def open_clients_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню клиентов", reply_markup=kb.get_clients_keyboard())
    await state.set_state(MenuStates.menu)


# records menu
@router.message(Text(text="Записи 📃"))
async def open_records_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню записей", reply_markup=kb.get_records_keyboard())
    await state.set_state(MenuStates.menu)


# analytics menu
@router.message(Text(text="Аналитика 📊"))
async def open_records_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню аналитики", reply_markup=kb.get_analytics_keyboard())
    await state.set_state(MenuStates.menu)


@router.message(Text(text="Назад"), MenuStates.menu)
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await message.answer("Главное меню", reply_markup=kb.get_main_keyboard())
    await state.clear()


# get data
@router.message(Text(text="График доходов 💶"))
async def get_finance_schedule(message: types.Message, state: FSMContext):
    await state.update_data(action=message.text)
    await state.set_state(MenuStates.set_time_period)
    await message.answer("Выберете период времени", reply_markup=kb.get_time_period_keyboard())


@router.message(Text(text="График времени ⏳"))
async def get_time_schedule(message: types.Message, state: FSMContext):
    await state.update_data(action=message.text)
    await state.set_state(MenuStates.set_time_period)
    await message.answer("Выберете период времени", reply_markup=kb.get_time_period_keyboard())


@router.message(Text(text="Завершенные записи ✅"))
async def get_complete_records(message: types.Message, state: FSMContext):
    await state.update_data(action=message.text)
    await state.set_state(MenuStates.set_time_period)
    await message.answer("Выберете период времени", reply_markup=kb.get_time_period_keyboard())


@router.message(Text(text="Назад"), MenuStates.set_time_period)
async def back_to_analytics_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню аналитики", reply_markup=kb.get_analytics_keyboard())
    await state.set_state(MenuStates.menu)


# general data
@router.message(Text(text="Общие данные 🗄"))
async def open_general_data_menu(message: types.Message, state: FSMContext):
    await state.set_state(MenuStates.general_data_menu)
    await message.answer("Меню общих сведений о доходах и расходах", reply_markup=kb.get_general_data_keyboard())


@router.message(Text(text="Назад"), MenuStates.general_data_menu)
async def back_to_analytics_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню аналитики", reply_markup=kb.get_analytics_keyboard())
    await state.set_state(MenuStates.menu)


# expenses
@router.message(Text(text="Расходы 💸"))
async def open_expenses_menu(message: types.Message, state: FSMContext):
    await state.set_state(MenuStates.expenses_menu)
    await message.answer("Меню расходов", reply_markup=kb.get_expenses_keyboard())


@router.message(Text(text="Назад"), MenuStates.expenses_menu)
async def back_to_general_data_menu(message: types.Message, state: FSMContext):
    await message.answer("Меню общих сведений о доходах и расходах", reply_markup=kb.get_general_data_keyboard())
    await state.set_state(MenuStates.menu)
