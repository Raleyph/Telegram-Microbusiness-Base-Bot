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


class RecordStates(StatesGroup):
    set_new_record_client = State()
    set_new_record_date = State()
    set_new_record_confirm = State()
    select_current_record = State()
    remove_record_confirm = State()
    commit_current_record = State()
    set_record_service = State()
    set_record_price = State()
    set_record_tips = State()
    set_record_additional = State()
    set_record_work_time = State()
    commit_record_confirm = State()


# add
@router.message(Text(text="Добавить запись"), F.text)
async def add_record(message: types.Message, state: FSMContext):
    client_list = db.get_client_list()

    if client_list:
        await state.set_state(RecordStates.set_new_record_client)
        await message.answer("Выберете клиента из списка", reply_markup=kb.get_clients_choose_keyboard(client_list))
    else:
        await state.clear()
        await message.answer("Похоже, что вы не добавили ни одного клиента!", reply_markup=kb.get_main_keyboard())


@router.callback_query(RecordStates.set_new_record_client)
async def select_current_client(call: types.CallbackQuery, state: FSMContext):
    client_data = db.get_client_from_id(call.data)

    if client_data:
        await state.update_data(record_client_id=call.data)
        await state.set_state(RecordStates.set_new_record_date)
        await call.message.answer("Введите дату и время записи в формате 2022-11-01 15:00", reply_markup=types.ReplyKeyboardRemove)


@router.message(F.text, RecordStates.set_new_record_date)
async def set_record_datetime(message: types.Message, state: FSMContext):
    if re.match(r'^202[2-5]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:00$', message.text):
        split_datetime = message.text.split()
        entered_date = datetime.strptime(message.text, "%Y-%m-%d %H:%M")

        if entered_date > datetime.now():
            if not db.check_records(split_datetime[0], split_datetime[1]):
                record_data = await state.get_data()
                current_client = db.get_client_from_id(record_data['record_client_id'])[1]

                await state.update_data(record_date=split_datetime[0])
                await state.update_data(record_time=split_datetime[1])
                await state.set_state(RecordStates.set_new_record_confirm)
                await message.answer(f"Подтвердить добавление записи на {message.text} для клиента {current_client}?",
                                     reply_markup=kb.get_confirm_keyboard())
            else:
                await message.answer("Время уже занято!")
        else:
            await message.answer("Невозможно добавить запись на прошедшую дату или время!")
    else:
        await message.answer("Некорректный ввод даты и времени!")


@router.callback_query(RecordStates.set_new_record_confirm)
async def confirm_record(call: types.callback_query, state: FSMContext):
    if call.data == "yes":
        record_data = await state.get_data()
        db.add_record(record_data['record_date'], record_data['record_time'], False, record_data['record_client_id'])
        await call.message.answer("Запись успешно добавлена!", reply_markup=kb.get_main_keyboard())
    elif call.data == "no":
        await call.message.answer("Отмена!", reply_markup=kb.get_main_keyboard())

    await state.clear()


# remove
@router.message(Text(text="Удалить запись"), F.text)
async def remove_record(message: types.Message, state: FSMContext):
    records_list = db.get_current_records()

    if records_list:
        await state.set_state(RecordStates.select_current_record)
        await message.answer("Выберете запись для удаления", reply_markup=kb.get_current_records_choose_keyboard(records_list))
    else:
        await state.clear()
        await message.answer("Записей для удаления нет!", reply_markup=kb.get_main_keyboard())


@router.callback_query(RecordStates.select_current_record)
async def select_current_record(call: types.callback_query, state: FSMContext):
    current_record = db.get_current_records()

    for record in current_record:
        if int(call.data) is int(record[0]):
            await state.update_data(record_id=record[0])
            await state.set_state(RecordStates.remove_record_confirm)
            await call.message.answer(f"Подтвердить удаление записи на {record[1]} {record[2]}?",
                                      reply_markup=kb.get_confirm_keyboard())


@router.callback_query(RecordStates.remove_record_confirm)
async def remove_confirm(call: types.callback_query, state: FSMContext):
    if call.data == "yes":
        record_data = await state.get_data()
        db.remove_record(record_data['record_id'])
        await call.message.answer("Запись успешно удалена!", reply_markup=kb.get_main_keyboard())
    elif call.data == "no":
        await call.message.answer("Отмена!", reply_markup=kb.get_main_keyboard())

    await state.clear()


# get current list
@router.message(Text(text="Текущие записи"), F.text)
async def get_current_records(message: types.Message, state: FSMContext):
    records_list = db.get_current_records()

    if records_list:
        image = types.FSInputFile(gp.get_current_records_dataframe())
        await message.answer_photo(image, reply_markup=kb.get_main_keyboard())
    else:
        await state.clear()
        await message.answer("Текущих записей нет!", reply_markup=kb.get_main_keyboard())


