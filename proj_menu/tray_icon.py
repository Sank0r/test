from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QMainWindow
from PyQt6.QtGui import QAction, QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import QObject, pyqtSignal
import sys
import os
from path_helper import get_resource_path

class TrayIconManager(QObject):
    show_window_signal = pyqtSignal()
    exit_app_signal = pyqtSignal()
    
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window
        self.tray_icon = None
        self.setup_tray_icon()
        self.show_window_signal.connect(self.show_window)
        self.exit_app_signal.connect(self.exit_application)

    def setup_tray_icon(self):
        try:
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.tray_icon = QSystemTrayIcon()
                icon_path = get_resource_path("icon.png")
                if os.path.exists(icon_path):
                    self.tray_icon.setIcon(QIcon(icon_path))
                else:
                    pixmap = QPixmap(32, 32)
                    pixmap.fill(Qt.GlobalColor.transparent)
                    painter = QPainter(pixmap)
                    painter.setBrush(QColor(74, 134, 232))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(4, 4, 24, 24)
                    painter.end()
                    self.tray_icon.setIcon(QIcon(pixmap))
                menu = QMenu()
                
                show_action = QAction("Показать", self.tray_icon)
                show_action.triggered.connect(lambda: self.show_window_signal.emit())
                menu.addAction(show_action)
                
                menu.addSeparator()
                
                exit_action = QAction("Выход", self.tray_icon)
                exit_action.triggered.connect(lambda: self.exit_app_signal.emit())
                menu.addAction(exit_action)
                
                self.tray_icon.setContextMenu(menu)
                
                # Подключаем клик по иконке
                self.tray_icon.activated.connect(self.on_tray_icon_activated)
                
                # Показываем иконку
                self.tray_icon.show()
                
                print("DEBUG: Трей-иконка создана успешно")
                
            else:
                print("WARNING: Системный трей не доступен")
                self.tray_icon = None
                
        except Exception as e:
            print(f"ERROR: Ошибка создания трей-иконки: {e}")
            self.tray_icon = None

    def on_tray_icon_activated(self, reason):
        if reason in [QSystemTrayIcon.ActivationReason.DoubleClick, 
                      QSystemTrayIcon.ActivationReason.Trigger]:
            self.show_window_signal.emit()

    def show_window(self):
        if self.login_window:
            try:
                if self.login_window.isMinimized():
                    self.login_window.showNormal()
                else:
                    self.login_window.show()
                
                self.login_window.raise_()
                self.login_window.activateWindow()
                
            except Exception as e:

    def exit_application(self):
        
        if self.tray_icon:
            try:
                self.tray_icon.hide()
                self.tray_icon = None
            except:
                pass
        
        if self.login_window:
            try:
                self.login_window.close()
            except:
                pass
        
        app = QApplication.instance()
        if app:
            app.quit()

    def set_login_window(self, login_window):
        self.login_window = login_window

    def sysMsg(self, msg, title="Системное сообщение", show_tray=True, show_os_notification=True):
        print(f"[SYSTEM] {title}: {msg}")
        
        if show_tray and self.tray_icon:
            try:
                self.tray_icon.showMessage(title, msg, QSystemTrayIcon.MessageIcon.Information, 3000)
            except Exception as e:
                print(f"ERROR: Не удалось показать уведомление в трее: {e}")