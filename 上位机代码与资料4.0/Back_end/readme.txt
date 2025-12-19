后端代码说明（Back_end）
========================

本目录主要完成 **Modbus RTU 通信、PLC/传感器数据采集、数据库访问以及相机/实时监控界面** 等后端逻辑。  
下面按文件进行说明，并给出主要对外接口（函数 / 类）的 API 表。

--------------------------------
1. camera.py — 相机采集线程
--------------------------------

**功能概述：**
- 基于 `QThread` 封装一个相机采集线程 `CameraThread`。
- 使用 OpenCV 读取摄像头画面，将每一帧转换为 `QImage` 通过信号发给 UI，用于实时显示。

**主要类与接口：**

| 名称 | 类型 | 参数 | 返回值 | 说明 |
|------|------|------|--------|------|
| `CameraThread` | `QThread` 子类 | `device_index=0, width=None, height=None, fps=30, parent=None` | - | 相机采集线程，周期性读取摄像头帧并发射信号 |
| `CameraThread.frameReady` | 信号 | `QImage` | - | 每获取到一帧图像时发射，用于 UI 显示 |
| `CameraThread.startedOk` | 信号 | - | - | 相机初始化成功后发射 |
| `CameraThread.error` | 信号 | `str` | - | 相机初始化或采集出错时发射错误信息 |
| `CameraThread.run()` | 方法（线程入口） | - | - | 打开摄像头、循环采集帧并通过 `frameReady` 发送 |
| `CameraThread.stop(wait_timeout_ms=1000)` | 方法 | `wait_timeout_ms` 超时(ms) | - | 请求线程停止并在指定超时时间内等待退出 |

**调用示例（伪代码）：**
```python
cam = CameraThread(device_index=0, width=1280, height=720, fps=25)
cam.frameReady.connect(self.on_frame)   # 在 UI 中显示图像
cam.error.connect(self.on_error)
cam.start()
...
cam.stop()
```

--------------------------------
2. database.py — 通用数据库管理类（新版本）
--------------------------------

**功能概述：**
- 使用 `pyodbc` 访问 SQL Server。
- 封装通用查询 / 插入 / 更新接口，通过 schema + table + 列名组合构建 SQL。
- 适合作为统一的数据库访问封装，在 UI 或业务层中直接调用。

**主要类与接口：**

| 名称 | 类型 | 参数 | 返回值 | 说明 |
|------|------|------|--------|------|
| `TrainDatabaseManager` | 类 | `server, database, username, password, driver="{ODBC Driver 17 for SQL Server}", timeout=5` | - | 通用数据库管理器 |
| `_connect()` | 私有方法 | - | `pyodbc.Connection` | 建立数据库连接（上下文管理器中使用） |
| `query_all(schema, table)` | 方法 | `schema: str, table: str` | `(columns: List[str], rows: List[pyodbc.Row])` | 查询整张表：`SELECT * FROM [schema].[table]` |
| `query_by_id(schema, table, id_column, value)` | 方法 | `schema: str, table: str, id_column: str, value` | 同上 | 按主键或任意列精确查询 |
| `insert_row(schema, table, data)` | 方法 | `schema: str, table: str, data: dict` | `None` / 异常 | 按 `data` 字典列名和值插入一行记录 |
| `update_row_by_id(schema, table, id_column, id_value, data)` | 方法 | `schema, table, id_column, id_value, data: dict` | `None` / 异常 | 按 id 更新指定列，`data` 仅包含需要修改的列 |

**说明：**
- 此文件中的 `TrainDatabaseManager` 是 **推荐在前端/业务层使用的版本**，结构更通用、安全性更好（使用参数化查询）。

--------------------------------
3. data12.py — 旧版/示例化数据库管理类
--------------------------------

