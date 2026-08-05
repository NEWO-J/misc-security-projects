import pyotp
import psycopg
import hashlib
import time

def authenticate(username, pwhash):
    conn = psycopg.connect(dbname='auth', user='postgres', password='postgres', host='localhost')
    cursor = conn.cursor()
    cursor.execute("SELECT password, secret FROM users WHERE username = %s", (username,))
    pw_hash, secret = cursor.fetchone()

    if pw_hash == pwhash.encode('utf-8'):
        return secret
    else:
        return False

def connect():
    username = input("Please enter your username to authenticate: ").strip()
    pw = input("Please enter your password to authenticate: ").strip()
    hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    secret = authenticate(username, hash)
    if not secret:
        print("Error! authentication failed")
        exit()

    totp = pyotp.TOTP(secret)
    current_totp = totp.now()

    

    try:
        while True:
            current_time = time.time()
            if totp.now() != current_totp:
                current_totp = totp.now()
            print(f"\rOne Time Password: {totp.now()} | Expires in: {30 - int(current_time % 30)} ",end="",flush=True)
    except KeyboardInterrupt:
        print("Exiting..")
        exit()



if __name__ == "__main__":
    connect()