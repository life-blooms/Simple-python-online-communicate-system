import socket
import threading
clients = []
def handle_client(client_socket, client_address):
    print(f"新连接: {client_address}")
    clients.append(client_socket)

    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                broadcast(message, client_socket)
            else:
                break
        except:
            break

    client_socket.close()
    clients.remove(client_socket)
    print(f"连接关闭: {client_address}")


def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            client.send(message.encode('utf-8'))


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5555))
    server.listen(5)
    print("服务器启动，等待连接...")

    while True:
        client_socket, client_address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()


if __name__ == "__main__":
    main()