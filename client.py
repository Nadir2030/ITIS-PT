import socket
import threading

from protocol import send_message, recv_message

HOST = "127.0.0.1"
PORT = 5555


def receive_messages(sock):
    try:
        while True:
            result = recv_message(sock)

            if result is None:
                break

            command, payload = result

            print(f"\n[{command}] {payload.decode('utf-8')}")
            print("> ", end="", flush=True)

    except ConnectionResetError:
        print("\nServer closed the connection")

    except ConnectionError:
        print("\nConnection closed")

    finally:
        sock.close()


def send_messages(sock, username):
    try:
        send_message(sock, "JOIN", username.encode("utf-8"))

        while True:
            text = input("> ")

            if text == "/quit":
                send_message(sock, "QUIT", b"")
                break

            elif text == "/list":
                send_message(sock, "LIST", b"")

            else:
                send_message(sock, "TEXT", text.encode("utf-8"))

    except BrokenPipeError:
        print("Server connection is unavailable")

    except ConnectionResetError:
        print("Server reset the connection")

    finally:
        sock.close()


def main():
    username = input("Username: ")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    receiver = threading.Thread(
        target=receive_messages,
        args=(sock,)
    )

    receiver.start()

    send_messages(sock, username)


if __name__ == "__main__":
    main()