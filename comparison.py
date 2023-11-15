import pandas as pd
import math
import numpy as np

from mappings import complex_mapping_dict


# --- Вспомогательные функции ---

def get_equipment_name(category, size):
    size = str(size)

    if 'x' in size and '/' in size:
        if len(size.split('/')) == 2:
            if 'x' in size.split('/')[0] and 'x' in size.split('/')[1]:
                size_type = 'quadruple'
            else:
                size_type = 'double'
        else:
            size_type = 'triple'
    elif 'x' in size:
        size_type = 'rectangle'
    else:
        size_type = 'single'


    category_mapping = complex_mapping_dict.get(category, {})


    # Сначала проверяем size_type, затем default
    equipment_data = category_mapping.get(size_type, category_mapping.get('default'))


    # Если equipment_data является строкой, преобразуем ее в словарь
    if isinstance(equipment_data, str):
        equipment_data = {'name': equipment_data}

    return equipment_data, size_type


def swap_sizes_if_needed_for_vrezka(standardized_size, equipment):
    """При необходимости меняет местами размеры."""

    equipment_to_check = ['Врезка Круглые', 'Врезка Прямоугольные', 'Врезка Прямоугольные-не ВСН']

    if equipment not in equipment_to_check:
        return standardized_size  # Если оборудование не в списке, то просто возвращаем исходный размер

    size_parts = standardized_size.split('-')
    if len(size_parts) != 2:
        return standardized_size  # Если у нас не два числа, то просто возвращаем исходный размер

    size1, size2 = float(size_parts[0]), float(size_parts[1])
    if size1 > size2:
        return f"{int(size2)}-{int(size1)}"
    return standardized_size


def format_size(size):
    """Преобразование размера к стандартному виду."""
    size = str(size)
    if "/" in size:
        parts = size.split("/")
        if "x" in parts[0] or "x" in parts[1]:  # Если x есть в одной из частей
            # Сравниваем обе части и выбираем ту, в которой есть x
            size = parts[0] if "x" in parts[0] else parts[1]
        else:
            size = "-".join(parts)  # Для формата 500/400

    formatted_size = size.replace("x", "-")
    return formatted_size


# --- Основные функции ---


def find_most_similar_in_new_price(equipment, size, new_price_df):
    if equipment not in complex_mapping_dict:
        return None, None, None, None

    matched_equipment_data, size_type = get_equipment_name(equipment, size)
    if not matched_equipment_data:
        return None, None, None, None
    matched_equipment_name = matched_equipment_data.get('name')
    matched_equipment_model = matched_equipment_data.get('model', None)

    matched_rows = new_price_df[new_price_df['Оборудование'] == matched_equipment_name]

    if matched_equipment_model:
        matched_equipment_model = matched_equipment_model.replace("\s+", " ").replace("\n", " ").strip()
        matched_rows = matched_rows[matched_rows['Модель'] == matched_equipment_model]

    # Конвертирование размера к стандартному виду
    standardized_size = format_size(size)

    if (equipment == 'Врезка Круглые' and size_type == 'double') or \
            (equipment == 'Врезка Прямоугольные') or \
            (equipment == 'Врезка Прямоугольные-не ВСН' and size_type == 'double'):
        standardized_size = swap_sizes_if_needed_for_vrezka(standardized_size, equipment)

    # Попытка найти точное совпадение размера
    matched_rows_exact = matched_rows[matched_rows['Размер'] == standardized_size]

    if not matched_rows_exact.empty:
        return matched_rows_exact['Оборудование'].iloc[0], matched_rows_exact['Модель'].iloc[0], \
            matched_rows_exact.get('Размер', None).iloc[0], matched_rows_exact.get('Цена', None).iloc[0]

    # Если размер состоит из двух чисел, ищем ближайший больший размер для каждого из чисел
    if "-" in standardized_size:
        size_parts = standardized_size.split("-")
        try:
            size1_value = float(size_parts[0])
            size2_value = float(size_parts[1])
            matched_rows = matched_rows[matched_rows['Размер'].str.contains("-")]
            matched_rows['Size1'] = matched_rows['Размер'].str.split('-').str[0].astype(float)
            matched_rows['Size2'] = matched_rows['Размер'].str.split('-').str[1].astype(float)

            closest_size1 = matched_rows[matched_rows['Size1'] >= size1_value]['Size1'].min()
            closest_size2 = matched_rows[matched_rows['Size2'] >= size2_value]['Size2'].min()

            closest_matched_rows = matched_rows[
                (matched_rows['Size1'] == closest_size1) & (matched_rows['Size2'] == closest_size2)]
            if not closest_matched_rows.empty:
                return closest_matched_rows['Оборудование'].iloc[0], closest_matched_rows['Модель'].iloc[0], \
                    closest_matched_rows.get('Размер', None).iloc[0], closest_matched_rows.get('Цена', None).iloc[0]
        except ValueError:
            pass

    return None, None, None, None


def calculate_total_price(n_value, l_value, similar_price):

    # Преобразовать строку в число или вернуть NaN
    def to_number(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return np.nan

    # Преобразуем в числа
    n_value = to_number(n_value)
    l_value = to_number(l_value)

    similar_price = to_number(similar_price)

    if np.isnan(similar_price):
        return None

    # Если только n_value заполнено или l_value равно NaN:
    if not np.isnan(n_value) and np.isnan(l_value):
        result = n_value * similar_price
        return result
    # Если только l_value заполнено или n_value равно NaN:
    elif not np.isnan(l_value) and np.isnan(n_value):
        result = l_value * similar_price
        return result

    # Если оба значения заполнены:
    elif not np.isnan(n_value) and not np.isnan(l_value):
        result = l_value * similar_price
        return result

    # Если оба значения не заполнены:
    else:
        return None


def compare_spec_and_price(spec_df, new_price_df):
    results_df = pd.DataFrame(
        columns=['Оборудование из спецификации', 'Размер из спецификации', 'N из спецификации', 'L[м] из спецификации',
                 'Схожее оборудование из прайса', 'Модель из прайса', 'Размер из прайса', 'Цена из прайса',
                 'Итого цена'])

    for _, row in spec_df.iterrows():
        similar_equipment, similar_model, similar_size, similar_price = find_most_similar_in_new_price(
            row['Оборудование'], row['Размер'], new_price_df)

        if not similar_equipment:
            similar_equipment = "Совпадений не найдено"

        n_value = row.get('N', None)
        l_value = row.get('L\\[м]', None)
        price = similar_price

        total_price = calculate_total_price(n_value, l_value, price)

        # Теперь добавляем значения 'N' и 'L[м]' из spec_df
        results_df.loc[len(results_df)] = [row['Оборудование'], row['Размер'], row.get('N', ''), row.get('L\\[м]', ''),
                                           similar_equipment, similar_model or "", similar_size or "",
                                           similar_price or "", total_price or ""]

    return results_df
