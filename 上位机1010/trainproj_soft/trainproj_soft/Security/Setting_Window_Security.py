# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QDialog,QApplication
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtSerialPort import QSerialPortInfo
from UI import connect_setting_Security


class SettingForm(QDialog):
    def __init__(self, button_value,serial_channel):
        super().__init__()
        self.ui = connect_setting_Security.Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("./Picture/logo.ico"))
        self.button_value = button_value
        self.serial_channel = serial_channel
        self.UI_Init()
        self.setButtonValue()

    def UI_Init(self):
        self.SerialInfo = [0, 0, 0, 0]
        self.ui.pushButton_1.clicked.connect(self.pushButton_1) # 确认按键
        if self.serial_channel == 1:
            self.ui.label_3.setVisible(False)
            self.ui.label_4.setVisible(False)
            self.ui.comboBox_3.setVisible(False)
            self.ui.comboBox_4.setVisible(False)

    def setButtonValue(self):
        print(self.button_value)
        if self.button_value == 'button_1':
            # 读取上一次保存的串口信息
            settings = QSettings("config_Security.ini", QSettings.IniFormat)
            self.SerialInfo[0] = settings.value("Security_serial/master_PortName_1")
            self.SerialInfo[1] = settings.value("Security_serial/master_BaudRate_1")
            if self.serial_channel == 2:
                self.SerialInfo[2] = settings.value("Security_serial/slave_PortName")
                self.SerialInfo[3] = settings.value("Security_serial/slave_BaudRate")
            self.serial_info(self.SerialInfo)
        elif self.button_value == 'button_2':
            # 读取上一次保存的串口信息
            settings = QSettings("config_Security.ini", QSettings.IniFormat)
            self.SerialInfo[0] = settings.value("Security_serial/master_PortName_2")
            self.SerialInfo[1] = settings.value("Security_serial/master_BaudRate_2")
            if self.serial_channel == 2:
                self.SerialInfo[2] = settings.value("Security_serial/slave_PortName")
                self.SerialInfo[3] = settings.value("Security_serial/slave_BaudRate")
            self.serial_info(self.SerialInfo)
        elif self.button_value == 'button_3':
            # 读取上一次保存的串口信息
            settings = QSettings("config_Security.ini", QSettings.IniFormat)
            self.SerialInfo[0] = settings.value("Security_serial/master_PortName_3")
            self.SerialInfo[1] = settings.value("Security_serial/master_BaudRate_3")
            if self.serial_channel == 2:
                self.SerialInfo[2] = settings.value("Security_serial/slave_PortName")
                self.SerialInfo[3] = settings.value("Security_serial/slave_BaudRate")
            self.serial_info(self.SerialInfo)
        elif self.button_value == 'button_4':
            # 读取上一次保存的串口信息
            settings = QSettings("config_Security.ini", QSettings.IniFormat)
            self.SerialInfo[0] = settings.value("Security_serial/master_PortName_4")
            self.SerialInfo[1] = settings.value("Security_serial/master_BaudRate_4")
            if self.serial_channel == 2:
                self.SerialInfo[2] = settings.value("Security_serial/slave_PortName")
                self.SerialInfo[3] = settings.value("Security_serial/slave_BaudRate")
            self.serial_info(self.SerialInfo)
    
    def pushButton_1(self): # 确认按键
        channel = self.button_value[-1]
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        settings.setValue("Security_serial/master_PortName_" + channel, self.ui.comboBox_1.currentText())
        settings.setValue("Security_serial/master_BaudRate_" + channel, self.ui.comboBox_2.currentText())
        if self.serial_channel == 2:
            settings.setValue("Security_serial/slave_PortName", self.ui.comboBox_3.currentText())
            settings.setValue("Security_serial/slave_BaudRate", self.ui.comboBox_4.currentText())
        del settings
        self.close()
    
    # 添加串口信息
    def serial_info(self, serial_list):
        print(serial_list)
        port_list = QSerialPortInfo.availablePorts()
        port_list = [obj.portName() for obj in port_list]
        self.ui.comboBox_1.clear()
        if self.serial_channel == 2:
            self.ui.comboBox_3.clear()
        
        for port_info in port_list:
            self.ui.comboBox_1.addItem(port_info)
            if self.serial_channel == 2:
                self.ui.comboBox_3.addItem(port_info)
        self.ui.comboBox_1.addItem(" ")
        if self.serial_channel == 2:
            self.ui.comboBox_3.addItem(" ")

        if serial_list[0] in port_list:
            self.ui.comboBox_1.setCurrentText(serial_list[0])
        else:
            self.ui.comboBox_1.setCurrentText(" ")
        if self.serial_channel == 2:
            if serial_list[2] in port_list:
                self.ui.comboBox_3.setCurrentText(serial_list[2])
            else:
                self.ui.comboBox_3.setCurrentText(" ")
        if serial_list[1] in ['9600','115200']:
            self.ui.comboBox_2.setCurrentText(serial_list[1])
        if self.serial_channel == 2:
            if serial_list[3] in ['9600','115200']:
                self.ui.comboBox_4.setCurrentText(serial_list[3])
            
    def closeEvent(self, event):
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingForm('button_4',2)
    window.show()
    sys.exit(app.exec_())