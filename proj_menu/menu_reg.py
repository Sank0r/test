import os
import sys
import socket
from datetime import datetime
import chat
import importlib.util
import subprocess
from PyQt6.QtCore import Qt, QSize, QPoint, QTime
from PyQt6.QtWidgets import (
    QGroupBox, QApplication, QMainWindow, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QWidget, QMessageBox, QLabel, QTextEdit, QDateEdit, QScrollArea, QDialog, 
    QFrame, QComboBox, QCheckBox, QSlider, QHBoxLayout, QStatusBar)
from PyQt6.QtGui import QIcon, QPixmap, QAction, QPainter, QColor, QFont, QCursor
import db_main
import common
import grid_main
from settings_qmenu import SettingsManager
from language_values import LanguageConstants
from tray_icon import TrayIconManager
from canvas import Canvas

from PyQt6.QtCore import QCoreApplication

APPLICATION_LANGUAGE = ""
APPLICATION_SCREEN_SIZE = (640, 480)
PALETTE_SCREEN_SIZE = (640, 480)

def load_stylesheet(style):
    try:
        with open(style, "r", encoding='utf-8') as file:  
            return file.read()
    except FileNotFoundError:
        print(LanguageConstants.get_constant("STYLESHEET_FILE_NOT_FOUND", APPLICATION_LANGUAGE))
        return ""

class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(LanguageConstants.get_constant("SETTINGS", APPLICATION_LANGUAGE))
        self.setFixedSize(600, 500) 
        self.setWindowIcon(QIcon("gear.png"))

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.inputs = {}

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        current_setting = SettingsManager.get_next_section()
        while True:
            section_data = current_setting()
            if not section_data:
                break
            
            section_values, section_name = section_data
            
            # Группа для секции
            group = QGroupBox(LanguageConstants.get_section_name(section_name, APPLICATION_LANGUAGE))
            group_layout = QFormLayout()
            group_layout.setVerticalSpacing(10)
            
            for key, value in section_values.items():
                label = QLabel(LanguageConstants.get_param_name(key, APPLICATION_LANGUAGE) + ":")
                line_edit = QLineEdit(value)
                group_layout.addRow(label, line_edit)
                self.inputs[f"{section_name}@@{key}"] = line_edit
            
            group.setLayout(group_layout)
            content_layout.addWidget(group)
        
        content_layout.addStretch()
        scroll.setWidget(content_widget)
        self.layout.addWidget(scroll)

        btn_save = QPushButton(LanguageConstants.get_constant("SAVE", APPLICATION_LANGUAGE))
        btn_save.clicked.connect(self.save_settings)
        self.layout.addWidget(btn_save)

    def save_settings(self):
        for key, line_edit in self.inputs.items():
            section, param = key.split("@@")
            SettingsManager.set_setting(section, param, line_edit.text())
        
        SettingsManager.save_settings()
        QMessageBox.information(self, LanguageConstants.get_constant("SETTINGS", APPLICATION_LANGUAGE),LanguageConstants.get_constant("SETTINGS_SAVED", APPLICATION_LANGUAGE))

