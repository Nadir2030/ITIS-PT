
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QPushButton,
    QListWidget, QLabel, QMessageBox
)


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Manager 2.0")
        self.resize(500, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Название задачи")

        self.char_label = QLabel("Название: 0 символов")

        self.task_description = QTextEdit()
        self.task_description.setPlaceholderText("Описание задачи")

        self.add_button = QPushButton("Добавить задачу")
        self.clear_button = QPushButton("Очистить список")

        self.task_list = QListWidget()

        self.status_label = QLabel("Задач: 0")

        self.main_layout.addWidget(self.task_input)
        self.main_layout.addWidget(self.char_label)
        self.main_layout.addWidget(self.task_description)
        self.main_layout.addWidget(self.add_button)
        self.main_layout.addWidget(self.task_list)
        self.main_layout.addWidget(self.status_label)
        self.main_layout.addWidget(self.clear_button)

        self.add_button.clicked.connect(self.add_task)
        self.clear_button.clicked.connect(self.clear_tasks)
        self.task_input.textChanged.connect(self.update_char_count)

        # Стили
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f2f4f8;
            }

            QLineEdit, QTextEdit {
                background-color: white;
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
                font-size: 14px;
            }

            QPushButton:hover {
                background-color: #245dcc;
            }

            QListWidget {
                background-color: white;
                border: 1px solid #b8c2d1;
                border-radius: 6px;
                padding: 5px;
                font-size: 14px;
            }

            QLabel {
                color: #303846;
                font-size: 13px;
            }
        """)

    def add_task(self):
        title = self.task_input.text().strip()
        description = self.task_description.toPlainText().strip()

        if not title:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Введите название задачи!"
            )
            return

        if description:
            task_text = f"{title} — {description}"
        else:
            task_text = title

        self.task_list.addItem(task_text)

        self.task_input.clear()
        self.task_description.clear()

        self.update_status()

    def update_char_count(self, text):
        count = len(text)
        self.char_label.setText(
            f"Название: {count} символов"
        )

    def update_status(self):
        count = self.task_list.count()
        self.status_label.setText(f"Задач: {count}")

    def clear_tasks(self):
        if self.task_list.count() == 0:
            QMessageBox.information(
                self,
                "Информация",
                "Список задач уже пуст."
            )
            return

        answer = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы действительно хотите удалить все задачи?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.task_list.clear()
            self.update_status()


app = QApplication(sys.argv)
window = TaskManager()
window.show()
sys.exit(app.exec())
