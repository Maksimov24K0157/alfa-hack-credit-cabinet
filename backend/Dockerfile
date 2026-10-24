# Build context is the project root (see docker-compose.yml),
# so paths below are relative to alfa-hack-credit-cabinet/.
FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/ml/src \
    MODEL_PATH=/ml/models/model.pkl

WORKDIR /app

# Install dependencies first so this layer is cached between code changes
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY ml/src /ml/src
COPY ml/models /ml/models

RUN mkdir -p /data

EXPOSE 8000

CMD ["uvicorn", "app.test_app:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/app"]
