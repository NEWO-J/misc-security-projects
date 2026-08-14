FROM python:3.12-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

COPY ./app /code/app

EXPOSE 8000

CMD ["fastapi", "dev", "/code/app/dashboard.py", "--host", "0.0.0.0", "--port", "8000"]