# Базовый образ с конкретной версией
FROM python:3.10-slim

# Создаем непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser

# Устанавливаем системные зависимости (если нужны)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем только requirements.txt сначала (для кэширования)
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY dashboard.py loader.py ./

# Переключаемся на непривилегированного пользователя
USER appuser

# Команда по умолчанию (для analytics_app)
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