**功能概述：**
- 使用 `pyodbc` 连接 SQL Server。
- 封装了一组**针对具体表名**的业务方法（火车型号表、到位表、速度表、入库表、下料记录表等）。
- 同时在底部有部分“新接口风格”的 `query_all` / `query_by_train_type_id` 示例，但其内部仍使用 `_connect()`（实际未在此类中定义，可能是历史遗留）。

**主要类与接口（业务方法）：**

| 名称 | 类型 | 参数 | 返回值 | 说明 |
|------|------|------|--------|------|
| `TrainDatabaseManager` | 类 | `server, database, username, password` | - | 旧版数据库管理器，内置长连接 |
| `connect()` | 方法 | - | - | 建立数据库连接，设置 `self.conn`/`self.cursor` |
| `close()` | 方法 | - | - | 关闭连接及游标 |
| `execute_query(query, params=None, fetch_all=True)` | 方法 | SQL 字符串，参数 | `list[Row]` 或单行 | 通用查询封装 |
| `execute_update(query, params=None)` | 方法 | SQL 字符串，参数 | `bool` | 通用增删改封装 |
| `get_all_train_models()` | 方法 | - | 查询结果 | `SELECT * FROM [Train Model Table]` |
| `add_train_model(model_data)` | 方法 | 参数元组 | `bool` | 往 `[Train Model Table]` 插入一条新火车型号记录 |
| `get_train_arrivals()` | 方法 | - | 查询结果 | 查询 `[Train Arrival Table]` |
| `update_train_arrival_status(train_id, status)` | 方法 | train_id, status | `bool` | 更新到位状态及时间 |
| `get_train_speeds()` / `add_speed_record(speed_data)` | 方法 | - | 见代码 | 针对 `[Train Speed Table]` 的操作 |
| `get_inventory_records()` / `add_inventory_record(inventory_data)` | 方法 | - | 见代码 | 针对入库表的操作 |
| `get_layoff_history()` / `add_layoff_record(layoff_data)` | 方法 | - | 见代码 | 针对下料历史表的操作 |

**建议：**
- 生产环境建议逐步迁移到 `database.py` 中的新版本封装，`data12.py` 可以作为**兼容旧逻辑或业务示例**保留。

--------------------------------
4. modbus_RTU.py — 进制转换 & CRC16 计算
--------------------------------

**功能概述：**
- 提供 `Binary` 类进行十六进制/十进制/二进制转换。
- 提供 `CRC` 类计算 Modbus RTU 使用的 CRC16 校验码（0xA001 多项式）。
- 该模块被 `modbus_send.py` 等用于生成完整的 Modbus RTU 帧。

**主要接口：**

| 名称 | 类型 | 参数 | 返回值 | 说明 |
|------|------|------|--------|------|
| `Binary.Hex2Dex(e_hex)` | 静态方法 | 十六进制字符串 | `int` | hex → dec |
| `Binary.Hex2Bin(e_hex)` | 静态方法 | 十六进制字符串 | `str` | hex → bin 字符串 |
| `Binary.Dex2Bin(e_dex)` | 静态方法 | `int` | `str` | dec → bin 字符串 |
| `CRC` | 类 | - | - | CRC 计算器 |
| `CRC.CRC16(hex_num)` | 方法 | 形如 `'01 03 00 01 00 02'` 的 hex 字符串 | `(crc_hex, crc_H, crc_L)` | 计算 Modbus CRC16，返回完整 4 位 hex 以及高/低字节字符串 |

--------------------------------
5. modbus_send.py — Modbus 主站发送 & 串口封装
--------------------------------

**功能概述：**
- 使用 `QSerialPort` 封装主动串口对象 `Serial_Qthread_function`，支持在线程中异步收发。
- 基于 `CRC` 构造完整 Modbus RTU 报文。
- 提供高层的 `ModbusSender` 类，按功能码生成无 CRC 的 PDU，供上层调用。
- 提供同步等待一帧响应的封装 `wait_for_last_frame`。

**串口相关主要接口：**

