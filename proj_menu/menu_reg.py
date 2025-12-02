import os
import sys
import socket
from datetime import datetime
import chat
import importlib.util
import lib.server as server
import lib.client as client
import json
import subprocess
import threading
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
        self.port = 3333
        self.nickname = ""
        self.peer = ""
        self.peerIP = "0"
        self.peerPort = "0"
        self.historyLog = []
        self.messageLog = []
        self.historyPos = 0
        self.chatServer = None
        self.chatClient = None

        # Настройка статусбара и меню
        self.statusBar()
        
        # Действие для настроек
        self.setAct = QAction(QIcon('gear.png'), '&Settings', self)
        self.setAct.setShortcut('Ctrl+Q')
        self.setAct.setStatusTip('Set Up Application')
        self.setAct.triggered.connect(self.show_settings)

        # Создание меню
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('&Manager')
        self.fileMenu.addAction(self.setAct)
        
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

        try:
            jsonSettings = open('settings.json')
            self.settings = json.loads(jsonSettings.read())
            jsonSettings.close()
            jsonFile = open('lang/{0}.json'.format(self.settings['language']))
        except Exception:
            jsonFile = open('lang/en.json')
        self.lang = json.loads(jsonFile.read())
        jsonFile.close()
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            self.hostname = s.getsockname()[0]
            s.close()
        except socket.error as error:
            self.tray_icon_manager.sysMsg(self.lang['noInternetAccess'], "Сетевая ошибка", False, False)
            self.tray_icon_manager.sysMsg(self.lang['failedFetchPublicIP'], "Сетевая ошибка", False, False)
            self.hostname = "0.0.0.0"

    def sysMsg(self, msg, title="Системное сообщение", show_tray=True, show_os_notification=True):
        self.tray_icon_manager.sysMsg(msg, title, show_tray, show_os_notification)

    def closeEvent(self, event):
        if self.chatServer:
            try:
                self.chatServer.stop()
            except:
                pass
        if self.chatClient:
            try:
                self.chatClient.stop()
            except:
                pass
        event.accept() 

    def show_settings(self):
        settings_window = SettingsWindow()
        settings_window.exec()

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
                self.tray_icon_manager.sysMsg(f"Успешный вход пользователя: {username}", "Авторизация", True, False)
                self.open_welcome_window(username)
            else:
                self.tray_icon_manager.sysMsg("Неверное имя пользователя или пароль", "Ошибка авторизации", True, False)

        except db_main.DatabaseException as ex:
            self.tray_icon_manager.sysMsg(f"Ошибка базы данных: {ex.msg}", "Критическая ошибка", True, False)
        finally:
            if 'conn' in locals():
                db_main.disconnect_db(conn)

    def open_welcome_window(self, username):
        self.welcome_window = WelcomeWindow(self.tray_icon_manager, username, self)
        self.welcome_window.show()
        self.hide()

    def open_registration_window(self):
        self.registration_window = RegistrationWindow(self.tray_icon_manager)
        self.registration_window.show()
        self.hide()

