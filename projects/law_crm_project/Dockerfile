FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    musl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копирование requirements
COPY requirements.txt .

# Установка Python зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Создание директорий для медиа и статики
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Открытие порта
EXPOSE 8000

# Команда запуска (будет переопределена в docker-compose)
CMD ["gunicorn", "law_crm.wsgi:application", "--bind", "0.0.0.0:8000"]

