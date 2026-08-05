import socket
import pyotp
import psycopg
import hashlib

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
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    username = input("Please enter your username to authenticate: ").strip()
    pw = input("Please enter your password to authenticate: ").strip()
    hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    secret = authenticate(username, hash)
    if not secret:
        print("Error! authentication failed")
        exit()

    totp = pyotp.TOTP(secret)

    user_code = input("[2FA] Enter your one time code: ")

    if not totp.verify(user_code):
        print("Error! MFA failed")
        exit()

    client_socket.connect(('localhost', 1237))
    try:
        while True:
            message = input("Enter your input: ")
            data = message.encode('utf-8')

            try:
                client_socket.sendall(data)
            except:
                print("Client socket error")


    except KeyboardInterrupt:
        print("Closing connection")
        client_socket.close()
        

if __name__ == "__main__":
    connect()