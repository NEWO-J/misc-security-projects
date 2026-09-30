from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
import psycopg
import argon2
import pgpy
from pgpy.constants import PubKeyAlgorithm, KeyFlags, HashAlgorithm, SymmetricKeyAlgorithm, CompressionAlgorithm

app = FastAPI.app()


@app.post("/register")
def register( payload: dict = Body(...) ):

    if not payload or not payload["user"] or not payload["pass"] or not payload["email"]:
        raise HTTPException(status_code="401", detail="Incomplete authentication details provided")

    connection = psycopg.connect(dbname="auth",user="postgres",password="postgres",host="authdb")
    cursor = connection.cursor()

    cursor.execute("SELECT 1 FROM users WHERE name == %s", (payload["user"]))

    data = cursor.fetchone()

    if data:
        raise HTTPException(status_code=403, detail="Username is not available")
    
    ph = argon2.PasswordHasher()
    hash = ph.hash(payload["pass"].strip())

    key = pgpy.PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 4096)
    uid = pgpy.PGPUID.new(payload["name"], email=payload["email"])
    key.add_uid(uid, usage=[KeyFlags.Sign, KeyFlags.EncryptCommunications])
    pubkey = str(key.pub)
    privkey = str(key)

    cursor.execute("INSERT INTO users (name, email, pubkey, password) VALUES (%s, %s, %s, %s')", (payload["user"], payload["email"], pubkey, hash))

    response = JSONResponse(
                    status_code=200,
                    content={"status":"success"}
                    key={"private":privkey}
                )

    return response



    