| 名称 | 类型 | 参数 | 返回值 | 说明 |
|------|------|------|--------|------|
| `Serial_Qthread_function` | 类（QObject） | - | - | 串口读写封装，在线程中运行 |
| `Serial_Qthread_function.signal_pushButton_Open` | 信号 | 参数 dict | - | 触发打开/关闭串口 |
| `Serial_Qthread_function.signal_SendData` | 信号 | 参数 dict | - | 触发发送 bytes 数据 |
| `Serial_Qthread_function.signal_frameReceived` | 信号 | `bytes` | - | 每收到一帧完整 Modbus RTU 帧时发射 |
| `Serial_Qthread_function.slot_pushButton_Open(paremeter)` | 槽 | `{'PortName_master','BaudRate_master',...}` | - | 打开/关闭串口 |
| `Serial_Qthread_function.slot_SendData(parameter)` | 槽 | `{'data': bytes}` | - | 通过串口发送数据 |
| `wait_for_last_frame(serial_obj, timeout_ms=2000)` | 函数 | 串口对象, 超时(ms) | `str or None` | 阻塞等待一帧到达，返回 hex 字符串 |
| `modbus_RTU(sendbytes)` | 函数 | hex 字符串（无 CRC，如 `'01 03 00 08 00 05'`） | `bytes` | 自动计算 CRC 并返回完整帧 bytes |

**Modbus 报文构造接口（ModbusSender）：**

| 名称 | 类型 | 参数 | 返回值 | 说明 |
|------|------|------|--------|------|
| `ModbusSender` | 类 | - | - | 高层帧构造器，不含 CRC |
| `build_modbus_frame(slave_addr, func_code, data=None)` | 方法 | 地址、功能码、数据字节 | `str` hex 字符串 | 构造无 CRC 的 PDU |
| `read_coils(slave_addr, start_addr, quantity)` | 方法 | - | hex 字符串 | 功能码 0x01 |
| `read_discrete_inputs(...)` | 方法 | - | hex 字符串 | 功能码 0x02 |
| `read_holding_registers(...)` | 方法 | - | hex 字符串 | 功能码 0x03 |
| `read_input_registers(...)` | 方法 | - | hex 字符串 | 功能码 0x04 |
| `write_single_coil(...)` | 方法 | - | hex 字符串 | 功能码 0x05 |
| `write_single_register(...)` | 方法 | - | hex 字符串 | 功能码 0x06 |
| `write_multiple_coils(...)` | 方法 | - | hex 字符串 | 功能码 0x0F |
| `write_multiple_registers(...)` | 方法 | - | hex 字符串 | 功能码 0x10 |

--------------------------------
6. modbus_receive.py — Modbus 从站/通用帧解析
--------------------------------

**功能概述：**
- 完整实现 Modbus RTU 帧接收状态机、CRC 校验及错误统计。
- 提供 `Modbus_receive_Interface` 作为**统一解析入口**：传入一帧的十六进制字符串，返回地址、功能码、数据区及状态。

**核心数据结构与常量：**

| 名称 | 类型 | 说明 |
|------|------|------|
| `tUartParms` | 类 | 保存一个 Modbus 通道的接收状态、缓存、错误计数等 |
| `ModBusCounters` | 类 | 统计 CRC 错误 / 地址错误 / 功能码错误 / 帧损坏 / 成功帧数量 |
| `EnFlagFalse / EnFlagTrue` | 常量 | 定时器/标志位布尔量 |
| `ADDR_err, Length_err, FuncID_err, Frame_broken, CRC_err, Frame_OK` | 常量 | 帧结果标志位 |

**主要接口函数：**

