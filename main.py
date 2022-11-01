from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from datetime import datetime, timedelta, time

import re
import os
import asyncio
import aioschedule
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import config
import database
import keyboard

storage = MemoryStorage()
bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=storage)


class StateGroup(StatesGroup):
    menu = State()

    set_client_name = State()
    set_client_description = State()
    set_client_contacts = State()
    set_client_confirm = State()

    update_current_client = State()
    update_client_name = State()
    update_client_description = State()
    update_client_contacts = State()
    update_client_confirm = State()

    set_record_date = State()
    set_record_client = State()
    set_record_current_client = State()
    set_record_confirm = State()

    commit_current_record = State()
    commit_record_service = State()
    commit_record_price = State()
    commit_record_tips = State()
    commit_record_additional = State()
    commit_record_work_time = State()
    commit_record_expense = State()
    commit_record_confirm = State()

    remove_record = State()
    remove_record_confirm = State()

    fast_set_client = State()

    analytics_menu = State()
    analytics_general_menu = State()
    analytics_get_menu = State()

    analytics_expense_menu = State()
    analytics_expense_type_menu = State()
    analytics_expense_price_menu = State()
    analytics_expense_date_menu = State()

    analytics_set_expense_material_name = State()
    analytics_set_expense_material_count = State()
    analytics_set_expense_material_consumption = State()
    analytics_set_expense_material_confirm = State()

    analytics_set_expense_description = State()
    analytics_set_expense_confirm = State()

    analytics_remove_expense = State()
    analytics_remove_expense_confirm = State()


# MAIN MENU
# start command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.chat.id in config.whitelist:
        if not database.user_check(message.chat.id):
            us_id = message.from_user.id
            us_name = message.from_user.first_name
            username = message.from_user.username

            database.user_login(user_id=us_id, user_name=us_name, username=username)

        await message.answer(config.start_message, reply_markup=keyboard.main_keyboard, parse_mode='html', disable_web_page_preview=True)
        await StateGroup.menu.set()


# cancel command
@dp.message_handler(commands=['cancel'], state=StateGroup.all_states)
async def cancel(message: types.Message, state: FSMContext):
    await bot.send_message(message.chat.id, 'Отмена!', reply_markup=keyboard.main_keyboard)
    await StateGroup.menu.set()
    await state.reset_data()


# client keyboard
@dp.message_handler(lambda message: message.text == 'Клиенты 🙎‍♀‍', state=StateGroup.menu)
async def clients_menu(message: types.Message):
    await bot.send_message(message.chat.id, 'Меню клиентов', reply_markup=keyboard.clients_keyboard)


# records keyboard
@dp.message_handler(lambda message: message.text == 'Записи 📃', state=StateGroup.menu)
async def records_menu(message: types.Message):
    await bot.send_message(message.chat.id, 'Меню записей', reply_markup=keyboard.records_keyboard)


# analytics keyboard
@dp.message_handler(lambda message: message.text == 'Аналитика 📊', state=StateGroup.menu)
async def analytics_menu(message: types.Message):
    await bot.send_message(message.chat.id, 'Меню аналитики', reply_markup=keyboard.analytics_keyboard)
    await StateGroup.analytics_menu.set()


@dp.message_handler(lambda message: message.text == 'График доходов 💶', state=StateGroup.analytics_menu)
async def analytics_finance_menu(message: types.Message, state: FSMContext):
    await state.update_data(user_data=message.text)
    await bot.send_message(message.chat.id, 'Выберете период времени', reply_markup=keyboard.analytics_delta_time_keyboard)
    await StateGroup.analytics_get_menu.set()


@dp.message_handler(lambda message: message.text == 'График времени ⏳', state=StateGroup.analytics_menu)
async def analytics_finance_menu(message: types.Message, state: FSMContext):
    await state.update_data(user_data=message.text)
    await bot.send_message(message.chat.id, 'Выберете период времени', reply_markup=keyboard.analytics_delta_time_keyboard)
    await StateGroup.analytics_get_menu.set()


@dp.message_handler(lambda message: message.text == 'Общие данные 🗄', state=StateGroup.analytics_menu)
async def get_all_data(message: types.Message):
    await bot.send_message(message.chat.id, 'Выберете параметр', reply_markup=keyboard.analytics_general_keyboard)
    await StateGroup.analytics_general_menu.set()


@dp.message_handler(lambda message: message.text == 'Завершенные записи ✅', state=StateGroup.analytics_menu)
async def analytics_completed_records(message: types.Message, state: FSMContext):
    await state.update_data(user_data=message.text)
    await bot.send_message(message.chat.id, 'Выберете период времени', reply_markup=keyboard.analytics_delta_time_keyboard)
    await StateGroup.analytics_get_menu.set()


# expense menu
@dp.message_handler(lambda message: message.text == 'Расходы 💸', state=StateGroup.analytics_general_menu)
async def expense_menu(message: types.Message):
    await bot.send_message(message.chat.id, 'Меню расходов', reply_markup=keyboard.analytics_expenses_keyboard)
    await StateGroup.analytics_expense_menu.set()


# to main menu
@dp.message_handler(lambda message: message.text == 'Назад', state=StateGroup.menu)
async def back_to_menu(message: types.Message):
    await bot.send_message(message.chat.id, 'Назад', reply_markup=keyboard.main_keyboard)


# to main menu from analytics
@dp.message_handler(lambda message: message.text == 'Назад', state=StateGroup.analytics_menu)
async def back_to_menu(message: types.Message):
    await StateGroup.menu.set()
    await bot.send_message(message.chat.id, 'Назад', reply_markup=keyboard.main_keyboard)


# to analytics menu from get menu
@dp.message_handler(lambda message: message.text == 'Назад', state=StateGroup.analytics_get_menu)
async def back_to_menu(message: types.Message):
    await StateGroup.analytics_menu.set()
    await bot.send_message(message.chat.id, 'Назад', reply_markup=keyboard.analytics_keyboard)


# to analytics menu from general analytics
@dp.message_handler(lambda message: message.text == 'Назад', state=StateGroup.analytics_general_menu)
async def back_to_menu(message: types.Message):
    await StateGroup.analytics_menu.set()
    await bot.send_message(message.chat.id, 'Назад', reply_markup=keyboard.analytics_keyboard)


# to analytics general menu from expenses
@dp.message_handler(lambda message: message.text == 'Назад', state=StateGroup.analytics_expense_menu)
async def back_to_menu(message: types.Message):
    await StateGroup.analytics_general_menu.set()
    await bot.send_message(message.chat.id, 'Назад', reply_markup=keyboard.analytics_general_keyboard)


