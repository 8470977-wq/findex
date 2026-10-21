FROM python:3.10-slim

WORKDIR /app

# Оновлюємо pip
RUN pip install --no-cache-dir --upgrade pip

COPY . /app

# Встановлюємо необхідні залежності та пакет findex
RUN pip install --no-cache-dir .

# Створюємо non-root користувача
RUN useradd -m findexuser && chown -R findexuser:findexuser /app
USER findexuser

EXPOSE 8000

CMD ["findex", "serve", "--host", "0.0.0.0", "--port", "8000"]
