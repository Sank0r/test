from PyQt6.QtWidgets import QLabel, QLineEdit
from PyQt6.QtGui import QPixmap, QPainter, QColor, QTransform, QFont, QPen
from PyQt6.QtCore import Qt, QPoint, QEvent, QRect

class Canvas(QLabel):
    def __init__(self, width=2000, height=2000):
        super().__init__()
        self.drawing = False
        self.last_coords = None
        self.leftButton = False
        self.eraser_mode = False
        self.text_mode = False
        self.shape_mode = False 
        self.shape_type = None   
        self.shape_start = None  
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
        
        self.original_pixmap = self.drawing_pixmap.copy()
        
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

    def set_shape_mode(self, enabled): 
        if not enabled:
            self.finish_text_input()
        self.shape_mode = enabled

    def set_shape_type(self, shape_type):  
        self.shape_type = shape_type

    def set_pencil_color(self, color):
        self.pencil_color = color
        if hasattr(self, 'text_edit') and self.text_edit:
            self.text_edit.setStyleSheet(f"color: {color.name()}; background: rgba(255,255,255,150); border: 1px dashed gray;")

    def set_line_width(self, width):
        self.line_width = width
        if hasattr(self, 'text_edit') and self.text_edit and not self.text_mode:
            font = self.text_edit.font()
            font.setPixelSize(width * 3)
            self.text_edit.setFont(font)

    def set_text_size(self, size):
        self.line_width = size // 3  
        if hasattr(self, 'text_edit') and self.text_edit:
            font = self.text_edit.font()
            font.setPixelSize(size)
            self.text_edit.setFont(font)

    def mousePressEvent(self, event):
        if self.text_mode and event.button() == Qt.MouseButton.LeftButton:
            self.start_text_input(event.pos())
            return
            
        if self.shape_mode and event.button() == Qt.MouseButton.LeftButton:  # Добавлено
            self.shape_start = self.transform_position(event.pos())
            self.leftButton = True
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
        elif self.shape_mode and self.leftButton:  
            current_pos = self.transform_position(event.pos())
            temp_pixmap = self.drawing_pixmap.copy()
            
            painter = QPainter(temp_pixmap)
            pen = painter.pen()
            pen.setWidth(self.line_width)
            pen.setColor(self.pencil_color)
            painter.setPen(pen)
            
            if self.shape_type == "rectangle":
                rect = QRect(self.shape_start, current_pos)
                painter.drawRect(rect)
            elif self.shape_type == "circle":
                radius = int(((current_pos.x() - self.shape_start.x())**2 + 
                           (current_pos.y() - self.shape_start.y())**2)**0.5)
                painter.drawEllipse(self.shape_start, radius, radius)
            elif self.shape_type == "line":
                painter.drawLine(self.shape_start, current_pos)
                
            painter.end()
            self.setPixmap(temp_pixmap)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.shape_mode and self.leftButton:  # Добавлено
            current_pos = self.transform_position(event.pos())
            
            painter = QPainter(self.drawing_pixmap)
            pen = painter.pen()
            pen.setWidth(self.line_width)
            pen.setColor(self.pencil_color)
            painter.setPen(pen)
            
            if self.shape_type == "rectangle":
                rect = QRect(self.shape_start, current_pos)
                painter.drawRect(rect)
            elif self.shape_type == "circle":
                radius = int(((current_pos.x() - self.shape_start.x())**2 + 
                           (current_pos.y() - self.shape_start.y())**2)**0.5)
                painter.drawEllipse(self.shape_start, radius, radius)
            elif self.shape_type == "line":
                painter.drawLine(self.shape_start, current_pos)
                
            painter.end()
            self.update_canvas()
            
        if event.button() == Qt.MouseButton.LeftButton:
            self.leftButton = False
            self.last_coords = None
            self.shape_start = None  
        else:
            super().mouseReleaseEvent(event)

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
            new_pos = QPoint(int(pos.x() - shift_w), int(pos.y() - shift_h))
        else:
            new_pos = pos
        return new_pos

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
        
    def scale_pixmap(self):
        scaled_pixmap = self.original_pixmap.scaled(
            self.original_pixmap.size() * self.scale_factor,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pixmap)
        self.drawing_pixmap = scaled_pixmap

    def set_scale(self, scale_factor):
        self.scale_factor = scale_factor
        self.scale_pixmap()

    def clear_canvas(self):
        self.drawing_pixmap.fill(QColor('white'))
        self.text_items = []
        self.current_text_item = None
        if hasattr(self, 'text_edit') and self.text_edit:
            self.text_edit.hide()
        self.update_canvas()

    def set_bg_color(self, color):
        self.bg_color = color
        self.update()

    def set_show_grid(self, show):
        self.show_grid = show
        self.update()
