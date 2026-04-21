import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QColorDialog, QSlider, QLabel, QGraphicsView,
    QGraphicsScene, QGraphicsItem, QGraphicsPathItem,
    QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsRectItem,
    QGraphicsTextItem, QFileDialog, QMessageBox, QSpinBox,
    QComboBox, QFrame, QToolBar, QStatusBar
)
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF, QSize, QTimer
from PyQt6.QtGui import (
    QPainter, QPen, QBrush, QColor, QAction, QIcon,
    QPainterPath, QFont, QImage, QPixmap, QCursor,
    QTransform
)

class ImprovedGraphicsView(QGraphicsView):
    
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        
        self.panning = False
        self.last_mouse_pos = QPointF()
        self.pan_button = Qt.MouseButton.MiddleButton

        self.drawing = False
        self.current_path = None
        self.current_item = None
        self.current_pen = QPen(QColor('#007BFF'), 3)
        self.current_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        self.current_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        
        self.current_mode = "draw"
        self.start_point = None

        self.temp_item = None

        self.scale_factor = 1.0
        self.min_scale = 0.1
        self.max_scale = 10.0
        
        self.show_grid = True
        self.grid_size = 50
        self.grid_color = QColor(220, 220, 220)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.pan_timer = QTimer()
        self.pan_timer.setSingleShot(True)
        self.pan_timer.timeout.connect(self.reset_pan_mode)
        
    def reset_pan_mode(self):
        self.panning = False
        self.setCursor(Qt.CursorShape.ArrowCursor)
        
    def wheelEvent(self, event):
        if not self.drawing:
            zoom_in_factor = 1.15
            zoom_out_factor = 1 / zoom_in_factor

            old_pos = self.mapToScene(event.position().toPoint())
            if event.angleDelta().y() > 0:
                zoom_factor = zoom_in_factor
            else:
                zoom_factor = zoom_out_factor
            
            new_scale = self.scale_factor * zoom_factor
            if self.min_scale <= new_scale <= self.max_scale:
                self.scale(zoom_factor, zoom_factor)
                self.scale_factor = new_scale

                new_pos = self.mapToScene(event.position().toPoint())
                delta = new_pos - old_pos
                self.translate(delta.x(), delta.y())

                self.viewport().update()
    
    def mousePressEvent(self, event):
        scene_pos = self.mapToScene(event.position().toPoint())

        if event.button() == self.pan_button:
            self.panning = True
            self.last_mouse_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
            
        elif event.button() == Qt.MouseButton.LeftButton:
            if self.current_mode == "draw":
                self.drawing = True
                self.current_path = QPainterPath()
                self.current_path.moveTo(scene_pos)
                
                self.current_item = QGraphicsPathItem(self.current_path)
                self.current_item.setPen(self.current_pen)
                self.scene().addItem(self.current_item)

                event.accept()
                return
                
            elif self.current_mode in ["line", "rect", "ellipse"]:
                self.drawing = True
                self.start_point = scene_pos

                if self.current_mode == "line":
                    self.temp_item = QGraphicsLineItem()
                elif self.current_mode == "rect":
                    self.temp_item = QGraphicsRectItem()
                else:
                    self.temp_item = QGraphicsEllipseItem()
                
                self.temp_item.setPen(self.current_pen)
                self.scene().addItem(self.temp_item)
                
                event.accept()
                return

        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.position().toPoint())
 
        if isinstance(self.parent(), QMainWindow):
            self.parent().statusBar().showMessage(
                f"Position: ({int(scene_pos.x())}, {int(scene_pos.y())}) | "
                f"Zoom: {int(self.scale_factor * 100)}% | "
                f"Mode: {self.current_mode}"
            )

        if self.panning and event.buttons() & self.pan_button:
            delta = event.position() - self.last_mouse_pos
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y())
            )
            self.last_mouse_pos = event.position()
            event.accept()
            return

        if self.drawing:
            if self.current_mode == "draw" and self.current_path is not None:
                self.current_path.lineTo(scene_pos)
                self.current_item.setPath(self.current_path)
                event.accept()
                return
                
            elif self.current_mode in ["line", "rect", "ellipse"] and self.start_point is not None:
                if self.current_mode == "line" and isinstance(self.temp_item, QGraphicsLineItem):
                    line = QLineF(self.start_point, scene_pos)
                    self.temp_item.setLine(line)
                    
                elif self.current_mode == "rect" and isinstance(self.temp_item, QGraphicsRectItem):
                    rect = QRectF(self.start_point, scene_pos).normalized()
                    self.temp_item.setRect(rect)
                    
                elif self.current_mode == "ellipse" and isinstance(self.temp_item, QGraphicsEllipseItem):
                    rect = QRectF(self.start_point, scene_pos).normalized()
                    self.temp_item.setRect(rect)
                
                event.accept()
                return

        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        scene_pos = self.mapToScene(event.position().toPoint())
        
        if event.button() == self.pan_button and self.panning:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        

        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            if self.current_mode == "draw":
                self.drawing = False
                self.current_path = None
                self.current_item = None
                
            elif self.current_mode in ["line", "rect", "ellipse"] and self.start_point is not None:
                if self.temp_item is not None:
                    self.scene().removeItem(self.temp_item)
                    self.temp_item = None

                if self.current_mode == "line":
                    item = QGraphicsLineItem(QLineF(self.start_point, scene_pos))
                elif self.current_mode == "rect":
                    item = QGraphicsRectItem(QRectF(self.start_point, scene_pos).normalized())
                else:
                    item = QGraphicsEllipseItem(QRectF(self.start_point, scene_pos).normalized())
                
                item.setPen(self.current_pen)
                self.scene().addItem(item)
                
                self.drawing = False
                self.start_point = None
            
            event.accept()
            return
        
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.panning = True
            self.last_mouse_pos = self.mapFromGlobal(QCursor.pos())
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        elif event.key() == Qt.Key.Key_Escape:
            if self.drawing:
                self.drawing = False
                if self.temp_item is not None:
                    self.scene().removeItem(self.temp_item)
                    self.temp_item = None
                self.start_point = None
                self.current_path = None
                self.current_item = None
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space and self.panning:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().keyReleaseEvent(event)
    
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        if self.show_grid:
            painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DotLine))

            grid_size = self.grid_size
            
            left = int(rect.left()) - (int(rect.left()) % grid_size)
            top = int(rect.top()) - (int(rect.top()) % grid_size)

            x = left
            while x < rect.right():
                painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
                x += grid_size

            y = top
            while y < rect.bottom():
                painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
                y += grid_size

            painter.setPen(QPen(QColor(100, 100, 100), 2))
            painter.drawLine(QPointF(0, rect.top()), QPointF(0, rect.bottom()))
            painter.drawLine(QPointF(rect.left(), 0), QPointF(rect.right(), 0))
    
    def set_mode(self, mode):
        self.current_mode = mode
        self.drawing = False
        self.start_point = None
        self.current_path = None
        self.current_item = None
        
        if self.temp_item is not None:
            self.scene().removeItem(self.temp_item)
            self.temp_item = None
    
    def set_pen_color(self, color):
        self.current_pen.setColor(color)
    
    def set_pen_width(self, width):
        self.current_pen.setWidth(width)
    
    def set_show_grid(self, show):
        self.show_grid = show
        self.viewport().update()
    
    def fit_to_view(self):
        self.fitInView(self.scene().itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.scale_factor = self.transform().m11()
    
    def zoom_in(self):
        self.scale(1.2, 1.2)
        self.scale_factor *= 1.2
    
    def zoom_out(self):
        self.scale(1/1.2, 1/1.2)
        self.scale_factor /= 1.2
    
    def zoom_100(self):
        self.resetTransform()
        self.scale_factor = 1.0


class ImprovedDrawingApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Professional Drawing App")
        self.setGeometry(100, 100, 1400, 900)

        self.scene = QGraphicsScene()

        self.view = ImprovedGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)

        self.create_toolbars()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def create_toolbars(self):
        main_toolbar = QToolBar("Tools", self)
        main_toolbar.setIconSize(QSize(32, 32))
        main_toolbar.setMovable(False)
        self.addToolBar(main_toolbar)
        
        self.draw_action = QAction(" Draw", self)
        self.draw_action.setCheckable(True)
        self.draw_action.setChecked(True)
        self.draw_action.triggered.connect(lambda: self.set_mode("draw"))
        main_toolbar.addAction(self.draw_action)
        
        self.line_action = QAction(" Line", self)
        self.line_action.setCheckable(True)
        self.line_action.triggered.connect(lambda: self.set_mode("line"))
        main_toolbar.addAction(self.line_action)
        
        self.rect_action = QAction(" Rectangle", self)
        self.rect_action.setCheckable(True)
        self.rect_action.triggered.connect(lambda: self.set_mode("rect"))
        main_toolbar.addAction(self.rect_action)
        
        self.ellipse_action = QAction(" Ellipse", self)
        self.ellipse_action.setCheckable(True)
        self.ellipse_action.triggered.connect(lambda: self.set_mode("ellipse"))
        main_toolbar.addAction(self.ellipse_action)
        
        main_toolbar.addSeparator()
        
        self.color_btn = QPushButton("")
        self.color_btn.setToolTip("Choose color")
        self.color_btn.setFixedSize(40, 40)
        self.color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.view.current_pen.color().name()};
                border: 2px solid #dee2e6;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                border-color: #007BFF;
            }}
        """)
        self.color_btn.clicked.connect(self.choose_color)
        main_toolbar.addWidget(self.color_btn)
        
        main_toolbar.addWidget(QLabel(" Width:"))
        
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 50)
        self.width_spin.setValue(3)
        self.width_spin.setFixedWidth(60)
        self.width_spin.valueChanged.connect(self.view.set_pen_width)
        main_toolbar.addWidget(self.width_spin)
        
        main_toolbar.addSeparator()
        
        self.grid_action = QAction(" Grid", self)
        self.grid_action.setCheckable(True)
        self.grid_action.setChecked(True)
        self.grid_action.triggered.connect(lambda: self.view.set_show_grid(self.grid_action.isChecked()))
        main_toolbar.addAction(self.grid_action)
        
        self.fit_action = QAction(" Fit All", self)
        self.fit_action.triggered.connect(self.view.fit_to_view)
        main_toolbar.addAction(self.fit_action)
        
        self.zoom_in_action = QAction(" Zoom In", self)
        self.zoom_in_action.triggered.connect(self.view.zoom_in)
        main_toolbar.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction(" Zoom Out", self)
        self.zoom_out_action.triggered.connect(self.view.zoom_out)
        main_toolbar.addAction(self.zoom_out_action)
        
        self.zoom_100_action = QAction(" 100%", self)
        self.zoom_100_action.triggered.connect(self.view.zoom_100)
        main_toolbar.addAction(self.zoom_100_action)
        
        main_toolbar.addSeparator()
        
        self.save_action = QAction(" Save", self)
        self.save_action.triggered.connect(self.save_drawing)
        main_toolbar.addAction(self.save_action)
        
        self.load_action = QAction(" Load", self)
        self.load_action.triggered.connect(self.load_drawing)
        main_toolbar.addAction(self.load_action)
        
        self.clear_action = QAction(" Clear", self)
        self.clear_action.triggered.connect(self.clear_scene)
        main_toolbar.addAction(self.clear_action)

        self.mode_actions = [
            self.draw_action, self.line_action,
            self.rect_action, self.ellipse_action
        ]
    
    def set_mode(self, mode):
        for action in self.mode_actions:
            action.setChecked(False)
        
        sender = self.sender()
        if sender:
            sender.setChecked(True)

        self.view.set_mode(mode)

        mode_names = {
            "draw": "Free Draw",
            "line": "Line",
            "rect": "Rectangle",
            "ellipse": "Ellipse"
        }
        self.status_bar.showMessage(f"Mode: {mode_names.get(mode, mode)}")
    
    def choose_color(self):
        color = QColorDialog.getColor(
            self.view.current_pen.color(), 
            self, 
            "Choose color",
            QColorDialog.ColorDialogOption.DontUseNativeDialog
        )
        
        if color.isValid():
            self.view.set_pen_color(color)
            self.color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color.name()};
                    border: 2px solid #dee2e6;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    border-color: #007BFF;
                }}
            """)
    
    def save_drawing(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Drawing", "", 
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*)"
        )
        
        if file_path:
            rect = self.scene.itemsBoundingRect()
            image = QImage(rect.size().toSize(), QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.white)
            
            painter = QPainter(image)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.scene.render(painter, target=QRectF(image.rect()), source=rect)
            painter.end()
            
            image.save(file_path)
            self.status_bar.showMessage(f"Saved: {file_path}", 3000)
    
    def load_drawing(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Drawing", "",
            "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.scene.addPixmap(pixmap)
                self.status_bar.showMessage(f"Loaded: {file_path}", 3000)
    
    def clear_scene(self):
        reply = QMessageBox.question(
            self, "Clear", "Are you sure you want to clear everything?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scene.clear()
            self.status_bar.showMessage("Scene cleared", 3000)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = ImprovedDrawingApp()
    window.show()
    
    sys.exit(app.exec())
