from PyQt6.QtWidgets import (QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView,QGridLayout,QPushButton,QColorDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor

class GridWindow(QMainWindow):
    def __init__(self, main_window=None):
        super().__init__()
        self.setWindowTitle("Grid Window")
        self.setGeometry(100, 100, 600, 400)
        self.main_window = main_window  
        self.current_tool = None  
        self.pencil_color = QColor('black')  
        self.line_width = 7

        self.table_widget = QTableWidget()
        self.table_widget.setRowCount(1)
        self.table_widget.setColumnCount(1)
        self.table_widget.setHorizontalHeaderLabels(["Инструменты"])
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.horizontalHeader().setDefaultSectionSize(50)

        self.populate_table()

        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def populate_table(self):
        icons = [
            "icon1.png", "icon2.png", "icon3.png",
            "icon4.png", "icon5.png", "icon6.png"]
        icon_widget = QWidget()
        icon_layout = QGridLayout(icon_widget)
        icon_layout.setSpacing(10)
        icon_layout.setContentsMargins(10, 10, 10, 10)

        for i in range(6):
            icon_button = QPushButton()
            icon_button.setObjectName("iconButton")  
            if i < len(icons):
                icon_button.setIcon(QIcon(icons[i]))      
            else:
                icon_button.setText("-" if i == 6 else "+")
            icon_button.setIconSize(QSize(32, 32))
            icon_button.setFixedSize(40, 40)
            icon_button.clicked.connect(lambda checked, i=i: self.on_icon_clicked(i))
            icon_layout.addWidget(icon_button, 0, i) 

        icon_widget.setLayout(icon_layout)
        self.table_widget.setCellWidget(0, 0, icon_widget)
        self.table_widget.setRowHeight(0, 60)
        self.table_widget.setColumnWidth(0, 400)

    def on_icon_clicked(self, icon_index):
        if icon_index == 0:  # Карандаш
            self.current_tool = "pencil"
            self.main_window.canvas.set_drawing(True)
            self.main_window.canvas.set_eraser_mode(False)
            self.main_window.canvas.set_text_mode(False)
            self.main_window.show_line_width_slider()
        elif icon_index == 1:  # Выбор цвета
            self.current_tool = "color_picker"
            self.choose_pencil_color()
        elif icon_index == 2:  # Ластик
            self.current_tool = "eraser"
            self.main_window.canvas.set_drawing(True)
            self.main_window.canvas.set_eraser_mode(True)
            self.main_window.canvas.set_text_mode(False)
            self.main_window.show_line_width_slider()
        elif icon_index == 3:  # Текст
            self.current_tool = "text"
            self.main_window.canvas.set_drawing(False)
            self.main_window.canvas.set_eraser_mode(False)
            self.main_window.canvas.set_text_mode(True)
            self.main_window.slider_container.hide()
        elif icon_index == 4:  
            self.current_tool = None
            self.main_window.canvas.set_drawing(False)
            self.main_window.canvas.set_text_mode(False)
            self.main_window.slider_container.hide()
        elif icon_index == 5:  # Масштаб
            self.current_tool = None
            self.main_window.canvas.set_drawing(False)
            self.main_window.canvas.set_text_mode(False)
            self.main_window.toggle_slider()

        for i in range(6):
            button = self.table_widget.cellWidget(0, 0).layout().itemAt(i).widget()
            button.setProperty("active", i == icon_index)
            button.style().polish(button)  

    def choose_pencil_color(self):
        color_dialog = QColorDialog(self)
        color_dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, on=True)
        color_dialog.setWindowIcon(QIcon("icon2.png")) 
        color_dialog.setWindowTitle("Выберите цвет")

        if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
            color = color_dialog.currentColor()
            if color.isValid():
                self.pencil_color = color
                self.main_window.canvas.set_pencil_color(color)
