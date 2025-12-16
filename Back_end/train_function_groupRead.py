from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QObject, QIODevice, QThread, QTimer
from PyQt5.QtWidgets import QApplication
import sys
from modbus_RTU import CRC
from modbus_send import ModbusSender, Serial_Qthread_function, SerialThread, modbus_RTU, last_frame, wait_for_last_frame
from modbus_receive import tUartParms, InitModBus, ModBusFlag_Slave, ModBus_Rcv_Callback, ModBusCheck
from modbus_receive import EnFlagTrue, Frame_OK, ADDR_err, CRC_err, Frame_broken
from modbus_receive import Modbus_receive_Interface
import time

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
def read_coils_0_13(): return modbus_query(1, 1, 0, 14)                  # 一次性从PLC（地址1）读取0-13号线圈，返回modbus查询帧
def read_coils_16_24(): return modbus_query(1, 1, 16, 10)               # 一次性从PLC（地址1）读取16-24号线圈，返回modbus查询帧
def read_coils_27_31(): return modbus_query(1, 1, 27, 5)                # 一次性从PLC（地址1）读取27-31号线圈，返回modbus查询帧
def read_holding_registers_0_13(): return modbus_query(1, 3, 0, 13)     # 一次性从PLC（地址1）读取0-13号保持寄存器，返回modbus查询帧
def read_holding_registers_16_24(): return modbus_query(1, 3, 16, 9)    # 一次性从PLC（地址1）读取16-24号保持寄存器，返回modbus查询帧
def read_holding_registers_32_39(): return modbus_query(1, 3, 32, 8)    # 一次性从PLC（地址1）读取32-39号保持寄存器，返回modbus查询帧
def read_coils_0_8(): return modbus_query(1, 1, 0, 8)                  # 一次性从PLC（地址1）读取0-7号线圈，返回modbus查询帧

# 接受帧内容的全局变量
RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, function_name = 0, 0, 0, [], 0, ""
# 保存接收到的帧数据(字典形式,即所有功能函数执行完，解包完，分析完后的数据结果，方便给qt界面展示)
all_data_dict = {}

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
# 间隔（毫秒）
CYCLE_INTERVAL_MS = 5000  # 每轮之间等 5 秒

def run_queries_in_sequence(functions, index=0):
    global RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, function_name
    if index >= len(functions):
        print("所有查询执行完成，本轮结束")
        print(f"等待 {CYCLE_INTERVAL_MS/1000} 秒，开始下一轮...\n" + "-"*100)
        QTimer.singleShot(CYCLE_INTERVAL_MS, lambda: run_queries_in_sequence(functions, 0))
        return

    func = functions[index]
    print(f"执行第 {index+1} 个函数: {func.__name__}")
    rcv_hex_str = func()

    if not rcv_hex_str:
        print("未收到有效响应（超时或无数据），跳过解析。")
        print("-" * 150)
        QTimer.singleShot(1000, lambda: run_queries_in_sequence(functions, index+1))
        return

    RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT = Modbus_receive_Interface(rcv_hex_str)
    function_name = func.__name__

    if Mdbs_state & Frame_OK:
        print(f"解析结果 - 地址: {RxAddr}, 功能码: {RxFuncID}, 数据长度: {RxDataLen}, 数据: {RxData}, 状态: {Mdbs_state}, 计数: {MdbsCNT}")
        save_frame_data()
    else:
        print("无效帧，无法解析！！")

    print("-" * 150)
    QTimer.singleShot(1000, lambda: run_queries_in_sequence(functions, index+1))  # 1秒间隔执行下一个


# ------------------- 新增：线程2接收被动帧的回调 -------------------
def on_passive_frame_received(frame: bytes):
    """
    线程2接收到外部主动发来的Modbus RTU帧时执行
    """
    hex_str = frame.hex()
    print("\n=== [被动监听 - 收到外部帧] ===")
    print("原始HEX:", hex_str)

    # 解析帧内容
    RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT = Modbus_receive_Interface(hex_str)

    if Mdbs_state & Frame_OK:
        print(f"解析结果 - 地址: {RxAddr}, 功能码: {RxFuncID}, 数据长度: {RxDataLen}, 数据: {RxData}")
    else:
        print("无效帧，无法解析！！")

    print("==============================\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 开线程1（主动查询）
    serial_obj = Serial_Qthread_function()
    thread = SerialThread(serial_obj)
    serial_obj.moveToThread(thread)
    serial_obj.signal_pushButton_Open.connect(serial_obj.slot_pushButton_Open)
    serial_obj.signal_SendData.connect(serial_obj.slot_SendData)
    serial_obj.signal_frameReceived.connect(on_frame_received)
    thread.start()

    # 开线程2（被动监听模式）
    serial_obj_2 = Serial_Qthread_function()
    thread_2 = SerialThread(serial_obj_2)
    serial_obj_2.moveToThread(thread_2)
    serial_obj_2.signal_pushButton_Open.connect(serial_obj_2.slot_pushButton_Open)
    serial_obj_2.signal_SendData.connect(serial_obj_2.slot_SendData)
    serial_obj_2.signal_frameReceived.connect(on_passive_frame_received)  # 被动监听
    thread_2.start()

    open_param = {
        'PortName_master': 'COM5',
        'BaudRate_master': 9600,
        'data': b''
    }
    serial_obj.signal_pushButton_Open.emit(open_param)

    open_param2 = {
        'PortName_master': 'COM20',
        'BaudRate_master': 9600,
        'data': b''  # 被动监听模式，不发送
    }
    serial_obj_2.signal_pushButton_Open.emit(open_param2)

    # -------------------------------------线程1功能执行--------------------------------------------------------
    funcs = [read_coils_0_8, read_coils_0_13, read_coils_16_24, read_coils_27_31,
             read_holding_registers_0_13, read_holding_registers_16_24, read_holding_registers_32_39]

    # 启动第一轮
    run_queries_in_sequence(funcs)

    sys.exit(app.exec_())