| 名称 | 类型 | 参数 | 返回值 | 说明 |
|------|------|------|--------|------|
| `InitModBus(UartInfoTmp, Instance, MasterSlave, MyID)` | 函数 | `tUartParms`, 实例号, 主/从, 本机ID | - | 初始化 Modbus 通道参数 |
| `ModBus_TIM_Callback(UartInfoTmp)` | 函数 | `tUartParms` | - | 模拟接收超时定时器，用于判断一帧结束 |
| `ModBus_Rcv_Callback(UartInfoTmp, RcvData)` | 函数 | `tUartParms, int(字节)` | - | 串口每收到一个字节时调用，缓存并更新状态 |
| `ModBusCheck(UartInfoTmp)` | 函数 | `tUartParms` | - | 在检测到帧结束后调用，解析帧并更新错误计数 |
| `AnalyFrm(UartInfoTmp)` | 函数 | `tUartParms` | `int` 状态标志 | 校验地址/长度/功能码/CRC，返回综合状态 |
| `CRC16(puchMsg, usDataLen)` | 函数 | 缓冲区、长度 | 16 位整数 | 表驱动 CRC16 实现 |
| `Deal_OKfrm(UartInfoTmp)` | 函数 | `tUartParms` | - | 对有效帧按功能码分发到对应 `Reply_xx` |
| `Reply_01 ... Reply_10` | 函数 | `tUartParms` | - | 各功能码的回复占位接口（当前仅打印） |
| `Modbus_receive_Interface(rcv_hex_str)` | 函数 | 字符串 `"01 03 04 00 00 ..."` 或无空格 hex 串 | `(RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT)` | 高层解析入口，自动完成状态机与 CRC 校验并解包数据区 |

**推荐对外使用的接口：**
- **只需要解析 Modbus RTU 帧** 时，直接调用：  
  `RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT = Modbus_receive_Interface(rcv_hex_str)`

--------------------------------
7. train_function.py — 单点业务查询（一次一类数据）
--------------------------------

**功能概述：**
- 基于 `modbus_send` 和 `modbus_receive`，实现若干**单个业务变量/设备状态**的读取函数，例如：交易状态、下料机状态、阀门角度等。
- 使用 `modbus_query` 统一完成：构帧 → 发送 → 等待响应 → 返回收到的原始十六进制字符串。
- 提供一个 `run_queries_in_sequence` 函数，按顺序执行一组业务查询（适合作为调试脚本）。

**主要接口函数：**

| 名称 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `modbus_query(slave_addr, func_ID, start_addr, quantity)` | 从站地址、功能码、起始地址、数量 | 响应帧 hex 字符串或 `None` | 通用查询函数，内部使用 `ModbusSender` + `modbus_RTU` + `wait_for_last_frame` |
| `transaction_status_query()` | - | 响应 hex 字符串 | 问 PLC：牵引车状态 |
| `machine_status()` | - | 响应 hex 字符串 | 问 PLC：下料机状态 |
| `valve_open_angel()` | - | 响应 hex 字符串 | 问 PLC：阀门开启角度 |
| `Lifting_height()` | - | 响应 hex 字符串 | 问 PLC：升降高度 |
| `Flip_plate_height()` | - | 响应 hex 字符串 | 问 PLC：翻板高度 |
| `Full_ornot()` | - | 响应 hex 字符串 | 问 PLC：仓位是否满载 |
| `Load_progress()` | - | 响应 hex 字符串 | 问 PLC：装载进度 |
| `Coal_height()` / `Liaoweiji()` | - | 响应 hex 字符串 | 某些传感器高度/料位信息（地址见代码） |
| `run_queries_in_sequence(functions, index=0)` | 函数列表 | - | 顺序执行一批查询，内部调用 `Modbus_receive_Interface` 解析并打印结果 |

**备注：**
- `warehouse_number()、operater_name()、train_ID()` 当前仅打印说明，返回 0，表示这些数据来源于其他系统（数据库/视觉系统）。

--------------------------------
8. train_function_groupRead.py — 旧版“集群读取”实现
--------------------------------

**功能概述：**
- 在一个串口上，轮询执行多个“区间批量读”函数（例如一次读取 0–13 号线圈、16–24 号线圈等）。
- 每个函数最终都会返回一个 Modbus RTU 响应 hex 字符串，再通过 `Modbus_receive_Interface` 解析。
- 全局字典 `all_data_dict` 用于保存所有功能函数对应的解析结果，方便前端展示。

