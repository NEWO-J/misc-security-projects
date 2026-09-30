FROM python:3.12-alpine
WORKDIR /app
RUN apk add --no-cache postgresql
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
COPY psql_seedfile.txt /docker-entrypoint-initdb.d/seed.sql
CMD ["python", "auth.py"]