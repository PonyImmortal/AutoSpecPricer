# Вложенный словарь для сопоставления
complex_mapping_dict = {
    'Переход Круглые': {
        'double': 'Переход Прямоуг. SAF',
    },
    'Врезка Прямоугольные-не ВСН': {
        'single': {'name':'Седло Плоск. Кругл. APT', 'model': 'APT (с прокладкой)'},
        'double': 'Седло Прямоуг. AOF',
        'rectangle': 'Седло Прямоуг. APF',
    },
    'Врезка Круглые': {
        'single': 'Седло Кругл. AOT',
        'double': 'Седло Прямоуг. AOF',
    },
    'Переход Прямоугольные-не ВСН': {
        'double': 'Переход Прямоуг. SAF',
        'quadruple': 'Переход Прямоуг. SSF',
    },
    'Переход Прямоугольные': {
            'double': 'Переход Прямоуг. SAF',
    },
    'Переход (4) Прямоугольные-не ВСН': {
            'quadruple': 'Переход Прямоуг. SSF',
    },
    # 'Регулирующ.клапан *': {
    #     'default': {'name': 'Заслонка Кругл. и Клапаны', 'model': 'Ручного управления AGRJ-R'}
    # }
}

simple_mapping_dict = {
    'Воздуховод Круглые': 'Воздуховод Кругл. OS',
    'Воздуховод Прямоугольные': 'Воздуховод Прямоуг. OF',
    'Воздуховод Прямоугольные-не ВСН': 'Воздуховод Прямоуг. OF',
    'Отвод-45 Круглые': {'name': 'Отвод Клугл. AT-45,90', 'model': 'AT-45 Сегментное (с прокладкой)'},
    'Отвод-45 Прямоугольные-не ВСН': 'Отвод Прямоуг. AF-45',
    'Отвод-90 Круглые': {'name': 'Отвод Клугл. AT-45,90', 'model': 'AT-90 Сегментное (с прокладкой)'},
    'Отвод-90 Прямоугольные-не ВСН': 'Отвод Прямоуг. AF-90',
    'Отвод-90 Прямоугольные': 'Отвод Прямоуг. AF-90',
    'Врезка Прямоугольные': 'Седло Прямоуг. AOF',
    'Переход ': {'name': 'Переход Кругл. PCT PET', 'model': 'PCT (с прокладкой)'},
    'Переход Круглые': {'name': 'Переход Кругл. PCT PET', 'model': 'PCT (с прокладкой)'},
    'Заглушка Круглые': 'Заглушка Кругл. AKT',
    'Заглушка Прямоугольные-не ВСН': 'Заглушка Прямоуг. AKF',
    'Шумоглушитель ШГ10': {'name': 'Шумоглушитель AGS, AVGS, SPS', 'model': 'L = 900 мм'}
}

# Список категорий для регулирующего клапана
regulating_valve_categories = [
    "Регулирующ.клапан DATL",
    "Регулирующ.клапан ДАСЛ",
    "Регулирующ.клапан РК1",
    "Регулирующ.клапан ФИЫЫ"
]

# Искомые параметры для всех категорий регулирующего клапана
regulating_valve_params = {
    'name': 'Заслонка Кругл. и Клапаны',
    'model': 'Ручного управления AGRJ-R'
}

# Обновление словаря для каждой категории
for category in regulating_valve_categories:
    complex_mapping_dict[category] = {'default': regulating_valve_params}

# Объединение
for key, value in simple_mapping_dict.items():
    if isinstance(value, str):
        value = {'name': value}
    complex_mapping_dict.setdefault(key, {})['default'] = value
