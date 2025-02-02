import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QWidget, QMessageBox, QLabel, QTextEdit, QDateEdit,QScrollArea,QDialog,QFrame,QComboBox,QCheckBox
)

from PyQt6.QtGui import QPainter

class Grid(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMinimumSize(800, 600)
        self.columns = 40
        self.rows = 30

        # some random objects
        self.objects = [
            (10, 20), 
            (11, 21), 
            (12, 20), 
            (12, 22), 
        ]

    def resizeEvent(self, event):
        # compute the square size based on the aspect ratio, assuming that the
        # column and row numbers are fixed
        reference = self.width() * self.rows / self.columns
        if reference > self.height():
            # the window is larger than the aspect ratio
            # use the height as a reference (minus 1 pixel)
            self.squareSize = (self.height() - 1) / self.rows
        else:
            # the opposite
            self.squareSize = (self.width() - 1) / self.columns

    def paintEvent(self, event):
        print("1")
        qp = QPainter(self)
        # translate the painter by half a pixel to ensure correct line painting
        qp.translate(.5, .5)
        print("2")
        qp.setRenderHints(qp.Antialiasing)

        width = self.squareSize * self.columns
        height = self.squareSize * self.rows
        # center the grid
        left = (self.width() - width) / 2
        top = (self.height() - height) / 2
        y = top
        # we need to add 1 to draw the topmost right/bottom lines too
        for row in range(self.rows + 1):
            qp.drawLine(left, y, left + width, y)
            y += self.squareSize
        x = left
        for column in range(self.columns + 1):
            qp.drawLine(x, top, x, top + height)
            x += self.squareSize
        print("3")
        # create a smaller rectangle
        objectSize = self.squareSize * .8
        margin = self.squareSize* .1
        objectRect = QRectF(margin, margin, objectSize, objectSize)
        print("4")
        qp.setBrush(Qt.blue)
        for col, row in self.objects:
            qp.drawEllipse(objectRect.translated(
                left + col * self.squareSize, top + row * self.squareSize))


class GridWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Grid Window")
        self.setFixedSize(700,600)
        print("before")
        self.widget = Grid()
        print("after")
        self.vbox = QVBoxLayout()              

        self.label = QLabel(self)
        self.label.setText("Open Grid")
        self.vbox.addWidget(self.label)
        self.widget.setLayout(self.vbox)

        self.setCentralWidget(self.widget)
        
