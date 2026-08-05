import socket
import ssl

hostname = "Jonah Owen"

def run_client():

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    

    try:
        sock.connect(('127.0.0.1', 1234))

        context = ssl.create_default_context()
        context.load_verify_locations(cafile="domain.crt") 
        sec_sock = context.wrap_socket(sock, server_hostname=hostname)

        message = "Hello, Python Sockets!"
        print(f"Sending message: {message}")

        sec_sock.sendall(message.encode('utf-8'))

        response = sec_sock.recv(1024)

        print(f"Recieved echo from server: {response.decode('utf-8')}")

    except Exception as e:
        print(f"Connection error {e}")
    finally:
        sec_sock.close()
        print("Client socket closed.")


if __name__ == '__main__':
    run_client()