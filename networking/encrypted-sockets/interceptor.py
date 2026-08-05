import socket
import select

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 1234
TARGET_HOST = '127.0.0.1'
TARGET_PORT = 9443

def main():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((PROXY_HOST, PROXY_PORT))
    server_sock.listen(1)
    print(f"[*] MITM Proxy listening on {PROXY_HOST}:{PROXY_PORT}")

    client, addr = server_sock.accept()
    print(f"Intercepted connection from {addr}")

    target_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_sock.connect((TARGET_HOST, TARGET_PORT))

    sockets = [client, target_sock]

    try:
        while True:
            readable, _, _, = select.select(sockets, [], [])
            for sock in readable:
                data = sock.recv(4096)
                if not data:
                    return
                else:
                    print(data.decode('utf-8', errors='ignore'))
                if sock is client:
                    target_sock.sendall(data)
                else:
                    client.sendall(data)

    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        client.close()
        target_sock.close()
        server_sock.close()

if __name__ == "__main__":
    main()