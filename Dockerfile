FROM python:3.10-slim

WORKDIR /app

# Оновлюємо pip
RUN pip install --no-cache-dir --upgrade pip

COPY . /app

# Встановлюємо залежності та сам проєкт
RUN pip install --no-cache-dir .

# Створюємо користувача non-root для безпеки
RUN useradd -m findexuser && chown -R findexuser:findexuser /app
USER findexuser

EXPOSE 8000

CMD ["findex", "serve", "--host", "0.0.0.0", "--port", "8000"]
