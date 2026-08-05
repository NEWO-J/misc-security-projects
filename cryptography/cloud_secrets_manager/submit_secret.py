import secrets
import psycopg
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap, InvalidUnwrap

import os

kek = os.environ.get("SECRET_KEK").encode('utf-8')

def get_secret(name):
    with psycopg.connect("dbname=secrets_db user=postgres password=postgres host=localhost") as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM secrets WHERE secretname = %s", (name,))

            tenant_id, secretname, ciphertext, nonce, wrapped_key = cur.fetchone()

            try: 
                key = aes_key_unwrap(kek, wrapped_key)
            except InvalidUnwrap:
                print("Failed to unwrap key")

            aesgcm = AESGCM(key)

            plaintext = aesgcm.decrypt(nonce, ciphertext, str(tenant_id).encode('utf-8'))

            print(plaintext.decode('utf-8'))



def store_secret(name, secret, tenant_id):
    dek = secrets.token_bytes(32)

    aesgcm = AESGCM(dek)

    nonce = os.urandom(12)

    ciphertext = aesgcm.encrypt(nonce, secret.encode('utf-8'), tenant_id.encode('utf-8'))

    wrapped_key = aes_key_wrap(kek, dek)
    
    with psycopg.connect("dbname=secrets_db user=postgres password=postgres host=localhost") as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO secrets (tenant_id, secretname, ciphertext, nonce, key) VALUES (%s, %s, %s, %s, %s)", (tenant_id, name, ciphertext, nonce, wrapped_key))


if __name__ == "__main__":

    store_secret("testing", "test", "1")
    get_secret("testing")