class LoginWindow(QMainWindow):
    def __init__(self, tray_icon_manager):
        super().__init__()
        self.tray_icon_manager = tray_icon_manager

        # Настройка статусбара и меню
        self.statusBar()
        
        # Действие для настроек
        self.setAct = QAction(QIcon('gear.png'), '&Settings', self)
        self.setAct.setShortcut('Ctrl+Q')
        self.setAct.setStatusTip('Set Up Application')
        self.setAct.triggered.connect(self.show_settings)

        # Действие для сетевого взаимодействия 
        self.setNet = QAction(QIcon('gear.png'), '&Connection', self)
        self.setNet.setShortcut('Ctrl+R')
        self.setNet.setStatusTip('Set Up Connection')
        self.setNet.triggered.connect(self.show_network)
        
        # Создание меню
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('&Manager')
        self.fileMenu.addAction(self.setAct)

        self.fileMenu = self.menubar.addMenu('&Network')
        self.fileMenu.addAction(self.setNet)
        
        # Основные настройки окна
        self.setWindowTitle(LanguageConstants.get_constant("LOGIN", APPLICATION_LANGUAGE))
        self.setFixedSize(APPLICATION_SCREEN_SIZE[0], APPLICATION_SCREEN_SIZE[1])
        self.setWindowIcon(QIcon("icon.png"))

        # Центральный виджет и основной лейаут
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        form_layout = QFormLayout()
        
        # Поле ввода имени пользователя
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(LanguageConstants.get_constant("USERNAME_PLACEHOLDER", APPLICATION_LANGUAGE))
        form_layout.addRow(LanguageConstants.get_constant("USERNAME_WINDOW", APPLICATION_LANGUAGE), self.username_input)

        # Поле ввода пароля
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(LanguageConstants.get_constant("PASSWORD_PLACEHOLDER", APPLICATION_LANGUAGE))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(LanguageConstants.get_constant("PASSWORD_WINDOW", APPLICATION_LANGUAGE), self.password_input)

        # Кнопки входа и регистрации
        self.login_button = QPushButton(LanguageConstants.get_constant("LOGIN", APPLICATION_LANGUAGE))
        self.login_button.clicked.connect(self.handle_login)

        self.register_button = QPushButton(LanguageConstants.get_constant("REGISTER", APPLICATION_LANGUAGE))
        self.register_button.clicked.connect(self.open_registration_window)

        # Добавление элементов в лейаут
        layout.addLayout(form_layout)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

    def closeEvent(self, event):
        event.accept() 

    def show_settings(self):
        settings_window = SettingsWindow()
        settings_window.exec()

    def show_network(self):
        chatApp = chat.ChatApp().run()

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        password = common.get_md5_of_string(password)

        try:
            conn = db_main.connect_db("users.db", False)
            data = db_main.request_select_db(conn, "SELECT count(*) FROM users WHERE login=? AND password=?", (username, password))
                
            count_user = data[0][0]
            user_exist = bool(count_user)

            if user_exist:
                self.open_welcome_window(username)
            else:
                QMessageBox.warning(self, "Warning", "Invalid username or password")

        except db_main.DatabaseException as ex:
            QMessageBox.critical(self, "Critical", ex.msg)
        finally:
            if 'conn' in locals():
                db_main.disconnect_db(conn)

    def open_welcome_window(self, username):
        self.welcome_window = WelcomeWindow(self.tray_icon_manager, username)
        self.welcome_window.show()
        self.hide()

    def open_registration_window(self):
        self.registration_window = RegistrationWindow(self.tray_icon_manager)
        self.registration_window.show()
        self.hide()
        
