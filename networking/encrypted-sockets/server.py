import socket
import ssl

def run_server():

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="domain.crt", keyfile="domain.key")

    server_sock.bind(('127.0.0.1', 9443))

    server_sock.listen(5)

    print("Listening..")

    try:
        connection, client_address = server_sock.accept()
        print(f"Connected by a client at: {client_address}")

        with context.wrap_socket(connection, server_side=True) as secure_client:
            while True:
                data = secure_client.recv(1024)
                if not data:
                    break

                print(f"Received from client: {data.decode('utf-8')}")

                secure_client.sendall(data)

    except Exception as e:
        print(f"An error occured {e}")

    finally:
        connection.close()
        server_sock.close()
        print("Connection closed")


if __name__ == '__main__':
    run_server()