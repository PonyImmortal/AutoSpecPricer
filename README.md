# AutoSpecPricer

AutoSpecPricer — это веб-приложение, разработанное для автоматического расценивания спецификаций из Magicad согласно прайсу поставщика. Приложение реализовано на Flask и предназначено для упрощения процессов ценообразования в строительной и инженерной отраслях.

## Особенности

- Автоматическая обработка и анализ данных из Excel.
- Сопоставление спецификаций с прайс-листами и расчет итоговой стоимости.
- Интерактивный веб-интерфейс для загрузки и обработки файлов.
- Контейнеризация с использованием Docker для легкого развертывания.

## Начало работы

Для запуска проекта у вас должен быть установлен Docker. Выполните следующие шаги:

1. Клонируйте репозиторий
2. Запустите контейнеры с помощью Docker Compose:
   docker-compose up --build
3. После сборки и запуска приложение будет доступно по адресу `http://localhost:5003`.