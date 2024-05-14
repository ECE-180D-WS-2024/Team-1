from glwidget import GLWidget
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QGridLayout
from PyQt5 import QtWidgets
from PyQt5 import QtCore

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.resize(300, 300)
        self.setWindowTitle("Hello OpenGL App")

        self.glWidget = GLWidget(self)
        self.initGUI()

        timer = QtCore.QTimer(self)
        timer.setInterval(int((1 / 60) * 1000))
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()

    def initGUI(self):
        central_widget = QtWidgets.QWidget()
        gui_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(gui_layout)

        self.setCentralWidget(central_widget)

        gui_layout.addWidget(self.glWidget)
        buttonGrid = QGridLayout(self)
        
        btnRotXPos = QPushButton("Rotate +X", self)
        btnRotXPos.clicked.connect(lambda: self.glWidget.rotateXPositive())
        btnRotXNeg = QPushButton("Rotate -X", self)
        btnRotXNeg.clicked.connect(lambda: self.glWidget.rotateXNegative())

        btnRotYPos = QPushButton("Rotate +Y", self)
        btnRotYPos.clicked.connect(lambda: self.glWidget.rotateYPositive())
        btnRotYNeg = QPushButton("Rotate -Y", self)
        btnRotYNeg.clicked.connect(lambda: self.glWidget.rotateYNegative())

        btnRotZPos = QPushButton("Rotate +Z", self)
        btnRotZPos.clicked.connect(lambda: self.glWidget.rotateZPositive())
        btnRotZNeg = QPushButton("Rotate -Z", self)
        btnRotZNeg.clicked.connect(lambda: self.glWidget.rotateZNegative())

        buttonGrid.addWidget(btnRotXPos, 0, 0)
        buttonGrid.addWidget(btnRotXNeg, 0, 1)

        buttonGrid.addWidget(btnRotYPos, 1, 0)
        buttonGrid.addWidget(btnRotYNeg, 1, 1)

        buttonGrid.addWidget(btnRotZPos, 2, 0)
        buttonGrid.addWidget(btnRotZNeg, 2, 1)

        """ sliderX = QSlider(QtCore.Qt.Horizontal)
        sliderX.valueChanged.connect(lambda val: self.glWidget.setRotX(val))

        sliderY = QSlider(QtCore.Qt.Horizontal)
        sliderY.valueChanged.connect(lambda val: self.glWidget.setRotY(val))

        sliderZ = QSlider(QtCore.Qt.Horizontal)
        sliderZ.valueChanged.connect(lambda val: self.glWidget.setRotZ(val)) """

        gui_layout.addLayout(buttonGrid)
        """ gui_layout.addWidget(sliderY) """
        """ gui_layout.addWidget(sliderZ) """

if __name__ == '__main__':
    app = QApplication(sys.argv)

    win = MainWindow()
    win.show()

    sys.exit(app.exec_())