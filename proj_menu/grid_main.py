import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, 
                            QColorDialog, QFileDialog, QMessageBox, 
                            QMenu, QHBoxLayout, QFrame, QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QColor, QPixmap, QPainter, QPen
from path_helper import get_resource_path

class GridWindow(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window  
        self.current_tool = None  
        self.pencil_color = QColor('#007BFF')
        self.line_width = 7
        self.shape_type = None

        self.setObjectName("ToolbarWindow")
        
        self.setup_ui()
        self.setFixedHeight(100)

    def setup_ui(self):
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(15, 8, 15, 8)

        self.create_tool_groups()
        
        self.setLayout(self.main_layout)

    def create_tool_groups(self):
        # Группа рисования
        drawing_icons = ["icon1.png", "icon2.png", "icon3.png"]
        drawing_names = ["Карандаш", "Цвет", "Ластик"]
        self.create_tool_group(drawing_icons, drawing_names, 0)
        
        self.add_separator()
        
        # Группа объектов
        object_icons = ["icon4.png", "icon5.png", "icon6.png"]
        object_names = ["Текст", "Фигуры", "Масштаб"]
        self.create_tool_group(object_icons, object_names, 3)
        
        self.add_separator()

        file_icons = ["8.png", "9.png", "10.png"]  
        file_names = ["Сохранить", "Загрузить", "Назад"]  
        self.create_tool_group(file_icons, file_names, 6)

    def create_tool_group(self, icons, names, start_index):
        for i, (icon_name, tool_name) in enumerate(zip(icons, names)):
            self.create_tool_button(icon_name, tool_name, start_index + i)

    def create_tool_button(self, icon_name, tool_name, index):
        button_container = QWidget()
        button_container.setFixedWidth(70)
        
        container_layout = QVBoxLayout(button_container)
        container_layout.setSpacing(4)
        container_layout.setContentsMargins(5, 5, 5, 5)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_button = QPushButton()
        icon_button.setObjectName(f"toolButton_{index}")
        icon_button.setProperty("class", "toolIconButton") 
        icon_button.setToolTip(tool_name)
        icon_button.setCursor(Qt.CursorShape.PointingHandCursor)

        icon_path = get_resource_path(icon_name)
        if os.path.exists(icon_path):
            icon_button.setIcon(QIcon(icon_path))
            icon_button.setIconSize(QSize(28, 28))
        else:
            icon_button.setText(tool_name[0])
            icon_button.setStyleSheet("font-weight: bold; font-size: 14px; color: #007BFF;")
        
        icon_button.setFixedSize(50, 50)
        icon_button.clicked.connect(lambda checked, idx=index: self.on_icon_clicked(idx))

        label = QPushButton(tool_name)
        label.setObjectName("toolLabel")  
        label.setFlat(True)
        label.setEnabled(False)
        label.setFixedHeight(16)
        
        container_layout.addWidget(icon_button, 0, Qt.AlignmentFlag.AlignHCenter)
        container_layout.addWidget(label, 0, Qt.AlignmentFlag.AlignHCenter)
        
        self.main_layout.addWidget(button_container)

        if not hasattr(self, 'tool_buttons'):
            self.tool_buttons = []
        self.tool_buttons.append(icon_button)

    def add_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setFixedWidth(1)
        self.main_layout.addWidget(separator)

    def on_icon_clicked(self, icon_index):
        button = self.tool_buttons[icon_index]

        for i, btn in enumerate(self.tool_buttons):
            btn.setProperty("active", i == icon_index)
            btn.style().polish(btn)

        if icon_index == 0:  # Карандаш
            self.activate_tool("pencil", icon_index)
            self.main_window.canvas.set_drawing(True)
            self.main_window.canvas.set_eraser_mode(False)
            self.main_window.canvas.set_text_mode(False)
            self.main_window.canvas.set_shape_mode(False)  
            self.main_window.show_line_width_slider()
            
        elif icon_index == 1:  # Выбор цвета
            self.current_tool = "color_picker"
            self.choose_pencil_color()
            
        elif icon_index == 2:  # Ластик
            self.activate_tool("eraser", icon_index)
            self.main_window.canvas.set_drawing(True)
            self.main_window.canvas.set_eraser_mode(True)
            self.main_window.canvas.set_text_mode(False)
            self.main_window.canvas.set_shape_mode(False)  
            self.main_window.show_eraser_slider()
            
        elif icon_index == 3:  # Текст
            self.activate_tool("text", icon_index)
            self.main_window.canvas.set_drawing(False)
            self.main_window.canvas.set_eraser_mode(False)
            self.main_window.canvas.set_text_mode(True)
            self.main_window.canvas.set_shape_mode(False)  
            self.main_window.show_text_slider()
            
        elif icon_index == 4:  # Фигуры
            self.current_tool = "shape"
            self.show_shape_menu()
            
        elif icon_index == 5:  # Масштаб
            self.activate_tool("zoom", icon_index)
            self.main_window.canvas.set_drawing(False)
            self.main_window.canvas.set_text_mode(False)
            self.main_window.canvas.set_shape_mode(False)  
            self.main_window.toggle_slider()
            
        elif icon_index == 6:  # Сохранение
            self.save_canvas()
            
        elif icon_index == 7:  # Загрузка
            self.load_canvas()
            
        elif icon_index == 8:  # Кнопка "Назад"
            self.go_back_to_menu()

    def activate_tool(self, tool_name, icon_index):
        self.current_tool = tool_name

    def show_shape_menu(self):
        menu = QMenu(self)
        menu.setObjectName("shapeMenu")
        
        shapes = [
            ("Прямоугольник", "rectangle"),
            ("Круг", "circle"),
            ("Линия", "line"),
        ]
        
        for name, shape_type in shapes:
            action = menu.addAction(name)
            action.triggered.connect(lambda checked, st=shape_type: self.set_shape_type(st))

        if len(self.tool_buttons) > 4:
            menu.exec(self.tool_buttons[4].mapToGlobal(
                self.tool_buttons[4].rect().bottomLeft()
            ))

    def set_shape_type(self, shape_type):
        self.shape_type = shape_type
        self.activate_tool("shape", 4)
        self.main_window.canvas.set_shape_type(shape_type)
        self.main_window.canvas.set_drawing(False)
        self.main_window.canvas.set_text_mode(False)
        self.main_window.canvas.set_eraser_mode(False)
        self.main_window.canvas.set_shape_mode(True)
        self.main_window.show_line_width_slider()

    def choose_pencil_color(self):
        color_dialog = QColorDialog(self.pencil_color, self)
        color_dialog.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, on=True)
        color_dialog.setWindowTitle("Выбор цвета")
        
        if color_dialog.exec() == QColorDialog.DialogCode.Accepted:
            color = color_dialog.selectedColor()
            if color.isValid():
                self.pencil_color = color
                self.main_window.canvas.set_pencil_color(color)

    def save_canvas(self):
        if not self.main_window or not self.main_window.canvas:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Сохранить изображение", 
            "", 
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;All Files (*)"
        )
            
        if file_path:
            if file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                format = "JPEG"
            else:
                if not file_path.endswith('.png'):
                    file_path += '.png'
                format = "PNG"
                
            if not self.main_window.canvas.drawing_pixmap.save(file_path, format):
                QMessageBox.warning(self, "Ошибка", "Не удалось сохранить изображение")

    def load_canvas(self):
        if not self.main_window or not self.main_window.canvas:
            return
        
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Загрузить изображение", 
                "", 
                "Изображения (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
            )
            
            if not file_path:  
                return
                
            loaded_pixmap = QPixmap(file_path)
            if loaded_pixmap.isNull():
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")
                return

            old_width = self.main_window.canvas.drawing_pixmap.width()
            old_height = self.main_window.canvas.drawing_pixmap.height()

            scaled_pixmap = loaded_pixmap.scaled(
                old_width, old_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)

            self.main_window.canvas.drawing_pixmap = QPixmap(old_width, old_height)
            self.main_window.canvas.drawing_pixmap.fill(Qt.GlobalColor.white)

            painter = QPainter(self.main_window.canvas.drawing_pixmap)
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.end()
            
            self.main_window.canvas.scale_factor = 1.0
            self.main_window.canvas.update_canvas()
            
            if hasattr(self.main_window, 'zoom_slider'):
                self.main_window.zoom_slider.setValue(100)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при загрузке:\n{str(e)}")

    def go_back_to_menu(self):
        if self.main_window:
            username = getattr(self.main_window, 'username', 'Пользователь')
            tray_manager = getattr(self.main_window, 'tray_icon_manager', None)
            login_window = getattr(self.main_window, 'login_window', None)

            self.main_window.close()

            if tray_manager and login_window:
                from menu_reg import WelcomeWindow
                welcome_window = WelcomeWindow(tray_manager, username, login_window)
                welcome_window.show()
