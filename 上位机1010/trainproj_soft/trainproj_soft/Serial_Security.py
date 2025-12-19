# -*- coding: utf-8 -*-
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QObject, QIODevice, QThread
from PyQt5.QtWidgets import QApplication
import sys

 
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
        #self.serial_master.errorOccurred.connect(self.handleErrorclear)
        self.serial_master.errorOccurred.connect(self.handleError)

class SerialThread(QThread):
    def __init__(self, serial_obj):
        super().__init__()
        self.serial = serial_obj
        
    def run(self):
        print("串口线程启动")
        # 启动事件循环
        self.exec_()
        
    def stop(self):
        self.quit()
        self.wait()

"""if __name__ == "__main__":
    ser = Serial_Qthread_function()
    ser.Serial_qthread_function_Init()
    paremeter = {'PortName_master':'COM4','BaudRate_master':9600,'data': b'\x01\x03\x00\x08\x00\x05\x04\x0B' }
    ser.slot_pushButton_Open(paremeter)
    ser.slot_SendData(paremeter)"""


if __name__ == "__main__":
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 创建串口对象和线程
    serial_obj = Serial_Qthread_function()
    thread = SerialThread(serial_obj)
    
    # 将串口对象移动到新线程
    serial_obj.moveToThread(thread)
    
    # 连接信号
    serial_obj.signal_pushButton_Open.connect(serial_obj.slot_pushButton_Open)
    serial_obj.signal_SendData.connect(serial_obj.slot_SendData)
    
    # 启动线程
    thread.start()
    
    # 创建测试参数
    parameter = {
        'PortName_master': 'COM4',
        'BaudRate_master': 9600,
        'data': b'\x01\x03\x00\x08\x00\x05\x04\x0B'
    }
    
    # 通过信号触发串口操作（确保操作在正确线程执行）
    serial_obj.signal_pushButton_Open.emit(parameter)
    
    # 稍等一会儿，确保串口已打开
    import time
    time.sleep(1)
    
    # 发送测试数据
    serial_obj.signal_SendData.emit({'data': parameter['data']})
    
    # 等待一段时间后停止线程
    time.sleep(3)
    thread.stop()
    
    # 退出应用程序
    sys.exit(app.exec_())