# commit
@router.message(Text(text="Завершить запись"), F.text)
async def commit_record(message: types.Message, state: FSMContext):
    records_list = db.get_current_records()

    if records_list:
        await state.set_state(RecordStates.commit_current_record)
        await message.answer("Выберете запись для завершения",
                             reply_markup=kb.get_current_records_choose_keyboard(records_list))
    else:
        await state.clear()
        await message.answer("Записей для завершения нет!", reply_markup=kb.get_main_keyboard())


@router.callback_query(RecordStates.commit_current_record)
async def commit_current_record(call: types.callback_query, state: FSMContext):
    current_record = db.get_current_records()

    for record in current_record:
        if int(call.data) is int(record[0]):
            await state.update_data(record_id=record[0])
            await state.update_data(record_datetime=f"{record[1]} {record[2]}")
            await state.update_data(client_id=record[3])
            await state.set_state(RecordStates.set_record_service)
            await call.message.answer("Введите оказанную услугу", reply_markup=types.ReplyKeyboardRemove)


@router.message(F.text, RecordStates.set_record_service)
async def set_record_service(message: types.Message, state: FSMContext):
    if len(message.text) < 52:
        await state.update_data(service=message.text)
        await state.set_state(RecordStates.set_record_price)
        await message.answer("Введите заработок", reply_markup=types.ReplyKeyboardRemove)
    else:
        await message.answer("Описание услуги слишком длинное!")


@router.message(F.text, RecordStates.set_record_price)
async def set_record_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if len(message.text) < 7:
            await state.update_data(price=message.text)
            await state.set_state(RecordStates.set_record_tips)
            await message.answer("Введите информацию о чаевых", reply_markup=kb.get_skip_button())
        else:
            await message.answer("Не многовато ли?")
    else:
        await message.answer("Введите числовое значение")


@router.message(F.text, RecordStates.set_record_tips)
async def set_record_tips(message: types.Message, state: FSMContext):
    if len(message.text) < 52:
        await state.update_data(tips=message.text)
        await state.set_state(RecordStates.set_record_additional)
        await message.answer("Введите дополнительную информацию", reply_markup=kb.get_skip_button())
    else:
        await message.answer("Чаевых слишком много!")


@router.message(F.text, RecordStates.set_record_additional)
async def set_record_additional(message: types.Message, state: FSMContext):
    if len(message.text) < 52:
        await state.update_data(additional=message.text)
        await state.set_state(RecordStates.set_record_work_time)
        await message.answer("Введите время работы", reply_markup=types.ReplyKeyboardRemove)
    else:
        await message.answer("Дополнительная информация слишком длинная!")


@router.message(F.text, RecordStates.set_record_work_time)
async def set_record_work_time(message: types.Message, state: FSMContext):
    work_time = None

    if re.match(r"^[0-9]+,?[0-9]*$", message.text):
        work_time = message.text.replace(",", ".")
    elif re.match(r"^[0-9]+.?[0-9]*$", message.text):
        work_time = message.text
    else:
        await message.answer("Некорректный ввод!")

    if work_time:
        if len(message.text) < 5:
            await state.update_data(work_time=work_time)
            await state.set_state(RecordStates.commit_record_confirm)
            record_data = await state.get_data()
            current_client = db.get_client_from_id(record_data['client_id'])
            space = "\n"

            await message.answer(f"Подтвердить завершение записи?\n"
                                 f"\n"
                                 f"<b>Дата:</b> {record_data['record_datetime']}\n"
                                 f"<b>Клиент:</b> {current_client[1]}\n"
                                 f"<b>Услуга:</b> {record_data['service']}\n"
                                 f"<b>Стоимость:</b> {record_data['price']} у.е.\n"
                                 f"{'<b>Чаевые:</b> ' + record_data['tips'] + ' у.е.' + space if record_data['tips'] != 'Пропустить' else ''}"
                                 f"{'<b>Дополнительно:</b> ' + record_data['additional'] + space if record_data['additional'] != 'Пропустить' else ''}"
                                 f"<b>Время работы:</b> {record_data['work_time']} ч.\n",
                                 reply_markup=kb.get_confirm_keyboard(), parse_mode='html')


@router.callback_query(RecordStates.commit_record_confirm)
async def commit_record_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        record_data = await state.get_data()
        if record_data['tips'] == "Пропустить":
            await state.update_data(tips="Нет")
        if record_data['additional'] == "Пропустить":
            await state.update_data(additional="Нет")

        record_data = await state.get_data()
        db.commit_record(record_data['record_id'], record_data['service'], record_data['price'],
                         record_data['tips'], record_data['additional'], record_data['work_time'])
        db.add_client_visits_count(record_data['client_id'])
        await call.message.answer("Запись успешно завершена!", reply_markup=kb.get_main_keyboard())
    elif call.data == "no":
        await call.message.answer("Отмена!")

    await state.clear()
