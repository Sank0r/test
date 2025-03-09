import pystray
from pystray import MenuItem as item
from PIL import Image
from PyQt6.QtWidgets import QApplication

class TrayIconManager:
    def __init__(self, login_window):
        self.login_window = login_window
        self.tray_icon = None
        self.setup_tray_icon()

    def setup_tray_icon(self):
        try:
            icon_image = Image.open("icon.png")
            menu = (
                item('Показать', self.show_window),
                item('Выход', self.exit_application)
            )
            self.tray_icon = pystray.Icon("k", icon_image, menu=menu)
            self.tray_icon.run_detached()
        except FileNotFoundError:
            print("Файл иконки не найден!")
        except Exception as e:
            print(f"Ошибка при создании иконки в трее: {e}")

    def show_window(self, icon=None, item=None):
        if self.login_window:
            self.login_window.showNormal()
            self.login_window.activateWindow()

    def exit_application(self, icon=None, item=None):
        self.tray_icon.stop()
        QApplication.quit()

    def show_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.visible = True

    def set_login_window(self, login_window):
        self.login_window = login_window
