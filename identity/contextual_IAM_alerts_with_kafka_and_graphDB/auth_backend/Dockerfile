FROM python:3.12-slim

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*


COPY ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

COPY ./app /code/app

EXPOSE 8000

CMD ["fastapi", "dev", "/code/app/auth.py", "--host", "0.0.0.0", "--port", "8000"]