from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QPainter, QColor, QTransform
from PyQt6.QtCore import Qt

class Canvas(QLabel):
    def __init__(self, width=2000, height=2000):
        super().__init__()
        self.drawing = False
        self.last_coords = None
        self.leftButton = False
        self.setStyleSheet("border: 1px solid red")
        self.setScaledContents(False)

        self.drawing_pixmap = QPixmap(width,height)
        self.drawing_pixmap.fill(QColor('white')) 
        
        self.scale_factor = 1.0
        self.pencil_color = QColor('black')  
        self.line_width = 7
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_canvas()

    def set_drawing(self, drawing):
        self.drawing = drawing

    def set_pencil_color(self, color):
        self.pencil_color = color

    def set_line_width(self, width):
        self.line_width = width

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
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
            pen.setWidth(self.line_width)
            pen.setColor(self.pencil_color) 
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
        combined_pixmap = self.drawing_pixmap.copy()
        
        scaled_pixmap = combined_pixmap.transformed(QTransform().scale(self.scale_factor, self.scale_factor), Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pixmap)

    def set_scale(self, scale_factor):
        self.scale_factor = scale_factor
        self.update_canvas()
        
