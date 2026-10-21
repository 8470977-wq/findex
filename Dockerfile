# Stage 1: Build stage
FROM python:3.10-slim as builder

WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip build

COPY . /app
RUN python -m build --wheel

# Stage 2: Final runtime stage
FROM python:3.10-slim as runner

WORKDIR /app
RUN useradd -m findexuser

COPY --from=builder /app/dist/*.whl /app/
# Оновлюємо pip та встановлюємо wheel без конфліктів залежностей
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /app/*.whl

USER findexuser
EXPOSE 8000

CMD ["findex", "serve", "--host", "0.0.0.0", "--port", "8000"]
