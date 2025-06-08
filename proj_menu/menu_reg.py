import sys
from PyQt6.QtCore import Qt, QSize, QPoint,QTime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QWidget, QMessageBox, QLabel, QTextEdit, QDateEdit, QScrollArea, QDialog, QFrame, QComboBox, QCheckBox, QSlider, QHBoxLayout, QStatusBar)
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
        with open(style, "r") as file:
            return file.read()
    except FileNotFoundError:
        print(LanguageConstants.get_constant("STYLESHEET_FILE_NOT_FOUND", APPLICATION_LANGUAGE))
        return ""

class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(LanguageConstants.get_constant("SETTINGS", APPLICATION_LANGUAGE))
        self.setFixedSize(APPLICATION_SCREEN_SIZE[0], APPLICATION_SCREEN_SIZE[1])
        self.setWindowIcon(QIcon("gear.png"))

        self.layout = QVBoxLayout(self)
        
        self.inputs = {} 

        current_setting = SettingsManager.get_next_section()
        while True:
            section_data = current_setting()
            if not section_data:
                break
            
            section_values, section_name = section_data
            
            label = QLabel(f"[{section_name}]")
            self.layout.addWidget(label)

            for key, value in section_values.items():
                line_edit = QLineEdit(value)
                line_edit.setPlaceholderText(key)
                self.layout.addWidget(line_edit)
                self.inputs[section_name + "@@" + key] = line_edit  

        save_button = QPushButton(LanguageConstants.get_constant("SAVE", APPLICATION_LANGUAGE))
        save_button.clicked.connect(self.save_settings)
        self.layout.addWidget(save_button)

        self.setLayout(self.layout)

    def save_settings(self):
        for key, line_edit in self.inputs.items():
            (section_name, real_key) = key.split("@@")
            if section_name:
                SettingsManager.set_setting(section_name, real_key, line_edit.text())

        SettingsManager.save_settings()
        QMessageBox.information(self, "Settings", LanguageConstants.get_constant("SETTINGS_SAVED", APPLICATION_LANGUAGE))

