from PyQt6.QtWidgets import QLabel, QLineEdit
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PyQt6.QtCore import Qt, QPoint, QRect
import datetime

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
        
        self.original_width = width
        self.original_height = height
        
        self.drawing_pixmap = QPixmap(width, height)
        self.drawing_pixmap.fill(QColor('white'))
        
        self.display_pixmap = QPixmap()
        
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
            
    #Обработка нажатия кнопки мыши
    def mousePressEvent(self, event):
        if self.text_mode and event.button() == Qt.MouseButton.LeftButton:
            self.start_text_input(event.pos())
            return
            
        if self.shape_mode and event.button() == Qt.MouseButton.LeftButton:
            pos = self.transform_position(event.pos())
            if pos.x() >= 0 and pos.y() >= 0:
                self.shape_start = pos
                self.leftButton = True
            return
            
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            pos = self.transform_position(event.pos())
            if pos.x() >= 0 and pos.y() >= 0:
                self.leftButton = True
                self.last_coords = pos
        else:
            super().mousePressEvent(event)
    #Обработка движения мыши
    def mouseMoveEvent(self, event):
        if self.drawing and self.leftButton:
            if self.last_coords is None:
                return

            current_pos = self.transform_position(event.pos())
            
            if current_pos.x() < 0 or current_pos.y() < 0:
                return

            painter = QPainter(self.drawing_pixmap)
            pen = painter.pen()
            pen_width = max(1, int(self.line_width))
            pen.setWidth(pen_width)
            
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
            
            if current_pos.x() < 0 or current_pos.y() < 0:
                return
            
            temp_pixmap = self.drawing_pixmap.copy()
            
            painter = QPainter(temp_pixmap)
            pen = painter.pen()
            pen_width = max(1, int(self.line_width))
            pen.setWidth(pen_width)
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
            
            if self.scale_factor != 1.0:
                temp_display = temp_pixmap.scaled(
                    temp_pixmap.size() * self.scale_factor,
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setPixmap(temp_display)
            else:
                self.setPixmap(temp_pixmap)
        else:
            super().mouseMoveEvent(event)
            
    #Обработка отпускания кнопки мыши
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.shape_mode and self.leftButton:
            current_pos = self.transform_position(event.pos())
            
            if (current_pos.x() >= 0 and current_pos.y() >= 0 and
                self.shape_start.x() >= 0 and self.shape_start.y() >= 0):
                
                painter = QPainter(self.drawing_pixmap)
                pen = painter.pen()
                pen_width = max(1, int(self.line_width))
                pen.setWidth(pen_width)
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
        
        screen_pos = self.transform_position(pos)
        if screen_pos.x() < 0 or screen_pos.y() < 0:
            return
            
        self.current_text_item = {
            'pos': screen_pos,
            'text': '',
            'color': self.pencil_color,
            'font_size': max(10, int(self.line_width * 3))
        }
        
        self.text_edit.move(pos.x(), pos.y())
        self.text_edit.resize(200, max(30, int(self.line_width * 4)))
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

        display_size = self.drawing_pixmap.size() * self.scale_factor
        container_size = self.size()
        
        shift_x = max(0, (container_size.width() - display_size.width()) // 2)
        shift_y = max(0, (container_size.height() - display_size.height()) // 2)
        
        display_x = pos.x() - shift_x
        display_y = pos.y() - shift_y
        
        if (display_x < 0 or display_x >= display_size.width() or
            display_y < 0 or display_y >= display_size.height()):
            return QPoint(-1, -1)
        
        canvas_x = int(display_x / self.scale_factor)
        canvas_y = int(display_y / self.scale_factor)
        
        canvas_x = max(0, min(canvas_x, self.drawing_pixmap.width() - 1))
        canvas_y = max(0, min(canvas_y, self.drawing_pixmap.height() - 1))
        
        return QPoint(canvas_x, canvas_y)
        
    def update_canvas(self):
        start_time = datetime.datetime.now()
        
        if self.scale_factor != 1.0:
            self.display_pixmap = self.drawing_pixmap.scaled(self.drawing_pixmap.size() * self.scale_factor,Qt.AspectRatioMode.IgnoreAspectRatio,Qt.TransformationMode.SmoothTransformation)
        else:
            self.display_pixmap = self.drawing_pixmap.copy()
        
        scale_time = datetime.datetime.now()
        
        if self.current_text_item and self.current_text_item.get('text'):
            painter = QPainter(self.display_pixmap)
            font = painter.font()
            display_font_size = int(self.current_text_item['font_size'] * self.scale_factor)
            font.setPixelSize(max(10, display_font_size))
            painter.setFont(font)
            painter.setPen(self.current_text_item['color'])
            
            text_pos = QPoint(int(self.current_text_item['pos'].x() * self.scale_factor),int(self.current_text_item['pos'].y() * self.scale_factor))
            painter.drawText(text_pos, self.current_text_item['text'])
            painter.end()
        
        draw_time = datetime.datetime.now()
        
        self.setPixmap(self.display_pixmap)
        
        set_time = datetime.datetime.now()
              
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

    def set_bg_color(self, color):
        self.bg_color = color
        self.update()

    def set_show_grid(self, show):
        self.show_grid = show
        self.update()
