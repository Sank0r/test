from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction, QIcon

class TrayIconManager:
    def __init__(self, login_window):
        self.login_window = login_window
        self.tray_icon = None
        self.setup_tray_icon()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon("icon.png"))

        menu = QMenu()
        show_action = QAction("Показать", self.tray_icon)
        show_action.triggered.connect(self.show_window)
        exit_action = QAction("Выход", self.tray_icon)
        exit_action.triggered.connect(self.exit_application)

        menu.addAction(show_action)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def show_window(self):
        if self.login_window:
            self.login_window.showNormal()
            self.login_window.activateWindow()

    def exit_application(self):
        print("Завершение приложения...")
        
        if self.login_window:
            self.login_window.close()
            
        if self.tray_icon:
            self.tray_icon.hide()

        QApplication.instance().quit()

    def set_login_window(self, login_window):
        self.login_window = login_window
