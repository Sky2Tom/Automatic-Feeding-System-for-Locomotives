# -*- coding: utf-8 -*-
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QObject, QIODevice

 
class Serial_Qthread_function(QObject):

    signal_Serial_qthread_function_Init = pyqtSignal()
    signal_pushButton_Open           = pyqtSignal(object)
    signal_pushButton_Open_flage     = pyqtSignal(object)
    signal_readyRead                 = pyqtSignal(object)
    signal_SendData                  = pyqtSignal(object)

    def __init__(self):
        super(Serial_Qthread_function,self).__init__()
        self.state = 0 #0未打开，1已打开
    
    def slot_pushButton_Open(self,paremeter):
        if self.state == 0:
            print("打开:",paremeter)
            self.serial_master.setPortName(paremeter['PortName_master'])
            self.serial_master.setBaudRate(paremeter['BaudRate_master'])
            self.serial_master.setDataBits(QSerialPort.Data8)  # 设置数据位
            self.serial_master.setParity(QSerialPort.NoParity)  # 设置校验位
            self.serial_master.setStopBits(QSerialPort.OneStop)  # 设置停止位
            self.serial_master.open(QIODevice.ReadWrite)

        elif self.state != 0:
            self.serial_master.close()
        
        if self.serial_master.isOpen():
            self.state = 1
            self.signal_pushButton_Open_flage.emit(1)
        else:
            self.state = 0
            self.signal_pushButton_Open_flage.emit(2)
    
    def slot_SendData(self,parameter):
        if self.state != 1:
            return
        self.serial_master.write(parameter['data'])
    
    def slot_readyRead(self): 
        buf = self.serial_master.readAll()
        data = {}
        data['buf']  = buf
        self.signal_readyRead.emit(data)
    
    def handleError(self,error): # 处理异常
        if error == QSerialPort.PermissionError:
            print("串口已被占用！")
        elif error == QSerialPort.DeviceNotFoundError:
            print("串口不存在！")
        elif error == QSerialPort.ResourceError:
            print("串口异常退出！")
            self.signal_pushButton_Open_flage.emit(2)

    def Serial_qthread_function_Init(self):
        self.serial_master = QSerialPort()
        self.serial_master.readyRead.connect(self.slot_readyRead)
        self.serial_master.errorOccurred.connect(self.handleError)

if __name__ == "__main__":
    ser = Serial_Qthread_function()
    ser.Serial_qthread_function_Init()
    paremeter = {'PortName_master':'COM1','BaudRate_master':9600}
    ser.slot_pushButton_Open(paremeter)
