from PyQt5.QtSerialPort import QSerialPort
from PyQt5.QtCore import pyqtSignal, QObject, QIODevice, QThread, QTimer
from PyQt5.QtWidgets import QApplication
import sys
from modbus_RTU import CRC
from modbus_send import ModbusSender, Serial_Qthread_function, SerialThread, modbus_RTU, last_frame, wait_for_last_frame
from modbus_receive import tUartParms, InitModBus, ModBusFlag_Slave, ModBus_Rcv_Callback, ModBusCheck
from modbus_receive import EnFlagTrue, Frame_OK, ADDR_err, CRC_err, Frame_broken
from modbus_receive import Modbus_receive_Interface

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

# ------------------- 所有功能函数 -------------------
def transaction_status_query(): return modbus_query(1, 1, 2, 1)     # 问PLC：牵引车状态是什么？
def warehouse_number(): print("仓库编号固定"); return 0              # 仓库编号固定
def operater_name(): print("操作员来自数据库"); return 0             # 操作员名称来自数据库
def train_ID(): print("火车型号来自视觉系统"); return 0               # 火车型号来自视觉系统
def machine_status(): return modbus_query(1, 1, 5, 1)               # 问PLC：下料机状态是什么？
def valve_open_angel(): return modbus_query(1, 3, 19, 1)            # 问PLC：阀门开启角度是多少？
def Lifting_height(): return modbus_query(1, 3, 20, 1)              # 问PLC：升降高度是多少？
def Flip_plate_height(): return modbus_query(1, 3, 21, 1)           # 问PLC：翻板高度是多少？
def Full_ornot(): return modbus_query(1, 1, 6, 1)                   # 问PLC：煤炭是否满载？
def Load_progress(): return modbus_query(3, 3, 18, 1)               # 问PLC：装载进度是多少？
def Coal_height(): return modbus_query(3, 3, 18, 1)                 # 问PLC：煤堆高度是多少？
def Liaoweiji(): return modbus_query(3, 3, 4118, 1)                 # 问PLC：煤堆高度是多少？
# ------------------- 串行执行控制 -------------------
def run_queries_in_sequence(functions, index=0):
    """    依次执行所有查询PLC和传感器的功能函数
    :param functions: 函数列表
    :param index: 当前执行的函数索引
    """
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

    if Mdbs_state & Frame_OK:
        print(f"解析结果 - 地址: {RxAddr}, 功能码: {RxFuncID}, 数据长度: {RxDataLen}, 数据: {RxData}, 状态: {Mdbs_state}, 计数: {MdbsCNT}")
    else:
        print("无效帧，无法解析！！")

    print("--------------------------------------------------------------------------------------------------------------------------------------------------")
    QTimer.singleShot(1000, lambda: run_queries_in_sequence(functions, index+1))


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
        'PortName_master': 'COM4',
        'BaudRate_master': 9600,
        'data': b''  # 这里先传空，不发送
    }
    serial_obj.signal_pushButton_Open.emit(open_param)

    funcs = [transaction_status_query, Coal_height, warehouse_number, operater_name,
             train_ID, machine_status, valve_open_angel, Lifting_height,
             Flip_plate_height, Full_ornot, Load_progress,Liaoweiji]

    run_queries_in_sequence(funcs)
    sys.exit(app.exec_())

