from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QObject, QIODevice, QThread, QTimer
from PyQt5.QtWidgets import QApplication
import sys
from modbus_RTU import CRC
from modbus_send import ModbusSender, Serial_Qthread_function, SerialThread, modbus_RTU, last_frame, wait_for_last_frame
from modbus_receive import tUartParms, InitModBus, ModBusFlag_Slave, ModBus_Rcv_Callback, ModBusCheck
from modbus_receive import EnFlagTrue, Frame_OK, ADDR_err, CRC_err, Frame_broken
from modbus_receive import Modbus_receive_Interface

# 接受帧内容的全局变量
RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, function_name = 0, 0, 0, [], 0, ""
# 保存接收到的帧数据(字典形式,即所有功能函数执行完，解包完，分析完后的数据结果，方便给qt界面展示)
all_data_dict = {}

# ------------------- modbus_query -------------------
def modbus_query(slave_addr, func_ID, start_addr, quantity):
    """    执行Modbus查询操作
    :param slave_addr: 从站地址 
    :param func_ID: 功能码
    :param start_addr: 起始地址
    :param quantity: 读取或写入的数量
    :return: 返回接收到的Modbus RTU帧的十六进制字符串（hex_str）
    例如：modbus_query(1, 3, 0, 10)         # 从地址1读取10个保持寄存器
    例如：modbus_query(1, 5, 0, 1)          # 向地址1写入单个线圈
    例如：modbus_query(1, 6, 0, 12345）     # 向地址1写入单个寄存器，值为12345
    """
    sender = ModbusSender()
    if func_ID == 1:
        data = sender.read_coils(slave_addr, start_addr, quantity)
    elif func_ID == 2:
        data = sender.read_discrete_inputs(slave_addr, start_addr, quantity)
    elif func_ID == 3:
        data = sender.read_holding_registers(slave_addr, start_addr, quantity)
    elif func_ID == 4:
        data = sender.read_input_registers(slave_addr, start_addr, quantity)
    elif func_ID == 5:
        data = sender.write_single_coil(slave_addr, start_addr, quantity)
    elif func_ID == 6:
        data = sender.write_single_register(slave_addr, start_addr, quantity)
    elif func_ID == 8:
        data = sender.diagnostic(slave_addr, start_addr, quantity)
    elif func_ID == 15:
        data = sender.write_multiple_coils(slave_addr, start_addr, quantity, [1] * quantity)
    elif func_ID == 16:
        data = sender.write_multiple_registers(slave_addr, start_addr, quantity, [1] * quantity)
    else:
        print("未知功能码")
        return None

    parameter = {'data': modbus_RTU(data)}
    serial_obj.signal_SendData.emit(parameter)

    # ✅ 不分从站地址，统一等待接收（带超时）
    hex_str = wait_for_last_frame(serial_obj, timeout_ms=2000)
    print("最终帧(hex字符串):", hex_str)

    return hex_str


def on_frame_received(frame: bytes):
    """    接收到完整的Modbus RTU帧时的回调函数
    :param frame: 接收到的Modbus RTU帧数据"""

    print("主线程收到完整帧:", frame.hex())
    return frame  # 可以在这里处理接收到的帧数据

# ------------------- 所有集群读取功能函数 -------------------
def read_coils_0_6(): return modbus_query(1, 1, 3, 6)                  # 一次性从PLC（地址1）读取0-13号线圈，返回modbus查询帧
def read_coils_16_24(): return modbus_query(1, 1, 16, 10)               # 一次性从PLC（地址1）读取16-24号线圈，返回modbus查询帧
def read_coils_27_31(): return modbus_query(1, 1, 27, 5)                # 一次性从PLC（地址1）读取27-31号线圈，返回modbus查询帧
def read_holding_registers_0_13(): return modbus_query(1, 3, 0, 10)     # 一次性从PLC（地址1）读取0-13号保持寄存器，返回modbus查询帧
def read_holding_registers_16_24(): return modbus_query(1, 3, 16, 9)    # 一次性从PLC（地址1）读取16-24号保持寄存器，返回modbus查询帧
def read_holding_registers_32_39(): return modbus_query(1, 3, 32, 8)    # 一次性从PLC（地址1）读取32-39号保持寄存器，返回modbus查询帧

# ------------------- 保存最终结果（为qt界面留存数据读取的API） -------------------
def save_frame_data():
    """    保存接收到的帧数据到全局变量
    :param frame: 接收到的Modbus RTU帧数据"""
    global RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, function_name, all_data_dict
    # 保存当前函数的接收数据到字典
    all_data_dict[function_name] = {
            'RxAddr': RxAddr,
            'RxFuncID': RxFuncID,
            'RxDataLen': RxDataLen,
            'RxData': RxData,
            'Mdbs_state': Mdbs_state
        }

# ------------------- 串行执行控制 -------------------
def run_queries_in_sequence(functions, index=0):
    """    依次执行所有查询PLC和传感器的功能函数
    :param functions: 函数列表
    :param index: 当前执行的函数索引
    """
    global RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, function_name
    if index >= len(functions):
        print("所有查询执行完成")
        QTimer.singleShot(1000, app.quit)
        return

    func = functions[index]
    print(f"执行第 {index+1} 个函数: {func.__name__}")
    rcv_hex_str = func()

    if not rcv_hex_str:
        print("未收到有效响应（超时或无数据），跳过解析。")
        print("--------------------------------------------------------------------------------------------------------------------------------------------------")
        QTimer.singleShot(1000, lambda: run_queries_in_sequence(functions, index+1))
        return  # ✅ 直接返回，不再执行后面的解析

    RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT = Modbus_receive_Interface(rcv_hex_str)
    function_name = func.__name__

    if Mdbs_state & Frame_OK:
        print(f"解析结果 - 地址: {RxAddr}, 功能码: {RxFuncID}, 数据长度: {RxDataLen}, 数据: {RxData}, 状态: {Mdbs_state}, 计数: {MdbsCNT}")
        save_frame_data()
    else:
        print("无效帧，无法解析！！")

    print("--------------------------------------------------------------------------------------------------------------------------------------------------")
    QTimer.singleShot(3000, lambda: run_queries_in_sequence(functions, index+1))


# ------------------- 主程序 -------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    serial_obj = Serial_Qthread_function()
    thread = SerialThread(serial_obj)
    serial_obj.moveToThread(thread)
    serial_obj.signal_pushButton_Open.connect(serial_obj.slot_pushButton_Open)
    serial_obj.signal_SendData.connect(serial_obj.slot_SendData)
    rcv_frame = serial_obj.signal_frameReceived.connect(on_frame_received)
    thread.start()

    # ✅ 只在这里打开一次串口
    open_param = {
        'PortName_master': 'COM5',
        'BaudRate_master': 9600,
        'data': b''  # 这里先传空，不发送
    }
    serial_obj.signal_pushButton_Open.emit(open_param)
    # funcs = [read_coils_0_8]

    funcs = [read_holding_registers_0_13]

    run_queries_in_sequence(funcs)
    sys.exit(app.exec_())