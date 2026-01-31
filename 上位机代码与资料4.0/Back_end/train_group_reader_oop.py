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

import sys, time, threading, struct
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

        # === 写操作任务队列 ===
        self.pending_writes = []  # 存储待执行的写任务: [{'name':str, 'params':tuple}]

        # 线程并发保护
        self._lock = threading.Lock()

    @classmethod
    def instance(cls):
        with cls._lock_inst:
            if cls._instance is None:
                cls._instance = SharedDataStore()
            return cls._instance

    def add_write_task(self, func_name, slave, func_id, addr, value):
        """添加一个写任务到队列中"""
        with self._lock:
            self.pending_writes.append({
                'name': func_name,
                'params': (slave, func_id, addr, value)
            })
            print(f"[DataStore] 已加入写任务队列: {func_name} (Addr:{addr}, Val:{value})")

    def pop_write_task(self):
        """取出一个写任务"""
        with self._lock:
            if self.pending_writes:
                return self.pending_writes.pop(0)
            return None

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
        self._is_opened = False  # 新增：状态跟踪
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
        if not self._is_opened:
            self.thread.start()
            open_param = {'PortName_master': self._port_name, 'BaudRate_master': self._baudrate}
            self.serial_obj.signal_pushButton_Open.emit(open_param)
            self._is_opened = True
            print(f"--- 串口 {self._port_name} 已启动并占用 ---")

    def stop(self):
        if self._is_opened:
            open_param = {'PortName_master': self._port_name, 'BaudRate_master': self._baudrate}
            self.serial_obj.signal_pushButton_Open.emit(open_param)  # 触发关闭
            self._is_opened = False
        self.thread.quit()
        self.thread.wait()

    def send_bytes(self, data: bytes):
        if self._is_opened:
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
        hex_str = wait_for_last_frame(self.serial_worker.serial_obj, timeout_ms=200)
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
    def _regs_to_float(self, reg_high, reg_low):
        """将两个 16 位寄存器（十六进制字符串或整数）转换为 IEEE 754 浮点数"""
        try:
            h = int(reg_high, 16) if isinstance(reg_high, str) else reg_high
            l = int(reg_low, 16) if isinstance(reg_low, str) else reg_low
            # 组合成 32 位二进制数据 (大端模式)
            combined = (h << 16) | l
            # 使用 struct 将 32 位整数转换为浮点数
            return round(struct.unpack('>f', struct.pack('>I', combined))[0], 3)
        except Exception:
            return 0.0

    def _regs_to_uint32(self, reg_high, reg_low):
        """将两个 16 位寄存器转换为 32 位无符号整数"""
        try:
            h = int(reg_high, 16) if isinstance(reg_high, str) else reg_high
            l = int(reg_low, 16) if isinstance(reg_low, str) else reg_low
            return (h << 16) | l
        except Exception:
            return 0

    def analyze(self, func_name: str, parsed: dict) -> dict:
        """
        输入：解析后的 dict
        输出：可直接给 UI 展示的 dict，包含根据业务含义重命名的字段
        """
        # 1. 创建副本并处理不可 JSON 序列化的对象 (ModBusCounters)
        final_dict = {}
        for k, v in parsed.items():
            if k == "MdbsCNT":
                final_dict[k] = {
                    "CRCerr_CNT": v.CRCerr_CNT,
                    "Addrerr_CNT": v.Addrerr_CNT,
                    "IDerr_CNT": v.IDerr_CNT,
                    "Frabrk_CNT": v.Frabrk_CNT,
                    "Frame_CNT": v.Frame_CNT
                }
            else:
                final_dict[k] = v
        
        data = final_dict.get('RxData', [])
        if not data:
            return final_dict

        # 2. 根据不同的查询函数名进行详细解析
        try:
            if func_name == "read_coils_16_35":
                # 20 个线圈状态位 (16-35)
                mapping = [
                    "plc_status", "is_overspeed", "bin_gate_control", "lifting_device_control",
                    "lower_flap_gate_control", "hydraulic_system_control", "control_system_control",
                    "bin_gate_fault", "lifting_device_fault", "lower_flap_gate_fault",
                    "reserved_1", "reserved_2", "reserved_3", "reserved_4", "reserved_5", "reserved_6",
                    "is_full", "bin_gate_status", "lifting_device_status", "lower_flap_gate_status"
                ]
                for i, name in enumerate(mapping):
                    if i < len(data):
                        final_dict[name] = data[i]

            elif func_name == "read_holding_registers_0_14":
                # 26 个保持寄存器 (0-25)
                if len(data) >= 26:
                    final_dict["train_model"] = int(data[0], 16)
                    final_dict["int_length"] = int(data[1], 16)
                    final_dict["int_width"] = int(data[2], 16)
                    final_dict["int_height"] = int(data[3], 16)
                    final_dict["floor_height"] = int(data[4], 16)
                    # 容积 (float) - 寄存器 5, 6
                    final_dict["volume"] = self._regs_to_float(data[5], data[6])
                    # 焦炭密度 (float) - 寄存器 7, 8
                    final_dict["coke_density"] = self._regs_to_float(data[7], data[8])
                    
                    final_dict["bin_gate_opening_control"] = int(data[9], 16)
                    final_dict["lifting_height_control"] = int(data[10], 16)
                    final_dict["lower_flap_angle_control"] = int(data[11], 16)
                    
                    # 火车速度 (uint32) - 寄存器 16, 17
                    final_dict["train_speed"] = self._regs_to_uint32(data[16], data[17])
                    # 料位高度 (float) - 寄存器 18, 19
                    final_dict["material_level_plc"] = self._regs_to_float(data[18], data[19])
                    # 激光距离 (uint32) - 寄存器 20, 21
                    final_dict["laser_distance_plc"] = self._regs_to_uint32(data[20], data[21])
                    
                    final_dict["positioning_distance"] = int(data[22], 16)
                    final_dict["bin_gate_opening_status"] = int(data[23], 16)
                    final_dict["lifting_height_status"] = int(data[24], 16)
                    final_dict["lower_flap_angle_status"] = int(data[25], 16)

            elif func_name == "read_level_gauge_sensor":
                # 料位高度 (float) - 2 个寄存器
                if len(data) >= 2:
                    val = self._regs_to_float(data[0], data[1])
                    final_dict["material_level"] = val
                    print(f"DEBUG: 解析到料位高度 = {val} m")

            elif func_name == "read_laser_sensor":
                # 激光距离 (uint32) - 2 个寄存器
                if len(data) >= 2:
                    total_val = self._regs_to_uint32(data[0], data[1])
                    final_dict['laser_decimal'] = total_val
                    print(f"DEBUG: 解析到激光距离 = {total_val}")

        except Exception as e:
            print(f"ERROR: 解析 {func_name} 业务数据失败: {e}")
                
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
        # --- 新增逻辑：在本轮轮询(所有读函数)执行完后，优先处理写任务队列 ---
        if self._idx >= len(self.functions):
            write_task = DATAS.pop_write_task()
            if write_task:
                func_name = write_task['name']
                slave, fid, start, val = write_task['params']
                print(f"[GroupQuery] --- 触发写操作指令: {func_name} ---")
                
                # 执行写操作 (重用 client.modbus_query)
                hex_str = self.client.modbus_query(slave, fid, start, val)
                
                if hex_str:
                    RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT = self.parser.parse(hex_str)
                    if Mdbs_state & Frame_OK:
                        print(f"--- [SUCCESS] 写指令 {func_name} 执行成功，从站已响应 ---")
                        # 记录最近一帧
                        DATAS.write_last_frame(func_name, RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state)
                    else:
                        print(f"--- [ERROR] 写指令 {func_name} 响应异常 (CRC错误等) ---")
                else:
                    print(f"--- [TIMEOUT] 写指令 {func_name} 无响应 ---")
                
                # 执行完一个写任务后，再次触发定时器检查队列中是否还有更多写任务，或者结束本轮
                self._step_timer.start(80)
                return

            # 如果没有写任务，则按原逻辑结束本轮
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

        # 200ms 后继续下一个查询，加快轮询节奏
        self._idx += 1
        self._step_timer.start(70)