**主要接口：**

| 名称 | 类型 | 参数 | 返回值 | 说明 |
|------|------|------|--------|------|
| `modbus_query(...)` | 函数 | 同 `train_function.py` | hex 字符串 | 通用查询 |
| `read_coils_0_13()` 等 | 函数 | - | hex 字符串 | 一次性读取不同地址区间的线圈/寄存器 |
| `all_data_dict` | 全局 dict | - | - | `{function_name: {'RxAddr','RxFuncID','RxDataLen','RxData','Mdbs_state'}}` |
| `save_frame_data()` | 函数 | - | - | 将当前解析结果保存到 `all_data_dict` |
| `run_queries_in_sequence(functions, index=0)` | 函数 | 函数列表 | - | 以 1 秒间隔顺序执行所有查询；每轮之间等待 5 秒 |
| `on_passive_frame_received(frame)` | 函数 | `bytes` | - | 在线程2中被动监听外部帧并解析打印（不写入 `all_data_dict`） |

**说明：**
- 这是 **函数式/全局变量风格的早期实现**，已被 `train_group_reader_oop.py` 中的 OOP 版本所增强，但仍可作为调试脚本使用。

--------------------------------
9. train_group_reader_oop.py — OOP 版集群读取 & 数据仓库（推荐）
--------------------------------

**功能概述：**
- 将原有“集群读取 + 全局变量”方案升级为 **面向对象 + 线程安全数据仓库**：
  - `SharedDataStore`：集中保存最近一帧解析结果和所有功能函数的最终数据，提供 `snapshot()` 方法和信号。
  - `SerialPortWorker`：管理一个串口线程（主动口/被动口）。
  - `ModbusClient`：封装一次完整的 Modbus 查询流程（构帧+发送+等待响应）。
  - `GroupQueryScheduler`：按固定顺序和节奏循环执行多组查询。
  - `PassiveListener`：在被动串口上监听外部主动发来的帧。
  - `TrainGroupReaderApp`：将上述组件组装成完整应用，供外部（如 UI）直接启动。

**核心类与对外 API：**

| 名称 | 类型 | 关键方法/属性 | 说明 |
|------|------|---------------|------|
| `SharedDataStore` | 单例类（QObject） | `snapshot(), write_last_frame(), write_func_result()`；信号 `snapshotUpdated, oneFuncUpdated` | 线程安全数据仓库，**对外推荐读取接口：`DATAS.snapshot()`** |
| `DATAS` | 全局对象 | - | `SharedDataStore.instance()` 的别名，供其它模块导入 |
| `SerialPortWorker(port_name, baudrate)` | 类 | `start(), stop(), send_bytes()`；信号 `frameReceived(bytes)` | 封装一个串口线程及打开/关闭/发送逻辑 |
| `ModbusClient` | 类 | `modbus_query(slave, func_id, start, qty)` | 高层查询封装，内部使用 `modbus_RTU` + `wait_for_last_frame` |
| `FrameParser` | 类 | `parse(hex_str)` | 调用 `Modbus_receive_Interface` 完成解析 |
| `Analyzer` | 类 | `analyze(func_name, parsed)` | 业务层可在此将解析结果转为更友好的结构，当前为透传 |
| `GroupQueryScheduler` | 类 | `start()`；信号 `oneQueryFinished, oneRoundFinished` | 管理主动口的轮询查询逻辑 |
| `PassiveListener` | 类 | - | 监听被动串口，解析帧并写入 `DATAS` 中的“最近一帧” |
| `TrainGroupReaderApp(active_port, passive_port, baudrate=9600)` | 类 | `start(), stop()` | **外部推荐调用入口**：启动/停止整个后端采集系统 |

**查询函数集合（保持原语义）：**

