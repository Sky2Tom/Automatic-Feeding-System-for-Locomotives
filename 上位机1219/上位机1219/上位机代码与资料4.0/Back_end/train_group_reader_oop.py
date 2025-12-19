# -*- coding: utf-8 -*-
"""
train_group_reader_oop.py
OOP 版“集群读取”脚本，保留原逻辑与节奏，新增：
1) 线程安全的全局数据仓库 SharedDataStore
2) 每次 query 后更新：
   - RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, function_name
   - all_data_dict[function_name] = 最终可展示的数据

依赖你现有项目中的模块：
- modbus_send.py（Serial_Qthread_function, SerialThread, ModbusSender, modbus_RTU, wait_for_last_frame）
- modbus_receive.py（Modbus_receive_Interface, Frame_OK）

作者：你
"""

import sys, time, threading
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread
from PyQt5.QtWidgets import QApplication

# === 复用你现有的发送/接收/构帧能力 ===
from modbus_send import (
    Serial_Qthread_function,
    SerialThread,
    ModbusSender,
    modbus_RTU,
    wait_for_last_frame,
)
from modbus_receive import (
    Modbus_receive_Interface,
    Frame_OK,
)

# ---------------------------------------------------------------------
# A) 线程安全的“全局”数据仓库（保持原全局变量语义，不改调用习惯）
# ---------------------------------------------------------------------
class SharedDataStore(QObject):
    """
    充当原来全局变量的“唯一真身”。对外暴露与原全局变量等价的字段名，
    并提供线程安全的更新/读取方法。
    """
    # 数据已更新信号：方便外部（例如 UI）订阅变化
    snapshotUpdated = pyqtSignal(dict)          # 推送全量快照
    oneFuncUpdated = pyqtSignal(str, dict)      # 推送某个功能函数的结果

    _instance = None
    _lock_inst = threading.Lock()

    def __init__(self):
        super().__init__()
        # === 原全局变量：接受帧内容 ===
        self.RxAddr = 0
        self.RxFuncID = 0
        self.RxDataLen = 0
        self.RxData = []
        self.Mdbs_state = 0
        self.function_name = ""
        # === 原全局变量：汇总展示用字典 ===
        self.all_data_dict = {}

        # 线程并发保护
        self._lock = threading.Lock()

    @classmethod
    def instance(cls):
        with cls._lock_inst:
            if cls._instance is None:
                cls._instance = SharedDataStore()
            return cls._instance

    # —— 写入一帧的“原始字段”（解析结果） —— #
    def write_last_frame(self, fn_name: str, RxAddr: int, RxFuncID: int,
                         RxDataLen: int, RxData, Mdbs_state: int):
        with self._lock:
            self.function_name = fn_name
            self.RxAddr = RxAddr
            self.RxFuncID = RxFuncID
            self.RxDataLen = RxDataLen
            self.RxData = RxData
            self.Mdbs_state = Mdbs_state

    # —— 写入某功能函数的“最终可展示结果”（已解包/分析） —— #
    def write_func_result(self, fn_name: str, final_result: dict):
        with self._lock:
            # 这里直接覆盖本次函数的结果；如需历史，可扩展为列表
            self.all_data_dict[fn_name] = final_result

            # 发布两类通知（小粒度 & 大粒度）
            self.oneFuncUpdated.emit(fn_name, final_result)
            snap = self._make_snapshot_locked()
            self.snapshotUpdated.emit(snap)

    def _make_snapshot_locked(self) -> dict:
        """在持锁条件下，制作全量快照（浅拷贝）"""
        return {
            "RxAddr": self.RxAddr,
            "RxFuncID": self.RxFuncID,
            "RxDataLen": self.RxDataLen,
            "RxData": list(self.RxData) if isinstance(self.RxData, (list, tuple)) else self.RxData,
            "Mdbs_state": self.Mdbs_state,
            "function_name": self.function_name,
            "all_data_dict": dict(self.all_data_dict),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def snapshot(self) -> dict:
        with self._lock:
            return self._make_snapshot_locked()


# 便于与你旧代码对齐的“全局别名”（可选）
# 你仍可从外部 import 这两个名字来读数据（读操作用 snapshot() 更安全）
DATAS = SharedDataStore.instance()
all_data_dict = DATAS.all_data_dict  # 引用（注意：若要线程安全访问，建议用 DATAS.snapshot()）


# ---------------------------------------------------------------------
# B) 线程包装：串口工作者
# ---------------------------------------------------------------------
class SerialPortWorker(QObject):
    frameReceived = pyqtSignal(bytes)  # 若底层暴露完整帧信号，可转发供被动监听使用

    def __init__(self, port_name: str, baudrate: int):
        super().__init__()
        self._port_name = port_name
        self._baudrate = baudrate
        self.serial_obj = Serial_Qthread_function()
        self.thread = SerialThread(self.serial_obj)
        self.serial_obj.moveToThread(self.thread)

        # 基本信号连接
        self.serial_obj.signal_pushButton_Open.connect(self.serial_obj.slot_pushButton_Open)
        self.serial_obj.signal_SendData.connect(self.serial_obj.slot_SendData)

        # 如果底层实现了 signal_frameReceived，就桥接出去
        try:
            self.serial_obj.signal_frameReceived.connect(self.frameReceived.emit)
        except Exception:
            pass

    def start(self):
        self.thread.start()
        open_param = {'PortName_master': self._port_name, 'BaudRate_master': self._baudrate}
        self.serial_obj.signal_pushButton_Open.emit(open_param)

    def stop(self):
        open_param = {'PortName_master': self._port_name, 'BaudRate_master': self._baudrate}
        self.serial_obj.signal_pushButton_Open.emit(open_param)  # 触发关闭
        self.thread.quit()
        self.thread.wait()

    def send_bytes(self, data: bytes):
        self.serial_obj.signal_SendData.emit({'data': data})


# ---------------------------------------------------------------------
# C) Modbus 客户端（构帧 + 发送 + 等待应答）
# ---------------------------------------------------------------------
class ModbusClient(QObject):
    def __init__(self, serial_worker: SerialPortWorker):
        super().__init__()
        self.serial_worker = serial_worker
        self._sender = ModbusSender()

    def modbus_query(self, slave_addr: int, func_id: int, start_addr: int, quantity: int):
        # 构造无 CRC 的 PDU
        if func_id == 1:
            hex_no_crc = self._sender.read_coils(slave_addr, start_addr, quantity)
        elif func_id == 2:
            hex_no_crc = self._sender.read_discrete_inputs(slave_addr, start_addr, quantity)
        elif func_id == 3:
            hex_no_crc = self._sender.read_holding_registers(slave_addr, start_addr, quantity)
        elif func_id == 4:
            hex_no_crc = self._sender.read_input_registers(slave_addr, start_addr, quantity)
        elif func_id == 5:
            hex_no_crc = self._sender.write_single_coil(slave_addr, start_addr, quantity)
        elif func_id == 6:
            hex_no_crc = self._sender.write_single_register(slave_addr, start_addr, quantity)
        elif func_id == 15:
            hex_no_crc = self._sender.write_multiple_coils(slave_addr, start_addr, quantity, [1] * quantity)
        elif func_id == 16:
            hex_no_crc = self._sender.write_multiple_registers(slave_addr, start_addr, quantity, [1] * quantity)
        else:
            print("未知功能码")
            return None

        # 加 CRC -> 发送
        payload = modbus_RTU(hex_no_crc)
        self.serial_worker.send_bytes(payload)

        # 等待一帧（带超时）
        hex_str = wait_for_last_frame(self.serial_worker.serial_obj, timeout_ms=2000)
        return hex_str


# ---------------------------------------------------------------------
# D) 帧解析器
# ---------------------------------------------------------------------
class FrameParser(QObject):
    def parse(self, hex_str: str):
        # 返回：RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT
        return Modbus_receive_Interface(hex_str)


# ---------------------------------------------------------------------
# E) 结果“分析器”（可选：把解析后的 RxData 转为更贴近 UI 的字段）
# 默认直通；如果你已有具体的“分析/解包成业务含义”的函数，可在这里替换。
# ---------------------------------------------------------------------
class Analyzer(QObject):
    def analyze(self, func_name: str, parsed: dict) -> dict:
        """
        输入：解析后的 dict
        输出：可直接给 UI 展示的 dict（可附带单位/标注/组合字段等）
        这里默认透传；若你有具体规则，可自行实现。
        """
        final_dict = dict(parsed)  # 浅拷贝
        return final_dict


# ---------------------------------------------------------------------
# F) 查询调度器（顺序执行 + 每轮间隔循环）
# ---------------------------------------------------------------------
class GroupQueryScheduler(QObject):
    oneQueryFinished = pyqtSignal(str, dict)  # (func_name, result_dict)
    oneRoundFinished = pyqtSignal()

    def __init__(self, modbus_client: ModbusClient, parser: FrameParser,
                 functions: list, cycle_interval_ms: int = 5000, analyzer: Analyzer = None):
        super().__init__()
        self.client = modbus_client
        self.parser = parser
        self.functions = functions
        self._idx = 0
        self._cycle_interval_ms = cycle_interval_ms
        self._analyzer = analyzer or Analyzer()

        self._step_timer = QTimer(self)
        self._step_timer.setSingleShot(True)
        self._step_timer.timeout.connect(self._do_one)

        self._between_round_timer = QTimer(self)
        self._between_round_timer.setSingleShot(True)
        self._between_round_timer.timeout.connect(self.start)

    def start(self):
        self._idx = 0
        self._do_one()

    def _do_one(self):
        if self._idx >= len(self.functions):
            print(f"所有查询执行完成，本轮结束。等待 {self._cycle_interval_ms/1000} 秒进入下一轮...")
            self.oneRoundFinished.emit()
            self._between_round_timer.start(self._cycle_interval_ms)
            return

        func = self.functions[self._idx]
        func_name = func.__name__
        print(f"[GroupQuery] 执行第 {self._idx+1}/{len(self.functions)} 个：{func_name}")

        slave, fid, start, qty = func()

        # —— 发送并等待帧 —— #
        hex_str = self.client.modbus_query(slave, fid, start, qty)

        result = {'hex': None, 'parsed': None, 'ok': False}

        if hex_str:
            result['hex'] = hex_str
            RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT = self.parser.parse(hex_str)
            parsed = {
                'RxAddr': RxAddr, 'RxFuncID': RxFuncID,
                'RxDataLen': RxDataLen, 'RxData': RxData,
                'Mdbs_state': Mdbs_state, 'MdbsCNT': MdbsCNT
            }
            result['parsed'] = parsed
            ok = bool(Mdbs_state & Frame_OK)
            result['ok'] = ok

            # ——【关键】写入“最近一帧”的全局字段 —— #
            DATAS.write_last_frame(func_name, RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state)

            if ok:
                # —— 分析成 UI 更友好的结果（如无规则则透传 parsed） —— #
                final_result = self._analyzer.analyze(func_name, parsed)

                # ——【关键】写入 all_data_dict[function_name] —— #
                DATAS.write_func_result(func_name, final_result)

                print(f"[GroupQuery][OK] {func_name}: {final_result}")
            else:
                print(f"[GroupQuery][NG] {func_name}: 无效帧/CRC异常等")
        else:
            print(f"[GroupQuery][TIMEOUT] {func_name}: 未收到有效响应")

        # 通知上层
        self.oneQueryFinished.emit(func_name, result)

        # 1 秒后继续
        self._idx += 1
        self._step_timer.start(1000)


# ---------------------------------------------------------------------
# G) 被动监听（第二路串口线程）
# ---------------------------------------------------------------------
class PassiveListener(QObject):
    def __init__(self, serial_worker: SerialPortWorker, parser: FrameParser):
        super().__init__()
        self.serial_worker = serial_worker
        self.parser = parser
        self.serial_worker.frameReceived.connect(self._on_frame)

    def _on_frame(self, frame: bytes):
        hex_str = frame.hex()
        print("\n=== [被动监听-收到外部帧] ===")
        print("HEX:", hex_str)
        RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT = self.parser.parse(hex_str)

        # 被动帧也更新“最近一帧”，但不写入 all_data_dict（避免覆盖主动查询结果）
        DATAS.write_last_frame("passive_rx", RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state)

        if Mdbs_state & Frame_OK:
            print(f"解析结果 - 地址:{RxAddr}, 功能码:{RxFuncID}, 数据长度:{RxDataLen}, 数据:{RxData}")
        else:
            print("无效帧，无法解析！！")
        print("============================\n")


# ---------------------------------------------------------------------
# H) 查询函数集合（保持你原本的“区间批量读”逻辑 & 参数）
# ---------------------------------------------------------------------
def read_coils_0_13():              return (1, 1, 0, 14)
def read_coils_16_24():             return (1, 1, 16, 10)
def read_coils_27_31():             return (1, 1, 27, 5)
def read_holding_registers_0_13():  return (1, 3, 0, 13)
def read_holding_registers_16_24(): return (1, 3, 16, 9)
def read_holding_registers_32_39(): return (3, 3, 4096, 12)
# def read_holding_registers_2(): return (3, 3, 4096, 12)
def read_holding_registers_3(): return (3, 3, 4352, 9)


# ---------------------------------------------------------------------
# I) 应用装配（端到端）
# ---------------------------------------------------------------------
class TrainGroupReaderApp(QObject):
    def __init__(self, active_port: str, passive_port: str, baudrate: int = 9600):
        super().__init__()
        self.active_serial = SerialPortWorker(active_port, baudrate)
        self.passive_serial = SerialPortWorker(passive_port, baudrate)

        self.client = ModbusClient(self.active_serial)
        self.parser = FrameParser()
        self.analyzer = Analyzer()

        functions = [
            read_coils_0_13,
            read_coils_16_24,
            read_coils_27_31,
            read_holding_registers_0_13,
            read_holding_registers_16_24,
            read_holding_registers_32_39,
            read_holding_registers_3,
        ]
        self.scheduler = GroupQueryScheduler(
            self.client, self.parser, functions, cycle_interval_ms=5000, analyzer=self.analyzer
        )
        self.scheduler.oneQueryFinished.connect(self.on_one_query_finished)
        self.scheduler.oneRoundFinished.connect(self.on_one_round_finished)

        self.passive_listener = PassiveListener(self.passive_serial, self.parser)

        # 示例：订阅数据仓库的变化（UI 可以直接连这两个信号）
        DATAS.oneFuncUpdated.connect(self.on_func_data_updated)
        DATAS.snapshotUpdated.connect(self.on_snapshot_updated)

    def start(self):
        self.active_serial.start()
        self.passive_serial.start()
        self.scheduler.start()

    def stop(self):
        self.active_serial.stop()
        self.passive_serial.stop()

    # —— 调度器回调 —— #
    def on_one_query_finished(self, func_name: str, result: dict):
        print(f"[回调] {func_name} -> ok={result['ok']}")

    def on_one_round_finished(self):
        print("[回调] 本轮查询完成。")

    # —— 数据仓库回调（可直接驱动 UI）—— #
    def on_func_data_updated(self, fn: str, final_result: dict):
        # 你可以在这里把 final_result 渲染到界面/写数据库
        print(f"[DataStore] {fn} 更新：{final_result}")

    def on_snapshot_updated(self, snap: dict):
        # 若 UI 需要整体快照（包括最近一帧 + 汇总字典）
        # print("[DataStore] Snapshot:", snap)   # 调试时打开
        pass


# ---------------------------------------------------------------------
# J) 程序入口
# ---------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    active_port = "COM5"   # 主动轮询口
    passive_port = "COM6"  # 被动监听口（如无第二口，可同指 COM5）
    baudrate = 9600

    app_obj = TrainGroupReaderApp(active_port, passive_port, baudrate)
    app_obj.start()

    ret = app.exec_()
    app_obj.stop()
    sys.exit(ret)
