from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView, QGridLayout, QPushButton
from PyQt6.QtCore import Qt,QSize
from PyQt6.QtGui import QIcon, QPixmap

class GridWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Window")
        self.setGeometry(100, 100, 600, 400)

        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(5)  # 5 строк
        self.table_widget.setColumnCount(3)  # 3 столбца

        self.table_widget.setHorizontalHeaderLabels(["Column 1", "Инструменты", "Column 3"])

        self.populate_table()

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def populate_table(self):
        data = [
            ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
            ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
            ["Row 3 Col 1", "Row 3 Col 2", "Row 3 Col 3"],
            ["Row 4 Col 1", "Row 4 Col 2", "Row 4 Col 3"],
            ["Row 5 Col 1", "Row 5 Col 2", "Row 5 Col 3"]
        ]

        # Иконки для инструментов
        icons = [
            "icon1.png", "icon2.png", "icon3.png",
            "icon4.png", "icon5.png", "icon6.png"
        ]

        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                if row_idx == 0 and col_idx == 1:
                    icon_widget = QWidget()
                    icon_layout = QGridLayout(icon_widget)
                    for i in range(6):
                        icon_button = QPushButton()
                        icon_button.setIcon(QIcon(icons[i]))
                        icon_button.setIconSize(QSize(32, 32))  
                        icon_button.clicked.connect(lambda checked, i=i: self.on_icon_clicked(i))  
                        icon_layout.addWidget(icon_button, i // 3, i % 3)  
                    icon_widget.setLayout(icon_layout)
                    self.table_widget.setCellWidget(row_idx, col_idx, icon_widget)
                else:
                    self.table_widget.setItem(row_idx, col_idx, item)

        # Pазмер строк и столбцов
        self.table_widget.setRowHeight(1, 80)  
        self.table_widget.setColumnWidth(1, 150)  

    def on_icon_clicked(self, icon_index):
        print(f"Иконка {icon_index + 1} нажата!")
        if icon_index == 0:
            print("Действие для иконки 1")
        elif icon_index == 1:
            print("Действие для иконки 2")
        elif icon_index == 2:
            print("Действие для иконки 3")
        elif icon_index == 3:
            print("Действие для иконки 4")
        elif icon_index == 4:
            print("Действие для иконки 5")
        elif icon_index == 5:
            print("Действие для иконки 6")
