import sqlite3
import os
import re
import pandas as pd

conn = sqlite3.connect('db/data.db', check_same_thread=False)
cursor = conn.cursor()


def check_dirs():
	if not os.path.exists("db/csv"):
		os.makedirs("db/csv")
	if not os.path.exists("db/img"):
		os.makedirs("db/img")


# user
def user_check(user_id: int):
	rows = cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchall()
	return True if rows else False


def user_login(user_id: int, user_name: str, username: str):
	cursor.execute('INSERT INTO users (user_id, user_name, username) VALUES (?, ?, ?)', (user_id, user_name, username))
	conn.commit()


def user_delete(user_id: int):
	cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
	conn.commit()


def get_user_id():
	return cursor.execute('SELECT user_id FROM users WHERE id = 1').fetchall()


# client
def check_contacts(contacts: str):
	return False if cursor.execute('SELECT * FROM clients WHERE contacts = ?', (contacts,)).fetchone() else True


def add_client(name: str, description: str, contacts: str, return_id: bool):
	cursor.execute('INSERT INTO clients (name, description, contacts, visits_count) VALUES (?, ?, ?, ?)', (name, description, contacts, 0))
	conn.commit()
	return cursor.execute('SELECT last_insert_rowid()').fetchone() if return_id else None


def update_client_info(client_id: int, name: str, description: str, contacts: str):
	query = 'UPDATE clients SET name = ?, description = ?, contacts = ? WHERE id = ?'
	cursor.execute(query, (name, description, contacts, client_id,))
	conn.commit()


def get_client_list():
	return cursor.execute('SELECT * FROM clients').fetchall()


def get_client_from_id(client_id: int):
	return cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()


def add_client_visits_count(client_id: int):
	cursor.execute('UPDATE clients SET visits_count = visits_count + 1 WHERE id = ?', (client_id,))
	conn.commit()


# records
def check_records(date: str, time: str):
	return cursor.execute('SELECT * FROM records WHERE date = ? AND time = ?', (date, time)).fetchall()


def add_record(date: str, time: str, is_completed: bool, client_id: int):
	cursor.execute('INSERT INTO records (date, time, complete, client_id) VALUES (?, ?, ?, ?)', (date, time, is_completed, client_id))
	conn.commit()


def remove_record(record_id: int):
	cursor.execute('DELETE FROM records WHERE id = ?', (record_id,))
	conn.commit()


def get_current_records():
	data = cursor.execute('SELECT * FROM records WHERE complete = 0').fetchall()
	return sorted(data, key=lambda date: date[1])


def commit_record(record_id: int, service: str, price: int, tips: str, additional: str, work_time: int):
	query = 'UPDATE records SET complete = ?, service = ?, price = ?, tips = ?, additional = ?, work_time = ? WHERE id = ?'
	cursor.execute(query, (True, service, price, tips, additional, work_time, record_id,))
	conn.commit()


def get_records_delta_data(now_date: str, last_date: str):
	return cursor.execute('SELECT * FROM records WHERE (date BETWEEN ? AND ?) AND complete = 1', (now_date, last_date,)).fetchall()


def get_records_all_data():
	return cursor.execute('SELECT * FROM records WHERE complete = 1').fetchall()


# expenses
def set_expense_material(expense_type: str, name: str, price: int, date: str, count: float, consumption: float):
	cursor.execute('INSERT INTO expenses (type, name, price, date, count, new_count, consumption) VALUES (?, ?, ?, ?, ?, ?, ?)', (expense_type, name, price, date, count, count, consumption))
	conn.commit()


def set_expenses(expense_type: str, price: int, date: str, description: str):
	cursor.execute('INSERT INTO expenses (type, price, date, description) VALUES (?, ?, ?, ?)', (expense_type, price, date, description))
	conn.commit()


def get_expense_material_count():
	return cursor.execute('SELECT * FROM expenses WHERE type = "Материал" AND consumption IS NOT NULL').fetchall()


def get_expense_from_id(material_id: int):
	return cursor.execute('SELECT * FROM expenses WHERE id = ?', material_id).fetchall()


def set_expense_material_count(new_count: float, expense_id: int):
	cursor.execute('UPDATE expenses SET count = ? WHERE id = ?', (new_count, expense_id,))
	conn.commit()


def remove_expense(expense_id):
	cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
	conn.commit()


def get_expenses():
	return cursor.execute('SELECT * FROM expenses').fetchall()


def update_expenses(new_count: float, expense_id):
	cursor.execute('UPDATE expenses SET new_count = ? WHERE id = ? AND count > 0', (new_count, expense_id,))
	conn.commit()


