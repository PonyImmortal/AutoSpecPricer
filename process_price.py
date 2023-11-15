import pandas as pd
import re


def is_number(s):
    """Проверка строки на представление числа."""
    if s is None:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def is_mm_value(value):
    """Проверка является ли значение значением в мм."""
    # Проверка на наличие значения
    if pd.notna(value):
        if isinstance(value, (int, float)):
            return True

        value = str(value).strip()
        # Регулярные выражения для разных форматов значений в мм
        patterns = [
            r'^\d+(\.\d+)?$',  # Пример: 100 или 0.5
            r'^\d+(\.\d+)?\s+\d+(\.\d+)?мм$',  # Пример: 100 0.5мм
            r'^\d+(\.\d+)?мм$',  # Пример: 0.5мм
            r'^\d+(-\d+)?$',  # Пример: 10-20
            r'^-\d+$'  # Пример: -10
        ]
        return any(re.match(pattern, value) for pattern in patterns)
    return False


def extract_mm_values(sheet_data, col_index_mm, row_mm):
    """Извлекаем значения мм из определенной колонки."""
    mm_values = []
    base_size = None

    for i in range(row_mm + 1, len(sheet_data)):
        value_mm = str(sheet_data.iloc[i, col_index_mm]).strip()
        value_mm = value_mm.replace('–', '-')

        # Прекращаем обработку при пустом значении
        if value_mm == 'nan' or not value_mm:
            break

        # Обработка разных форматов значений
        if '-' in value_mm and not value_mm.startswith('-'):
            base_size = value_mm.split('-')[0].strip()
            mm_values.append(value_mm)
        elif value_mm.startswith('-'):
            if base_size:
                mm_values.append(f"{base_size}{value_mm}")
            else:
                print(f"Warning: No base size found for value {value_mm} in column {col_index_mm} at row {i}")
        else:
            base_size = value_mm
            mm_values.append(value_mm)

    return mm_values


def check_above_cells(sheet_data, row_mm, col_name_mm):
    """Проверяем содержимое ячеек выше определенной ячейки."""
    col_index_mm = sheet_data.columns.get_loc(col_name_mm)
    cells_above = [
        str(sheet_data.iloc[row_mm - 1, col_index_mm]).strip().lower(),
        str(sheet_data.iloc[row_mm - 2, col_index_mm]).strip().lower() if row_mm - 2 >= 0 else ""
    ]
    for cell in cells_above:
        if cell.startswith('d'):
            return True, cell
    return False, ""


def extract_data_from_sheet(sheet_data, sheet_name):
    """Извлечение данных из стандартного листа."""
    local_data_list = []
    positions_mm = sheet_data[sheet_data == "мм"].stack().index.tolist()
    for (row_mm, col_mm) in positions_mm:
        is_valid, _ = check_above_cells(sheet_data, row_mm, col_mm)
        if not is_valid:
            continue

        col_index_mm = sheet_data.columns.get_loc(col_mm)
        mm_values = extract_mm_values(sheet_data, col_index_mm, row_mm)

        # Обработка столбцов справа от столбца мм
        for col in sheet_data.columns[col_index_mm + 1:]:
            if sheet_data.at[row_mm, col] == "мм" and check_above_cells(sheet_data, row_mm, col)[0]:
                break
            if sheet_data.at[row_mm, col] in ["Цена", "Цена, Евро", "Цена, Рубль"]:
                price_values = [sheet_data.iloc[i, sheet_data.columns.get_loc(col)] for i in
                                range(row_mm + 1, row_mm + 1 + len(mm_values))]
                model = sheet_data.iloc[row_mm - 1, sheet_data.columns.get_loc(col)] if pd.notna(
                    sheet_data.iloc[row_mm - 1, sheet_data.columns.get_loc(col)]) else sheet_data.iloc[
                    row_mm - 2, sheet_data.columns.get_loc(col)]

                for size, price in zip(mm_values, price_values):
                    if pd.isna(size) or pd.isna(price):
                        continue
                    local_data_list.append([sheet_name, size, model, price])

    return local_data_list


def extract_data_from_special_sheet(sheet_data, sheet_name):
    """Извлечение данных из специальных листов с форматами "Прямоуг" или "Обвод"."""
    local_data_list = []
    bh_positions = sheet_data[sheet_data.isin(["B       H", "B         H"])].stack().index.tolist()

    if not bh_positions:
        return local_data_list

    for (row_bh, col_bh_name) in bh_positions:
        col_bh = sheet_data.columns.get_loc(col_bh_name)
        second_sizes = [x for x in sheet_data.iloc[row_bh, col_bh + 1:].tolist() if is_number(x)]

        for i in range(row_bh + 1, len(sheet_data)):
            first_value = str(sheet_data.iloc[i, col_bh]).strip()
            if not is_number(first_value) or first_value == "nan":
                continue

            # Обработка столбцов справа от столбца B H
            for j, second_size in enumerate(second_sizes, start=col_bh + 1):
                price = sheet_data.iloc[i, j]
                if pd.notna(price) and isinstance(price, (int, float)):
                    if pd.isna(second_size):
                        continue
                    size = f"{first_value}-{int(float(second_size))}"
                    local_data_list.append([sheet_name, size, None, price])

    return local_data_list


def process_excel_file(filename, new_filename):
    """Основная функция обработки файла."""
    data_list = []
    with pd.ExcelFile(filename) as xls:
        for sheet_name in xls.sheet_names:
            if any(substring in sheet_name for substring in
                   ["Крестовина KT,KTRT", "шумоглушитель", "Возд-распредел. AD,AVI,AHIA,AHI"]):
                continue
            sheet_data = pd.read_excel(xls, sheet_name)

            if any(substring in sheet_name for substring in ["Прямоуг", "Обвод"]):
                data_list.extend(extract_data_from_special_sheet(sheet_data, sheet_name))
            else:
                data_list.extend(extract_data_from_sheet(sheet_data, sheet_name))

    df = pd.DataFrame(data_list, columns=['Оборудование', 'Размер', 'Модель', 'Цена'])

    df = df.drop_duplicates(subset=['Оборудование', 'Размер', 'Модель', 'Цена'])
    df.to_excel(new_filename, index=False)