# CLIENTS
# add client
@dp.message_handler(lambda message: message.text == 'Добавить клиента', state=StateGroup.menu)
async def add_cilent(message: types.Message):
    await StateGroup.set_client_name.set()
    await bot.send_message(message.chat.id, 'Введите имя клиента')


@dp.message_handler(state=StateGroup.set_client_name)
async def set_client_name(message: types.Message, state: FSMContext):
    if len(message.text) < 22:
        await state.update_data(name=message.text)
        await StateGroup.set_client_description.set()
        await bot.send_message(message.chat.id, 'Введите краткое описание клиента')
    else:
        await bot.send_message(message.chat.id, "Имя слишком длинное!")


@dp.message_handler(state=StateGroup.set_client_description)
async def set_client_description(message: types.Message, state: FSMContext):
    if len(message.text) < 30:
        await state.update_data(description=message.text)
        await StateGroup.set_client_contacts.set()
        await bot.send_message(message.chat.id, 'Введите контактные данные клиента')
    else:
        await bot.send_message(message.chat.id, "Описание клиента слишком длинное!")


@dp.message_handler(state=StateGroup.set_client_contacts)
async def set_client_contacts(message: types.Message, state: FSMContext):
    if len(message.text) > 3:
        await state.update_data(contacts=message.text)
        await StateGroup.set_client_confirm.set()

        client_data = await state.get_data()
        await bot.send_message(message.chat.id, f"Подтвердить добавление клиента? \n"
                                                f"<b>Имя:</b> {client_data['name']}\n"
                                                f"<b>Описание:</b> {client_data['description']}\n"
                                                f"<b>Контакты:</b> {client_data['contacts']}\n", parse_mode='html', reply_markup=keyboard.confirm_keyboard)
    else:
        await bot.send_message(message.chat.id, "Контактные данные слишком короткие!")


@dp.callback_query_handler(state=StateGroup.set_client_confirm)
async def set_client_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        client_data = await state.get_data()
        database.add_client(client_data['name'], client_data['description'], client_data['contacts'], False)

        await bot.send_message(call.from_user.id, "Клиент успешно добавлен!", reply_markup=keyboard.main_keyboard)
    if call.data == "no":
        await bot.send_message(call.from_user.id, "Отмена!", reply_markup=keyboard.main_keyboard)

    await state.reset_data()
    await StateGroup.menu.set()


# edit client
@dp.message_handler(lambda message: message.text == 'Редактировать клиента', state=StateGroup.menu)
async def edit_client(message: types.Message):
    if database.get_client_list():
        await bot.send_message(message.chat.id, "Выберете клиента из списка", reply_markup=keyboard.set_clients_keyboard(database.get_client_list()))
        await StateGroup.update_current_client.set()
    else:
        await bot.send_message(message.chat.id, "Клиентов в базе не найдено!", reply_markup=keyboard.main_keyboard)


