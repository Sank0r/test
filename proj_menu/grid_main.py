from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView, QGridLayout, QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

class GridWindow(QMainWindow):
    def __init__(self, main_window=None):
        super().__init__()
        self.setWindowTitle("Grid Window")
        self.setGeometry(100, 100, 600, 400)
        self.main_window = main_window  
        self.current_tool = None  

        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(1)  # 1 строка
        self.table_widget.setColumnCount(1)  # 1 столбец

        self.table_widget.setHorizontalHeaderLabels(["Инструменты"])  # Заголовок столбца

        self.table_widget.verticalHeader().setVisible(False)

        self.populate_table()

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def populate_table(self):
        # Иконки для инструментов
        icons = [
            "icon1.png", "icon2.png", "icon3.png",
            "icon4.png", "icon5.png", "icon6.png"
        ]
        icon_widget = QWidget()
        icon_layout = QGridLayout(icon_widget)
        icon_layout.setSpacing(0)
        icon_layout.setContentsMargins(0, 0, 0, 0)

        for i in range(6):
            icon_button = QPushButton()
            icon_button.setIcon(QIcon(icons[i]))
            icon_button.setIconSize(QSize(32, 32))
            icon_button.setFixedSize(32, 32)
            icon_button.setStyleSheet("QPushButton { border: none; padding: 0; margin: 0; }")
            icon_button.clicked.connect(lambda checked, i=i: self.on_icon_clicked(i))
            icon_layout.addWidget(icon_button, 0, i) 

        icon_widget.setLayout(icon_layout)

        self.table_widget.setCellWidget(0, 0, icon_widget)

        self.table_widget.setRowHeight(0, 50) 
        self.table_widget.setColumnWidth(0, 300)  

    def on_icon_clicked(self, icon_index):
        print(f"Иконка {icon_index + 1} нажата!")
        if icon_index == 0:
            print("Действие для иконки 1")
            self.current_tool = "pencil"
            self.main_window.canvas.set_drawing(True)
        elif icon_index == 1:
            print("Действие для иконки 2")
            self.current_tool = None
            self.main_window.canvas.set_drawing(False)
        elif icon_index == 2:
            print("Действие для иконки 3")
            self.current_tool = None
            self.main_window.canvas.set_drawing(False)
        elif icon_index == 3:
            print("Действие для иконки 4")
            self.current_tool = None
            self.main_window.canvas.set_drawing(False)
        elif icon_index == 4:
            print("Действие для иконки 5")
            self.current_tool = None
            self.main_window.canvas.set_drawing(False)
        elif icon_index == 5:
            print("Зум")
            if self.main_window:
                self.main_window.toggle_zoom_slider()

        for i in range(6):
            button = self.table_widget.cellWidget(0, 0).layout().itemAt(i).widget()
            if i == icon_index:
                button.setStyleSheet("QPushButton { border: none; padding: 0; margin: 0; border-radius: 5px; background-color: rgba(0, 0, 0, 0.1); }")
            else:
                button.setStyleSheet("QPushButton { border: none; padding: 0; margin: 0; }")
