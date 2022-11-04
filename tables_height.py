def get_clients_table_height(dataframe):
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


def get_current_records_table_height(dataframe):
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


def get_completed_records_table_height(dataframe):
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


def get_expenses_table_height(dataframe):
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