class LoginWindow(QMainWindow):
    def __init__(self, tray_icon_manager):
        super().__init__()
        self.tray_icon_manager = tray_icon_manager

        self.statusBar()
        self.setAct = QAction(QIcon('gear.png'), '&Settings', self)
        self.setAct.setShortcut('Ctrl+Q')
        self.setAct.setStatusTip('Set Up Application')
        self.setAct.triggered.connect(self.show_settings)
        
        self.testAct = QAction(QIcon('television-test.png'), '&Test', self)
        self.testAct.setShortcut('Ctrl+T')
        self.testAct.setStatusTip('Test External Function')
        self.testAct.triggered.connect(self.test_function)
        
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('&{0}'.format('Manager'))
        self.fileMenu.addAction(self.setAct)
        self.fileMenu.addAction(self.testAct)

        self.setWindowTitle(LanguageConstants.get_constant("LOGIN", APPLICATION_LANGUAGE))
        self.setFixedSize(APPLICATION_SCREEN_SIZE[0], APPLICATION_SCREEN_SIZE[1])
        self.setWindowIcon(QIcon("icon.png"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        form_layout = QFormLayout()
        
        self.grid_window = grid_main.GridWindow()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(LanguageConstants.get_constant("USERNAME_PLACEHOLDER", APPLICATION_LANGUAGE))

        form_layout.addRow(LanguageConstants.get_constant("USERNAME_WINDOW", APPLICATION_LANGUAGE), self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(LanguageConstants.get_constant("PASSWORD_PLACEHOLDER", APPLICATION_LANGUAGE))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addRow(LanguageConstants.get_constant("PASSWORD_WINDOW", APPLICATION_LANGUAGE), self.password_input)

        self.login_button = QPushButton(LanguageConstants.get_constant("LOGIN", APPLICATION_LANGUAGE))
        self.login_button.clicked.connect(self.handle_login)

        self.register_button = QPushButton(LanguageConstants.get_constant("REGISTER", APPLICATION_LANGUAGE))
        self.register_button.clicked.connect(self.open_registration_window)

        layout.addLayout(form_layout)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

    def closeEvent(self, event):
        event.accept() 

    def show_settings(self):
        settings_window = SettingsWindow()
        settings_window.exec()

    def test_function(self):
        self.grid_window.show()

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        password = common.get_md5_of_string(password)

        try:
            conn = db_main.connect_db("users.db", False)
            data = db_main.request_select_db(conn, "SELECT count(*) FROM users WHERE login=? AND password=?", (username, password))
        except db_main.DatabaseException as ex:
            QMessageBox.critical(self, "Critical", ex.msg)
            return
            
        count_user = data[0][0]
        user_exist = bool(count_user)

        if user_exist:
            self.open_main_window()
        else:
            QMessageBox.warning(self, "Warning", "Неверный ввод данных")

        db_main.disconnect_db(conn)

    def open_registration_window(self):
        self.registration_window = RegistrationWindow(self.tray_icon_manager)
        self.registration_window.show()
        self.hide()

    def open_main_window(self):
        self.main_window = MainWindow(self.tray_icon_manager)
        self.main_window.show()
        self.hide()
        
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
        form_layout.addRow((LanguageConstants.get_constant("USERNAME_WINDOW", APPLICATION_LANGUAGE)), self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(LanguageConstants.get_constant("PASSWORD_PLACEHOLDER", APPLICATION_LANGUAGE))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow((LanguageConstants.get_constant("PASSWORD_WINDOW", APPLICATION_LANGUAGE)), self.password_input)

        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText(LanguageConstants.get_constant("NICKNAME_PLACEHOLDER", APPLICATION_LANGUAGE))
        form_layout.addRow((LanguageConstants.get_constant("NICKNAME", APPLICATION_LANGUAGE)), self.description_input)

        self.date_input = QDateEdit()
        form_layout.addRow((LanguageConstants.get_constant("DATE_OF_BIRTH", APPLICATION_LANGUAGE)), self.date_input)
        register_button = QPushButton(LanguageConstants.get_constant("REGISTER", APPLICATION_LANGUAGE))
        register_button.clicked.connect(self.register_user)

        back_button = QPushButton(LanguageConstants.get_constant("BACK", APPLICATION_LANGUAGE))
        back_button.clicked.connect(self.back_to_login)

        layout.addLayout(form_layout)
        layout.addWidget(register_button)
        layout.addWidget(back_button)

    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        password = common.get_md5_of_string(password)
        description = self.description_input.text()
        date_of_birth = self.date_input.date().toString("yyyy-MM-dd")

        try:
            conn = db_main.connect_db("users.db", False)
            data = db_main.request_select_db(conn, "SELECT count(*) FROM users WHERE login=? AND password=?", (username, password))
        except db_main.DatabaseException as ex:
            QMessageBox.critical(self, "Critical", ex.msg)
        try:
            conn = db_main.connect_db("users.db", False)
            db_main.request_update_db(conn, "INSERT INTO users (login, password, type) VALUES (?, ?, ?)", (username, password, 1))
            QMessageBox.information(self, (LanguageConstants.get_constant("REGISTRATION_COMPLETED_QMENU", APPLICATION_LANGUAGE)), (LanguageConstants.get_constant("REGISTRATION_COMPLETED", APPLICATION_LANGUAGE)))
            self.back_to_login()
        except db_main.DatabaseException as ex:
            QMessageBox.warning(self, (LanguageConstants.get_constant("USER_ERROR", APPLICATION_LANGUAGE)), (LanguageConstants.get_constant("USER_ALREADY_EXISTS", APPLICATION_LANGUAGE)))

        db_main.disconnect_db(conn)

    def back_to_login(self):
        self.login_window = LoginWindow(self.tray_icon_manager)
        self.login_window.show()
        self.close()

class MainWindow(QMainWindow):
    def __init__(self, tray_icon_manager):
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

        self.canvas = Canvas(4000, 4000)
        self.canvas.set_drawing(False)
        self.scroll.setWidget(self.canvas)
        main_layout.addWidget(self.scroll)

        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(10, 500)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.update_zoom)

        self.line_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.line_width_slider.setRange(1, 64)
        self.line_width_slider.setValue(7)
        self.line_width_slider.valueChanged.connect(self.update_line_width)

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
        self.pan_base_speed = 1.5  # Базовая скорость
        self.pan_max_speed = 4.0   # Максимальная скорость
        self.pan_smoothing = 0.2   

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
            
            speed_multiplier = min(self.pan_base_speed + current_speed * 10,self.pan_max_speed)
            
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
        
    def switch_slider(self, new_slider):
        self.slider_layout.removeWidget(self.current_slider)
        self.current_slider.hide()

        self.slider_layout.insertWidget(0, new_slider)
        new_slider.show()

        self.current_slider = new_slider
        if new_slider == self.zoom_slider:
            self.update_zoom(new_slider.value())
        else:
            self.update_line_width(new_slider.value())
    
    def update_zoom(self, value):
        zoom_level = value / 100.0
        self.value_label.setText(f"Масштаб: {value}%")
        self.canvas.set_scale(zoom_level)
    
    def update_line_width(self, value):
        self.value_label.setText(f"Толщина линии: {value}")
        self.line_width_status.setText(f"Толщина линии: {value}")
        self.canvas.set_line_width(value)

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
