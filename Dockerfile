# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы приложения и требования
COPY . .

EXPOSE 5003

# Запускаем gunicorn
CMD ["gunicorn", "--timeout", "220", "main:app", "-b", "0.0.0.0:5003"]