# ---------------------------------------------------------------------
# G) 被动监听（第二路串口线程）
# ---------------------------------------------------------------------
class PassiveListener(QObject):
    def __init__(self, serial_worker: SerialPortWorker, parser: FrameParser, analyzer: Analyzer = None):
        super().__init__()
        self.serial_worker = serial_worker
        self.parser = parser
        self.analyzer = analyzer or Analyzer()
        self.serial_worker.frameReceived.connect(self._on_frame)

    def _on_frame(self, frame: bytes):
        hex_str = frame.hex()
        # print("\n=== [被动监听-收到外部帧] ===")
        # print("HEX:", hex_str)
        RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT = self.parser.parse(hex_str)

        # 1. 记录最近一帧原始数据
        DATAS.write_last_frame("passive_rx", RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state)

        # 2. 如果帧有效，尝试进行业务分析并更新汇总字典
        if Mdbs_state & Frame_OK:
            # 根据地址和功能码推测这可能属于哪个功能函数，以便前端按 Key 读取
            possible_func = None
            if RxAddr == 1:
                if RxFuncID == 1: possible_func = "read_coils_0_21"
                elif RxFuncID == 3: 
                    if RxDataLen == 18: possible_func = "read_holding_registers_16_24"
                    elif RxDataLen == 30: possible_func = "read_holding_registers_0_14"
            elif RxAddr == 3 and RxFuncID == 3:
                possible_func = "read_level_gauge_sensor"
            elif RxAddr == 4 and RxFuncID == 3:
                possible_func = "read_laser_sensor"

            if possible_func:
                parsed_info = {
                    "RxAddr": RxAddr, "RxFuncID": RxFuncID, "RxDataLen": RxDataLen, 
                    "RxData": RxData, "Mdbs_state": Mdbs_state, "MdbsCNT": MdbsCNT
                }
                final_result = self.analyzer.analyze(possible_func, parsed_info)
                DATAS.write_func_result(possible_func, final_result)
                print(f"[被动监听] 已识别并更新功能块: {possible_func}")
            else:
                print(f"[被动监听] 收到有效帧但未匹配到功能块 (Addr:{RxAddr}, Func:{RxFuncID}, Len:{RxDataLen})")
        # else:
        #    print("被动监听：收到无效帧，跳过解析")



