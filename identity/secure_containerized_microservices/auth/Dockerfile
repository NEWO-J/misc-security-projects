FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY auth/requirements.txt .
RUN pip install -r requirements.txt

COPY auth/. .
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]