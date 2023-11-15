import os
from comparison import compare_spec_and_price
from process_price import process_excel_file
from working_with_data import save_to_excel, read_data_from_excel, clean_new_price_data, prepare_spec_data

# Константы
UPLOAD_FOLDER = 'uploads'
NEW_PREFIX = "new_"
COMPARED_FILENAME = "compared_price.xlsx"


def create_filepath(filename, prefix=None):
    """Создать полный путь к файлу с опциональным префиксом."""
    if prefix:
        filename = prefix + filename
    return os.path.join(UPLOAD_FOLDER, filename)


def update_and_process_file(price_filename):
    """Функция для обновления и обработки файла."""
    filepath = create_filepath(price_filename)
    new_filepath = create_filepath(price_filename, NEW_PREFIX)
    process_excel_file(filepath, new_filepath)


def compare_and_save(price_filename, spec_filename):
    """Функция для сравнения и сохранения."""
    price_filepath = create_filepath(price_filename, NEW_PREFIX)
    spec_filepath = create_filepath(spec_filename)

    new_price_df = read_data_from_excel(price_filepath)
    spec_df = read_data_from_excel(spec_filepath, skip_rows=6)

    new_price_df = clean_new_price_data(new_price_df)
    spec_df = prepare_spec_data(spec_df)

    results_df = compare_spec_and_price(spec_df, new_price_df)
    compared_filepath = create_filepath(COMPARED_FILENAME)
    save_to_excel(results_df, compared_filepath)

