from fastapi import FastAPI, Body, HTTPException, Header, Depends, Request, Response, Cookie
from fastapi.responses import JSONResponse
from typing import Annotated

from urllib.parse import parse_qs, urlparse

import psycopg
from psycopg import errors

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

import re
import jwt
from jwt import DecodeError, ExpiredSignatureError

import os
import redis

import uuid

import time

app = FastAPI()

origins = [
    "https://localhost:8082"
]

secret = os.environ.get("JWT_SECRET")

red = redis.Redis(host='cache', port=6379, db=0)

limit = 10

def rate_limiter(request: Request,
                 x_real_ip: Annotated[str | None, Header()] = None):
    
    ts = time.time()
    ip = x_real_ip
    key = f"rate_limit:{ip}"

    clear_before = ts - 60

    r = red.pipeline()

    r.zremrangebyscore(key, 0, clear_before)
    r.zcard(key)
    time_id = f"time-{uuid.uuid4().hex}"
    r.zadd(key, {time_id: ts})
    r.expire(key, 65)

    results = r.execute()
    current_count = results[1]

    if current_count >= limit:
        r.zrem(key, time_id)
        raise HTTPException(status_code=429, detail="Too many requests, try again later")
    else:
        return True


@app.post("/auth",)
def auth_form(
    response: Response,
    payload: dict = Body(...),
    data: Annotated[dict, Depends(rate_limiter)] = None):  


    username = payload['username']
    password = payload['password']
    
    if not username.strip():
        raise HTTPException(status_code=400, detail="Username cannot be empty")

    if not password.strip():
        raise HTTPException(status_code=400, detail="Password cannot be empty")

    conn = psycopg.connect(dbname="auth",user="postgres",password="postgres",host="db",port="5432")
    cursor = conn.cursor()
    data = cursor.execute("SELECT password FROM users WHERE name = %s", (username,))
    pwhash = data.fetchone()
    conn.close()

    ph = PasswordHasher()


    if not pwhash:
        dummy_hash = "$argon2id$v=19$m=65536,t=3,p=4$O1+K8lB5QvwpGSsackzUiw$R85j6VTse71S976V2CEl5NB25IdSsvBDaxK8/6SPzMk"
        try:
            ph.verify(dummy_hash, password)
        except VerifyMismatchError:
            raise HTTPException(status_code=403, detail="Authentication failed")
        
        raise HTTPException(status_code=403, detail="Authentication failed")

    

    try:
        ph.verify(pwhash[0], password)
    except VerifyMismatchError:
        raise HTTPException(status_code=403, detail="Authentication failed")

    encoded_jwt = jwt.encode({"user": username}, str(secret), algorithm="HS256")

    response = JSONResponse(
            content={"redirect_url": "https://localhost:8082/api/verify"},
            status_code=200
        )

    response.set_cookie(key="session", value=encoded_jwt, httponly=True, secure=True, samesite="strict")

    return response

pw_regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$")

@app.post("/register")
def register(
    payload: dict = Body(...),
    data: Annotated[dict, Depends(rate_limiter)] = None
):  
    
    username = payload['Username']
    password = payload['Password']

    if not username:
        raise HTTPException(status_code=400, detail="Username field must not be empty")

    if not password:
        raise HTTPException(status_code=400, detail="Password field must not be empty")

    if not re.match(pw_regex, password):
        raise HTTPException(status_code=400, detail="Password complexity is insufficient")

    conn = psycopg.connect(dbname="auth", user="postgres",password="postgres",host="db")
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM users WHERE name = %s", (username,))

    ph = PasswordHasher()
    phash = ph.hash(password.strip())

    try:
        cursor.execute("INSERT INTO users (name, password) VALUES (%s, %s)", (username, phash))
        conn.commit()
    except errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=401, detail="This username already exists!")

    return JSONResponse(
        content={"redirect_url": "https://localhost:8082/login"},
        status_code=200
    )

@app.get("/api/verify")
def verify(session: Annotated[str | None, Cookie()] = None):
    if not session:
        raise HTTPException(status_code=401, detail="Missing token")

    if not session:
        raise HTTPException(status_code=401, detail="Please send a token for validation")
    
    try:
        decoded_payload = jwt.decode(session, secret, algorithms=["HS256"])
    except DecodeError:
        raise HTTPException(status_code=401, detail="Malformed JWT token")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired JWT token")

    print(decoded_payload["user"])
    return JSONResponse(
            content={"user": decoded_payload["user"]},
            status_code=200
        )  

    