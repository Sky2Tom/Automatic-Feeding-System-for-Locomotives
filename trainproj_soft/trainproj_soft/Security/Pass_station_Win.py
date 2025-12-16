# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QDialog,QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from UI import Pass_station_Security

class Pass_station_setting(QDialog):
    pass_station_signal = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.ui = Pass_station_Security.Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("./Picture/logo.ico"))

        self.UI_Init()
    
    def UI_Init(self):
        self.ui.pushButton_1.clicked.connect(self.pushButton_1) # 确认按键
        self.ui.pushButton_2.clicked.connect(self.pushButton_2) # 取消按键

    def pushButton_1(self):
        self.pass_station_signal.emit(True)
        self.close()

    def pushButton_2(self):
        self.pass_station_signal.emit(False)
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Pass_station_setting()
    window.show()
    sys.exit(app.exec_())