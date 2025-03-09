import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QScrollArea
from PyQt6.QtGui import QPixmap, QColor, QPainter, QFont
from PyQt6.QtCore import Qt


class Canvas(QLabel):
    def __init__(self, width=2000, height=1000):
        super().__init__()
        self.drawing = False
        self.last_coords = None
        self.leftButton = False
        self.setStyleSheet("background-color: #E0FFFF")
        self.setScaledContents(False)

        pixmap = QPixmap(width, height)
        pixmap.fill(QColor('transparent'))
        self.setPixmap(pixmap)

    def set_drawing(self, drawing):
        self.drawing = drawing

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.last_coords = event.pos()
            canvas = self.pixmap()
            painter = QPainter(canvas)
            painter.setPen(QColor(250, 55, 55))
            painter.setFont(QFont('Decorative', 18))
            painter.drawText(self.last_coords,
                            f'вы кликнули: {self.last_coords.x()}/{self.last_coords.y()}')
            painter.end()
            self.setPixmap(canvas)
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftButton = True

    def mouseMoveEvent(self, event):
        if self.drawing and self.leftButton:
            if self.last_coords is None:
                self.last_coords = event.pos()
                return
            canvas = self.pixmap()
            painter = QPainter(canvas)
            pen = painter.pen()
            pen.setWidth(7)
            pen.setColor(QColor('black'))
            painter.setPen(pen)
            painter.drawLine(self.last_coords, event.pos())
            painter.end()
            self.setPixmap(canvas)
            self.last_coords = event.pos()

    def mouseReleaseEvent(self, event):
        self.last_coords = None
        self.leftButton = False

    def resizeEvent(self, event):
        super().resizeEvent(event)


class NoteEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        scroll = QScrollArea()
        self.canvas = Canvas(3000, 2000)
        self.canvas.set_drawing(True)
        scroll.setWidget(self.canvas)
        self.setCentralWidget(scroll)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteEditor()
    window.setWindowTitle('Example of drawing')
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
