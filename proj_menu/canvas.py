from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QPainter, QColor, QTransform
from PyQt6.QtCore import Qt

class Canvas(QLabel):
    def __init__(self, width=2000, height=2000):
        super().__init__()
        self.drawing = False
        self.last_coords = None
        self.leftButton = False
        self.setStyleSheet("background-color: #E0FFFF")
        self.setScaledContents(False)

        self.original_pixmap = QPixmap(width, height)
        self.original_pixmap.fill(QColor('#E0FFFF')) 

        self.drawing_pixmap = QPixmap(width, height)
        self.drawing_pixmap.fill(QColor('transparent')) 

        self.scale_factor = 1.0

        self.update_canvas()

    def set_drawing(self, drawing):
        self.drawing = drawing

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftButton = True
            self.last_coords = self.transform_position(event.pos())
        elif event.button() == Qt.MouseButton.RightButton:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.drawing and self.leftButton:
            if self.last_coords is None:
                self.last_coords = self.transform_position(event.pos())
                return

            current_pos = self.transform_position(event.pos())

            painter = QPainter(self.drawing_pixmap)
            pen = painter.pen()
            pen.setWidth(7)
            pen.setColor(QColor('brown'))
            painter.setPen(pen)
            painter.drawLine(self.last_coords, current_pos)
            painter.end()

            self.update_canvas()
            self.last_coords = current_pos
        else:
            event.ignore()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftButton = False
            self.last_coords = None

    def transform_position(self, pos):
        return pos / self.scale_factor

    def update_canvas(self):

        combined_pixmap = self.original_pixmap.copy()

        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, self.drawing_pixmap)
        painter.end()

        scaled_pixmap = combined_pixmap.transformed(QTransform().scale(self.scale_factor, self.scale_factor),Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pixmap)

    def set_scale(self, scale_factor):
        self.scale_factor = scale_factor
        self.update_canvas()
        
