from datetime import datetime, timedelta, time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

import database as db
import tables_height as th


def get_clients_dataframe():
    csv_file = open("db/csv/clients.csv", "w")
    csv_file.truncate()
    csv_file.close()

    if db.get_client_list():
        db.get_csv_clients()
        dataframe = pd.read_csv("db/csv/clients.csv")
        table_height = th.get_clients_table_height(dataframe)
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
        figure.write_image("db/img/clients.png")
        return "db/img/clients.png"


def get_current_records_dataframe():
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

    csv_file = open("db/csv/current_records.csv", "w")
    csv_file.truncate()
    csv_file.close()

    if db.get_current_records():
        db.get_csv_current_records(get_records_time(week_data), week_data)
        dataframe = pd.read_csv("db/csv/current_records.csv")
        table_height = th.get_current_records_table_height(dataframe)
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
        figure.write_image("db/img/current_records.png")
        return "db/img/current_records.png"


def get_all_records_dataframe():
    csv_file = open("db/csv/all_records.csv", "w")
    csv_file.truncate()
    csv_file.close()

    if db.get_csv_all_records():
        dataframe = pd.read_csv("db/csv/all_records.csv")
        dataframe.to_excel("db/csv/all_records.xlsx")
        return True
    else:
        return False


def get_completed_records_dataframe(delta_days: int):
    csv_file = open("db/csv/records.csv", "w")
    csv_file.truncate()
    csv_file.close()

    last_delta_days = delta_days - 1
    now_date = datetime.now()
    last_date = now_date - timedelta(days=float(last_delta_days))

    now_date_str = now_date.strftime("%Y-%m-%d")
    last_date_str = last_date.strftime("%Y-%m-%d")

    if db.get_csv_records(last_date_str, now_date_str):
        dataframe = pd.read_csv("db/csv/records.csv")
        table_height = th.get_completed_records_table_height(dataframe)
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
        figure.write_image("db/img/records.png")
        return "db/img/records.png"


def get_expenses_dataframe():
    csv_file = open("db/csv/expenses.csv", "w")
    csv_file.truncate()
    csv_file.close()

    if db.get_expenses():
        db.get_csv_expenses()
        dataframe = pd.read_csv("db/csv/expenses.csv")
        table_height = th.get_expenses_table_height(dataframe)
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
        figure.write_image("db/img/expenses.png")
        return "db/img/expenses.png"


def get_data_from_time_period(days: int, index: int):
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

    data = db.get_records_delta_data(last_date_str, now_date_str)
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


def get_alltime_data_schedule(value: int, label: str):
    values = db.get_records_all_data()
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
    figure.write_image("db/img/graph.png")

    return "db/img/graph.png"


def get_last_time(days_count: int):
    days = 0
    last_days = []
    now_date = datetime.now()

    while days < days_count:
        last_day = now_date - timedelta(days=float(days))
        last_days.append(last_day.strftime("%d.%m"))
        days += 1

    return last_days


def get_data_schedule(days_count: int, value: int, label: str):
    dates = get_data_from_time_period(days_count, value)
    days = get_last_time(days_count)
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
    figure.write_image("db/img/graph.png")

    return "db/img/graph.png"
