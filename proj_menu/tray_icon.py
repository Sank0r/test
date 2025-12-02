from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QAction, QIcon

class TrayIconManager:
    def __init__(self, login_window):
        self.login_window = login_window
        self.tray_icon = None
        self.setup_tray_icon()

    def setup_tray_icon(self):
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon("icon.png"))
        
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        menu = QMenu()
        show_action = QAction("Показать", self.tray_icon)
        show_action.triggered.connect(self.show_window)
        exit_action = QAction("Выход", self.tray_icon)
        exit_action.triggered.connect(self.exit_application)

        menu.addAction(show_action)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

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

    def sysMsg(self, msg, title="Системное сообщение", show_tray=True, show_os_notification=True):
        if show_tray and self.tray_icon:
            self.tray_icon.showMessage(title, msg, QSystemTrayIcon.MessageIcon.Information, 3000)

        if show_os_notification:
            self.show_windows_notification(title, msg)

        print(f"[SYSTEM] {msg}")

    def show_windows_notification(self, title, message):
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                title=title,
                msg=message,
                duration=3,
                threaded=True
            )
        except ImportError:
            self.fallback_windows_notification(title, message)

    def fallback_windows_notification(self, title, message):
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, 0)