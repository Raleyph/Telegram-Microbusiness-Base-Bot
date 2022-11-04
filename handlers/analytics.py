from aiogram import Router
from aiogram import types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
import graphic_representation as gp

router = Router()


@router.message(Text(text="За неделю"))
async def get_week_data(message: types.Message, state: FSMContext):
    state_data = await state.get_data()

    if db.get_records_all_data():
        if state_data['action'] == "График доходов 💶":
            image = types.FSInputFile(gp.get_data_schedule(7, 6, "График заработка за неделю"))
            await message.answer_photo(image, reply_markup=kb.get_main_keyboard())
        elif state_data['action'] == "График времени ⏳":
            image = types.FSInputFile(gp.get_data_schedule(7, 9, "График времени за неделю"))
            await message.answer_photo(image, reply_markup=kb.get_main_keyboard())
        elif state_data['action'] == "Завершенные записи ✅":
            image = types.FSInputFile(gp.get_completed_records_dataframe(7))
            await message.answer_photo(image, reply_markup=kb.get_main_keyboard())

    await state.clear()


@router.message(Text(text="За месяц"))
async def get_month_data(message: types.Message, state: FSMContext):
    state_data = await state.get_data()

    if db.get_records_all_data():
        if state_data['action'] == "График доходов 💶":
            image = types.FSInputFile(gp.get_data_schedule(31, 6, "График заработка за месяц"))
            await message.answer_photo(image, reply_markup=kb.get_main_keyboard())
        elif state_data['action'] == "График времени ⏳":
            image = types.FSInputFile(gp.get_data_schedule(31, 9, "График времени за месяц"))
            await message.answer_photo(image, reply_markup=kb.get_main_keyboard())
        elif state_data['action'] == "Завершенные записи ✅":
            image = types.FSInputFile(gp.get_completed_records_dataframe(31))
            await message.answer_photo(image, reply_markup=kb.get_main_keyboard())

    await state.clear()


@router.message(Text(text="За все время"))
async def get_month_data(message: types.Message, state: FSMContext):
    state_data = await state.get_data()

    if db.get_records_all_data():
        if state_data['action'] == "График доходов 💶":
            image = types.FSInputFile(gp.get_alltime_data_schedule(6, "График заработка за все время"))
            await message.answer_photo(image, reply_markup=kb.get_main_keyboard())
        elif state_data['action'] == "График времени ⏳":
            image = types.FSInputFile(gp.get_alltime_data_schedule(9, "График времени за все время"))
            await message.answer_photo(image, reply_markup=kb.get_main_keyboard())
        elif state_data['action'] == "Завершенные записи ✅":
            if gp.get_all_records_dataframe():
                document = types.FSInputFile("db/csv/all_records.xlsx")
                await message.answer_document(document, reply_markup=kb.get_main_keyboard())
            else:
                await message.answer("Ошибка конвертации!", reply_markup=kb.get_main_keyboard())

    await state.clear()
