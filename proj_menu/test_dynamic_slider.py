import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QSlider, QLabel
)
from PyQt6.QtCore import Qt


class SliderWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Sliders")
        self.setGeometry(100, 100, 400, 250) 
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        self.button_layout = QHBoxLayout()
        
        self.slider1_button = QPushButton("Слайдер 1 (0-100)")
        self.slider1_button.setCheckable(True)
        self.slider1_button.setChecked(True)
        self.slider1_button.clicked.connect(self.show_slider1)
        
        self.slider2_button = QPushButton("Слайдер 2 (-100-100)")
        self.slider2_button.setCheckable(True)
        self.slider2_button.clicked.connect(self.show_slider2)
        
        self.button_layout.addWidget(self.slider1_button)
        self.button_layout.addWidget(self.slider2_button)
        
        self.slider1 = QSlider(Qt.Orientation.Horizontal)
        self.slider1.setRange(0, 100)
        self.slider1.setValue(50)
        self.slider1.valueChanged.connect(self.update_value_label)
        
        self.slider2 = QSlider(Qt.Orientation.Horizontal)
        self.slider2.setRange(-100, 100)
        self.slider2.setValue(0)
        self.slider2.valueChanged.connect(self.update_value_label)
        
        self.value_label = QLabel("Текущее значение: 50")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.slider_container = QWidget()
        self.slider_layout = QVBoxLayout(self.slider_container)
        
        self.current_slider = self.slider1
        self.slider_layout.addWidget(self.current_slider)
        self.slider_layout.addWidget(self.value_label)
        
        main_layout.addLayout(self.button_layout)
        main_layout.addWidget(self.slider_container)
        
    def show_slider1(self):
        self.slider1_button.setChecked(True)
        self.slider2_button.setChecked(False)
        self.switch_slider(self.slider1)
        
    def show_slider2(self):
        self.slider1_button.setChecked(False)
        self.slider2_button.setChecked(True)
        self.switch_slider(self.slider2)
        
    def switch_slider(self, new_slider):
        self.slider_layout.removeWidget(self.current_slider)
        self.current_slider.hide()

        self.slider_layout.insertWidget(0, new_slider)  
        new_slider.show()

        self.current_slider = new_slider
        self.update_value_label(new_slider.value())
    
    def update_value_label(self, value):
        self.value_label.setText(f"Текущее значение: {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = SliderWindow()
    window.show()
    sys.exit(app.exec())
