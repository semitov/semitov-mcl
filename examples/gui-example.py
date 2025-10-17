#!/usr/bin/env python3

from PyQt6.QtWidgets import QMainWindow, QApplication, QStackedWidget, QSlider, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from qt_material import apply_stylesheet
import sys

from mcl import Board

class MainWindow(QMainWindow):

    __WIDTH = 640
    __HEIGHT= 480

    __examplesList = [ "Blinking LED", "PWM LED" ]

    __status = False

    def make_title_layout(self):
        TitleLayout = QHBoxLayout()

        title = QLabel("SemiTO-V MCL")
        title.setStyleSheet("font: 30px;")


        TitleLayout.addSpacing(210)
        TitleLayout.addWidget(title)

        return TitleLayout

    def make_button_layout(self,text, bindedFoo):
        ButtonLayout = QHBoxLayout()

        button = QPushButton(text)
        button.clicked.connect(bindedFoo)

        ButtonLayout.addSpacing(900)
        ButtonLayout.addWidget(button)

        return ButtonLayout

    __selectedExampleIndex = 0
    __selectedPin = 0
    def go_back_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def __init__(self):
        super().__init__()

        self.board = Board("/dev/ttyACM0")

        self.setWindowTitle("SemiTOV MCL Example")

        self.stacked_widget = QStackedWidget()

        self.default_page = self.make_default_page()
        self.blinkingled_page = self.make_blinkingled_page()
        self.pwm_page = self.make_pwm_page()

        self.stacked_widget.addWidget(self.default_page)
        self.stacked_widget.addWidget(self.blinkingled_page)
        self.stacked_widget.addWidget(self.pwm_page)
        self.setCentralWidget(self.stacked_widget)
        self.setFixedWidth(self.__WIDTH)
        self.setFixedHeight(self.__HEIGHT)


    def make_default_page(self):

        widget = QWidget()

        Vlayout = QVBoxLayout()
        Hlayout = QHBoxLayout()

        TitleLayout = self.make_title_layout()
        ButtonLayout = self.make_button_layout("Next!", self.select_example_page)

        label = QLabel("Select an example: ")
        label.setStyleSheet("font: 20px;")

        examples = QComboBox()
        examples.addItems(self.__examplesList)
        examples.currentIndexChanged.connect( self.index_changed )

        Hlayout.addWidget(label)
        Hlayout.addWidget(examples)

        Vlayout.addLayout(TitleLayout)
        Vlayout.addSpacing(100)
        Vlayout.addLayout(Hlayout)
        Vlayout.addSpacing(200)
        Vlayout.addLayout(ButtonLayout)

        widget.setLayout(Vlayout)

        return widget

    def index_changed(self, s):
        self.__selectedExampleIndex = int(s)

    def select_example_page(self, checked):
        self.stacked_widget.setCurrentIndex(self.__selectedExampleIndex + 1)


    def setup_led(pinNumber):
        from machine import Pin

        led = Pin(pinNumber, Pin.OUT)

        return led

    def turn_on_led(self,checked):
        led = self.board.def_function(self.setup_led)(self.__selectedPin)

        self.__status = not self.__status

        led.value(self.__status)

        if(self.__status == True):
            self.__statusButton.setText("Turn OFF")
        else:
            self.__statusButton.setText("Turn ON")
    def make_blinkingled_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        chooseLayout = QHBoxLayout()
        chooseLabel = QLabel("Choose a PIN:")
        chooseLabel.setStyleSheet("font: 20px;")

        statusPinLayout = QHBoxLayout()
        self.__statusButton = QPushButton("Turn ON")
        self.__statusButton.clicked.connect(self.turn_on_led)
        self.__statusButton.setStyleSheet("font: 30px")

        pins = QComboBox()
        for x in range(24):
            pins.addItem(str(x))

        pins.currentTextChanged.connect( self.text_changed )

        chooseLayout.addWidget(chooseLabel)
        chooseLayout.addWidget(pins)

        statusPinLayout.addSpacing(150)
        statusPinLayout.addWidget(self.__statusButton)
        statusPinLayout.addSpacing(150)



        layout.addLayout(self.make_title_layout())
        layout.addSpacing(100)
        layout.addLayout(chooseLayout)
        layout.addSpacing(155)
        layout.addLayout(statusPinLayout)
        layout.addLayout(self.make_button_layout("Back", self.go_back_page))

        widget.setLayout(layout)

        return widget

    def text_changed(self, s): # s is a str
        self.__selectedPin = int(s)


    def setup_pwm(self):
        from machine import PWM
        from machine import Pin

        pwm = PWM(Pin(self.__selectedPin), freq=50, duty_u16=8192)
        return pwm

    def pwm_text_changed(self, s): # s is a str
        self.__selectedPin = int(s)
        self.__pwm = self.board.def_function(self.setup_pwm)(self.__selectedPin)
        self.__pwm.init(freq=5000, duty_ns=5000)
        self.__pwm.duty_ns = 1000


    def make_pwm_page(self):
        widget = QWidget()
        layout = QVBoxLayout()

        chooseLayout = QHBoxLayout()
        chooseLabel = QLabel("Choose an Analog PIN:")
        chooseLabel.setStyleSheet("font: 20px;")

        Hlayout = QHBoxLayout()
        pwmLabel = QLabel("Drag the slider to set the PIN Brightness!")
        pwmLabel.setStyleSheet("font: 20px;")
        Hlayout.addSpacing(130)
        Hlayout.addWidget(pwmLabel)

        pwmLayout = QHBoxLayout()
        pwmSlider = QSlider(Qt.Orientation.Horizontal)

        pwmSlider.setMinimum(0)
        pwmSlider.setMaximum(65000)

        pwmSlider.valueChanged.connect(self.pwm_set_value)

        pins = QComboBox()
        pins.addItems(["27","28","29"])

        pins.currentTextChanged.connect( self.pwm_text_changed )

        chooseLayout.addWidget(chooseLabel)
        chooseLayout.addWidget(pins)

        pwmLayout.addSpacing(200)
        pwmLayout.addWidget(pwmSlider)
        pwmLayout.addSpacing(200)

        layout.addLayout(self.make_title_layout())
        layout.addSpacing(100)
        layout.addLayout(chooseLayout)
        layout.addSpacing(87)
        layout.addLayout(Hlayout)
        layout.addLayout(pwmLayout)
        layout.addLayout(self.make_button_layout("Back", self.go_back_page))

        widget.setLayout(layout)


        self.__pwm = self.board.def_function(self.setup_pwm)(self.__selectedPin)
        self.__pwm.init(freq=5000, duty_ns=5000)
        self.__pwm.duty_ns = 1000

        return widget



    def pwm_set_value(self,i):
        self.__pwm.duty_u16(i)

app = QApplication(sys.argv)
w = MainWindow()
apply_stylesheet(app,theme='dark_blue.xml')
w.show()
app.exec()
