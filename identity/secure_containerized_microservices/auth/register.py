import psycopg
from fastapi import FastAPI, Form, HTTPException
import re
import hashlib

app = FastAPI()

pw_regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

@app.post("/register")
def register(
    username: str = Form(...),
    password: str = Form(...),
):  

    username = username.strip()
    password = password.strip()

    if not username:
        raise HTTPException(status_code=400, detail="Username field must not be empty")

    if not password:
        raise HTTPException(status_code=400, detail="Password field must not be empty")

    if not re.match(pw_regex, password):
        raise HTTPException(status_code=400, detail="Password complexity is insufficient")

    conn = psycopg.connect(dbname="auth", user="postgres",password="postgres",host="db")
    cursor = conn.cursor()

    user = cursor.execute("SELECT 1 FROM auth WHERE username = %s", username)
    user.fetchone()

    if user:
        raise HTTPException(status_code=400, detail="This username already exists!")

    phash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    cursor.execute("INSERT INTO auth (username, password) VALUES (%s, %s)", (username, phash))
    conn.commit()
