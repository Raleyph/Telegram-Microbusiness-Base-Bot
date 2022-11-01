from aiogram.types import KeyboardButton, InlineKeyboardButton

token = ''
whitelist = []

start_message = '<b>Добро пожаловать!</b> 👋\n' \
                '\n' \
                '<b>Что умеет этот бот?</b>\n' \
                '· Сохранение ифнормации о клиентах\n' \
                '· Сохранение информации об обслуживании клиента\n' \
                '· Подсчет дохода и времени работы\n' \
                '· Сохранение данных о расходах\n' \
                '· Подсчет рентабельности\n' \
                '\n' \
                '<b>📥 GitHub:</b>\n' \
                'https://github.com/Raleyph/Telegram-Miscrobusiness-Base-Bot\n' \
                '\n' \
                'v. 2.0\n' \
                '<b>© MG Technologies Inc., 2022</b>\n'

main_clients = KeyboardButton("Клиенты 🙎‍♀‍")
main_records = KeyboardButton("Записи 📃")
main_analytics = KeyboardButton("Аналитика 📊")

add_client = KeyboardButton("Добавить клиента")
update_client = KeyboardButton("Редактировать клиента")
client_list = KeyboardButton("Список клиентов")

add_record = KeyboardButton("Добавить запись")
remove_record = KeyboardButton("Удалить запись")
now_records = KeyboardButton("Текущие записи")
complete_record = KeyboardButton("Завершить запись")

write_finance_schedule = KeyboardButton("График доходов 💶")
write_visits_schedule = KeyboardButton("График времени ⏳")
general_data = KeyboardButton("Общие данные 🗄")
write_complete_records = KeyboardButton("Завершенные записи ✅")

week_analytics = KeyboardButton("За неделю")
month_analytics = KeyboardButton("За месяц")
all_analytics = KeyboardButton("За все время")

enter_expenses = KeyboardButton("Расходы 💸")
get_total_earnings = KeyboardButton("Доходы 💰")
write_profitability_schedule = KeyboardButton("Рентабельность 📈")

add_expense = KeyboardButton("Добавить расход")
remove_expense = KeyboardButton("Удалить расход")
expenses_list = KeyboardButton("Список расходов")

back_button = KeyboardButton("Назад")
skip_button = KeyboardButton("Пропустить")

client_from_list = InlineKeyboardButton('Клиент из списка', callback_data='client_from_list')
client_new = InlineKeyboardButton('Новый клиент', callback_data='new_client')

confirm_yes = InlineKeyboardButton('Да', callback_data='yes')
confirm_no = InlineKeyboardButton('Нет', callback_data='no')

expense_material = InlineKeyboardButton("Материал", callback_data='material')
expense_salary = InlineKeyboardButton("Зарплата", callback_data='salary')
expense_transportation = InlineKeyboardButton("Перевозка", callback_data='transportation')
expense_tax = InlineKeyboardButton("Налог", callback_data='tax')
