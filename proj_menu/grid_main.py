import os
from PyQt6.QtWidgets import (QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, 
                            QWidget, QHeaderView, QGridLayout, QPushButton, 
                            QColorDialog, QFileDialog, QMessageBox, QDialog, QHBoxLayout)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor, QPixmap

class GridWindow(QMainWindow):
    def __init__(self, main_window=None):
        super().__init__()
        self.setWindowTitle("Grid Window")
        self.setGeometry(100, 100, 600, 400)
        self.main_window = main_window  
        self.current_tool = None  
        self.pencil_color = QColor('black')  
        self.line_width = 7
        self.current_shape = None

        self.shape_icons = {
            "Круг": QIcon("circle.png"),
            "Квадрат": QIcon("square.png")
        }

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
            "icon4.png", "icon5.png", "icon6.png",
            "8.png", "9.png" 
        ]
        
        icon_widget = QWidget()
        icon_layout = QGridLayout(icon_widget)
        icon_layout.setSpacing(10)
        icon_layout.setContentsMargins(10, 10, 10, 10)

        for i in range(8):  
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
            self.main_window.canvas.set_shape_mode(False)
            self.main_window.show_line_width_slider()
        elif icon_index == 1:  # Выбор цвета
            self.current_tool = "color_picker"
            self.choose_pencil_color()
        elif icon_index == 2:  # Ластик
            self.current_tool = "eraser"
            self.main_window.canvas.set_drawing(True)
            self.main_window.canvas.set_eraser_mode(True)
            self.main_window.canvas.set_text_mode(False)
            self.main_window.canvas.set_shape_mode(False)
            self.main_window.show_line_width_slider()
        elif icon_index == 3:  # Текст
            self.current_tool = "text"
            self.main_window.canvas.set_drawing(False)
            self.main_window.canvas.set_eraser_mode(False)
            self.main_window.canvas.set_text_mode(True)
            self.main_window.canvas.set_shape_mode(False)
            self.main_window.slider_container.hide()
        elif icon_index == 4:  # Фигуры
            self.current_tool = "shape"
            self.show_shape_dialog()
        elif icon_index == 5:  # Масштаб
            self.current_tool = None
            self.main_window.canvas.set_drawing(False)
            self.main_window.canvas.set_text_mode(False)
            self.main_window.canvas.set_shape_mode(False)
            self.main_window.toggle_slider()
        elif icon_index == 6:  # Сохранение
            self.save_canvas()
        elif icon_index == 7:  # Загрузка
            self.load_canvas()

        for i in range(8): 
            button = self.table_widget.cellWidget(0, 0).layout().itemAt(i).widget()
            button.setProperty("active", i == icon_index)
            button.style().polish(button)  

    def show_shape_dialog(self):
        shape_dialog = QDialog(self)
        shape_dialog.setWindowTitle("Выберите фигуру")
        shape_dialog.setFixedSize(250, 100)
        
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        for shape_name, icon in self.shape_icons.items():
            btn = QPushButton()
            btn.setIcon(icon)
            btn.setIconSize(QSize(48, 48))
            btn.setToolTip(shape_name)
            btn.setFixedSize(60, 60)
            btn.setStyleSheet("""
                QPushButton {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 5px;
                    background: white;
                }
                QPushButton:hover {
                    background: #f0f0f0;
                }
                QPushButton:pressed {
                    background: #e0e0e0;
                }
            """)
            btn.clicked.connect(lambda _, s=shape_name: self.on_shape_selected(s))
            layout.addWidget(btn)
        
        shape_dialog.setLayout(layout)
        shape_dialog.exec()

    def on_shape_selected(self, shape):
        if not self.main_window or not hasattr(self.main_window, 'canvas'):
            return
            
        self.current_shape = shape
        self.main_window.canvas.set_drawing(True)
        self.main_window.canvas.set_shape_mode(True, shape)
        self.main_window.show_line_width_slider()
        
        for i in range(8):
            btn = self.table_widget.cellWidget(0, 0).layout().itemAt(i).widget()
            btn.setProperty("active", i == 4)
            btn.style().polish(btn)

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

    def save_canvas(self):
        if not self.main_window or not self.main_window.canvas:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "", "PNG Files (*.png);;All Files (*)")
            
        if file_path:
            if not file_path.endswith('.png'):
                file_path += '.png'
            if not self.main_window.canvas.drawing_pixmap.save(file_path, "PNG"):
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изображение")

    def load_canvas(self):
        if not self.main_window or not self.main_window.canvas:
            return
        
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Загрузить изображение", "", "PNG Files (*.png);;All Files (*)")
            
            if not file_path:  
                return

            if not os.path.exists(file_path):
                QMessageBox.warning(self, "Ошибка", "Файл не существует")
                return
                
            loaded_pixmap = QPixmap(file_path)
            if loaded_pixmap.isNull():
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")
                return

            old_width = self.main_window.canvas.drawing_pixmap.width()
            old_height = self.main_window.canvas.drawing_pixmap.height()

            scaled_pixmap = loaded_pixmap.scaled(
                old_width, old_height,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            
            self.main_window.canvas.drawing_pixmap = scaled_pixmap
            self.main_window.canvas.original_pixmap = scaled_pixmap.copy()
            
            self.main_window.canvas.scale_factor = 1.0
            self.main_window.canvas.update_canvas()
            
            if hasattr(self.main_window, 'zoom_slider'):
                self.main_window.zoom_slider.setValue(100)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при загрузке:\n{str(e)}")
