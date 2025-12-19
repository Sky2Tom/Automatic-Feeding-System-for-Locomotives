# -*- coding: utf-8 -*-
from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QObject, QIODevice, QThread
from PyQt5.QtWidgets import QApplication
import sys
from PyQt5.QtCore import QTimer
from modbus_RTU import CRC

class Serial_Qthread_function(QObject):
    signal_Serial_qthread_function_Init = pyqtSignal()
    signal_pushButton_Open = pyqtSignal(object)
    signal_pushButton_Open_flage = pyqtSignal(object)
    signal_readyRead = pyqtSignal(object)
    signal_SendData = pyqtSignal(object)

    def __init__(self):
        super(Serial_Qthread_function, self).__init__()
        self.state = 0  # 0未打开，1已打开
        self.serial_master = None
        
    def init_serial(self):
        """在线程中初始化串口"""
        self.serial_master = QSerialPort()
        self.serial_master.readyRead.connect(self.slot_readyRead)
        self.serial_master.errorOccurred.connect(self.handleError)
        print("串口初始化完成")

    def slot_pushButton_Open(self, paremeter):
        if self.state == 0:
            print("尝试打开串口:", paremeter)
            if not self.serial_master:
                self.init_serial()
                
            self.serial_master.setPortName(paremeter['PortName_master'])
            self.serial_master.setBaudRate(paremeter['BaudRate_master'])
            self.serial_master.setDataBits(QSerialPort.Data8)  # 设置数据位
            self.serial_master.setParity(QSerialPort.NoParity)  # 设置校验位
            self.serial_master.setStopBits(QSerialPort.OneStop)  # 设置停止位
            
            if not self.serial_master.open(QIODevice.ReadWrite):
                self.handleError(self.serial_master.error())
                return

        elif self.state == 1:
            print("关闭串口")
            self.serial_master.close()
            self.state = 0
            self.signal_pushButton_Open_flage.emit(2)
            return

        if self.serial_master.isOpen():
            self.state = 1
            self.signal_pushButton_Open_flage.emit(1)
            print(f"串口 {paremeter['PortName_master']} 已成功打开")
        else:
            self.state = 0
            self.signal_pushButton_Open_flage.emit(2)
            print(f"串口 {paremeter['PortName_master']} 打开失败")

    def slot_SendData(self, parameter):
        if self.state != 1 or not self.serial_master:
            print("尝试发送数据但串口未打开")
            return
        data_to_send = parameter['data']
        bytes_written = self.serial_master.write(data_to_send)
        print(f"发送数据: {data_to_send.hex()} (共 {bytes_written} 字节)")

    def slot_readyRead(self):
        if not self.serial_master:
            return
        buf = self.serial_master.readAll()
        if buf.size() > 0:
            data = {'buf': buf}
            self.signal_readyRead.emit(data)
            print(f"收到数据: {bytes(buf.data()).hex()}")

    def handleError(self, error):  # 处理异常
        if error == QSerialPort.PermissionError:
            print("串口已被占用！")
        elif error == QSerialPort.DeviceNotFoundError:
            print("串口不存在！")
        elif error == QSerialPort.ResourceError:
            print("串口异常退出！")
        self.signal_pushButton_Open_flage.emit(2)
        self.state = 0


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

def shutdown():
    print("准备关闭程序...")
    thread.stop()
    app.quit()

def modbus_RTU(sendbytes):
    # 生成CRC16校验码
    CRC_obj = CRC()
    crc, crc_H, crc_L = CRC_obj.CRC16(sendbytes)

    # 生成完整报文（字符串）
    send_str = sendbytes + ' ' + crc_L + ' ' + crc_H  # 如 "01 03 00 08 00 05 04 b0"
    
    # 将字符串转为 bytes
    hex_list = send_str.split()  # 分割成 ['01', '03', '00', '08', '00', '05', '04', 'b0']
    byte_data = bytes.fromhex(''.join(hex_list))  # 转为 b'\x01\x03\x00\x08\x00\x05\x04\xb0'
    
    return byte_data

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
        'PortName_master': 'COM5',
        'BaudRate_master': 9600,

        'data': '04 03 00 15 00 02'
    }
    parameter['data'] = modbus_RTU(parameter['data'])
    
    # 通过信号触发串口操作（确保操作在正确线程执行）
    serial_obj.signal_pushButton_Open.emit(parameter)
       
    # 发送测试数据
    serial_obj.signal_SendData.emit({'data': parameter['data']})

    # 设置定时器来关闭程序
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(shutdown)
    timer.start(3000)  # 3秒后关闭

    # 退出应用程序
    sys.exit(app.exec_())