class WelcomeWindow(QMainWindow):
    def __init__(self, tray_icon_manager, username):
        super().__init__()
        self.tray_icon_manager = tray_icon_manager
        self.username = username
        self.canvas_size = (4000, 4000)
        self.user_id = None
        self.setWindowTitle("Меню")
        self.setFixedSize(1200, 800)
        self.setWindowIcon(QIcon("icon.png"))

        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Файл")
        help_menu = menubar.addMenu("Справка")
        
        new_action = QAction("Новый холст", self)
        new_action.triggered.connect(self.focus_on_new_canvas)
        file_menu.addAction(new_action)
        
        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        help_action = QAction("Помощь", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        welcome_label = QLabel(f"Добро пожаловать, {username}")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(welcome_label)
        
        content_layout = QHBoxLayout()
        
        nav_frame = QFrame()
        nav_frame.setFrameShape(QFrame.Shape.StyledPanel)
        nav_layout = QVBoxLayout(nav_frame)
        
        self.btn_new_canvas = QPushButton("Новый холст")
        self.btn_new_canvas.clicked.connect(self.focus_on_new_canvas)
        
        # Кнопка получения ID
        self.btn_get_id = QPushButton("Получить ID")
        self.btn_get_id.clicked.connect(self.get_user_id)
        
        nav_layout.addWidget(self.btn_new_canvas)
        nav_layout.addWidget(self.btn_get_id)
        
        nav_layout.addStretch()
        
        self.btn_exit = QPushButton("Выход")
        self.btn_exit.clicked.connect(self.close)
        nav_layout.addWidget(self.btn_exit)
        
        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.Shape.StyledPanel)
        content_inner_layout = QVBoxLayout(content_frame)
        
        size_group = QGroupBox("Создать новый холст")
        size_layout = QVBoxLayout()
        
        self.size_combobox = QComboBox()
        self.size_combobox.addItem("Маленький (2000x2000)", (2000, 2000))
        self.size_combobox.addItem("Средний (4000x4000)", (4000, 4000))
        self.size_combobox.addItem("Большой (6000x6000)", (6000, 6000))
        self.size_combobox.addItem("Очень большой (8000x8000)", (8000, 8000))
        self.size_combobox.setCurrentIndex(1)
        
        size_layout.addWidget(QLabel("Выберите размер холста:"))
        size_layout.addWidget(self.size_combobox)
        
        self.bg_color_check = QCheckBox("Белый фон")
        self.bg_color_check.setChecked(True)
        size_layout.addWidget(self.bg_color_check)
        
        self.grid_check = QCheckBox("Показывать сетку")
        size_layout.addWidget(self.grid_check)
        
        self.create_btn = QPushButton("Создать")
        self.create_btn.clicked.connect(self.open_main_window)
        size_layout.addWidget(self.create_btn)
        
        size_group.setLayout(size_layout)
        content_inner_layout.addWidget(size_group)
        
        chat_group = QGroupBox("Чат")
        chat_layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Сначала получите ID...")
        self.chat_input.setEnabled(False)
        self.chat_input.returnPressed.connect(self.send_chat_message)
        
        self.send_button = QPushButton("Отправить")
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send_chat_message)
        
        chat_layout.addWidget(self.chat_display)
        chat_layout.addWidget(self.chat_input)
        chat_layout.addWidget(self.send_button)
        
        chat_group.setLayout(chat_layout)
        content_inner_layout.addWidget(chat_group)
        
        content_layout.addWidget(nav_frame, stretch=1)
        content_layout.addWidget(content_frame, stretch=3)
        main_layout.addLayout(content_layout)
        
        self.chat_messages = []
        
    def get_user_id(self):
        """Метод для получения ID пользователя в формате имяПК_время"""
        try:
            # Генерируем ID в формате имяПК_время
            name = socket.gethostname()
            time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.user_id = f"{name}_{time}"
            
            self.enable_chat()
            self.chat_display.append(f"[SYSTEM] Ваш ID: {self.user_id}")
            self.chat_display.append(f"[SYSTEM] Теперь вы можете писать в чат")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при получении ID: {str(e)}")
    
    def enable_chat(self):
        """Включает возможность писать в чат после получения ID"""
        self.chat_input.setEnabled(True)
        self.chat_input.setPlaceholderText("Введите сообщение...")
        self.send_button.setEnabled(True)
        self.btn_get_id.setEnabled(False)
        
    def send_chat_message(self):
        if not self.user_id:
            QMessageBox.warning(self, "Внимание", "Сначала получите ID!")
            return
            
        message = self.chat_input.text().strip()
        if message:
            timestamp = QTime.currentTime().toString("hh:mm")
            formatted_message = f"{timestamp} [{self.user_id}] {self.username}: {message}"
            self.chat_messages.append(formatted_message)
            self.chat_display.setPlainText("\n".join(self.chat_messages[-20:])) 
            self.chat_input.clear()
            self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def focus_on_new_canvas(self):
        self.size_combobox.setFocus()
        
    def show_help(self):
        QMessageBox.information(self, "Справка", 
            "Это главное меню приложения.\n\n"
            "Для начала работы:\n"
            "1. Получите ваш уникальный ID\n"
            "2. Выберите размер холста\n"
            "3. Нажмите 'Создать'\n\n"
            "Без ID вы не сможете общаться в чате.")
        
    def show_settings(self):
        settings_window = SettingsWindow()
        settings_window.exec()
        
    def open_main_window(self):
        self.canvas_size = self.size_combobox.currentData()
        
        bg_color = Qt.GlobalColor.white if self.bg_color_check.isChecked() else Qt.GlobalColor.transparent
        show_grid = self.grid_check.isChecked()
        
        self.main_window = MainWindow(self.tray_icon_manager, self.canvas_size)
        self.main_window.canvas.set_bg_color(bg_color)
        self.main_window.canvas.set_show_grid(show_grid)
        self.main_window.show()
        self.close()
        
