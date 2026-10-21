FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

COPY . /app

RUN pip install --no-cache-dir .

# Генерація тестового індексу при збірці контейнера
RUN mkdir -p data && \
    echo "python search engine inverted index" > data/doc1.txt && \
    echo "fastapi web search engine with ranking bm25" > data/doc2.txt && \
    echo "findex cli application typer rich" > data/doc3.txt && \
    findex index data --out index.bin

RUN useradd -m findexuser && chown -R findexuser:findexuser /app
USER findexuser

EXPOSE 8000

CMD ["findex", "serve", "--host", "0.0.0.0", "--port", "8000"]
