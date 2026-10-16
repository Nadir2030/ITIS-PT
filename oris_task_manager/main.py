
import sys

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QPushButton,
    QGroupBox,
    QComboBox,
)


class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Менеджер задач")
        self.resize(600, 750)

        self.tasks = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        title_label = QLabel("Название задачи:")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(
            "Введите название задачи"
        )

        main_layout.addWidget(title_label)
        main_layout.addWidget(self.title_input)

        description_label = QLabel("Описание:")
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Опишите задачу..."
        )
        self.description_input.setFixedHeight(100)

        main_layout.addWidget(description_label)
        main_layout.addWidget(self.description_input)

        priority_group = QGroupBox("Приоритет")
        priority_layout = QHBoxLayout()
        priority_group.setLayout(priority_layout)

        self.low_radio = QRadioButton("Низкий")
        self.medium_radio = QRadioButton("Средний")
        self.high_radio = QRadioButton("Высокий")

        self.priority_buttons = QButtonGroup(self)
        self.priority_buttons.addButton(self.low_radio)
        self.priority_buttons.addButton(self.medium_radio)
        self.priority_buttons.addButton(self.high_radio)

        self.medium_radio.setChecked(True)

        priority_layout.addWidget(self.low_radio)
        priority_layout.addWidget(self.medium_radio)
        priority_layout.addWidget(self.high_radio)

        main_layout.addWidget(priority_group)

        settings_group = QGroupBox("Дополнительные настройки")
        settings_layout = QVBoxLayout()
        settings_group.setLayout(settings_layout)

        self.important_checkbox = QCheckBox("Важная задача")
        self.notification_checkbox = QCheckBox(
            "Отправить уведомление"
        )

        settings_layout.addWidget(self.important_checkbox)
        settings_layout.addWidget(self.notification_checkbox)

        main_layout.addWidget(settings_group)

        buttons_layout = QHBoxLayout()

        self.create_button = QPushButton("Создать задачу")
        self.clear_button = QPushButton("Очистить")
        self.delete_button = QPushButton(
            "Удалить последнюю задачу"
        )

        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.delete_button)

        main_layout.addLayout(buttons_layout)

        filter_layout = QHBoxLayout()

        filter_label = QLabel("Фильтр по приоритету:")

        self.priority_filter = QComboBox()
        self.priority_filter.addItems(
            ["Все", "Низкий", "Средний", "Высокий"]
        )

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.priority_filter)

        main_layout.addLayout(filter_layout)

        self.tasks_output = QTextEdit()
        self.tasks_output.setReadOnly(True)
        self.tasks_output.setPlaceholderText(
            "Созданные задачи появятся здесь..."
        )

        main_layout.addWidget(self.tasks_output)

        self.status_label = QLabel("Статус: Готов к работе")
        self.counter_label = QLabel("Создано задач: 0")

        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.counter_label)

        self.create_button.clicked.connect(self.create_task)
        self.clear_button.clicked.connect(self.clear_form)
        self.delete_button.clicked.connect(self.delete_last_task)

        self.priority_filter.currentTextChanged.connect(
            self.show_tasks
        )

    def get_selected_priority(self):
        if self.low_radio.isChecked():
            return "Низкий"

        if self.high_radio.isChecked():
            return "Высокий"

        return "Средний"

    def create_task(self):
        title = self.title_input.text().strip()

        description = (
            self.description_input.toPlainText().strip()
        )

        if not title:
            self.status_label.setText(
                "Статус: Введите название задачи"
            )
            self.title_input.setFocus()
            return
            
        task = {
            "title": title,
            "description": description,
            "priority": self.get_selected_priority(),
            "important": self.important_checkbox.isChecked(),
            "notification": (
                self.notification_checkbox.isChecked()
            ),
        }

        self.tasks.append(task)

        self.counter_label.setText(
            f"Создано задач: {len(self.tasks)}"
        )

        self.status_label.setText("Статус: Задача создана")
        
        self.show_tasks()
        self.clear_form()

    def show_tasks(self):
        selected_priority = self.priority_filter.currentText()

        self.tasks_output.clear()

        visible_tasks = self.tasks

        if selected_priority != "Все":
            visible_tasks = [
                task for task in self.tasks
                if task["priority"] == selected_priority
            ]

        if not visible_tasks:
            self.tasks_output.setPlainText(
                "Нет задач для отображения."
            )
            return

        for number, task in enumerate(visible_tasks, start=1):
            important = (
                "Да" if task["important"] else "Нет"
            )

            notification = (
                "Да" if task["notification"] else "Нет"
            )

            task_text = (
                f"Задача №{number}\n"
                f"Название: {task['title']}\n"
                f"Описание: "
                f"{task['description'] or 'Без описания'}\n"
                f"Приоритет: {task['priority']}\n"
                f"Важная задача: {important}\n"
                f"Уведомление: {notification}\n"
                f"{'-' * 35}\n"
            )

            self.tasks_output.append(task_text)

    def clear_form(self):

        self.title_input.clear()
        self.description_input.clear()

        self.medium_radio.setChecked(True)

        self.important_checkbox.setChecked(False)
        self.notification_checkbox.setChecked(False)

        self.title_input.setFocus()

    def delete_last_task(self):
        if not self.tasks:
            self.status_label.setText(
                "Статус: Нет задач для удаления"
            )
            return

        self.tasks.pop()

        self.counter_label.setText(
            f"Создано задач: {len(self.tasks)}"
        )

        self.status_label.setText(
            "Статус: Последняя задача удалена"
        )

        self.show_tasks()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TaskManager()
    window.show()

    sys.exit(app.exec())
