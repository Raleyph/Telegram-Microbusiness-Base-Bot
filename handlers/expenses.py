from aiogram import Router
from aiogram import types
from aiogram import F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from datetime import datetime
import re

import database as db
import keyboards as kb
import graphic_representation as gp

router = Router()


class ExpensesState(StatesGroup):
    expenses_menu = State()
    set_expense_price = State()
    set_expense_date = State()
    set_expense_type = State()
    set_expense_description = State()
    set_expense_material_name = State()
    set_expense_material_count = State()
    set_expense_material_consumption = State()
    add_expense_material_confirm = State()
    add_expense_confirm = State()
    remove_expense = State()
    remove_expense_confirm = State()


# get income
@router.message(Text(text="Доходы 💰"))
async def get_all_income(message: types.Message, state: FSMContext):
    try:
        db.get_expense_material_count()
        money = db.get_finance_sum()
        tips = db.get_tips_sum()

        await message.answer(f"<b>Сумма дохода:</b> {money} у.е.\n"
                             f"<b>Сумма чаевых:</b> {tips} у.е.\n"
                             f"<b>Общий заработок:</b> {money + tips} у.е.\n",
                             reply_markup=kb.get_main_keyboard(), parse_mode='html')
    except:
        await message.answer("Недостаточно данных для вывода информации о доходах! Завершите хотя-бы одну запись.",
                             reply_markup=kb.get_main_keyboard())
    await state.clear()


# get profitability
@router.message(Text(text="Рентабельность 📈"))
async def get_profitability(message: types.Message, state: FSMContext):
    try:
        expenses = db.get_expenses()
        expense_dates = {}
        last_dates = []

        for expense in expenses:
            if expense[3] in expense_dates:
                expense_dates[expense[3]] += 1
            else:
                expense_dates[expense[3]] = 1

        current_value = max(expense_dates.values())

        for k, v in expense_dates.items():
            if v == current_value:
                last_dates.append(k)

        last_dates_sort = sorted(last_dates, key=lambda date: date[0])
        now_date = datetime.now()
        now_date_str = now_date.strftime("%Y-%m-%d")
        last_date_str = last_dates_sort[0]

        data = db.get_profitability_data(last_date_str, now_date_str)
        await message.answer(f"Рентабельность и чистая прибыль вычисляется в промежуток от даты последней крупной закупки, до сегодняшнего дня без учета чаевых.\n"
                             f"\n"
                             f"<b>Рентабельность:</b> {data[1]}%\n"
                             f"<b>Чистая прибыль:</b> {data[0] if data[0] > 0 else 'отсутствует'} у.е.\n",
                             reply_markup=kb.get_main_keyboard(), parse_mode='html')
    except:
        await message.answer("Недостаточно данных для вычисления рентабельности! Должны быть внесены сведения о прибыли и расходах.",
                             reply_markup=kb.get_main_keyboard())
    await state.clear()