class RegistrationWindow(QMainWindow):
    def __init__(self, tray_icon_manager):
        super().__init__()
        self.tray_icon_manager = tray_icon_manager
        self.setWindowTitle(LanguageConstants.get_constant("REGISTER", APPLICATION_LANGUAGE))
        self.setFixedSize(APPLICATION_SCREEN_SIZE[0], APPLICATION_SCREEN_SIZE[1])
        self.setWindowIcon(QIcon("icon.png"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(LanguageConstants.get_constant("USERNAME_PLACEHOLDER", APPLICATION_LANGUAGE))
        form_layout.addRow(QLabel(LanguageConstants.get_constant("USERNAME_WINDOW", APPLICATION_LANGUAGE)), self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(LanguageConstants.get_constant("PASSWORD_PLACEHOLDER", APPLICATION_LANGUAGE))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(QLabel(LanguageConstants.get_constant("PASSWORD_WINDOW", APPLICATION_LANGUAGE)), self.password_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(LanguageConstants.get_constant("NICKNAME_PLACEHOLDER", APPLICATION_LANGUAGE))
        form_layout.addRow(QLabel(LanguageConstants.get_constant("NICKNAME", APPLICATION_LANGUAGE)), self.description_input)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(False)  
        self.date_input.setDisplayFormat("dd.MM.yyyy")
        self.date_input.setButtonSymbols(QDateEdit.ButtonSymbols.NoButtons)
        
        form_layout.addRow(QLabel(LanguageConstants.get_constant("DATE_OF_BIRTH", APPLICATION_LANGUAGE)), self.date_input)

        register_button = QPushButton(LanguageConstants.get_constant("REGISTER", APPLICATION_LANGUAGE))
        register_button.clicked.connect(self.register_user)
        register_button.setDefault(True)

        back_button = QPushButton(LanguageConstants.get_constant("BACK", APPLICATION_LANGUAGE))
        back_button.clicked.connect(self.back_to_login)

        layout.addLayout(form_layout)
        layout.addWidget(register_button)
        layout.addWidget(back_button)

    def register_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        description = self.description_input.text().strip()
        date_of_birth = self.date_input.date().toString("yyyy-MM-dd")

        if not username:
            QMessageBox.warning(self,LanguageConstants.get_constant("WARNING", APPLICATION_LANGUAGE),LanguageConstants.get_constant("USERNAME_EMPTY", APPLICATION_LANGUAGE))
            self.username_input.setFocus()
            return

        if not password:
            QMessageBox.warning(self,LanguageConstants.get_constant("WARNING", APPLICATION_LANGUAGE),LanguageConstants.get_constant("PASSWORD_EMPTY", APPLICATION_LANGUAGE))
            self.password_input.setFocus()
            return

        if len(password) < 6:
            QMessageBox.warning(self,LanguageConstants.get_constant("WARNING", APPLICATION_LANGUAGE),LanguageConstants.get_constant("PASSWORD_TOO_SHORT", APPLICATION_LANGUAGE))
            self.password_input.setFocus()
            return

        if len(username) < 6:
            QMessageBox.warning(self,LanguageConstants.get_constant("WARNING", APPLICATION_LANGUAGE),LanguageConstants.get_constant("USERNAME_TOO_SHORT", APPLICATION_LANGUAGE))
            self.password_input.setFocus()
            return

        password_hash = common.get_md5_of_string(password)
        conn = None

        try:
            conn = db_main.connect_db("users.db", False)
            user_exists = db_main.request_select_db(conn,"SELECT count(*) FROM users WHERE login=?",(username,))[0][0]

            if user_exists:
                QMessageBox.warning(self,LanguageConstants.get_constant("USER_ERROR", APPLICATION_LANGUAGE),LanguageConstants.get_constant("USER_ALREADY_EXISTS", APPLICATION_LANGUAGE))
                self.username_input.setFocus()
                return

            db_main.request_update_db(conn,"INSERT INTO users (login, password, description, birth_date, type) VALUES (?, ?, ?, ?, ?)",(username, password_hash, description, date_of_birth, 1))

            QMessageBox.information(self,LanguageConstants.get_constant("REGISTRATION_COMPLETED_QMENU", APPLICATION_LANGUAGE),LanguageConstants.get_constant("REGISTRATION_COMPLETED", APPLICATION_LANGUAGE))
            
            self.back_to_login()

        except db_main.DatabaseException as ex:
            QMessageBox.critical(self,LanguageConstants.get_constant("ERROR", APPLICATION_LANGUAGE),f"{LanguageConstants.get_constant('DATABASE_ERROR', APPLICATION_LANGUAGE)}: {ex.msg}")
        finally:
            if conn:
                db_main.disconnect_db(conn)

    def back_to_login(self):
        self.login_window = LoginWindow(self.tray_icon_manager)
        self.login_window.show()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self, tray_icon_manager, canvas_size=(4000, 4000)):
        super().__init__()
        self.tray_icon_manager = tray_icon_manager
        self.setWindowTitle("Main Window")
        self.setFixedSize(PALETTE_SCREEN_SIZE[0], PALETTE_SCREEN_SIZE[1])
        self.setWindowIcon(QIcon("icon.png"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.grid_window = grid_main.GridWindow(self)  
        self.grid_window.setFixedHeight(150)
        main_layout.addWidget(self.grid_window)

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)

        self.canvas = Canvas(canvas_size[0], canvas_size[1])
        self.canvas.set_drawing(False)
        self.scroll.setWidget(self.canvas)
        main_layout.addWidget(self.scroll)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 200)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.update_zoom)

        self.line_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_width_slider.setRange(1, 64)
        self.line_width_slider.setValue(7)
        self.line_width_slider.valueChanged.connect(self.update_line_width)

        self.eraser_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.eraser_width_slider.setRange(1, 64)
        self.eraser_width_slider.setValue(7)
        self.eraser_width_slider.valueChanged.connect(self.update_eraser_width)

        self.text_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.text_size_slider.setRange(6, 192)  
        self.text_size_slider.setValue(21)      
        self.text_size_slider.valueChanged.connect(self.update_text_size)

        self.value_label = QLabel("Масштаб: 100%")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider_container = QWidget()
        self.slider_layout = QVBoxLayout(self.slider_container)
        
        self.current_slider = self.zoom_slider
        self.slider_layout.addWidget(self.current_slider)
        self.slider_layout.addWidget(self.value_label)
        self.slider_container.hide()  
        
        main_layout.addWidget(self.slider_container)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.line_width_status = QLabel("Толщина линии: 7")
        self.status_bar.addPermanentWidget(self.line_width_status)

        self.pan_start = QPoint()
        self.panning = False
        self.last_pan_time = QTime.currentTime()
        self.last_pan_pos = QPoint()
        self.pan_base_speed = 1.5
        self.pan_max_speed = 3.0
        self.pan_smoothing = 0.2

    def set_tool_mode(self, tool):
        if tool == "pencil":
            self.canvas.set_drawing(True)
            self.canvas.set_eraser_mode(False)
            self.canvas.set_text_mode(False)
            self.canvas.set_shape_mode(False)
            self.show_line_width_slider()
        elif tool == "eraser":
            self.canvas.set_drawing(True)
            self.canvas.set_eraser_mode(True)
            self.canvas.set_text_mode(False)
            self.canvas.set_shape_mode(False)
            self.show_eraser_slider()
        elif tool == "text":
            self.canvas.set_drawing(False)
            self.canvas.set_eraser_mode(False)
            self.canvas.set_text_mode(True)
            self.canvas.set_shape_mode(False)
            self.show_text_slider()
        elif tool == "shape":
            self.canvas.set_drawing(False)
            self.canvas.set_eraser_mode(False)
            self.canvas.set_text_mode(False)
            self.canvas.set_shape_mode(True)
            self.show_line_width_slider()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.pan_start = event.pos()
            self.last_pan_pos = event.pos()
            self.last_pan_time = QTime.currentTime()
            self.panning = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning:
            current_time = QTime.currentTime()
            current_pos = event.pos()

            time_diff = self.last_pan_time.msecsTo(current_time)
            time_diff = max(1, time_diff)  
            
            distance = (current_pos - self.last_pan_pos).manhattanLength()
            
            current_speed = distance / time_diff
            
            speed_multiplier = min(self.pan_base_speed + current_speed * 10, self.pan_max_speed)
            
            if hasattr(self, 'last_speed_multiplier'):
                speed_multiplier = (self.pan_smoothing * speed_multiplier + (1 - self.pan_smoothing) * self.last_speed_multiplier)
            self.last_speed_multiplier = speed_multiplier
            
            delta = current_pos - self.pan_start
            self.pan_start = current_pos
            
            x_scroll = self.scroll.horizontalScrollBar()
            y_scroll = self.scroll.verticalScrollBar()
            
            x_scroll.setValue(x_scroll.value() - int(delta.x() * speed_multiplier))
            y_scroll.setValue(y_scroll.value() - int(delta.y() * speed_multiplier))
            
            self.last_pan_pos = current_pos
            self.last_pan_time = current_time
            
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            if hasattr(self, 'last_speed_multiplier'):
                del self.last_speed_multiplier
        super().mouseReleaseEvent(event)

    def toggle_slider(self):
        if self.slider_container.isVisible():
            self.slider_container.hide()
        else:
            self.show_zoom_slider()
            self.slider_container.show()
            
    def show_zoom_slider(self):
        self.switch_slider(self.zoom_slider)
        self.update_zoom(self.zoom_slider.value())
        
    def show_line_width_slider(self):
        self.switch_slider(self.line_width_slider)
        self.update_line_width(self.line_width_slider.value())
        self.slider_container.show()
        
    def show_eraser_slider(self):
        self.switch_slider(self.eraser_width_slider)
        self.update_eraser_width(self.eraser_width_slider.value())
        self.slider_container.show()
        
    def show_text_slider(self):
        self.switch_slider(self.text_size_slider)
        self.update_text_size(self.text_size_slider.value())
        self.slider_container.show()
        
    def switch_slider(self, new_slider):
        self.slider_layout.removeWidget(self.current_slider)
        self.current_slider.hide()

        self.slider_layout.insertWidget(0, new_slider)
        new_slider.show()

        self.current_slider = new_slider
        if new_slider == self.zoom_slider:
            self.update_zoom(new_slider.value())
        elif new_slider == self.line_width_slider:
            self.update_line_width(new_slider.value())
        elif new_slider == self.eraser_width_slider:
            self.update_eraser_width(new_slider.value())
        elif new_slider == self.text_size_slider:
            self.update_text_size(new_slider.value())
    
    def update_zoom(self, value):
        zoom_level = value / 100.0
        self.value_label.setText(f"Масштаб: {value}%")
        self.canvas.set_scale(zoom_level)
    
    def update_line_width(self, value):
        self.value_label.setText(f"Толщина линии: {value}")
        self.line_width_status.setText(f"Толщина линии: {value}")
        self.canvas.set_line_width(value)
        
    def update_eraser_width(self, value):
        self.value_label.setText(f"Размер ластика: {value}")
        self.line_width_status.setText(f"Размер ластика: {value}")
        self.canvas.set_line_width(value)
        
    def update_text_size(self, value):
        self.value_label.setText(f"Размер текста: {value}")
        self.canvas.set_text_size(value)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self.canvas.text_edit and self.canvas.text_edit.isVisible():
                self.canvas.finish_text_input()
        super().keyPressEvent(event)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    SettingsManager.read_settings()
    APPLICATION_LANGUAGE = SettingsManager.default_setting("REGION_PARMS", "lang")
    APPLICATION_SCREEN_SIZE = tuple(map(int, SettingsManager.default_setting("SCREEN_PREFERENCES", "resolution").split('x')))
    PALETTE_SCREEN_SIZE = tuple(map(int, SettingsManager.default_setting("SCREEN_PREFERENCES_MAIN", "resolution").split('x')))
    app.setStyleSheet(load_stylesheet("style.qss"))

    tray_icon_manager = TrayIconManager(None)
    window = LoginWindow(tray_icon_manager)
    tray_icon_manager.set_login_window(window)  
    window.show()
    sys.exit(app.exec())
