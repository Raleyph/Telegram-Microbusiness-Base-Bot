from aiogram import Router
from aiogram import types
from aiogram import F
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import database as db
import keyboards as kb
import graphic_representation as gp

router = Router()


class ClientStates(StatesGroup):
    set_client_name = State()
    set_client_description = State()
    set_client_contacts = State()
    set_client_confirm = State()
    select_current_client = State()
    update_client_name = State()
    update_client_description = State()
    update_client_contacts = State()
    update_client_confirm = State()


# add
@router.message(Text(text="Добавить клиента"), F.text)
async def add_client(message: types.Message, state: FSMContext):
    await state.set_state(ClientStates.set_client_name)
    await message.answer("Введите имя клиента", reply_markup=types.ReplyKeyboardRemove)


@router.message(F.text, ClientStates.set_client_name)
async def set_client_name(message: types.Message, state: FSMContext):
    if len(message.text) < 22:
        await state.update_data(client_name=message.text)
        await state.set_state(ClientStates.set_client_description)
        await message.answer("Введите краткое описание клиента")
    else:
        await message.answer("Имя слишком длинное!")


@router.message(F.text, ClientStates.set_client_description)
async def set_client_description(message: types.Message, state: FSMContext):
    if len(message.text) < 35:
        await state.update_data(client_description=message.text)
        await state.set_state(ClientStates.set_client_contacts)
        await message.answer("Введите контактные данные клиента")
    else:
        await message.answer("Описание слишком длинное!")


@router.message(F.text, ClientStates.set_client_contacts)
async def set_client_contacts(message: types.Message, state: FSMContext):
    if len(message.text) > 3:
        if db.check_contacts(message.text):
            await state.update_data(client_contacts=message.text)
            await state.set_state(ClientStates.set_client_confirm)

            client_data = await state.get_data()
            await message.answer(f"Подтвердить добавление клиента?\n"
                                 f"\n"
                                 f"<b>Имя:</b> {client_data['client_name']}\n"
                                 f"<b>Описание:</b> {client_data['client_description']}\n"
                                 f"<b>Контакты:</b> {client_data['client_contacts']}",
                                 reply_markup=kb.get_confirm_keyboard(), parse_mode='html')
        else:
            await message.answer("Такие контактные данные уже имеются в базе!")
    else:
        await message.answer("Контактные данные слишком короткие!")


@router.callback_query(ClientStates.set_client_confirm)
async def set_client_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        client_data = await state.get_data()
        db.add_client(client_data['client_name'], client_data['client_description'], client_data['client_contacts'], False)
        await call.message.answer("Клиент успешно добавлен!", reply_markup=kb.get_main_keyboard())
    elif call.data == "no":
        await call.message.answer("Отмена!", reply_markup=kb.get_main_keyboard())

    await state.clear()


# edit
@router.message(Text(text="Редактировать клиента"), F.text)
async def update_client(message: types.Message, state: FSMContext):
    client_list = db.get_client_list()

    if client_list:
        await state.set_state(ClientStates.select_current_client)
        await message.answer("Выберете клиента из списка", reply_markup=kb.get_clients_choose_keyboard(client_list))
    else:
        await message.answer("Клиентов в базе не найдено!", reply_markup=kb.get_main_keyboard())
        await state.clear()


@router.callback_query(ClientStates.select_current_client)
async def select_current_client(call: types.CallbackQuery, state: FSMContext):
    client_data = db.get_client_from_id(call.data)

    if client_data:
        await state.update_data(update_client_id=call.data)
        await state.set_state(ClientStates.update_client_name)
        await call.message.answer("Введите измененное имя клиента", reply_markup=kb.get_skip_button())


@router.message(F.text, ClientStates.update_client_name)
async def update_client_name(message: types.message, state: FSMContext):
    if len(message.text) < 22:
        await state.update_data(update_client_name=message.text)
        await state.set_state(ClientStates.update_client_description)
        await message.answer("Введите измененное краткое описание клиента", reply_markup=kb.get_skip_button())
    else:
        await message.answer("Имя слишком длинное!")


@router.message(F.text, ClientStates.update_client_description)
async def update_client_description(message: types.Message, state: FSMContext):
    if len(message.text) < 35:
        await state.update_data(update_client_description=message.text)
        await state.set_state(ClientStates.update_client_contacts)
        await message.answer("Введите новые контактные данные клиента", reply_markup=kb.get_skip_button())
    else:
        await message.answer("Новое описание слишком длинное!")


@router.message(F.text, ClientStates.update_client_contacts)
async def update_client_contacts(message: types.Message, state: FSMContext):
    if len(message.text) > 3:
        await state.update_data(update_client_contacts=message.text)

        new_client_data = await state.get_data()
        current_client = db.get_client_from_id(new_client_data['update_client_id'])
        skip_count = 0

        if new_client_data['update_client_name'] == "Пропустить":
            await state.update_data(update_client_name=current_client[1])
            skip_count += 1
        if new_client_data['update_client_description'] == "Пропустить":
            await state.update_data(update_client_description=current_client[2])
            skip_count += 1
        if new_client_data['update_client_contacts'] == "Пропустить":
            await state.update_data(update_client_contacts=current_client[3])
            skip_count += 1

        if skip_count < 3:
            await state.set_state(ClientStates.update_client_confirm)

            new_client_data = await state.get_data()
            await message.answer(f"Подтвердить изменение информации о клиенте?\n"
                                 f"\n"
                                 f"<b>Имя:</b> {new_client_data['update_client_name']}\n"
                                 f"<b>Описание:</b> {new_client_data['update_client_description']}\n"
                                 f"<b>Контакты:</b> {new_client_data['update_client_contacts']}",
                                 reply_markup=kb.get_confirm_keyboard(), parse_mode='html')
        else:
            await message.answer("Отмена!", reply_markup=kb.get_main_keyboard())
            await state.clear()
    else:
        await message.answer("Новые контактные данные слишком короткие!")


@router.callback_query(ClientStates.update_client_confirm)
async def update_client_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data == "yes":
        new_client_data = await state.get_data()
        db.update_client_info(new_client_data['update_client_id'], new_client_data['update_client_name'],
                              new_client_data['update_client_description'], new_client_data['update_client_contacts'])
        await call.message.answer("Информация о клиенте успешно изменена!", reply_markup=kb.get_main_keyboard())
    elif call.data == "no":
        await call.message.answer("Отмена!", reply_markup=kb.get_main_keyboard())

    await state.clear()


# get list
@router.message(Text(text="Список клиентов"), F.text)
async def get_client_list(message: types.message, state: FSMContext):
    client_list = db.get_client_list()

    if client_list:
        image = types.FSInputFile(gp.get_clients_dataframe())
        await message.answer_photo(image, reply_markup=kb.get_main_keyboard())
    else:
        await message.answer("Клиентов в базе не найдено!", reply_markup=kb.get_main_keyboard())

    await state.clear()