@dp.callback_query_handler(state=StateGroup.update_current_client)
async def edit_current_client(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    client_data = database.get_client_from_id(call.data)

    if client_data:
        await state.update_data(client_id=client_data[0])
        await StateGroup.update_client_name.set()
        await bot.send_message(call.from_user.id, "Введите измененное имя клиента", reply_markup=keyboard.edit_keyboard)


@dp.message_handler(state=StateGroup.update_client_name)
async def edit_client_name(message: types.Message, state: FSMContext):
    if len(message.text) < 22:
        await state.update_data(update_name=message.text)
        await StateGroup.update_client_description.set()
        await bot.send_message(message.chat.id, 'Введите новое описание клиента', reply_markup=keyboard.edit_keyboard)
    else:
        await bot.send_message(message.chat.id, "Измененное имя слишком длинное!", reply_markup=keyboard.edit_keyboard)


@dp.message_handler(state=StateGroup.update_client_description)
async def edit_client_description(message: types.Message, state: FSMContext):
    if len(message.text) < 30:
        await state.update_data(update_description=message.text)
        await StateGroup.update_client_contacts.set()
        await bot.send_message(message.chat.id, 'Введите новые контактные данные клиента', reply_markup=keyboard.edit_keyboard)
    else:
        await bot.send_message(message.chat.id, "Новое описание клиента слишком длинное!", reply_markup=keyboard.edit_keyboard)


@dp.message_handler(state=StateGroup.update_client_contacts)
async def edit_client_contacts(message: types.Message, state: FSMContext):
    if len(message.text) > 3:
        await state.update_data(update_contacts=message.text)
        client_data = await state.get_data()
        client = database.get_client_from_id(client_data['client_id'])

        await StateGroup.update_client_confirm.set()

        if client_data['update_name'] == "Пропустить":
            await state.update_data(update_name=client[1])
        if client_data['update_description'] == "Пропустить":
            await state.update_data(update_description=(client[2] if client[2] is not None else None))
        if client_data['update_contacts'] == "Пропустить":
            await state.update_data(update_contacts=(client[3] if client[3] is not None else None))

        client_data = await state.get_data()

        await bot.send_message(message.chat.id, f"Подтвердить изменение информации о клиенте? \n"
                                                f"<b>Имя:</b> {client_data['update_name']}\n"
                                                f"<b>Описание:</b> {client_data['update_description'] if client_data['update_description'] is not None else 'нет'}\n"
                                                f"<b>Контакты:</b> {client_data['update_contacts'] if client_data['update_contacts'] is not None else 'нет'}\n",
                                                parse_mode='html', reply_markup=keyboard.confirm_keyboard)
    else:
        await bot.send_message(message.chat.id, "Новые контактные данные слишком короткие!", reply_markup=keyboard.edit_keyboard)


@dp.callback_query_handler(state=StateGroup.update_client_confirm)
async def edit_client_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        client_data = await state.get_data()
        database.update_client_info(client_data['client_id'], client_data['update_name'], client_data['update_description'], client_data['update_contacts'])

        await bot.send_message(call.from_user.id, "Данные клиента успешно обновлены!", reply_markup=keyboard.main_keyboard)
    if call.data == "no":
        await bot.send_message(call.from_user.id, "Отмена!", reply_markup=keyboard.main_keyboard)

    await state.reset_data()
    await StateGroup.menu.set()


# get client list
@dp.message_handler(lambda message: message.text == 'Список клиентов', state=StateGroup.menu)
async def get_client_list(message: types.Message):
    client_list = database.get_client_list()

    if client_list:
        await bot.send_photo(message.chat.id, await get_clients_dataframe(), reply_markup=keyboard.main_keyboard)
    else:
        await bot.send_message(message.chat.id, "Клиентов в базе не найдено!")


# fast client adding
@dp.message_handler(state=StateGroup.fast_set_client)
async def fast_set_client(message: types.Message, state: FSMContext):
    if len(message.text) > 2:
        new_client = database.add_client(message.text, None, None, True)
        await state.update_data(client_id=new_client[0])
        await bot.send_message(message.chat.id, "Клиент успешно добавлен! Ввести описание и контактные данные вы можете позже.\n"
                                                "\n"
                                                "Подтвердить запись?\n", reply_markup=keyboard.confirm_keyboard)
        await StateGroup.set_record_confirm.set()
    else:
        await bot.send_message(message.chat.id, "Имя слишком короткое!")


# RECORDS
# add record
@dp.message_handler(lambda message: message.text == 'Добавить запись', state=StateGroup.menu)
async def add_record(message: types.Message):
    await bot.send_message(message.chat.id, 'Введите дату и время в формате 2022-11-29 13:00')
    await StateGroup.set_record_date.set()


@dp.message_handler(state=StateGroup.set_record_date)
async def set_record_date(message: types.Message, state: FSMContext):
    if re.match(r'^202[2-5]-[0-1][0-9]-[0-3][0-9] [0-2][0-9]:00$', message.text):
        split_text = message.text.split()
        enter_date = datetime.strptime(split_text[0], "%Y-%m-%d")

        if enter_date > datetime.now() - timedelta(days=1):
            if not database.check_records(split_text[0], split_text[1]):
                await state.update_data(date=split_text[0])
                await state.update_data(time=split_text[1])
                await bot.send_message(message.chat.id, "Выберете клиента", reply_markup=keyboard.client_choose)
                await StateGroup.set_record_client.set()
            else:
                await bot.send_message(message.chat.id, "Время уже занято!")
        else:
            await bot.send_message(message.chat.id, "Невозможно добавить запись на прошедшую дату!")
    else:
        await bot.send_message(message.chat.id, "Некорректный ввод даты и времени!")


@dp.callback_query_handler(state=StateGroup.set_record_client)
async def set_record_client(call: types.CallbackQuery):
    if call.data == "client_from_list":
        if database.get_client_list():
            await bot.send_message(call.from_user.id, "Выберете клиента из списка", reply_markup=keyboard.set_clients_keyboard(database.get_client_list()))
            await StateGroup.set_record_current_client.set()
        else:
            await bot.send_message(call.from_user.id, "Клиентов в базе не найдено!", reply_markup=keyboard.main_keyboard)
            await StateGroup.menu.set()
    if call.data == "new_client":
        await StateGroup.fast_set_client.set()
        await bot.send_message(call.from_user.id, "Введите имя клиента")


@dp.callback_query_handler(state=StateGroup.set_record_current_client)
async def set_record_current_client(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    client_data = database.get_client_from_id(call.data)

    if client_data:
        await state.update_data(client_id=client_data[0])
        record_data = await state.get_data()

        await bot.send_message(call.from_user.id, f"<b>Подтвердить запись для клиента:</b> {client_data[1]} \n"
                                                  f"<b>На:</b> {record_data['date']} {record_data['time']} \n", parse_mode='html', reply_markup=keyboard.confirm_keyboard)
        await StateGroup.set_record_confirm.set()


@dp.callback_query_handler(state=StateGroup.set_record_confirm)
async def set_record_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        client_data = await state.get_data()
        database.add_record(client_data['date'], client_data['time'], False, client_data['client_id'])
        await bot.send_message(call.from_user.id, "Запись успешно добавлена!", reply_markup=keyboard.main_keyboard)
    if call.data == "no":
        await StateGroup.menu.set()
        await bot.send_message(call.from_user.id, "Отмена!", reply_markup=keyboard.main_keyboard)

    await state.reset_data()
    await StateGroup.menu.set()


# remove record
@dp.message_handler(lambda message: message.text == 'Удалить запись', state=StateGroup.menu)
async def remove_record(message: types.Message):
    now_records = database.get_now_records()

    if now_records:
        await bot.send_message(message.chat.id, "Выберете запись:", reply_markup=keyboard.set_records_keyboard(database.get_now_records()))
        await StateGroup.remove_record.set()
    else:
        await bot.send_message(message.chat.id, "Записей для удаления нет!", reply_markup=keyboard.main_keyboard)


@dp.callback_query_handler(state=StateGroup.remove_record)
async def remove_current_record(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    current_record = database.get_now_records()

    for record in current_record:
        if int(call.data) is int(record[0]):
            await state.update_data(record_id=record[0])
            await StateGroup.remove_record_confirm.set()
            await bot.send_message(call.from_user.id, f"Вы действительно хотите удалить запись на {record[1]}?", reply_markup=keyboard.confirm_keyboard)


@dp.callback_query_handler(state=StateGroup.remove_record_confirm)
async def remove_current_record_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        record_data = await state.get_data()
        database.remove_record(record_data['record_id'])

        await bot.send_message(call.from_user.id, "Запись успешно удалена!", reply_markup=keyboard.main_keyboard)
    if call.data == "no":
        await bot.send_message(call.from_user.id, "Отмена!", reply_markup=keyboard.main_keyboard)

    await StateGroup.menu.set()
    await state.reset_data()


# get now records
@dp.message_handler(lambda message: message.text == 'Текущие записи', state=StateGroup.menu)
async def get_now_records(message: types.Message):
    now_records = database.get_now_records()

    if now_records:
        await bot.send_photo(message.chat.id, await get_now_records_dataframe(), reply_markup=keyboard.main_keyboard)
        await remove_files()
    else:
        await bot.send_message(message.chat.id, "Текущих записей нет!", reply_markup=keyboard.main_keyboard)

    await StateGroup.menu.set()


# commit record
@dp.message_handler(lambda message: message.text == 'Завершить запись', state=StateGroup.menu)
async def commit_record(message: types.Message):
    now_records = database.get_now_records()

    if now_records:
        records = []

        for record in now_records:
            record_date = record[1]
            if datetime.strptime(record_date, "%Y-%m-%d") < datetime.now():
                records.append(record)

        if records:
            await bot.send_message(message.chat.id, "Выберете запись:", reply_markup=keyboard.set_records_keyboard(records))
            await StateGroup.commit_current_record.set()
        else:
            await bot.send_message(message.chat.id, "Записей для завершения нет!", reply_markup=keyboard.main_keyboard)
    else:
        await bot.send_message(message.chat.id, "Записей для завершения нет!", reply_markup=keyboard.main_keyboard)


@dp.callback_query_handler(state=StateGroup.commit_current_record)
async def commit_current_record(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    current_record = database.get_now_records()

    for record in current_record:
        if int(call.data) is int(record[0]):
            await state.update_data(client_id=record[3])
            await state.update_data(record_id=record[0])
            await state.update_data(record_datetime=(record[1] + " " + record[2]))
            await StateGroup.commit_record_service.set()
            await bot.send_message(call.from_user.id, "Введите оказанную услугу")


@dp.message_handler(state=StateGroup.commit_record_service)
async def commit_record_service(message: types.Message, state: FSMContext):
    if len(message.text) < 52:
        await state.update_data(service=message.text)
        await StateGroup.commit_record_price.set()
        await bot.send_message(message.chat.id, 'Введите заработок')
    else:
        await bot.send_message(message.chat.id, "Описание услуги слишком длинное!")


@dp.message_handler(state=StateGroup.commit_record_price)
async def commit_record_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        if len(message.text) < 7:
            await state.update_data(price=message.text)
            await StateGroup.commit_record_tips.set()
            await bot.send_message(message.chat.id, "Введите информацию о чаевых", reply_markup=keyboard.edit_keyboard)
        else:
            await bot.send_message(message.chat.id, "Не многовато ли?")
    else:
        await bot.send_message(message.chat.id, "Введите числовое значение")


@dp.message_handler(state=StateGroup.commit_record_tips)
async def commit_record_tips(message: types.Message, state: FSMContext):
    if len(message.text) < 52:
        await state.update_data(tips=message.text)
        await StateGroup.commit_record_additional.set()
        await bot.send_message(message.chat.id, "Введите дополнительную информацию", reply_markup=keyboard.edit_keyboard)
    else:
        await bot.send_message(message.chat.id, "Чаевых слишком много!")


@dp.message_handler(state=StateGroup.commit_record_additional)
async def commit_record_additional(message: types.Message, state: FSMContext):
    if len(message.text) < 52:
        await state.update_data(additional=message.text)
        await StateGroup.commit_record_work_time.set()
        await bot.send_message(message.chat.id, "Введите время выполнения работы в часах. Если вы хотите ввести не целое значение, то исользуйте формат 1.5", reply_markup=types.ReplyKeyboardRemove())
    else:
        await bot.send_message(message.chat.id, "Дополнительная информация слишком длинная!")


@dp.message_handler(state=StateGroup.commit_record_work_time)
async def commit_record_work_time(message: types.Message, state: FSMContext):
    work_time = None

    if re.match(r"^[0-9]+,?[0-9]*$", message.text):
        work_time = message.text.replace(",", ".")
    elif re.match(r"^[0-9]+.?[0-9]*$", message.text):
        work_time = message.text
    else:
        await bot.send_message(message.chat.id, "Некорректный ввод!")

    if work_time:
        if len(message.text) < 5:
            await state.update_data(work_time=work_time)

            record_data = await state.get_data()
            client = database.get_client_from_id(record_data['client_id'])
            space = "\n"
            await StateGroup.commit_record_confirm.set()
            await bot.send_message(message.chat.id, f"Подтвердить завершение записи {record_data['record_datetime']}?\n"
                                                    f"\n"
                                                    f"<b>Клиент:</b> {client[1]} {client[3]}\n"
                                                    f"<b>Услуга:</b> {record_data['service']}\n"
                                                    f"<b>Цена:</b> {record_data['price']} у.е.\n"
                                                    f"{'<b>Чаевые:</b> ' + record_data['tips'] + ' у.е.' + space if record_data['tips'] != 'Пропустить' else ''}"
                                                    f"{'<b>Дополнительно:</b> ' + record_data['additional'] + space if record_data['additional'] != 'Пропустить' else ''}"
                                                    f"<b>Время работы:</b> {record_data['work_time']} ч", reply_markup=keyboard.confirm_keyboard, parse_mode='html')
        else:
            await bot.send_message(message.chat.id, "Не слишком ли долго?")


async def set_expense_data(call: int, operation: str):
    expense_material = database.get_expense_from_id(call)[0]
    if call not in keyboard.expense_materials:
        keyboard.expense_materials[call] = 0

    messages = []

    if keyboard.expense_materials[call] < expense_material[5] and expense_material[6] > 0:
        if operation == "add":
            if keyboard.expense_materials[call] != 0:
                keyboard.expense_materials[call] -= expense_material[7]
            else:
                keyboard.expense_materials[call] = expense_material[6] - expense_material[7]

            messages.append(f"Выбрано: {expense_material[4]}\n"
                            f"\n")
            return messages
        elif operation == "delete":
            if keyboard.expense_materials[call] != 0:
                keyboard.expense_materials[call] += expense_material[7]
            else:
                keyboard.expense_materials[call] = expense_material[6] + expense_material[7]
            messages.remove(f"Выбрано: {expense_material[4]}\n"
                            f"\n")
            return messages


@dp.callback_query_handler(state=StateGroup.commit_record_expense)
async def commit_record_expense_materials(call: types.CallbackQuery, state: FSMContext):
    if call.data != "finish":
        data = call.data.split(" ")
        message = await set_expense_data(data[0], data[1])

        message_from_user = call.message.text + "\n"

        for m in message:
            message_from_user += m

        await call.message.edit_text(text=message_from_user, reply_markup=keyboard.set_expense_materials_keyboard(database.get_expense_material_count()))
        await call.answer()
    else:
        record_data = await state.get_data()
        await StateGroup.commit_record_confirm.set()
        await call.message.edit_text(f"{call.message.text}\n"
                                     f"\n"
                                     f"Подтвердить завершение записи {record_data['record_datetime']}?\n", reply_markup=keyboard.confirm_keyboard, parse_mode='html')


@dp.callback_query_handler(state=StateGroup.commit_record_confirm)
async def commit_record_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        record_data = await state.get_data()
        if record_data['tips'] == "Пропустить":
            await state.update_data(tips="Нет")
        if record_data['additional'] == "Пропустить":
            await state.update_data(additional="Нет")

        record_data = await state.get_data()
        database.commit_record(record_data['record_id'], record_data['service'], record_data['price'], record_data['tips'], record_data['additional'], record_data['work_time'])
        database.add_client_visits_count(record_data['client_id'])

        if database.get_expense_material_count():
            for value in keyboard.expense_materials:
                database.set_expense_material_count(keyboard.expense_materials[value], value)

        keyboard.expense_materials.clear()
        await bot.send_message(call.from_user.id, "Запись успешно завершена!", reply_markup=keyboard.main_keyboard)
    if call.data == "no":
        await bot.send_message(call.from_user.id, "Отмена!", reply_markup=keyboard.main_keyboard)

    await StateGroup.menu.set()
    await state.reset_data()


# ANALYTIC
# get data on current delta
async def get_schedule_data(days: int, index: int):
    now_date = datetime.now()
    last_date = now_date - timedelta(days=float(days - 1))
    now_date_str = now_date.strftime("%Y-%m-%d")
    last_date_str = last_date.strftime("%Y-%m-%d")

    some_days = 0
    dates_list = []

    while some_days < days:
        last_day = now_date - timedelta(days=float(some_days))
        dates_list.append(last_day.strftime("%Y-%m-%d"))
        some_days += 1

    data_dict = {}

    for d in dates_list:
        data_dict[d] = 0

    data = database.get_records_delta_data(last_date_str, now_date_str)
    sort_data = sorted(data, key=lambda date: date[1])

    for value in sort_data:
        some_date = value[1]
        current_value = value[index]
        if some_date not in data_dict:
            data_dict[some_date] = current_value
        elif some_date in data_dict:
            data_dict[some_date] += current_value
        else:
            data_dict[some_date] = 0

    return data_dict


async def get_last_time(days_count: int):
    days = 0
    last_days = []
    now_date = datetime.now()

    while days < days_count:
        last_day = now_date - timedelta(days=float(days))
        last_days.append(last_day.strftime("%d.%m"))
        days += 1

    return last_days


async def get_data_schedule(days_count: int, value: int, label: str):
    dates = await get_schedule_data(days_count, value)
    days = await get_last_time(days_count)
    data = []

    for date in dates:
        data.append(dates[date])

    days.reverse()
    data.reverse()

    figure = px.line(x=days, y=data, title=label, markers=True)
    figure.update_xaxes(title="")
    figure.update_yaxes(title="")
    figure.update_layout(autosize=False,
                         width=1280,
                         height=960,
                         font=dict(
                             size=20
                         ))
    figure.write_image("db/graph.png")

    return open("db/graph.png", "rb")


async def get_alltime_data_schedule(value: int, label: str):
    values = database.get_records_all_data()
    data = []
    days = []

    for d in values:
        data.append(d[value])
        days.append(d[1])

    figure = go.Figure(go.Bar(
        x=days,
        y=data
    ))
    figure.update_xaxes(title="", visible=True)
    figure.update_yaxes(title="")
    figure.update_layout(title=label,
                         autosize=False,
                         width=1280,
                         height=960,
                         font=dict(
                             size=20
                         ))
    figure.write_image("db/graph.png")

    return open("db/graph.png", "rb")


async def get_records_dataframe(delta_days: int):
    csv_file = open("db/records.csv", "w")
    csv_file.truncate()
    csv_file.close()

    last_delta_days = delta_days - 1
    now_date = datetime.now()
    last_date = now_date - timedelta(days=float(last_delta_days))

    now_date_str = now_date.strftime("%Y-%m-%d")
    last_date_str = last_date.strftime("%Y-%m-%d")

    if database.get_csv_records(last_date_str, now_date_str):
        dataframe = pd.read_csv("db/records.csv")
        table_height = await get_records_table_height(dataframe)
        figure = go.Figure(data=[go.Table(
            columnwidth=[300, 200, 500, 500, 150, 400, 500, 150],
            header=dict(
                values=['<b>Дата</b>', '<b>Время</b>', '<b>Клиент</b>', '<b>Услуга</b>', '<b>Цена</b>', '<b>Чаевые</b>', '<b>Дополнительно</b>', '<b>Время</b>'],
                align=['center'],
                height=40
            ),
            cells=dict(
                values=dataframe.transpose().values.tolist(),
                align=['center'],
                height=30
            ),
        )])
        figure.update_layout(autosize=False, margin={'l': 0, 'r': 0, 't': 0, 'b': 0}, width=1280, height=table_height)
        figure.write_image("db/records.png")
        return open("db/records.png", "rb")
    else:
        return False


async def get_all_records_dataframe():
    csv_file = open("db/all_records.csv", "w")
    csv_file.truncate()
    csv_file.close()

    if database.get_csv_all_records():
        dataframe = pd.read_csv("db/all_records.csv")
        dataframe.to_excel("db/all_records.xlsx")
        return True
    else:
        return False


async def get_clients_dataframe():
    csv_file = open("db/clients.csv", "w")
    csv_file.truncate()
    csv_file.close()

    if database.get_client_list():
        database.get_csv_clients()
        dataframe = pd.read_csv("db/clients.csv")
        table_height = await get_clients_table_height(dataframe)
        figure = go.Figure(data=[go.Table(
            columnwidth=[350, 600, 600, 150],
            header=dict(
                values=['<b>Имя</b>', '<b>Описание клиента</b>', '<b>Контактные данные</b>', '<b>Количество посещений</b>'],
                align=['center'],
                height=40
            ),
            cells=dict(
                values=dataframe.transpose().values.tolist(),
                align=['center'],
                height=30
            ),
        )])
        figure.update_layout(autosize=False, margin={'l': 0, 'r': 0, 't': 0, 'b': 0}, width=1280, height=table_height)
        figure.write_image("db/clients.png")
        return open("db/clients.png", "rb")


async def get_expenses_dataframe():
    csv_file = open("db/expenses.csv", "w")
    csv_file.truncate()
    csv_file.close()

    if database.get_expenses():
        database.get_csv_expenses()
        dataframe = pd.read_csv("db/expenses.csv")
        table_height = await get_expenses_table_height(dataframe)
        figure = go.Figure(data=[go.Table(
            columnwidth=[250, 150, 300, 400, 200, 200, 500],
            header=dict(
                values=['<b>Тип</b>', '<b>Стоимость</b>', '<b>Дата</b>', '<b>Назавние</b>', '<b>Количество</b>', '<b>Расход на клиента</b>', '<b>Описание</b>'],
                align=['center'],
                height=40
            ),
            cells=dict(
                values=dataframe.transpose().values.tolist(),
                align=['center'],
                height=30
            ),
        )])
        figure.update_layout(autosize=False, margin={'l': 0, 'r': 0, 't': 0, 'b': 0}, width=1280, height=table_height)
        figure.write_image("db/expenses.png")
        return open("db/expenses.png", "rb")


async def get_now_records_dataframe():
    def get_week_days():
        week_days = {
            "Monday": 0,
            "Tuesday": 1,
            "Wednesday": 2,
            "Thursday": 3,
            "Friday": 4,
            "Saturday": 5,
            "Sunday": 6
        }

        week = {}
        week_dates = []

        now_date = datetime.now()
        down_index = len(week_days) - (7 - now_date.weekday())
        first_week_day = now_date - timedelta(days=float(down_index))

        for day in week_days:
            week[day] = None

        date_index = 0
        day_index = 0

        while date_index < 7:
            next_date = first_week_day + timedelta(days=float(date_index))
            week_dates.append(next_date.strftime("%Y-%m-%d"))
            date_index += 1

        for day in week:
            week[day] = week_dates[day_index]
            day_index += 1

        return week

    def get_records_time(week: {}):
        times = []
        index = 0

        for day in week:
            some_day = datetime.strptime(week[day], "%Y-%m-%d")

            while index < 12:
                new_time = datetime.combine(some_day, time(9, 0)) + timedelta(hours=index)
                times.append(new_time.strftime("%H:%M"))
                index += 1

        return times

    week_data = get_week_days()

    csv_file = open("db/now_records.csv", "w")
    csv_file.truncate()
    csv_file.close()

    if database.get_now_records():
        database.get_csv_now_records(get_records_time(week_data), week_data)
        dataframe = pd.read_csv("db/now_records.csv")
        table_height = await get_now_records_table_height(dataframe)
        figure = go.Figure(data=[go.Table(
            columnwidth=[150, 200, 200, 200, 200, 200, 200],
            header=dict(
                values=['<b>Время</b>', '<b>Понедельник</b>', '<b>Втроник</b>', '<b>Среда</b>', '<b>Четверг</b>', '<b>Пятница</b>', '<b>Суббота</b>', '<b>Воскресенье</b>'],
                align=['center'],
                height=40
            ),
            cells=dict(
                values=dataframe.transpose().values.tolist(),
                align=['center'],
                height=30
            ),
        )])
        figure.update_layout(autosize=False, margin={'l': 0, 'r': 0, 't': 0, 'b': 0}, width=1280, height=table_height)
        figure.write_image("db/now_records.png")
        return open("db/now_records.png", "rb")


async def get_records_table_height(dataframe):
    rows = []
    double_height = 0

    for index, data in dataframe.iterrows():
        rows.append(index)
        if len(str(data[2])) > 33 or len(str(data[3])) > 30 or len(str(data[5])) > 30 or len(str(data[6])) > 30:
            double_height += 1

    one_rows_count = (len(rows) - double_height)
    one_rows = one_rows_count * 30
    double_rows = (double_height * 1.5 * 30) + len(rows) + 2

    return 40 + one_rows + double_rows


async def get_clients_table_height(dataframe):
    rows = []
    double_height = 0

    for index, data in dataframe.iterrows():
        rows.append(index)
        if len(str(data[0])) > 40 or len(str(data[1])) > 50 or len(str(data[2])) > 50:
            double_height += 1

    one_rows_count = (len(rows) - double_height)
    one_rows = one_rows_count * 30
    double_rows = double_height * 48

    return 45 + one_rows + double_rows


async def get_expenses_table_height(dataframe):
    rows = []
    double_height = 0

    for index, data in dataframe.iterrows():
        rows.append(index)
        if len(str(data[3])) > 28 or len(str(data[6])) > 28:
            double_height += 1

    one_rows_count = (len(rows) - double_height)
    one_rows = one_rows_count * 30
    double_rows = double_height * 48

    return 45 + one_rows + double_rows


async def get_now_records_table_height(dataframe):
    rows = []
    double_height = 0

    for index, data in dataframe.iterrows():
        rows.append(index)
        if len(data[2]) > 30 or len(data[3]) > 30 or len(data[4]) > 30 or len(data[5]) > 30 or len(data[5]) > 30 or len(data[6]) > 30 or len(data[7]) > 30:
            double_height += 1

    one_rows_count = (len(rows) - double_height)
    one_rows = one_rows_count * 30
    double_rows = double_height * 1.5 * 30

    return 40 + one_rows + double_rows


async def remove_files():
    if os.path.exists('db/graph.png'): os.remove('db/graph.png')
    if os.path.exists('db/records.png'): os.remove('db/records.png')
    if os.path.exists('db/clients.png'): os.remove('db/clients.png')
    if os.path.exists('db/expenses.png'): os.remove('db/expenses.png')
    if os.path.exists('db/now_records.png'): os.remove('db/now_records.png')

    if os.path.exists('db/all_records.csv'): os.remove('db/all_records.csv')
    if os.path.exists('db/records.csv'): os.remove('db/records.csv')
    if os.path.exists('db/clients.csv'): os.remove('db/clients.csv')
    if os.path.exists('db/expenses.csv'): os.remove('db/expenses.csv')
    if os.path.exists('db/now_records.csv'): os.remove('db/now_records.csv')

    if os.path.exists('db/all_records.xlsx'): os.remove('db/all_records.xlsx')


# get week data
@dp.message_handler(lambda message: message.text == 'За неделю', state=StateGroup.analytics_get_menu)
async def get_week_data(message: types.Message, state: FSMContext):
    mode = await state.get_data()

    if database.get_records_all_data():
        if mode['user_data'] == "График доходов 💶":
            await bot.send_photo(message.chat.id, await get_data_schedule(7, 6, 'График заработка за неделю'), reply_markup=keyboard.main_keyboard)
        elif mode['user_data'] == "График времени ⏳":
            await bot.send_photo(message.chat.id, await get_data_schedule(7, 9, 'График времени работы за неделю'), reply_markup=keyboard.main_keyboard)
        elif mode['user_data'] == "Завершенные записи ✅":
            await bot.send_photo(message.chat.id, await get_records_dataframe(7), reply_markup=keyboard.main_keyboard)
    else:
        await bot.send_message(message.chat.id, "Недостаточно данных!", reply_markup=keyboard.main_keyboard)

    await StateGroup.menu.set()
    await state.reset_data()
    await remove_files()


# get month data
@dp.message_handler(lambda message: message.text == 'За месяц', state=StateGroup.analytics_get_menu)
async def get_month_data(message: types.Message, state: FSMContext):
    mode = await state.get_data()

    if database.get_records_all_data():
        if mode['user_data'] == "График доходов 💶":
            await bot.send_photo(message.chat.id, await get_data_schedule(31, 6, 'График заработка за месяц'), reply_markup=keyboard.main_keyboard)
        elif mode['user_data'] == "График времени ⏳":
            await bot.send_photo(message.chat.id, await get_data_schedule(31, 9, 'График времени работы за месяц'), reply_markup=keyboard.main_keyboard)
        elif mode['user_data'] == "Завершенные записи ✅":
            await bot.send_photo(message.chat.id, await get_records_dataframe(31), reply_markup=keyboard.main_keyboard)
    else:
        await bot.send_message(message.chat.id, "Недостаточно данных!", reply_markup=keyboard.main_keyboard)

    await StateGroup.menu.set()
    await state.reset_data()
    await remove_files()


# get all data
@dp.message_handler(lambda message: message.text == 'За все время', state=StateGroup.analytics_get_menu)
async def get_all_data(message: types.Message, state: FSMContext):
    mode = await state.get_data()

    if database.get_records_all_data():
        if mode['user_data'] == "График доходов 💶":
            await bot.send_photo(message.chat.id, await get_alltime_data_schedule(6, 'График заработка за все время'), reply_markup=keyboard.main_keyboard)
        elif mode['user_data'] == "График времени ⏳":
            await bot.send_photo(message.chat.id, await get_alltime_data_schedule(9, 'График времени работы за все время'), reply_markup=keyboard.main_keyboard)
        elif mode['user_data'] == "Завершенные записи ✅":
            if await get_all_records_dataframe():
                await bot.send_document(message.chat.id, open("db/all_records.xlsx", "rb"), reply_markup=keyboard.main_keyboard)
            else:
                await bot.send_message(message.chat.id, "Ошибка конвертации!", reply_markup=keyboard.main_keyboard)
    else:
        await bot.send_message(message.chat.id, "Недостаточно данных!", reply_markup=keyboard.main_keyboard)

    await StateGroup.menu.set()
    await state.reset_data()
    await remove_files()


# add expense
@dp.message_handler(lambda message: message.text == 'Добавить расход', state=StateGroup.analytics_expense_menu)
async def add_expense_material(message: types.Message):
    await StateGroup.analytics_expense_price_menu.set()
    await bot.send_message(message.chat.id, "Введите сумму расходов", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=StateGroup.analytics_expense_price_menu)
async def set_expense_price(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(expense_price=message.text)
        await StateGroup.analytics_expense_date_menu.set()
        await bot.send_message(message.chat.id, "Введите дату в формате 2022-11-29")
    else:
        await bot.send_message(message.chat.id, "Введите числовое значение!")


@dp.message_handler(state=StateGroup.analytics_expense_date_menu)
async def set_expense_date(message: types.Message, state: FSMContext):
    if re.match(r'^202[2-5]-[0-1][0-9]-[0-3][0-9]$', message.text):
        await state.update_data(expense_date=message.text)
        await StateGroup.analytics_expense_type_menu.set()
        await bot.send_message(message.chat.id, "Выберете расход", reply_markup=keyboard.expense_type)
    else:
        await bot.send_message(message.chat.id, "Некорректный ввод даты и времени!")


@dp.callback_query_handler(state=StateGroup.analytics_expense_type_menu)
async def set_expense_type(call: types.CallbackQuery, state: FSMContext):
    if call.data == "material":
        await StateGroup.analytics_set_expense_material_name.set()
        await bot.send_message(call.from_user.id, "Введите название расходного материала")
        await state.update_data(expense_type="Материал")
    if call.data == "salary":
        await StateGroup.analytics_set_expense_description.set()
        await bot.send_message(call.from_user.id, "Введите имя и должность сотрудника")
        await state.update_data(expense_type="Зарплата")
    if call.data == "transportation":
        await StateGroup.analytics_set_expense_description.set()
        await bot.send_message(call.from_user.id, "Введите сведения о перевозке")
        await state.update_data(expense_type="Перевозка")
    if call.data == "tax":
        await StateGroup.analytics_set_expense_description.set()
        await bot.send_message(call.from_user.id, "Введите название налога")
        await state.update_data(expense_type="Налог")


# add expense material
@dp.message_handler(state=StateGroup.analytics_set_expense_material_name)
async def add_expense_material_name(message: types.Message, state: FSMContext):
    if len(message.text) > 2:
        await state.update_data(expense_name=message.text)
        await StateGroup.analytics_set_expense_material_count.set()
        await bot.send_message(message.chat.id, "Введите количество расходного материала")
    else:
        await bot.send_message(message.chat.id, "Название расходного материала слишком короткое!")


@dp.message_handler(state=StateGroup.analytics_set_expense_material_count)
async def add_expense_material_count(message: types.Message, state: FSMContext):
    if re.match(r"^[0-9]+,?[0-9]*$", message.text):
        await state.update_data(expense_count=float(message.text))
        await StateGroup.analytics_set_expense_material_consumption.set()
        await bot.send_message(message.chat.id, "Введите расход материала на одного клиента. Если вы хотите ввести не целое значение, то исользуйте формат 1.5.\n"
                                                "Если же он неизвестен, то нажмите <b>Пропустить</b>\n", reply_markup=keyboard.edit_keyboard, parse_mode='html')
    else:
        await bot.send_message(message.chat.id, "Введите числовое значение!")


@dp.message_handler(state=StateGroup.analytics_set_expense_material_consumption)
async def add_expense_material_consumption(message: types.Message, state: FSMContext):
    if re.match(r"^[0-9]+,?[0-9]*$", message.text) or message.text == 'Пропустить':
        if len(message.text) < 6 or message.text == 'Пропустить':
            await state.update_data(expense_consumption=message.text)
            await StateGroup.analytics_set_expense_material_confirm.set()

            expense_data = await state.get_data()
            await bot.send_message(message.chat.id, f"Подтвердить добавление расходного материала?\n"
                                                    f"<b>Дата:</b> {expense_data['expense_date']}\n"
                                                    f"<b>Название:</b> {expense_data['expense_name']}\n"
                                                    f"<b>Стоимость:</b> {expense_data['expense_price']} у.е.\n"
                                                    f"<b>Количество:</b> {expense_data['expense_count']}\n"
                                                    f"{'<b>Расход:</b> ' + expense_data['expense_consumption'] if expense_data['expense_consumption'] != 'Пропустить' else ''}\n", parse_mode='html', reply_markup=keyboard.confirm_keyboard)
        else:
            await bot.send_message(message.chat.id, "Не многовато ли?")
    else:
        await bot.send_message(message.chat.id, "Введите числовое значение!")


@dp.callback_query_handler(state=StateGroup.analytics_set_expense_material_confirm)
async def add_expense_material_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        expense_data = await state.get_data()
        database.set_expense_material(expense_data['expense_type'], expense_data['expense_name'], expense_data['expense_price'], expense_data['expense_date'], expense_data['expense_count'], expense_data['expense_consumption'] if expense_data['expense_consumption'] != 'Пропустить' else None)
        await bot.send_message(call.from_user.id, "Расходный материал успешно добавлен!", reply_markup=keyboard.main_keyboard)
    if call.data == "no":
        await bot.send_message(call.from_user.id, "Отмена!", reply_markup=keyboard.main_keyboard)

    await StateGroup.menu.set()
    await state.reset_data()


# remove expenses
@dp.message_handler(lambda message: message.text == 'Удалить расход', state=StateGroup.analytics_expense_menu)
async def remove_expense(message: types.Message):
    if database.get_expenses():
        await bot.send_message(message.chat.id, "Выберете расход", reply_markup=keyboard.set_expenses_keyboard(database.get_expenses()))
        await StateGroup.analytics_remove_expense.set()
    else:
        await bot.send_message(message.chat.id, "Расходы не внесены!")


@dp.callback_query_handler(state=StateGroup.analytics_remove_expense)
async def remove_current_expense(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(expense_id=call.data)
    expense = database.get_expense_from_id(call.data)
    await bot.send_message(call.from_user.id, f"Удалить расход от {expense[0][3]}: {expense[0][4] if expense[0][1] == 'Материал' else expense[0][9]}?", reply_markup=keyboard.confirm_keyboard)
    await StateGroup.analytics_remove_expense_confirm.set()


@dp.callback_query_handler(state=StateGroup.analytics_remove_expense_confirm)
async def remove_expense_material_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        expense_data = await state.get_data()
        database.remove_expense(expense_data['expense_id'])
        await bot.send_message(call.from_user.id, "Расходный материал успешно удален!", reply_markup=keyboard.main_keyboard)
    if call.data == "no":
        await bot.send_message(call.from_user.id, "Отмена!", reply_markup=keyboard.main_keyboard)

    await StateGroup.menu.set()
    await state.reset_data()


# get expenses
@dp.message_handler(lambda message: message.text == 'Список расходов', state=StateGroup.analytics_expense_menu)
async def get_expenses_list(message: types.Message):
    if database.get_expenses():
        await bot.send_photo(message.chat.id, await get_expenses_dataframe(), reply_markup=keyboard.main_keyboard)
        await remove_files()
    else:
        await bot.send_message(message.chat.id, "Расходы не внесены!")


# add expenses
@dp.message_handler(state=StateGroup.analytics_set_expense_description)
async def add_expense_description(message: types.Message, state: FSMContext):
    if len(message.text) > 2:
        await state.update_data(expense_description=message.text)
        await StateGroup.analytics_set_expense_confirm.set()
        expense_data = await state.get_data()
        string_expense_type = ""

        if expense_data['expense_type'] == "Зарплата":
            string_expense_type = "зраплате"
        elif expense_data['expense_type'] == "Перевозка":
            string_expense_type = "перевозке"
        elif expense_data['expense_type'] == "Налог":
            string_expense_type = "налоге"

        await state.update_data(string_type=string_expense_type)

        await bot.send_message(message.chat.id, f"Подтвердить внесение информации о {string_expense_type}?\n"
                                                f"<b>Описание:</b> {expense_data['expense_description']}\n"
                                                f"<b>Расход:</b> {expense_data['expense_price']} у.е.\n"
                                                f"<b>Дата: </b> {expense_data['expense_date']}", reply_markup=keyboard.confirm_keyboard, parse_mode='html')
    else:
        await bot.send_message(message.chat.id, "Данные о сотруднике слишком короткие!")


@dp.callback_query_handler(state=StateGroup.analytics_set_expense_confirm)
async def add_expense_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        expense_data = await state.get_data()
        database.set_expenses(expense_data['expense_type'], expense_data['expense_price'], expense_data['expense_date'], expense_data['expense_description'])
        await bot.send_message(call.from_user.id, f"Информация о {expense_data['string_type']} успешно добавлена!", reply_markup=keyboard.main_keyboard)
    if call.data == "no":
        await bot.send_message(call.from_user.id, "Отмена!", reply_markup=keyboard.main_keyboard)

    await StateGroup.menu.set()
    await state.reset_data()


# get all finance data
@dp.message_handler(lambda message: message.text == 'Доходы 💰', state=StateGroup.analytics_general_menu)
async def get_all_finance_data(message: types.Message, state: FSMContext):
    try:
        database.get_expense_material_count()
        money = database.get_finance_sum()
        tips = database.get_tips_sum()

        await bot.send_message(message.chat.id, f"<b>Сумма дохода:</b> {money} у.е.\n"
                                                f"<b>Сумма чаевых:</b> {tips} у.е.\n"
                                                f"<b>Общий заработок:</b> {money + tips} у.е.\n", reply_markup=keyboard.main_keyboard, parse_mode='html')
    except:
        await bot.send_message(message.chat.id, "Недостаточно данных для вывода информации о доходах! Завершите хотя-бы одну запись.", reply_markup=keyboard.main_keyboard)
    await StateGroup.menu.set()
    await state.reset_data()


# get profitability
@dp.message_handler(lambda message: message.text == 'Рентабельность 📈', state=StateGroup.analytics_general_menu)
async def get_profitability_data(message: types.Message):
    try:
        expenses = database.get_expenses()
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

        data = database.get_profitability_data(last_date_str, now_date_str)
        await bot.send_message(message.chat.id, f"Рентабельность и чистая прибыль вычисляется в промежуток от даты последней крупной закупки, до сегодняшнего дня без учета чаевых.\n"
                                                f"\n"
                                                f"<b>Рентабельность:</b> {data[1]}%\n"
                                                f"<b>Чистая прибыль:</b> {data[0] if data[0] > 0 else 'отсутствует'} у.е.\n", reply_markup=keyboard.main_keyboard, parse_mode='html')
    except:
        await bot.send_message(message.chat.id, "Недостаточно данных для вычисления рентабельности! Должны быть внесены сведения о прибыли и расходах.", reply_markup=keyboard.main_keyboard)
    await StateGroup.menu.set()


# NOTIFICATIONS
async def send_schedule():
    users = database.get_user_id()

    for user in users:
        await bot.send_photo(user[0], await get_data_schedule(7, 6, 'График заработка за неделю'))
        await bot.send_photo(user[0], await get_data_schedule(7, 9, 'График времени работы за неделю'))


async def scheduler():
    aioschedule.every().sunday.at("06:00").do(send_schedule)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
