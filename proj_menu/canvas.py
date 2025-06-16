from PyQt6.QtWidgets import QLabel, QLineEdit
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen, QBrush
from PyQt6.QtCore import Qt, QPoint, QRectF

class Canvas(QLabel):
    def __init__(self, width=2000, height=2000):
        super().__init__()
        self.drawing = False
        self.eraser_mode = False
        self.text_mode = False
        self.shape_mode = False
        self.fill_mode = False
        self.last_coords = None
        self.start_pos = None
        self.leftButton = False
        self.temp_pixmap = None
        self.current_shape = None
        self.current_text_item = None
        self.text_items = []
        self.setScaledContents(False)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drawing_pixmap = QPixmap(width, height)
        self.drawing_pixmap.fill(Qt.GlobalColor.white)
        self.original_pixmap = self.drawing_pixmap.copy()
        self.scale_factor = 1.0
        self.pencil_color = QColor(Qt.GlobalColor.black)
        self.fill_color = QColor(Qt.GlobalColor.transparent)
        self.line_width = 7
        
        self.text_edit = QLineEdit(self)
        self.text_edit.setStyleSheet(f"color: {self.pencil_color.name()}; background: rgba(255,255,255,150); border: 1px dashed gray;")
        font = self.text_edit.font()
        font.setPixelSize(self.line_width * 3)
        self.text_edit.setFont(font)
        self.text_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.text_edit.returnPressed.connect(self.finish_text_input)
        self.text_edit.hide()
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

    def set_shape_mode(self, enabled, shape=None):
        if not enabled:
            self.finish_text_input()
        self.shape_mode = enabled
        if shape:
            self.current_shape = shape.lower()

    def set_pencil_color(self, color):
        self.pencil_color = color
        self.text_edit.setStyleSheet(f"color: {color.name()}; background: rgba(255,255,255,150); border: 1px dashed gray;")

    def set_line_width(self, width):
        self.line_width = width
        font = self.text_edit.font()
        font.setPixelSize(width * 3)
        self.text_edit.setFont(font)

    def mousePressEvent(self, event):
        if self.text_mode and event.button() == Qt.MouseButton.LeftButton:
            self.start_text_input(event.pos())
            return
            
        if event.button() == Qt.MouseButton.LeftButton and (self.drawing or self.shape_mode):
            self.leftButton = True
            self.start_pos = self.transform_position(event.pos())
            self.last_coords = self.start_pos
            
            if self.shape_mode:
                self.temp_pixmap = self.drawing_pixmap.copy()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        try:
            if self.shape_mode and self.leftButton and self.temp_pixmap:
                current_pos = self.transform_position(event.pos())
                if current_pos == self.start_pos:
                    return
                    
                self.drawing_pixmap = self.temp_pixmap.copy()
                painter = QPainter(self.drawing_pixmap)
                self.setup_painter(painter)
                
                if self.current_shape == "круг":
                    rect = QRectF(
                        min(self.start_pos.x(), current_pos.x()), 
                        min(self.start_pos.y(), current_pos.y()),
                        abs(current_pos.x() - self.start_pos.x()), 
                        abs(current_pos.y() - self.start_pos.y()))
                    painter.drawEllipse(rect)
                elif self.current_shape == "квадрат":
                    rect = QRectF(
                        min(self.start_pos.x(), current_pos.x()), 
                        min(self.start_pos.y(), current_pos.y()),
                        abs(current_pos.x() - self.start_pos.x()), 
                        abs(current_pos.y() - self.start_pos.y()))
                    painter.drawRect(rect)
                    
                painter.end()
                self.update_canvas()
                
            elif self.drawing and self.leftButton:
                current_pos = self.transform_position(event.pos())
                if self.last_coords is None:
                    self.last_coords = current_pos
                    return
                    
                painter = QPainter(self.drawing_pixmap)
                pen = painter.pen()
                pen.setWidth(self.line_width)
                pen.setColor(Qt.GlobalColor.white if self.eraser_mode else self.pencil_color)
                painter.setPen(pen)
                painter.drawLine(self.last_coords, current_pos)
                painter.end()
                self.update_canvas()
                self.last_coords = current_pos
                
        except Exception as e:
            print(f"Ошибка рисования: {str(e)}")
            self.leftButton = False

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftButton = False
            if self.shape_mode:
                self.temp_pixmap = None
            self.last_coords = None
        else:
            super().mouseReleaseEvent(event)

    def setup_painter(self, painter):
        pen = painter.pen()
        pen.setWidth(self.line_width)
        pen.setColor(self.pencil_color)
        painter.setPen(pen)
        if self.fill_mode and self.fill_color != Qt.GlobalColor.transparent:
            painter.setBrush(QBrush(self.fill_color))

    def start_text_input(self, pos):
        self.finish_text_input()
        canvas_pos = self.transform_position(pos)
        self.current_text_item = {
            'pos': canvas_pos,
            'text': '',
            'color': self.pencil_color,
            'font_size': self.line_width * 3}
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
        src_size = self.drawing_pixmap.size()
        container_size = self.size()
        shift_w = int((container_size.width() - src_size.width()) / 2)
        shift_h = int((container_size.height() - src_size.height()) / 2)
        if shift_w > 0 and shift_h > 0:
            return QPoint(int(pos.x() - shift_w), int(pos.y() - shift_h))
        return pos

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
        self.setPixmap(temp_pixmap)

    def clear_canvas(self):
        self.drawing_pixmap.fill(Qt.GlobalColor.white)
        self.text_items = []
        self.current_text_item = None
        if hasattr(self, 'text_edit') and self.text_edit:
            self.text_edit.hide()
        self.update_canvas()
