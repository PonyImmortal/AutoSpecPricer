import pandas as pd
from openpyxl import Workbook
from excel_formatting import format_excel_from_dataframe


class MissingColumnsError(Exception):
    pass


def read_data_from_excel(file_name, skip_rows=None):
    """Читает данные из Excel файла."""
    df = pd.read_excel(file_name, skiprows=skip_rows, na_filter=False)
    return df


def remove_spaces_around_dash(text):
    """Удаляет пробелы вокруг дефисов в тексте."""
    return text.replace(' - ', '-').replace('- ', '-').replace(' -', '-')


def clean_new_price_data(df):
    """Очищает данные из файла new_price."""
    df['Модель'] = df['Модель'].str.replace("\s+", " ", regex=True).str.replace("\n", " ").str.strip()
    df['Размер'] = df['Размер'].apply(remove_spaces_around_dash)
    return df


def prepare_spec_data(df):
    """Подготавливает данные из файла spec."""
    columns = df.columns.str.strip()
    df.columns = columns
    if 'Класс' in columns and 'Тип' in columns:
        df['Оборудование'] = df['Класс'] + ' ' + df['Тип']
    else:
        raise MissingColumnsError("Столбцы 'Класс' или 'Тип' не найдены.")

    # Преобразование данных в столбце 'L[м]'
    df['L\\[м]'] = pd.to_numeric(df['L\\[м]'].replace('', pd.NA), errors='coerce')
    df['L\\[м]'] = df['L\\[м]'].round(2)

    return df


def save_to_excel(df, file_name):
    df_copy = df.copy()
    df_copy.to_excel(file_name, index=False)
    wb = Workbook()
    format_excel_from_dataframe(wb, df_copy, file_name)
