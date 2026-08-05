from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
import psycopg
import hashlib

app = FastAPI()

@app.post("/auth",)
def auth_form(
    payload: dict = Body(...)):  

    username = payload['username']
    password = payload['password']
    
    if not username.strip():
        raise HTTPException(status_code=00, detail="Username cannot be empty")

    if not password.strip():
        raise HTTPException(status_code=400, detail="Password cannot be empty")

    conn = psycopg.connect(dbname="auth",user="postgres",password="postgres",host="localhost",port="8081")
    cursor = conn.cursor()
    data = cursor.execute("SELECT password WHERE username = %s", (username,))
    pwhash = data.fetchone()
    conn.close()
    if not pwhash:
        raise HTTPException(status_code=403, detail="User not found")

    pw = hashlib.sha256(password.strip().encode('utf-8')).hexdigest()

    if pw != pwhash:
        raise HTTPException(status_code=403, detail="Authentication failed")

    return JSONResponse(
        content={"redirect_url": "https://frontend/authenticated"},
        status_code=200
    )