| 名称 | 返回值 | 说明 |
|------|--------|------|
| `read_coils_0_13()` | `(1, 1, 0, 14)` | 读从站1，线圈地址0–13 |
| `read_coils_16_24()` | `(1, 1, 16, 10)` | 读从站1，线圈地址16–24 |
| `read_coils_27_31()` | `(1, 1, 27, 5)` | ... |
| `read_holding_registers_0_13()` | `(1, 3, 0, 13)` | 读保持寄存器 0–13 |
| `read_holding_registers_16_24()` | `(1, 3, 16, 9)` | ... |
| `read_holding_registers_32_39()` | `(3, 3, 4096, 12)` | ... |
| `read_holding_registers_3()` | `(3, 3, 4352, 9)` | ... |

**UI 访问数据的推荐方式：**
- 在 UI 中导入：`from train_group_reader_oop import DATAS, TrainGroupReaderApp`
- 启动后台：`app = TrainGroupReaderApp("COMx", "COMy", 9600); app.start()`
- 在 UI 定时或通过信号读取数据：
  - 通过信号：`DATAS.snapshotUpdated.connect(self.on_snapshot)`  
  - 拉取快照：`snap = DATAS.snapshot()`，字段示例：
    - `snap["function_name"]`：最近一次更新的功能函数名  
    - `snap["RxAddr"], snap["RxFuncID"], snap["RxDataLen"], snap["RxData"], snap["Mdbs_state"]`  
    - `snap["all_data_dict"]`：所有功能函数的最终结果字典  

--------------------------------
10. live_frame_viewer.py — 实时帧监控窗口（前端示例）
--------------------------------

**功能概述：**
- 提供一个独立的 Qt 窗口，用于实时展示 `DATAS` 中“最近一帧”的 Modbus 数据以及 `all_data_dict` 的汇总信息。
- 可选择在同一进程内直接启动 `TrainGroupReaderApp`，或者只作为“查看器”连接已经运行的采集后端（当前实现为同进程模式）。

**主要类与接口：**

| 名称 | 类型 | 说明 |
|------|------|------|
| `SnapshotReader(interval_ms=200)` | QObject | 运行在独立线程中，定时从 `DATAS.snapshot()` 拉取数据并发射 `snapshotReady(dict)` 信号 |
| `LiveFrameWindow` | `QMainWindow` | UI 窗口，展示最近一帧的关键信息（Addr/FuncID/DataLen/状态/Data）以及 `all_data_dict` 表格 |
| `AppWithReader` | `QApplication` 子类 | 组装后台采集（可选）、读取线程、窗口，作为本文件独立运行的入口 |

**对外使用方式：**
- 在命令行直接运行：  
  `python live_frame_viewer.py`  
  即可同时启动主动/被动采集（若 `START_BACKEND=True`）和实时监控窗口。

--------------------------------
11. 总体接口使用建议
--------------------------------

**Modbus 收发 & 解析：**
- 构造和发送帧：  
  - 构造无 CRC 帧：`ModbusSender.read_holding_registers(...)` 等  
  - 加 CRC：`modbus_RTU(hex_str)` → `bytes`  
  - 串口发送：`Serial_Qthread_function.signal_SendData.emit({'data': bytes})`
- 解析收到的完整帧：  
  - 若已有 hex 字符串：`Modbus_receive_Interface(rcv_hex_str)`  
  - 若使用 OOP 集群读取：直接读 `DATAS.snapshot()` 中的字段。

**数据库：**
- 新项目优先使用 `database.py` 里的 `TrainDatabaseManager`，统一通过 `schema + table + data dict` 读写；
- 旧脚本/特定业务表仍可参考 `data12.py` 中方法。

**采集系统整体启动（推荐）：**
- 后台采集 + UI 监控：
  1. 在后端启动：`TrainGroupReaderApp("COMx", "COMy", 9600).start()`  
  2. 前端窗口使用 `DATAS.snapshot()` 或 `DATAS.snapshotUpdated` 信号取数据（示例已在 `live_frame_viewer.py` 中给出）。
