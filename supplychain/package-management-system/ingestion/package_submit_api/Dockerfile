FROM python:3.12-slim

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install -r /code/requirements.txt

EXPOSE 8000

CMD ["fastapi", "dev", "/code/app/upload.py", "--host", "0.0.0.0", "--port", "8000"]