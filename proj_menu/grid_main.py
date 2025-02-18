from PyQt6.QtWidgets import QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PyQt6.QtCore import Qt

class GridWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Window")
        self.setGeometry(100, 100, 600, 400)

        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(5)  
        self.table_widget.setColumnCount(3)  

        self.table_widget.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

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

        for row_idx, row_data in enumerate(data):
            for col_idx, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table_widget.setItem(row_idx, col_idx, item)
