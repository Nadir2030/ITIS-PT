
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QPushButton,
    QListWidget, QLabel, QMessageBox, QComboBox
)


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Task Manager 2.0")
        self.resize(550, 650)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Название задачи")

        self.char_label = QLabel("Название: 0 символов")

        self.task_description = QTextEdit()
        self.task_description.setPlaceholderText("Описание задачи")

        # Приоритет задачи
        self.priority_box = QComboBox()
        self.priority_box.addItems(["Низкий", "Средний", "Высокий"])
        self.priority_box.setCurrentText("Средний")

        self.add_button = QPushButton("Добавить задачу")
        self.delete_button = QPushButton("Удалить выбранную задачу")
        self.clear_button = QPushButton("Очистить список")

        self.task_list = QListWidget()

        self.status_label = QLabel("Задач: 0")

        self.main_layout.addWidget(self.task_input)
        self.main_layout.addWidget(self.char_label)
        self.main_layout.addWidget(self.task_description)
        self.main_layout.addWidget(QLabel("Приоритет:"))
        self.main_layout.addWidget(self.priority_box)
        self.main_layout.addWidget(self.add_button)
        self.main_layout.addWidget(self.task_list)
        self.main_layout.addWidget(self.status_label)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.clear_button)
        self.main_layout.addLayout(buttons_layout)

        # Signals & Slots
        self.add_button.clicked.connect(self.add_task)
        self.delete_button.clicked.connect(self.delete_task)
        self.clear_button.clicked.connect(self.clear_tasks)
        self.task_input.textChanged.connect(self.update_char_count)
        self.task_list.itemSelectionChanged.connect(
            self.update_button_states
        )

        # Единый блок стилей QSS
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f2f4f8;
            }

            QLineEdit, QTextEdit, QComboBox {
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
                font-size: 13px;
            }

            QPushButton:hover {
                background-color: #245dcc;
            }

            QPushButton:disabled {
                background-color: #c5ccd6;
                color: #727b89;
            }

            QListWidget {
                background-color: white;
                border: 1px solid #b8c2d1;
                border-radius: 6px;
                padding: 5px;
                font-size: 14px;
            }

            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e5e9f0;
            }

            QListWidget::item:selected {
                background-color: #dce8ff;
                color: #1c3d75;
            }

            QLabel {
                color: #303846;
                font-size: 13px;
            }
        """)

        self.update_button_states()

    def add_task(self):
        title = self.task_input.text().strip()
        description = self.task_description.toPlainText().strip()
        priority = self.priority_box.currentText()

        if not title:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Введите название задачи!"
            )
            return

        task_text = f"[{priority}] {title}"

        if description:
            task_text += f" — {description}"

        self.task_list.addItem(task_text)

        self.task_input.clear()
        self.task_description.clear()
        self.priority_box.setCurrentText("Средний")

        self.update_status()
        self.update_button_states()

    def update_char_count(self, text):
        self.char_label.setText(
            f"Название: {len(text)} символов"
        )

    def update_status(self):
        self.status_label.setText(
            f"Задач: {self.task_list.count()}"
        )

    def update_button_states(self):
        has_selection = self.task_list.currentRow() >= 0
        self.delete_button.setEnabled(has_selection)
        self.clear_button.setEnabled(self.task_list.count() > 0)

    def delete_task(self):
        row = self.task_list.currentRow()

        if row < 0:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Сначала выберите задачу для удаления."
            )
            return

        answer = QMessageBox.question(
            self,
            "Подтверждение",
            "Удалить выбранную задачу?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.task_list.takeItem(row)
            self.update_status()
            self.update_button_states()

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
            "Удалить все задачи?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer == QMessageBox.StandardButton.Yes:
            self.task_list.clear()
            self.update_status()
            self.update_button_states()


app = QApplication(sys.argv)
window = TaskManager()
window.show()
sys.exit(app.exec())
