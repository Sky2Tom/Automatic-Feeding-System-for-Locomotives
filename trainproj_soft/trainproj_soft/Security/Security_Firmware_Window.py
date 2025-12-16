# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QDialog,QApplication
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
import sys
from UI import firmware_setting_Security



class firmwaresetting(QDialog):
    def __init__(self, button):
        super().__init__()
        self.ui = firmware_setting_Security.Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("./Picture/logo.ico"))

        self.button = button
        self.UI_Init()

    def UI_Init(self):
        self.FirmInfo = ['','']
        self.ui.pushButton_1.clicked.connect(self.pushButton_1) # 确认按键

        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        if self.button == 'button_firm_1':
            self.FirmInfo[0] = settings.value("Security_firmware/firmName")
            self.FirmInfo[1] = settings.value("Security_firmware/firmVer")
        del settings

        if self.FirmInfo[0] is not None and self.FirmInfo[1] is not None:
            self.ui.lineEdit_1.setText(self.FirmInfo[0])
            self.ui.lineEdit_2.setText(self.FirmInfo[1])
    
    def pushButton_1(self):
        self.FirmInfo[0] = self.ui.lineEdit_1.text()
        self.FirmInfo[1] = self.ui.lineEdit_2.text()
        # 保存最新输入的固件信息
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        if self.button == 'button_firm_1':
            settings.setValue("Security_firmware/firmName", self.FirmInfo[0])
            settings.setValue("Security_firmware/firmVer", self.FirmInfo[1])
        del settings
        self.close()
    
    def closeEvent(self, event):
        event.accept()
    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = firmwaresetting('button_firm_1')
    window.show()
    sys.exit(app.exec_())