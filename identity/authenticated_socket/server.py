import socket

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind(('localhost', 1237))
    server_socket.listen(5)

    print("Listening")

    while True:
        client, addr = server_socket.accept()
        print(f"recieved connection from {addr}")
        while True:
            try: 
                data = client.recv(255)
                if data:
                    print(data.decode('utf-8'))
    
            except: 
                print("Error with socket")
    

if __name__ == "__main__":
    server()