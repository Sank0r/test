import sys
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPoint
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QWidget, QMessageBox, QLabel, QTextEdit, QDateEdit, QScrollArea, QDialog, QFrame, QComboBox, QCheckBox, QSlider, QHBoxLayout, QStatusBar
)
from PyQt6.QtGui import QIcon, QPixmap, QAction, QPainter, QColor, QFont

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

        self.canvas = Canvas(4000,4000)
        
        self.canvas.set_drawing(True)
        self.scroll.setWidget(self.canvas) 

        main_layout.addWidget(self.scroll)
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(0, 500)  
        self.zoom_slider.setValue(100) 
        self.zoom_slider.valueChanged.connect(self.update_zoom)

        self.zoom_status = QLabel("100%")
        self.zoom_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        #self.zoom_slider.setVisible(False)
        #self.zoom_status.setVisible(False)

        self.zoom_layout = QHBoxLayout()
        #zoom_layout.addWidget(self.zoom_slider)
        #zoom_layout.addWidget(self.zoom_status)
        main_layout.addLayout(self.zoom_layout)
        self.zoom_layout_status = False

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.line_width_label = QLabel("Толщина линии: 7")
        self.status_bar.addPermanentWidget(self.line_width_label)

        self.prev_pos = None
        self.horizontal_pos = 0
        self.vertical_pos = 0
        self.speed_factor = 3.5
        self.reverse = -1
        self.background_width = 3000
        self.background_height = 2000
        self.horizontal = lambda x: x if 0 <= x <= self.background_width else (0 if x < 0 else self.background_width)
        self.vertical = lambda y: y if 0 <= y <= self.background_height else (0 if y < 0 else self.background_height)

        self.scroll.mouseMoveEvent = self.mouseMoveEvent
        self.scroll.mousePressEvent = self.mousePressEvent
        self.scroll.mouseReleaseEvent = self.mouseReleaseEvent

    def toggle_zoom_slider(self):
        #self.zoom_slider.setVisible(not self.zoom_slider.isVisible())
        #self.zoom_status.setVisible(not self.zoom_status.isVisible())
        if not self.zoom_layout_status:
            self.zoom_layout.addWidget(self.zoom_slider)
            self.zoom_layout.addWidget(self.zoom_status)
        else:
            self.zoom_layout.removeWidget(self.zoom_slider)
            self.zoom_layout.removeWidget(self.zoom_status)
        self.zoom_layout_status =not self.zoom_layout_status
        

    def update_zoom(self):
        zoom_level = self.zoom_slider.value() / 100.0  
        self.zoom_status.setText(f"{int(zoom_level * 100)}%")
        self.canvas.set_scale(zoom_level)

    def update_line_width_status(self, width):
        self.line_width_label.setText(f"Толщина линии: {width}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.prev_pos = event.position()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.RightButton and self.prev_pos is not None:
            delta = self.speed_factor * (event.position() - self.prev_pos)
            new_pos = delta.toPoint()

            self.horizontal_pos += new_pos.x() * self.reverse
            self.horizontal_pos = self.horizontal(self.horizontal_pos)

            self.vertical_pos += new_pos.y() * self.reverse
            self.vertical_pos = self.vertical(self.vertical_pos)

            self.scroll.horizontalScrollBar().setValue(self.horizontal_pos)
            self.scroll.verticalScrollBar().setValue(self.vertical_pos)

            self.prev_pos = event.position()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.prev_pos = None
            
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