class WelcomeWindow(QMainWindow):
    def __init__(self, tray_icon_manager, username, login_window):
        super().__init__()
        self.tray_icon_manager = tray_icon_manager
        self.username = username
        self.canvas_size = (4000, 4000)
        self.user_id = None
        self.login_window = login_window
        
        self.port = login_window.port
        self.nickname = login_window.nickname
        self.peer = login_window.peer
        self.peerIP = login_window.peerIP
        self.peerPort = login_window.peerPort
        self.historyLog = login_window.historyLog
        self.messageLog = login_window.messageLog
        self.historyPos = login_window.historyPos
        self.chatServer = login_window.chatServer
        self.chatClient = login_window.chatClient
        self.hostname = login_window.hostname
        self.lang = login_window.lang
        
        self.user_role = None
        
        self.setWindowTitle("Главное меню")
        self.setFixedSize(1200, 800)
        self.setWindowIcon(QIcon("icon.png"))

        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Файл")
        network_menu = menubar.addMenu("Сеть")
        help_menu = menubar.addMenu("Справка")
        
        new_action = QAction("Новый холст", self)
        new_action.triggered.connect(self.focus_on_new_canvas)
        file_menu.addAction(new_action)
        
        settings_action = QAction("Настройки", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)
        
        network_action = QAction("Запустить чат", self)
        network_action.triggered.connect(self.show_network_chat)
        network_menu.addAction(network_action)
        
        help_action = QAction("Помощь", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        welcome_label = QLabel(f"Добро пожаловать, {username}!")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(welcome_label)
        
        content_layout = QHBoxLayout()
        
        nav_frame = QFrame()
        nav_frame.setFrameShape(QFrame.Shape.StyledPanel)
        nav_layout = QVBoxLayout(nav_frame)
        
        self.btn_new_canvas = QPushButton("Новый холст")
        self.btn_new_canvas.clicked.connect(self.focus_on_new_canvas)
        
        self.btn_get_id = QPushButton("Получить ID")
        self.btn_get_id.clicked.connect(self.get_user_id)
        
        self.btn_network = QPushButton("Сетевое подключение")
        self.btn_network.clicked.connect(self.create_connection)
        
        self.btn_be_creator = QPushButton("Создать комнату")
        self.btn_be_creator.clicked.connect(lambda: self.set_role("creator"))
        
        self.btn_be_user = QPushButton("Подключиться к комнате") 
        self.btn_be_user.clicked.connect(lambda: self.set_role("user"))
        
        nav_layout.addWidget(self.btn_new_canvas)
        nav_layout.addWidget(self.btn_get_id)
        nav_layout.addWidget(self.btn_network)
        nav_layout.addWidget(self.btn_be_creator)
        nav_layout.addWidget(self.btn_be_user)
        
        self.creator_port_input = QLineEdit()
        self.creator_port_input.setPlaceholderText("Порт комнаты (по умолчанию 3333)")
        self.creator_port_input.setText("3333") 
        self.creator_port_input.hide()
        
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.clicked.connect(self.connect_to_creator)
        self.connect_btn.hide()
        
        nav_layout.addWidget(self.creator_port_input)
        nav_layout.addWidget(self.connect_btn)
        
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

    def set_role(self, role):
        self.user_role = role
        
        if role == "creator":
            self.creator_port_input.hide()
            self.connect_btn.hide()
            self.chat_display.append("Вы создали комнату на порту 3333")
            self.create_connection()
            self.enable_chat()
            
        elif role == "user":
            self.creator_port_input.show() 
            self.connect_btn.show()
            self.chat_display.append("Введите порт создателя и нажмите 'Подключиться'")

    def connect_to_creator(self):
        """Подключение к создателю по порту"""
        try:
            port_text = self.creator_port_input.text().strip()
            if not port_text:
                port = 3333  
            else:
                port = int(port_text)
            
            if port < 1 or port > 65535:
                self.chat_display.append("Ошибка: порт должен быть в диапазоне 1-65535")
                return
                
            if self.chatClient:
                self.chatClient.conn(['127.0.0.1', port])
                self.chat_display.append(f"Подключаюсь к порту {port}...")
                self.enable_chat()
        except ValueError:
            self.chat_display.append("Ошибка: введите корректный номер порта")
        except Exception as e:
            self.chat_display.append(f"Ошибка подключения: {str(e)}")

    def send_chat_message(self):
        if not self.user_id:
            self.tray_icon_manager.sysMsg("Сначала получите ID для использования чата", "Внимание", True, False)
            return
            
        message = self.chat_input.text().strip()
        if message:
            timestamp = QTime.currentTime().toString("hh:mm")
            
            role_prefix = " СОЗДАТЕЛЬ" if self.user_role == "creator" else "👤 ПОЛЬЗОВАТЕЛЬ"
            formatted_message = f"{timestamp} {role_prefix}: {message}"
            
            self.chat_messages.append(formatted_message)
            self.chat_display.setPlainText("\n".join(self.chat_messages[-20:])) 
            self.chat_input.clear()
            self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())
            
            if self.chatClient and self.chatClient.isConnected:
                self.chatClient.send(message)
            
            self.tray_icon_manager.sysMsg(f"Сообщение отправлено: {message[:50]}...", "Чат", False, False)

    def sysMsg(self, msg, title="Системное сообщение", show_tray=True, show_os_notification=True):
        self.tray_icon_manager.sysMsg(msg, title, show_tray, show_os_notification)

    def is_port_available(self, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                result = s.connect_ex(('127.0.0.1', port))
                return result != 0  
        except:
            return False

    def get_available_port(self):
        for port in range(3333, 3344):
            if self.is_port_available(port):
                return port
        return None
        
    def create_connection(self):
        try:
            if self.chatServer:
                try:
                    self.chatServer.stop()
                    self.chatServer = None
                except:
                    pass
                    
            if self.chatClient:
                try:
                    self.chatClient.stop()
                    self.chatClient = None
                except:
                    pass
            
            creator_port = 3333
            
            if not self.is_port_available(creator_port):
                self.tray_icon_manager.sysMsg(f"Порт {creator_port} занят, невозможно создать комнату", "Ошибка сети", True, False)
                return
                
            self.port = creator_port
            self.login_window.port = creator_port
            
            self.chatServer = server.Server(self)
            self.chatServer.daemon = True
            self.chatServer.start()
            
            import time
            time.sleep(0.1)
            
            self.chatClient = client.Client(self)
            self.chatClient.start()
            
            self.chatClient.conn(['127.0.0.1', creator_port])
            
            self.tray_icon_manager.sysMsg(f"Комната создана на порту {creator_port}", "Сетевое подключение", True, False)
            
        except Exception as e:
            self.tray_icon_manager.sysMsg(f"Ошибка при создании подключения: {str(e)}", "Ошибка сети", True, False)
    
    def get_user_id(self):
        try:
            name = socket.gethostname()
            time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.user_id = f"{name}_{time}"
            
            self.enable_chat()
            self.chat_display.append(f"[SYSTEM] Ваш ID: {self.user_id}")
            self.chat_display.append(f"[SYSTEM] Теперь вы можете писать в чат")

            self.tray_icon_manager.sysMsg(f"Ваш ID: {self.user_id}", "Идентификатор пользователя", True, False)
            
        except Exception as e:
            error_msg = f"Ошибка при получении ID: {str(e)}"
            self.tray_icon_manager.sysMsg(error_msg, "Ошибка", True, False)
    
    def enable_chat(self):
        self.chat_input.setEnabled(True)
        self.chat_input.setPlaceholderText("Введите сообщение...")
        self.send_button.setEnabled(True)
        self.btn_get_id.setEnabled(False)
        
    def show_network_chat(self):
        try:
            thread = threading.Thread(target=self.run_chat_app)
            thread.daemon = True
            thread.start()
            
            self.tray_icon_manager.sysMsg("Чат-приложение запущено", "Сетевое подключение", True, False)
            
        except Exception as e:
            error_msg = f"Ошибка запуска чата: {str(e)}"
            self.tray_icon_manager.sysMsg(error_msg, "Ошибка", True, False)

    def run_chat_app(self):
        chat_app = chat.ChatApp()
        chat_app.run()

    def focus_on_new_canvas(self):
        self.size_combobox.setFocus()
        
    def show_help(self):
        help_text = (
            "Это главное меню приложения.\n\n"
            "Для начала работы:\n"
            "1. Получите ваш уникальный ID\n"
            "2. Выберите размер холста\n"
            "3. Нажмите 'Создать'\n\n"
            "Без ID вы не сможете общаться в чате.\n"
            "Для сетевого общения используйте кнопку 'Сетевое подключение'.")
        QMessageBox.information(self, "Справка", help_text)
        
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
        
        self.tray_icon_manager.sysMsg(f"Создан новый холст размером {self.canvas_size[0]}x{self.canvas_size[1]}", "Холст", True, False)
        
        self.close()
        
    def closeEvent(self, event):
        self.login_window.chatServer = self.chatServer
        self.login_window.chatClient = self.chatClient

        if self.chatServer:
            try:
                self.chatServer.stop()
                self.chatServer = None
            except:
                pass
        if self.chatClient:
            try:
                self.chatClient.stop()
                self.chatClient = None
            except:
                pass
            
        self.tray_icon_manager.sysMsg("Главное меню закрыто", "Система", False, False)
        event.accept()
            
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
            self.tray_icon_manager.sysMsg(LanguageConstants.get_constant("USERNAME_EMPTY", APPLICATION_LANGUAGE), "Предупреждение", True, False)
            self.username_input.setFocus()
            return

        if not password:
            self.tray_icon_manager.sysMsg(LanguageConstants.get_constant("PASSWORD_EMPTY", APPLICATION_LANGUAGE), "Предупреждение", True, False)
            self.password_input.setFocus()
            return

        if len(password) < 6:
            self.tray_icon_manager.sysMsg(LanguageConstants.get_constant("PASSWORD_TOO_SHORT", APPLICATION_LANGUAGE), "Предупреждение", True, False)
            self.password_input.setFocus()
            return

        if len(username) < 6:
            self.tray_icon_manager.sysMsg(LanguageConstants.get_constant("USERNAME_TOO_SHORT", APPLICATION_LANGUAGE), "Предупреждение", True, False)
            self.password_input.setFocus()
            return

        password_hash = common.get_md5_of_string(password)
        conn = None

        try:
            conn = db_main.connect_db("users.db", False)
            user_exists = db_main.request_select_db(conn,"SELECT count(*) FROM users WHERE login=?",(username,))[0][0]

            if user_exists:
                self.tray_icon_manager.sysMsg(LanguageConstants.get_constant("USER_ALREADY_EXISTS", APPLICATION_LANGUAGE), "Ошибка пользователя", True, False)
                self.username_input.setFocus()
                return

            db_main.request_update_db(conn,"INSERT INTO users (login, password, description, birth_date, type) VALUES (?, ?, ?, ?, ?)",(username, password_hash, description, date_of_birth, 1))

            self.tray_icon_manager.sysMsg(LanguageConstants.get_constant("REGISTRATION_COMPLETED", APPLICATION_LANGUAGE), "Регистрация завершена", True, False)
            
            self.back_to_login()

        except db_main.DatabaseException as ex:
            self.tray_icon_manager.sysMsg(f"{LanguageConstants.get_constant('DATABASE_ERROR', APPLICATION_LANGUAGE)}: {ex.msg}", "Ошибка", True, False)
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