# ---------------------------------------------------------------------
# H) 查询函数集合（保持你原本的“区间批量读”逻辑 & 参数）
# ---------------------------------------------------------------------
# 读取 plc 中 16-35号线圈的值（依次为： plc工作状态，超速与否，仓口阀门控制位，升降装置控制位，下部翻板阀门控制位，液压系统控制位，控制系统控制位、仓口阀门故障、升降装置故障、下部翻板阀门故障、空保留位、空保留位、空保留位、空保留位、空保留位、空保留位、装料是否装满、仓口阀门状态位、升降装置状态位、下部翻板阀门状态位）
def read_coils_16_35():              return (1, 1, 16, 20)
# 读取 plc 中 0-25号保持寄存器的值（依次为：火车型号unit16、内部长度unit16、内部宽度unit16、内部高度unit16、底板面高unit16、容量-高位float、容量-低位float、焦炭密度-高位float、焦炭密度-低位float、仓口阀门开度控制量unit16、升降高度控制量unit16、下部翻板角度控制量unit16、空保留位、空保留位、空保留位、空保留位、火车速度-高位uint32、火车速度-低位uint32、料位高度-高位float、料位高度-低位float、激光距离-高位uint32、激光距离-低位uint32、定位距离unit16、仓口阀门开度状态量unit16、升降高度状态量uint16、下部翻板角度状态量uint16）
def read_holding_registers_0_14():   return (1, 3, 0, 26)
# 读取料位计数据，float类型（依次为：料位高度-高位float、料位高度-低位float）
def read_level_gauge_sensor():       return (3, 3, 4098, 2)
# 新增激光传感器查询函数 (从站 4, 功能码 3, 地址 21, 数量 2)，激光距离，数据类型unit32
def read_laser_sensor():             return (4, 3, 21, 2)

# --- 新增写函数 (功能码 0x05, 0x06) ---
# 写单个线圈 (0x05): value 为 0xFF00 为开, 0x0000 为关
def write_single_coil(slave, addr, value): return (slave, 5, addr, value)
# 写单个保持寄存器 (0x06): value 为要写入的数值 (0-65535)
def write_single_register(slave, addr, value): return (slave, 6, addr, value)


# ---------------------------------------------------------------------
# I) 应用装配（端到端）
# ---------------------------------------------------------------------
class TrainGroupReaderApp(QObject):
    def __init__(self, active_port: str, passive_port: str, baudrate: int = 9600):
        super().__init__()
        # 1. 优化：如果端口相同，则共用同一个串口对象，避免多次打开报错
        self.active_serial = SerialPortWorker(active_port, baudrate)
        
        if active_port == passive_port:
            self.passive_serial = self.active_serial
            print(f"主动与被动端口相同({active_port})，将共用串口实例。")
        else:
            self.passive_serial = SerialPortWorker(passive_port, baudrate)

        self.client = ModbusClient(self.active_serial)
        self.parser = FrameParser()
        self.analyzer = Analyzer()

        # 轮回查询，确保每秒发送一次请求（五帧）
        functions = [
            read_coils_16_35,
            read_holding_registers_0_14,
            read_level_gauge_sensor,
            read_laser_sensor,
        ]

        # cycle_interval_ms=100 表示每轮查询结束后等待 1 秒再开始下一轮
        self.scheduler = GroupQueryScheduler(
            self.client, self.parser, functions, cycle_interval_ms=100, analyzer=self.analyzer
        )
        self.scheduler.oneQueryFinished.connect(self.on_one_query_finished)
        self.scheduler.oneRoundFinished.connect(self.on_one_round_finished)

        self.passive_listener = PassiveListener(self.passive_serial, self.parser, self.analyzer)

        # 示例：订阅数据仓库的变化（UI 可以直接连这两个信号）
        DATAS.oneFuncUpdated.connect(self.on_func_data_updated)
        DATAS.snapshotUpdated.connect(self.on_snapshot_updated)

    def start(self):
        self.active_serial.start()
        if self.passive_serial != self.active_serial:
            self.passive_serial.start()
        self.scheduler.start()

    def stop(self):
        self.active_serial.stop()
        if self.passive_serial != self.active_serial:
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

    active_port = "COM6"   # 主动轮询口
    passive_port = "COM6"  # 被动监听口（如无第二口，可同指 COM5）
    baudrate = 9600

    app_obj = TrainGroupReaderApp(active_port, passive_port, baudrate)
    app_obj.start()

    ret = app.exec_()
    app_obj.stop()
    sys.exit(ret)
