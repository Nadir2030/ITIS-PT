
import sys
import socket
import json
import queue

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QMessageBox
)

HOST = "127.0.0.1"
PORT = 5000


class SendThread(QThread):
    error = pyqtSignal(str)

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.messages = queue.Queue()

    def send(self, message):
        self.messages.put(message)

    def stop(self):
        self.messages.put(None)

    def run(self):
        while True:
            message = self.messages.get()

            if message is None:
                break

            try:
                data = (
                    json.dumps(message, ensure_ascii=False) + "\n"
                ).encode("utf-8")

                self.sock.sendall(data)

            except OSError as e:
                self.error.emit(str(e))
                break


class ReceiveThread(QThread):
    message_received = pyqtSignal(dict)
    disconnected = pyqtSignal()

    def __init__(self, sock):
        super().__init__()
        self.sock = sock

    def run(self):
        try:
            reader = self.sock.makefile("r", encoding="utf-8")

            for line in reader:
                try:
                    message = json.loads(line)

                    if isinstance(message, dict):
                        self.message_received.emit(message)

                except json.JSONDecodeError:
                    continue

        except (ConnectionError, OSError, UnicodeError):
            pass
        finally:
            self.disconnected.emit()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Сетевой чат PyQt6")
        self.resize(600, 450)

        self.sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.send_thread = None
        self.receive_thread = None
        self.connected = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Задание 1: имя пользователя
        layout.addWidget(QLabel("Ваше имя:"))

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(
            "Введите ваше имя"
        )
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("История сообщений:"))

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(self.chat_history)

        message_layout = QHBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText(
            "Введите сообщение..."
        )

        self.send_button = QPushButton("Send")

        message_layout.addWidget(self.input)
        message_layout.addWidget(self.send_button)

        layout.addLayout(message_layout)

        # Отправка сообщения кнопкой
        self.send_button.clicked.connect(
            self.on_send_clicked
        )

        # Задание 3: отправка по Enter
        self.input.returnPressed.connect(
            self.on_send_clicked
        )

        self.setStyleSheet("""
            QMainWindow {
                background-color: #f2f4f8;
            }

            QLineEdit, QTextEdit {
                background-color: white;
                color: #222222;
                border: 1px solid #b8c2d1;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }

            QPushButton {
                background-color: #3478f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
            }

            QPushButton:hover {
                background-color: #245dcc;
            }

            QLabel {
                color: #303846;
                font-size: 14px;
            }
        """)

        self.connect_to_server()

    def connect_to_server(self):
        try:
            self.sock.connect((HOST, PORT))
            self.connected = True

            self.send_thread = SendThread(self.sock)
            self.receive_thread = ReceiveThread(self.sock)

            self.receive_thread.message_received.connect(
                self.handle_message
            )

            self.receive_thread.disconnected.connect(
                self.on_disconnected
            )

            self.send_thread.error.connect(
                self.on_send_error
            )

            self.send_thread.start()
            self.receive_thread.start()

        except OSError:
            self.connected = False
            self.send_button.setEnabled(False)
            self.input.setEnabled(False)

            QMessageBox.warning(
                self,
                "Ошибка подключения",
                "Не удалось подключиться к серверу.\n"
                "Сначала запустите server.py"
            )

    def on_send_clicked(self):
        if not self.connected:
            return

        # Задание 2: защита от пустых сообщений
        text = self.input.text().strip()

        if not text:
            return

        username = self.username_input.text().strip()

        if not username:
            username = "Гость"

        # Задание 1: передача имени отправителя
        message = {
            "type": "chat",
            "username": username,
            "text": text
        }

        self.send_thread.send(message)

        # Очищаем поле только после принятия
        # непустого сообщения к отправке
        self.input.clear()

    def handle_message(self, message):
        # Задание 4: разные типы сообщений
        message_type = message.get("type")

        if message_type == "chat":
            username = message.get("username", "Гость")
            text = message.get("text", "")

            self.chat_history.append(
                f"{username}: {text}"
            )

        elif message_type == "system":
            text = message.get("text", "")

            self.chat_history.append(
                f"[Система] {text}"
            )

        else:
            # Неизвестный тип не вызывает ошибку
            pass

    def on_disconnected(self):
        self.connected = False
        self.send_button.setEnabled(False)
        self.input.setEnabled(False)

        self.handle_message({
            "type": "system",
            "text": "Соединение с сервером закрыто"
        })

    def on_send_error(self, error):
        self.handle_message({
            "type": "system",
            "text": f"Ошибка отправки: {error}"
        })

    def closeEvent(self, event):
        self.connected = False

        if self.send_thread is not None:
            self.send_thread.stop()

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        self.sock.close()

        if self.send_thread is not None:
            self.send_thread.wait(2000)

        if self.receive_thread is not None:
            self.receive_thread.wait(2000)

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
