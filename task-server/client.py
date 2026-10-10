import socket
import json

HOST = "127.0.0.1"
PORT = 5000


def receive_message(sock):
    data = b""
    while not data.endswith(b"\\n"):
        part = sock.recv(1)
        if not part:
            return None
        data += part
    return json.loads(data.decode("utf-8").rstrip("\\n"))


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((HOST, PORT))
        print(receive_message(client))
        print("Введите /help, чтобы посмотреть команды.")

        while True:
            command = input("> ").strip()
            if not command:
                print("Введите команду.")
                continue

            client.sendall((command + "\\n").encode("utf-8"))
            response = receive_message(client)

            if response is None:
                print("Соединение с сервером закрыто.")
                break

            print(response)

            if command.lower() == "/quit":
                break

    except ConnectionRefusedError:
        print("Не удалось подключиться. Сначала запустите server.py.")
    except (ConnectionError, OSError) as error:
        print(f"Ошибка соединения: {error}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
