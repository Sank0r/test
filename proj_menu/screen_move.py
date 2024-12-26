import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QPoint

class Screen_movement(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("window")
        self.setGeometry(50,50, 300, 300) 
        #self.setFixedSize(800, 800)
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap("k.jpg")) 
        self.image_label.setScaledContents(True)  
        self.setCentralWidget(self.image_label)

        self.prev_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.prev_pos = event.position()  

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.RightButton and self.prev_pos is not None:
            delta = event.position() - self.prev_pos  #смещение
            new_pos = self.image_label.pos() + delta.toPoint()  # Новая позиция QLabel
            self.image_label.move(new_pos)  # Перемещение QLabel
            self.prev_pos = event.position()  # Обновление предыдущей позиции

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.prev_pos = None  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Screen_movement()
    window.show()
    sys.exit(app.exec())
