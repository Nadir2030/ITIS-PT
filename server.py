import socket
import threading

from protocol import send_message, recv_message

HOST = "0.0.0.0"
PORT = 5555

clients = {}
lock = threading.Lock()


def broadcast(command, message, exclude=None):
    with lock:
        current_clients = list(clients.items())

    for sock, username in current_clients:
        if sock != exclude:
            try:
                send_message(sock, command, message.encode("utf-8"))
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass


def handle_client(sock, address):
    username = None

    try:
        command, payload = recv_message(sock)

        if command != "JOIN":
            send_message(sock, "ERRO", b"First command must be JOIN")
            return

        username = payload.decode("utf-8")

        with lock:
            clients[sock] = username

        print(f"{username} connected from {address}")

        broadcast("INFO", f"{username} joined the chat", exclude=sock)

        while True:
            command, payload = recv_message(sock)

            if command == "TEXT":
                message = payload.decode("utf-8")
                broadcast("TEXT", f"{username}: {message}", exclude=sock)

            elif command == "LIST":
                with lock:
                    users = list(clients.values())

                send_message(sock, "LIST", ", ".join(users).encode("utf-8"))

            elif command == "QUIT":
                break

            else:
                send_message(sock, "ERRO", f"Unknown command: {command}".encode("utf-8"))

    except ConnectionResetError:
        print(f"{username} connection reset")

    except BrokenPipeError:
        print(f"{username} broken pipe")

    except ConnectionError:
        print(f"{username} connection closed")

    finally:
        with lock:
            if sock in clients:
                del clients[sock]

        if username:
            broadcast("INFO", f"{username} left the chat", exclude=sock)

        sock.close()

        print(f"{username} disconnected")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((HOST, PORT))
    server.listen()

    print(f"Server started on {HOST}:{PORT}")

    while True:
        sock, address = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(sock, address)
        )

        thread.start()


if __name__ == "__main__":
    main()