# add expense
@router.message(Text(text="Добавить расход"))
async def add_expense(message: types.Message, state: FSMContext):
    await message.answer("Введите сумму расходов", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(ExpensesState.set_expense_price)


@router.message(F.text, ExpensesState.set_expense_price)
async def set_expense_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(expense_price=message.text)
        await state.set_state(ExpensesState.set_expense_date)
        await message.answer("Введите дату в формате 2022-11-29")
    else:
        await message.answer("Введите числовое значение!")


@router.message(F.text, ExpensesState.set_expense_date)
async def set_expense_date(message: types.Message, state: FSMContext):
    if re.match(r'^202[2-5]-[0-1][0-9]-[0-3][0-9]$', message.text):
        await state.update_data(expense_date=message.text)
        await state.set_state(ExpensesState.set_expense_type)
        await message.answer("Выберете расход", reply_markup=kb.get_expenses_type_keyboard())
    else:
        await message.answer("Некорректный ввод даты и времени!")


@router.callback_query(ExpensesState.set_expense_type)
async def set_expense_type(call: types.CallbackQuery, state: FSMContext):
    if call.data == "material":
        await state.set_state(ExpensesState.set_expense_material_name)
        await call.message.answer("Введите название расходного материала", reply_markup=types.ReplyKeyboardRemove)
        await state.update_data(expense_type="Материал")
    if call.data == "salary":
        await state.set_state(ExpensesState.set_expense_description)
        await call.message.answer("Введите имя и должность сотрудника", reply_markup=types.ReplyKeyboardRemove)
        await state.update_data(expense_type="Зарплата")
    if call.data == "transportation":
        await state.set_state(ExpensesState.set_expense_description, reply_markup=types.ReplyKeyboardRemove)
        await call.message.answer("Введите сведения о перевозке")
        await state.update_data(expense_type="Перевозка")
    if call.data == "tax":
        await state.set_state(ExpensesState.set_expense_description, reply_markup=types.ReplyKeyboardRemove)
        await call.message.answer("Введите название налога")
        await state.update_data(expense_type="Налог")


@router.message(ExpensesState.set_expense_material_name)
async def set_expense_material_name(message: types.Message, state: FSMContext):
    if len(message.text) > 2:
        await state.update_data(expense_name=message.text)
        await state.set_state(ExpensesState.set_expense_material_count)
        await message.answer("Введите количество расходного материала. В базе данных он будет записываться как числовое значение без единицы измерения.")
    else:
        await message.answer("Название расходного материала слишком короткое!")


@router.message(F.text, ExpensesState.set_expense_material_count)
async def set_expense_material_count(message: types.Message, state: FSMContext):
    if re.match(r"^[0-9]+,?[0-9]*$", message.text):
        await state.update_data(expense_count=float(message.text))
        await state.set_state(ExpensesState.set_expense_material_consumption)
        await message.answer("Введите расход материала на одного клиента. Если вы хотите ввести не целое значение, то исользуйте формат 1.5.\n"
                             "Если же он неизвестен, то нажмите <b>Пропустить</b>\n",
                             reply_markup=kb.get_skip_button(), parse_mode='html')
    else:
        await message.answer("Введите числовое значение!")


@router.message(F.text, ExpensesState.set_expense_material_consumption)
async def set_expense_material_consumption(message: types.Message, state: FSMContext):
    if re.match(r"^[0-9]+,?[0-9]*$", message.text) or message.text == 'Пропустить':
        if len(message.text) < 6 or message.text == 'Пропустить':
            await state.update_data(expense_consumption=message.text)
            await state.set_state(ExpensesState.add_expense_material_confirm)

            expense_data = await state.get_data()
            await message.answer(f"Подтвердить добавление расходного материала?\n"
                                 f"\n"
                                 f"<b>Дата:</b> {expense_data['expense_date']}\n"
                                 f"<b>Название:</b> {expense_data['expense_name']}\n"
                                 f"<b>Стоимость:</b> {expense_data['expense_price']} у.е.\n"
                                 f"<b>Количество:</b> {expense_data['expense_count']}\n"
                                 f"{'<b>Расход:</b> ' + expense_data['expense_consumption'] if expense_data['expense_consumption'] != 'Пропустить' else ''}\n",
                                 reply_markup=kb.get_confirm_keyboard(), parse_mode='html')
        else:
            await message.answer("Не многовато ли?")
    else:
        await message.answer("Введите числовое значение!")


@router.callback_query(ExpensesState.add_expense_material_confirm)
async def add_expense_material_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        expense_data = await state.get_data()
        db.set_expense_material(expense_data['expense_type'], expense_data['expense_name'],
                                expense_data['expense_price'], expense_data['expense_date'],
                                expense_data['expense_count'], expense_data['expense_consumption']
                                if expense_data['expense_consumption'] != 'Пропустить' else None)
        await call.message.answer("Расходный материал успешно добавлен!", reply_markup=kb.get_main_keyboard())
    elif call.data == "no":
        await call.message.answer("Отмена!", reply_markup=kb.get_main_keyboard())

    await state.clear()


@router.message(ExpensesState.set_expense_description)
async def set_expense_description(message: types.Message, state: FSMContext):
    if len(message.text) > 2:
        await state.update_data(expense_description=message.text)
        await state.set_state(ExpensesState.add_expense_confirm)
        expense_data = await state.get_data()
        string_expense_type = ""

        if expense_data['expense_type'] == "Зарплата":
            string_expense_type = "зраплате"
        elif expense_data['expense_type'] == "Перевозка":
            string_expense_type = "перевозке"
        elif expense_data['expense_type'] == "Налог":
            string_expense_type = "налоге"

        await state.update_data(string_type=string_expense_type)

        await message.answer(f"Подтвердить внесение информации о {string_expense_type}?\n"
                             f"\n"
                             f"<b>Описание:</b> {expense_data['expense_description']}\n"
                             f"<b>Расход:</b> {expense_data['expense_price']} у.е.\n"
                             f"<b>Дата: </b> {expense_data['expense_date']}",
                             reply_markup=kb.get_main_keyboard(), parse_mode='html')
    else:
        await message.answer("Данные о сотруднике слишком короткие!")


@router.callback_query(ExpensesState.add_expense_confirm)
async def add_expense_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        expense_data = await state.get_data()
        db.set_expenses(expense_data['expense_type'], expense_data['expense_price'], expense_data['expense_date'], expense_data['expense_description'])
        await call.message.answer(call.from_user.id, f"Информация о {expense_data['string_type']} успешно добавлена!",
                                  reply_markup=kb.get_main_keyboard())
    elif call.data == "no":
        await call.message.answer(call.from_user.id, "Отмена!", reply_markup=kb.get_main_keyboard())

    await state.clear()


# remove expense
@router.message(Text(text="Удалить расход"))
async def remove_expense(message: types.Message, state: FSMContext):
    all_expenses = db.get_expenses()

    if all_expenses:
        await state.set_state(ExpensesState.remove_expense)
        await message.answer("Выберете расход", reply_markup=kb.get_expenses_for_remove_keyboard(all_expenses))
    else:
        await message.answer("Расходы не внесены!", reply_markup=kb.get_main_keyboard())


@router.callback_query(ExpensesState.remove_expense)
async def remove_current_expense(call: types.CallbackQuery, state: FSMContext):
    expense = db.get_expense_from_id(call.data)

    await state.update_data(expense_id=call.data)
    await state.set_state(ExpensesState.remove_expense_confirm)
    await call.message.answer(f"Удалить расход от {expense[0][3]}: {expense[0][4] if expense[0][1] == 'Материал' else expense[0][9]}?",
                              reply_markup=kb.get_confirm_keyboard())


@router.callback_query(ExpensesState.remove_expense_confirm)
async def remove_expense_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        expense_data = await state.get_data()
        db.remove_expense(expense_data['expense_id'])
        await call.message.answer("Расходный материал успешно удален!", reply_markup=kb.get_main_keyboard())
    elif call.data == "no":
        await call.message.answer("Отмена!", reply_markup=kb.get_main_keyboard())

    await state.clear()


# get expenses
@router.message(Text(text="Список расходов"))
async def get_expenses_list(message: types.Message):
    if db.get_expenses():
        image = types.FSInputFile(gp.get_expenses_dataframe())
        await message.answer_photo(image, reply_markup=kb.get_main_keyboard())
    else:
        await message.answer("Расходы не внесены!", reply_markup=kb.get_main_keyboard())
