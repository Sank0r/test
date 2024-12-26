import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLineEdit, QPushButton, QLabel)
from PyQt6.QtCore import Qt

class ResolutionChanger(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Resolution Changer")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Ввод ширины и высоты
        width_layout = QHBoxLayout()
        width_label = QLabel("Ширина:")
        self.width_input = QLineEdit()
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_input)
        main_layout.addLayout(width_layout)

        height_layout = QHBoxLayout()
        height_label = QLabel("Высота:")
        self.height_input = QLineEdit()
        height_layout.addWidget(height_label)
        height_layout.addWidget(self.height_input)
        main_layout.addLayout(height_layout)


        # Кнопка изменения размера
        change_button = QPushButton("Изменить разрешение")
        change_button.clicked.connect(self.change_resolution)
        main_layout.addWidget(change_button)

        # Вывод текущего размера
        self.current_size_label = QLabel("Текущий размер: ")
        main_layout.addWidget(self.current_size_label)
        self.update_current_size()

    def change_resolution(self):
        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
            if width <= 0 or height <= 0:
                QMessageBox.warning(self, "Ошибка", "Ширина и высота должны быть положительными числами.")
                return

            self.setFixedSize(width, height)
            self.update_current_size()
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Введите целые числа для ширины и высоты.")

    def update_current_size(self):
        width = self.width()
        height = self.height()
        self.current_size_label.setText(f"Текущий размер: {width} x {height}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResolutionChanger()
    window.show()
    sys.exit(app.exec())
