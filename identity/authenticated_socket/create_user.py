import psycopg
import pyotp
import hashlib
import getpass


def add_user(username, pw):

    secret = pyotp.random_base32()

    conn = psycopg.connect(dbname="auth",user="postgres",password="postgres",host="localhost")

    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, secret) VALUES (%s, %s, %s);", (username, pw, secret,))
    conn.commit()


if __name__ == "__main__":
    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ").strip()

    pwhash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    add_user(username, pwhash)
