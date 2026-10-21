FROM python:3.10-slim

WORKDIR /app

# Оновлюємо pip
RUN pip install --no-cache-dir --upgrade pip

COPY . /app

# Встановлюємо залежності та пакет findex
RUN pip install --no-cache-dir .

# Створюємо базову папку data з файлами та будуємо index.bin
RUN mkdir -p data && \
    echo "python search engine inverted index" > data/doc1.txt && \
    echo "fastapi web search engine with ranking bm25" > data/doc2.txt && \
    echo "findex cli application typer rich" > data/doc3.txt && \
    findex index data/ --out index.bin

# Створюємо non-root користувача для безпеки
RUN useradd -m findexuser && chown -R findexuser:findexuser /app
USER findexuser

EXPOSE 8000

CMD ["findex", "serve", "--host", "0.0.0.0", "--port", "8000"]
