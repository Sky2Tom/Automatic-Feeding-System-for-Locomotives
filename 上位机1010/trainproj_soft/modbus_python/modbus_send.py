#-----------------------------------------------------发送modbus帧-------------------------------------------------------------
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


class ModbusSender(QObject):
    """
    Modbus RTU 主站发送功能模块
    修复进程无响应问题，保持所有功能完整
    """
    frame_constructed = pyqtSignal(bytes)
    
    def __init__(self):
        super().__init__()
        self.crc_calculator = CRC()
    
    def build_modbus_frame(self, slave_addr, func_code, data=None):
        """构造Modbus RTU帧（保持原有功能）"""
        frame = bytearray()
        frame.append(slave_addr)
        frame.append(func_code)
        
        if data is not None:
            if isinstance(data, bytes):
                frame.extend(data)
            else:
                frame.extend(bytes(data))
        
        hex_str = ' '.join(f'{b:02x}' for b in frame)
        # crc_str, _, _ = self.crc_calculator.CRC16(hex_str)
        # crc_int = int(crc_str, 16)
        
        # frame.append(crc_int & 0xFF)
        # frame.append((crc_int >> 8) & 0xFF)
        
        return hex_str
    
    # ---------------------------- 保留原有功能码封装 ----------------------------
    def read_coils(self, slave_addr, start_addr, quantity):
        """
        读取线圈状态 (功能码 0x01)
        :param slave_addr: 从站地址
        :param start_addr: 起始地址
        :param quantity: 读取数量 (1-2000)
        :return: 构造的帧
        """
        if quantity < 1 or quantity > 2000:
            raise ValueError("Quantity must be between 1 and 2000")
        
        data = [
            (start_addr >> 8) & 0xFF,  # 起始地址高字节
            start_addr & 0xFF,         # 起始地址低字节
            (quantity >> 8) & 0xFF,    # 数量高字节
            quantity & 0xFF            # 数量低字节
        ]
        return self.build_modbus_frame(slave_addr, 0x01, data)
    
    def read_discrete_inputs(self, slave_addr, start_addr, quantity):
        """
        读取离散输入 (功能码 0x02)
        :param slave_addr: 从站地址
        :param start_addr: 起始地址
        :param quantity: 读取数量 (1-2000)
        """
        if quantity < 1 or quantity > 2000:
            raise ValueError("Quantity must be between 1 and 2000")
        
        data = [
            (start_addr >> 8) & 0xFF,
            start_addr & 0xFF,
            (quantity >> 8) & 0xFF,
            quantity & 0xFF
        ]
        return self.build_modbus_frame(slave_addr, 0x02, data)

    def read_holding_registers(self, slave_addr, start_addr, quantity):
        """
        读取保持寄存器 (功能码 0x03)
        :param slave_addr: 从站地址
        :param start_addr: 起始地址
        :param quantity: 读取数量 (1-125)
        :return: 构造的帧
        """
        if quantity < 1 or quantity > 125:
            raise ValueError("Quantity must be between 1 and 125")
        
        data = [
            (start_addr >> 8) & 0xFF,
            start_addr & 0xFF,
            (quantity >> 8) & 0xFF,
            quantity & 0xFF
        ]
        return self.build_modbus_frame(slave_addr, 0x03, data)

    def read_input_registers(self, slave_addr, start_addr, quantity):
        """
        读取输入寄存器 (功能码 0x04)
        :param slave_addr: 从站地址
        :param start_addr: 起始地址
        :param quantity: 读取数量 (1-125)
        """
        if quantity < 1 or quantity > 125:
            raise ValueError("Quantity must be between 1 and 125")
        
        data = [
            (start_addr >> 8) & 0xFF,
            start_addr & 0xFF,
            (quantity >> 8) & 0xFF,
            quantity & 0xFF
        ]
        return self.build_modbus_frame(slave_addr, 0x04, data)

    def write_single_coil(self, slave_addr, output_addr, output_value):
        """
        写单个线圈 (功能码 0x05)
        :param slave_addr: 从站地址
        :param output_addr: 输出地址
        :param output_value: 输出值(0x0000=OFF, 0xFF00=ON)
        """
        data = [
            (output_addr >> 8) & 0xFF,
            output_addr & 0xFF,
            (output_value >> 8) & 0xFF,
            output_value & 0xFF
        ]
        return self.build_modbus_frame(slave_addr, 0x05, data)

    def write_single_register(self, slave_addr, register_addr, register_value):
        """
        写单个寄存器 (功能码 0x06)
        :param slave_addr: 从站地址
        :param register_addr: 寄存器地址
        :param register_value: 寄存器值
        """
        data = [
            (register_addr >> 8) & 0xFF,
            register_addr & 0xFF,
            (register_value >> 8) & 0xFF,
            register_value & 0xFF
        ]
        return self.build_modbus_frame(slave_addr, 0x06, data)

    def write_multiple_coils(self, slave_addr, start_addr, quantity, values):
        """
        写多个线圈 (功能码 15/0x0F)
        :param slave_addr: 从站地址
        :param start_addr: 起始地址
        :param quantity: 线圈数量(1-1968)
        :param values: 线圈值列表(每个字节包含8个线圈状态)
        """
        if quantity < 1 or quantity > 1968:
            raise ValueError("Quantity must be between 1 and 1968")
        
        byte_count = (quantity + 7) // 8
        if len(values) != byte_count:
            raise ValueError("Values length doesn't match quantity")
        
        data = [
            (start_addr >> 8) & 0xFF,
            start_addr & 0xFF,
            (quantity >> 8) & 0xFF,
            quantity & 0xFF,
            byte_count
        ]
        data.extend(values)
        return self.build_modbus_frame(slave_addr, 0x0F, data)

    def write_multiple_registers(self, slave_addr, start_addr, quantity, values):
        """
        写多个寄存器 (功能码 16/0x10)
        :param slave_addr: 从站地址
        :param start_addr: 起始地址
        :param quantity: 寄存器数量(1-123)
        :param values: 寄存器值列表(每个寄存器2字节)
        """
        if quantity < 1 or quantity > 123:
            raise ValueError("Quantity must be between 1 and 123")
        
        byte_count = quantity * 2
        if len(values) != quantity:
            raise ValueError("Values length doesn't match quantity")
        
        data = [
            (start_addr >> 8) & 0xFF,
            start_addr & 0xFF,
            (quantity >> 8) & 0xFF,
            quantity & 0xFF,
            byte_count
        ]
        # 将寄存器值填充到数据区
        for value in values:
            data.append((value >> 8) & 0xFF)
            data.append(value & 0xFF)
        return self.build_modbus_frame(slave_addr, 0x10, data)


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

    #构造帧
    sender = ModbusSender()
    data = sender.read_holding_registers(
                slave_addr=4,
                start_addr=21,
                quantity=2
            )
 
    """data = sender.write_single_register(
                slave_addr=1 , 
                register_addr=8 , 
                register_value=233
            )"""
    
    # 创建测试参数
    parameter = {
        'PortName_master': 'COM5',
        'BaudRate_master': 9600,
        'data': ''
    }
    parameter['data'] = data  # 使用构造的帧数据
    parameter['data'] = modbus_RTU(parameter['data']) #构造CRC校验码
    
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