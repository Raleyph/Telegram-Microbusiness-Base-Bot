from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
import config as cfg

expense_materials = {}

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cfg.main_clients, cfg.main_records, cfg.main_analytics)
clients_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cfg.add_client, cfg.update_client, cfg.client_list, cfg.back_button)
records_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cfg.add_record, cfg.remove_record, cfg.now_records, cfg.complete_record, cfg.back_button)
analytics_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cfg.write_finance_schedule, cfg.write_visits_schedule, cfg.general_data, cfg.write_complete_records, cfg.back_button)
analytics_delta_time_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cfg.week_analytics, cfg.month_analytics, cfg.all_analytics, cfg.back_button)
analytics_general_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cfg.enter_expenses, cfg.get_total_earnings, cfg.write_profitability_schedule, cfg.back_button)
analytics_expenses_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cfg.add_expense, cfg.remove_expense, cfg.expenses_list, cfg.back_button)
edit_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(cfg.skip_button)

confirm_keyboard = InlineKeyboardMarkup(row_width=2).add(cfg.confirm_yes, cfg.confirm_no)
client_choose = InlineKeyboardMarkup(row_width=1).add(cfg.client_from_list, cfg.client_new)
expense_type = InlineKeyboardMarkup(row_width=1).add(cfg.expense_material, cfg.expense_salary, cfg.expense_transportation, cfg.expense_tax)


def set_clients_keyboard(data):
    markup = InlineKeyboardMarkup(row_width=1)
    for i in data:
        markup.add(InlineKeyboardButton(i[1] + " " + ("" if i[3] is None else str(i[3])), callback_data=i[0]))
    return markup


def set_records_keyboard(data):
    markup = InlineKeyboardMarkup(row_width=1)
    for i in data:
        markup.add(InlineKeyboardButton(i[1] + " " + i[2], callback_data=i[0]))
    return markup


def set_expense_materials_keyboard(data):
    markup = InlineKeyboardMarkup(row_width=2)
    expense_id = data[0][0]
    for i in data:
        markup.add(InlineKeyboardButton(f"{i[4]}: {expense_materials[expense_id] if expense_id in expense_materials else i[6]}", callback_data=f"{i[0]} add"), InlineKeyboardButton("❌", callback_data=f"{i[0]} delete"))

    markup.add(InlineKeyboardButton("Завершить ✅", callback_data="finish"))
    return markup


def set_expenses_keyboard(data):
    markup = InlineKeyboardMarkup(row_width=1)
    for i in data:
        if i[1] == "Материал":
            markup.add(InlineKeyboardButton(i[3] + " " + i[4], callback_data=i[0]))
        else:
            markup.add(InlineKeyboardButton(i[3] + " " + i[8], callback_data=i[0]))
    return markup
