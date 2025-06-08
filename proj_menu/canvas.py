from PyQt6.QtWidgets import QLabel, QLineEdit
from PyQt6.QtGui import QPixmap, QPainter, QColor, QTransform, QFont
from PyQt6.QtCore import Qt, QPoint, QEvent

class Canvas(QLabel):
    def __init__(self, width=2000, height=2000):
        super().__init__()
        self.drawing = False
        self.last_coords = None
        self.leftButton = False
        self.eraser_mode = False
        self.text_mode = False
        self.setScaledContents(False)
        
        self.drawing_pixmap = QPixmap(width, height)
        self.drawing_pixmap.fill(QColor('white'))
        
        self.scale_factor = 1.0
        self.pencil_color = QColor('black')
        self.line_width = 7
        
        self.text_items = []
        self.current_text_item = None

        self.text_edit = QLineEdit(self)
        self.text_edit.setStyleSheet(f"color: {self.pencil_color.name()}; background: rgba(255,255,255,150); border: 1px dashed gray;")
        font = self.text_edit.font()
        font.setPixelSize(self.line_width * 3)
        self.text_edit.setFont(font)
        self.text_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.text_edit.returnPressed.connect(self.finish_text_input)
        self.text_edit.hide()
        
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_canvas()

    def set_drawing(self, drawing):
        if drawing:
            self.finish_text_input()
        self.drawing = drawing

    def set_eraser_mode(self, enabled):
        if enabled:
            self.finish_text_input()
        self.eraser_mode = enabled

    def set_text_mode(self, enabled):
        if not enabled:
            self.finish_text_input()
        self.text_mode = enabled

    def set_pencil_color(self, color):
        self.pencil_color = color
        if hasattr(self, 'text_edit') and self.text_edit:
            self.text_edit.setStyleSheet(f"color: {color.name()}; background: rgba(255,255,255,150); border: 1px dashed gray;")

    def set_line_width(self, width):
        self.line_width = width
        if hasattr(self, 'text_edit') and self.text_edit:
            font = self.text_edit.font()
            font.setPixelSize(width * 3)
            self.text_edit.setFont(font)

    def mousePressEvent(self, event):
        if self.text_mode and event.button() == Qt.MouseButton.LeftButton:
            self.start_text_input(event.pos())
            return
            
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.leftButton = True
            self.last_coords = self.transform_position(event.pos())
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing and self.leftButton:
            if self.last_coords is None:
                self.last_coords = self.transform_position(event.pos())
                return

            current_pos = self.transform_position(event.pos())

            painter = QPainter(self.drawing_pixmap)
            pen = painter.pen()
            pen.setWidth(self.line_width)
            
            if self.eraser_mode:
                pen.setColor(QColor('white'))
            else:
                pen.setColor(self.pencil_color)
                
            painter.setPen(pen)
            painter.drawLine(self.last_coords, current_pos)
            painter.end()

            self.update_canvas()
            self.last_coords = current_pos
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftButton = False
            self.last_coords = None
        else:
            super().mouseReleaseEvent(event)

    def start_text_input(self, pos):
        self.finish_text_input()
        
        canvas_pos = self.transform_position(pos)
        self.current_text_item = {
            'pos': canvas_pos,
            'text': '',
            'color': self.pencil_color,
            'font_size': self.line_width * 3
        }
        self.text_edit.move(pos.x(), pos.y())
        self.text_edit.resize(200, self.line_width * 4)
        self.text_edit.show()
        self.text_edit.setFocus()
        self.text_edit.clear()

    def finish_text_input(self):
        if not hasattr(self, 'text_edit') or not self.text_edit or not self.text_edit.isVisible():
            return
            
        text = self.text_edit.text()
        if text and self.current_text_item:
            self.current_text_item['text'] = text
            self.text_items.append(self.current_text_item.copy())
            
            painter = QPainter(self.drawing_pixmap)
            font = painter.font()
            font.setPixelSize(self.current_text_item['font_size'])
            painter.setFont(font)
            painter.setPen(self.current_text_item['color'])
            painter.drawText(self.current_text_item['pos'], text)
            painter.end()
            
            self.update_canvas()
        
        self.text_edit.hide()
        self.current_text_item = None

    def transform_position(self, pos):
        return pos / self.scale_factor

    def update_canvas(self):
        temp_pixmap = self.drawing_pixmap.copy()
        
        if self.current_text_item and self.current_text_item.get('text'):
            painter = QPainter(temp_pixmap)
            font = painter.font()
            font.setPixelSize(self.current_text_item['font_size'])
            painter.setFont(font)
            painter.setPen(self.current_text_item['color'])
            painter.drawText(self.current_text_item['pos'], self.current_text_item['text'])
            painter.end()
        
        scaled_pixmap = temp_pixmap.scaled(
            self.drawing_pixmap.size() * self.scale_factor,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pixmap)

    def set_scale(self, scale_factor):
        self.scale_factor = scale_factor
        self.update_canvas()

    def clear_canvas(self):
        self.drawing_pixmap.fill(QColor('white'))
        self.text_items = []
        self.current_text_item = None
        if hasattr(self, 'text_edit') and self.text_edit:
            self.text_edit.hide()
        self.update_canvas()
