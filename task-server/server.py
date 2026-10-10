import socket
import threading
import json

HOST = "127.0.0.1"
PORT = 5000

tasks = []
tasks_lock = threading.Lock()


def send_message(conn, message):
    conn.sendall((json.dumps(message, ensure_ascii=False) + "\\n").encode("utf-8"))


def handle_command(command):
    parts = command.strip().split(maxsplit=1)
    action = parts[0].lower() if parts else ""

    if action == "/add":
        if len(parts) < 2 or not parts[1].strip():
            return "Ошибка: укажите текст задачи. Пример: /add Купить кофе"

        task_text = parts[1].strip()
        with tasks_lock:
            tasks.append({"text": task_text, "done": False})
            number = len(tasks)

        return f"Задача добавлена под номером {number}."

    if action == "/list":
        with tasks_lock:
            if not tasks:
                return "Список задач пуст."

            lines = []
            for number, task in enumerate(tasks, start=1):
                mark = "x" if task["done"] else " "
                lines.append(f"{number}. [{mark}] {task['text']}")
        return "\\n".join(lines)

    if action == "/done":
        if len(parts) < 2:
            return "Ошибка: укажите номер задачи. Пример: /done 1"

        try:
            number = int(parts[1].strip())
        except ValueError:
            return "Ошибка: номер задачи должен быть целым числом."

        with tasks_lock:
            if number < 1 or number > len(tasks):
                return f"Ошибка: задачи с номером {number} не существует."
            tasks[number - 1]["done"] = True

        return f"Задача {number} отмечена как выполненная."

    if action == "/delete":
        if len(parts) < 2:
            return "Ошибка: укажите номер задачи. Пример: /delete 1"

        try:
            number = int(parts[1].strip())
        except ValueError:
            return "Ошибка: номер задачи должен быть целым числом."

        with tasks_lock:
            if number < 1 or number > len(tasks):
                return f"Ошибка: задачи с номером {number} не существует."
            removed = tasks.pop(number - 1)

        return f"Задача удалена: {removed['text']}"

    if action == "/help":
        return (
            "Доступные команды:\\n"
            "/add <текст> — добавить задачу\\n"
            "/list — показать все задачи\\n"
            "/done <номер> — отметить задачу выполненной\\n"
            "/delete <номер> — удалить задачу\\n"
            "/help — показать помощь\\n"
            "/quit — отключиться"
        )

    return "Неизвестная команда. Введите /help для списка команд."


def handle_client(conn, address):
    print(f"Клиент подключился: {address}")
    try:
        send_message(conn, "Добро пожаловать! Введите /help для списка команд.")

        # Один клиент может отправлять несколько команд за одно соединение.
        buffer = ""
        while True:
            data = conn.recv(4096)
            if not data:
                break

            buffer += data.decode("utf-8")
            while "\\n" in buffer:
                command, buffer = buffer.split("\\n", 1)
                command = command.strip()

                if not command:
                    send_message(conn, "Ошибка: пустая команда.")
                    continue

                if command.lower() == "/quit":
                    send_message(conn, "До свидания!")
                    return

                response = handle_command(command)
                send_message(conn, response)
    except (ConnectionError, OSError) as error:
        print(f"Соединение с {address} завершено: {error}")
    finally:
        conn.close()
        print(f"Клиент отключился: {address}")


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Сервер запущен на {HOST}:{PORT}")
        print("Ожидание клиентов...")

        while True:
            conn, address = server.accept()
            thread = threading.Thread(
                target=handle_client,
                args=(conn, address),
                daemon=True
            )
            thread.start()
    except KeyboardInterrupt:
        print("\\nСервер остановлен.")
    finally:
        server.close()


if __name__ == "__main__":
    main()
