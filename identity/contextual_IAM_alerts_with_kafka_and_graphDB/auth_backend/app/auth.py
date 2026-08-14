from fastapi import FastAPI, Body, HTTPException, Header, Response, Cookie, Query
from typing import Annotated, Optional
from fastapi.responses import JSONResponse
import psycopg
from kafka import KafkaProducer
import json
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import jwt
from jwt import DecodeError, ExpiredSignatureError
import os
from datetime import datetime

app = FastAPI()

producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
    request_timeout_ms=30000
)

secret = os.environ.get("JWT_SECRET")

@app.post("/login")
def login(
    response: Response,
    payload: dict = Body(...),
    service: str | None = Header(None),
    x_real_ip: Annotated[str | None, Header()] = None,
    ):

    if x_real_ip:
                ip = x_real_ip
    else:
        raise HTTPException(status_code=401, detail="x_real_ip header required")

    print(payload)
    username = payload["user"]
    password = payload["pass"]

    if not service:
        raise HTTPException(status_code=401, detail="Unknown service requested.")

    if not username or not password:
        raise HTTPException(status_code=401, detail="Please provide a username and password")

    connection = psycopg.connect(dbname="auth",user="postgres",password="postgres",host="postgres")
    cursor = connection.cursor()

    cursor.execute('SELECT password, "group" FROM users WHERE name = %s', (username,))

    data = cursor.fetchone()
    if not data:
        raise HTTPException(status_code=401, detail="Invalid login")
                
    pwhash = data[0]
    group = data[1]
    ph = PasswordHasher()

    try:
        is_valid = ph.verify(pwhash, password.strip())
    except VerifyMismatchError:
        print("invalid password")
        try:
            future = producer.send(
                "auth-logs", 
                key=payload["user"], 
                value={"ip": ip,
                        "service": service,
                        "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 
                        "status": "5512"}
            )
        except Exception as e:
            print("failed to send kafka logs")
            raise HTTPException(f"Failed to write log to Kafka: {e}")
        raise HTTPException(status_code=403, detail="Authentication failed")

    if is_valid:
        print(is_valid)
        cursor.execute('SELECT perms FROM groups WHERE "group" = %s', (group,))

        perms = cursor.fetchone()
        perms = perms[0]
        print(perms)
        if "r" in perms[service]:
            encoded_jwt = jwt.encode({"user": username, "group": group}, str(secret), algorithm="HS256")

            response = JSONResponse(
                status_code=200,
                content={"status":"success"}
            )

            response.set_cookie(key="session", value=encoded_jwt)

            

            return response
    

@app.get("/api/verify")
def verify(response: Response,
           session: Annotated[str | None, Cookie()] = None,
           service: Optional[str] = Query(None, max_length=50,),
           x_real_ip: Annotated[str | None, Header()] = None):
    
    if x_real_ip:
            ip = x_real_ip
    else:
        raise HTTPException(status_code=401, detail="x_real_ip header required")
    
    try:
        decoded_payload = jwt.decode(session, secret, algorithms=["HS256"])
    except DecodeError:
        raise HTTPException(status_code=401, detail="Malformed JWT token")
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Expired JWT token")
    
    group = decoded_payload["group"]
    connection = psycopg.connect(dbname="auth",user="postgres",password="postgres",host="postgres")
    cursor = connection.cursor()
    cursor.execute('SELECT perms FROM groups WHERE "group" = %s', (group,))
    
    perms = cursor.fetchone()
    perms = perms[0]
    print(perms)
    if "r" not in perms[service]:
        raise HTTPException(status_code=401, detail="User is not permitted")
    
    try:
        future = producer.send(
            "auth-logs", 
            key=decoded_payload["user"], 
            value={"ip": ip,
                   "service": service,
                   "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), 
                   "status": "5513"}
        )
        metadata = future.get(timeout=10)
    except Exception as e:
        raise HTTPException(f"Failed to write log to Kafka: {e}")
    return JSONResponse(status_code=200, content={"perms":perms})


    