# general data
def get_finance_sum():
	return cursor.execute('SELECT SUM(price) FROM records').fetchone()[0]


def get_tips_sum():
	return cursor.execute('SELECT SUM(tips) FROM records WHERE TYPEOF(tips) = "integer"').fetchone()[0]


def get_profitability_data(last_date: str, now_date: str):
	expense = cursor.execute('SELECT SUM(price) FROM expenses WHERE date BETWEEN ? and ?', (last_date, now_date)).fetchall()[0][0]
	earnings = cursor.execute('SELECT SUM(price) FROM records WHERE (date BETWEEN ? and ?) AND complete = 1', (last_date, now_date)).fetchall()[0][0]

	all_earning = earnings - expense
	profitability = round((all_earning / earnings) * 100, 2)
	return [all_earning, profitability]


# csv
def get_csv_records(now_date: str, last_date: str):
	data = cursor.execute('SELECT id, date, time, client_id, service, price, tips, additional, work_time FROM records WHERE (date BETWEEN ? and ?) AND complete = 1', (now_date, last_date)).fetchall()

	if data:
		dataframe = {}

		for value in data:
			client_data = get_client_from_id(value[3])
			client_text = f"<b>{client_data[1]}</b> {' - ' + client_data[2] if client_data[2] is not None else ''}"
			price_text = f"{value[5]} у.е."
			tips_text = f"{value[6]} {'у.е.' if type(value[6]) is int else ''}"
			time_text = f"{value[8]} ч"
			dataframe[value[0]] = [value[1], value[2], client_text, value[4], price_text, tips_text, value[7], time_text]

		db_df = pd.DataFrame.from_dict(dataframe, orient='index')
		db_df.sort_values(by=[0, 1], inplace=True, ascending=False)
		db_df.to_csv('db/csv/records.csv', index=False)
		return True
	else:
		return False


def get_csv_current_records(times: [], week: {}):
	data = get_current_records()
	week_data = {'Time': times} | week

	db_df = pd.DataFrame.from_dict(week_data, orient='columns')
	db_df.set_index('Time', inplace=True, drop=True)

	for value in data:
		for day in week:
			for time in times:
				if week[day] == value[1] and time == value[2]:
					client_data = get_client_from_id(value[3])
					db_df.at[time, day] = client_data[1]
				else:
					if re.match(r'^202[2-5]-[0-1][0-9]-[0-3][0-9]$', db_df.iloc[times.index(time)][day]):
						db_df.at[time, day] = " "

	db_df.to_csv('db/csv/current_records.csv', index=True)


def get_csv_all_records():
	data = cursor.execute('SELECT id, date, time, client_id, service, price, tips, additional, work_time FROM records WHERE complete = 1').fetchall()
	dataframe = {}

	if data:
		for value in data:
			client_data = get_client_from_id(value[3])
			client_text = f"{client_data[1]} {' - ' + client_data[2] if client_data[2] is not None else ''}"
			price_text = f"{value[5]} у.е."
			tips_text = f"{value[6]} {'у.е.' if type(value[6]) is int else ''}"
			time_text = f"{value[8]} ч"
			dataframe[value[0]] = [value[1], value[2], client_text, value[4], price_text, tips_text, value[7], time_text]

		db_df = pd.DataFrame.from_dict(dataframe, orient='index')
		db_df[0] = pd.to_datetime(db_df[0], dayfirst=True)
		db_df.sort_values(by=[0, 1], inplace=True, ascending=False)
		db_df.to_csv('db/csv/all_records.csv', index=False)
		return True
	else:
		return False


def get_csv_clients():
	data = cursor.execute('SELECT * FROM clients').fetchall()
	dataframe = {}

	for value in data:
		dataframe[value[0]] = [value[1], value[2], value[3], value[4]]

	db_df = pd.DataFrame.from_dict(dataframe, orient='index')
	db_df.to_csv('db/csv/clients.csv', index=False)


def get_csv_expenses():
	data = cursor.execute('SELECT * FROM expenses').fetchall()
	dataframe = {}

	for value in data:
		expense_name = value[4] if value[4] is not None else "Нет"
		expense_count = f"{value[6]} / {value[5]}" if value[5] is not None else "Нет"
		expense_consumption = value[7] if value[7] is not None else "Нет"
		expense_description = value[8] if value[8] is not None else "Нет"
		dataframe[value[0]] = [value[1], value[2], value[3], expense_name, expense_count, expense_consumption, expense_description]

	db_df = pd.DataFrame.from_dict(dataframe, orient='index')
	db_df.to_csv('db/csv/expenses.csv', index=False)
