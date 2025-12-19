## Back_end 模块说明（后端核心逻辑）

> 提示：此文件是根目录 `README.md` 中“后端部分”的精简/独立版，方便单独查看与 GitHub 浏览。  
> 若需整个项目的完整说明，请阅读仓库根目录的 `README.md`。

本目录主要完成 **Modbus RTU 通信、PLC/传感器数据采集、数据库访问以及相机/实时监控界面** 等后端逻辑，是上位机的“数据与通讯核心”。

---

## 1. 文件一览

- `camera.py`：相机采集线程模块，使用 OpenCV + PyQt5。
- `data12.py`：旧版数据库管理示例，按具体业务表封装方法。
- `database.py`：新版通用数据库管理器（推荐），面向 SQL Server。
- `env_test.py`：环境自检脚本，检测 Python 版本与关键依赖是否可用。
- `live_frame_viewer.py`：实时 Modbus 数据帧监控窗口，可与 OOP 集群读取联动。
- `modbus_RTU.py`：Modbus RTU 进制转换与 CRC16 校验工具。
- `modbus_receive.py`：Modbus RTU 帧接收状态机与解析入口。
- `modbus_send.py`：Modbus 主站发送逻辑与串口线程封装。
- `train_function.py`：按业务含义封装的“单点查询”函数集合。
- `train_function_groupRead.py`：函数式“集群读取”实现（早期版本）。
- `train_group_reader_oop.py`：OOP + 线程安全数据仓库的集群读取实现（推荐）。
- `readme.txt`：较早的后端说明（内容已基本被本文件和根目录 README 覆盖）。

---

## 2. Modbus 通信与串口相关

### 2.1 CRC 与进制工具：`modbus_RTU.py`

- `Binary` 类：
  - `Hex2Dex(e_hex)`：十六进制字符串 → 十进制整数。
  - `Hex2Bin(e_hex)`：十六进制字符串 → 二进制字符串。
  - `Dex2Bin(e_dex)`：十进制整数 → 二进制字符串。
- `CRC` 类：
  - `CRC16(hex_num)`：输入形如 `'01 03 00 01 00 02'` 的 hex 字符串，返回：
    - `(crc_hex, crc_H, crc_L)`：完整 CRC16 的 4 位 hex 字符串、高字节、低字节。

### 2.2 发送端主站封装：`modbus_send.py`

**串口与帧切分：**

- `Serial_Qthread_function`（QObject）：
  - 内部持有 `QSerialPort`，在独立线程中运行。
  - 关键信号：
    - `signal_pushButton_Open(object)`：打开/关闭串口。
    - `signal_SendData(object)`：发送数据（`{'data': bytes}`）。
    - `signal_frameReceived(bytes)`：每当拼出一帧完整的 Modbus RTU 帧时发射。
  - 关键槽：
    - `slot_pushButton_Open(paremeter)`：根据端口名、波特率打开/关闭串口。
    - `slot_SendData(parameter)`：写入字节流。
  - 内部使用定时器 + 协议推断切分完整帧，自动处理粘包与超时。

- `SerialThread(QThread)`：
  - 承载 `Serial_Qthread_function` 的事件循环，方便独立启动和停止串口线程。

**帧构造与同步等待：**

- `modbus_RTU(sendbytes_str)`：
  - 输入：不带 CRC 的报文十六进制字符串（如 `'01 03 00 08 00 05'`）。
  - 输出：附加 CRC16 后的字节串 `bytes`，可直接通过串口发送。

- `ModbusSender`：
  - 调用方式：
    - `read_coils(slave_addr, start_addr, quantity)` → hex 字符串（不含 CRC）
    - `read_holding_registers(...)` / `write_single_coil(...)` / `write_multiple_registers(...)` 等。
  - **注意**：返回值为 hex 字符串，需要再通过 `modbus_RTU` 加 CRC 变成 `bytes`。

- `wait_for_last_frame(serial_obj, timeout_ms=2000)`：
  - 在当前事件循环中阻塞，等待 `signal_frameReceived` 到达或超时。
  - 返回：收到的帧的十六进制字符串 `hex_str` 或 `None`。

### 2.3 接收端帧解析：`modbus_receive.py`

- `tUartParms`：
  - 保存一个 Modbus 通道的状态，包括接收缓冲区 `RxData`、当前地址/功能码、计数器、错误统计等。
- `ModBusCounters`：
  - 记录 CRC 错误、地址错误、功能码错误、帧损坏、成功帧计数。
- 关键常量：
  - `ADDR_err, Length_err, FuncID_err, Frame_broken, CRC_err, Frame_OK` 作为状态位。

**主要函数：**

- `InitModBus(UartInfoTmp, Instance, MasterSlave, MyID)`：初始化通道。
- `ModBus_Rcv_Callback(UartInfoTmp, RcvData)`：每收到一个字节即调用，填充缓冲区并驱动状态机。
- `ModBus_TIM_Callback(UartInfoTmp)`：配合定时器判断一帧结束。
- `ModBusCheck(UartInfoTmp)`：帧结束时调用，执行完整检测（地址/长度/功能码/CRC），更新状态与计数器。
- `AnalyFrm(UartInfoTmp)`：仅负责综合校验逻辑，返回状态位。
- `Modbus_receive_Interface(rcv_hex_str)`：
  - 高层入口，输入十六进制字符串（可无空格）。
  - 输出：
    - `RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, MdbsCNT`
  - 根据功能码自动将数据区解释为：
    - 线圈/离散输入 → 位数组
    - 寄存器 → 16 位寄存器值列表

---

## 3. 业务查询函数（函数式版本）

### 3.1 单点查询：`train_function.py`

- `modbus_query(slave_addr, func_ID, start_addr, quantity)`：
  - 使用 `ModbusSender` 构造 PDU → `modbus_RTU` 加 CRC → 串口发送 → `wait_for_last_frame` 获取回应。
  - 返回：回应帧十六进制字符串 `hex_str`（若超时则为 `None`）。

- 业务函数示例（部分）：
  - `transaction_status_query()`：查询牵引车交易/运行状态（读线圈）。
  - `machine_status()`：下料机状态。
  - `valve_open_angel()`：阀门开度。
  - `Lifting_height()`：升降高度。
  - `Flip_plate_height()`：翻板高度。
  - `Full_ornot()`：仓位是否满载。
  - `Load_progress()`：装载进度。
  - `Coal_height()` / `Liaoweiji()`：煤堆/料位高度等。

- `run_queries_in_sequence(functions, index=0)`：
  - 顺序执行给定列表中的函数，每次调用后使用 `Modbus_receive_Interface` 解析并打印结果。
  - 适合在命令行/终端中进行联调。

### 3.2 集群读取（早期函数式版本）：`train_function_groupRead.py`

- 定义一系列“批量区间读取”函数，如：
  - `read_coils_0_13()`：读从站 1 的线圈 0–13。
  - `read_coils_16_24()`、`read_coils_27_31()` 等。
  - `read_holding_registers_0_13()`、`read_holding_registers_16_24()`、`read_holding_registers_32_39()` 等。

- 全局变量：
  - `RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, function_name`：最近一次解析结果。
  - `all_data_dict`：`{function_name: {...}}` 汇总，方便前端展示。

- `save_frame_data()`：
  - 将最近解析结果写入 `all_data_dict[function_name]`。

- `run_queries_in_sequence(functions, index=0)`：
  - 与 `train_function.py` 类似，但在每轮结束后还会等待一段时间后再次从第一条开始轮询。

> 该版本实现清晰直观，适合对协议与业务初步理解，但在线程安全和解耦方面不如 OOP 版本。

---

## 4. OOP 版集群读取与数据仓库（推荐）`train_group_reader_oop.py`

### 4.1 线程安全数据仓库：`SharedDataStore`

- 单例类（通过 `SharedDataStore.instance()` 获取），全局别名 `DATAS`。
- 字段：
  - `RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, function_name`
  - `all_data_dict`：保存所有功能函数最终结果。
- 方法：
  - `write_last_frame(fn_name, RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state)`：
    - 写入最近一帧解析结果。
  - `write_func_result(fn_name, final_result)`：
    - 写入某功能函数的最终结果（可为分析后的字典）。
  - `snapshot()`：
    - 返回线程安全的快照 dict：
      - `{"RxAddr", "RxFuncID", "RxDataLen", "RxData", "Mdbs_state", "function_name", "all_data_dict", "timestamp"}`。
- 信号：
  - `snapshotUpdated(dict)`：任意数据更新时推一次完整快照。
  - `oneFuncUpdated(str, dict)`：某一功能函数结果更新时触发。

> UI 模块可以只依赖 `DATAS`，通过 `snapshot()` 或信号获取所有需要的数据。

### 4.2 串口工作者与 Modbus 客户端

- `SerialPortWorker(port_name, baudrate)`：
  - 内部创建 `Serial_Qthread_function` + `SerialThread`。
  - `start()`：启动线程并打开串口。
  - `stop()`：关闭串口并停止线程。
  - `send_bytes(data: bytes)`：发送报文。
  - 信号：
    - `frameReceived(bytes)`：透传底层 `signal_frameReceived`。

- `ModbusClient`：
  - `modbus_query(slave_addr, func_id, start_addr, quantity)`：
    - 使用 `ModbusSender` 构造 PDU → `modbus_RTU` 加 CRC → `SerialPortWorker.send_bytes` 发送；
    - 使用 `wait_for_last_frame` 获取回应；
    - 返回回应 hex 字符串或 `None`。

- `FrameParser`：
  - `parse(hex_str)`：调用 `Modbus_receive_Interface` 完成解析。

- `Analyzer`：
  - `analyze(func_name, parsed)`：可在此对 `parsed` 进行业务层转换（当前默认透传）。

### 4.3 查询调度与被动监听

- `GroupQueryScheduler`：
  - 构造参数：
    - `modbus_client, parser, functions_list, cycle_interval_ms=5000, analyzer=None`
  - 行为：
    - 按 `functions_list` 顺序依次执行（每次间隔 1 秒）；
    - 每轮结束后等待 `cycle_interval_ms` 再重新开始；
    - 对于每次查询：
      - 调用如 `read_coils_0_13()` → 得到 `(slave, func_id, start, qty)`；
      - `modbus_query(...)` 发送并等待回应；
      - 解析后调用 `DATAS.write_last_frame()` 和 `DATAS.write_func_result()`；
      - 触发相应信号与日志输出。
  - 信号：
    - `oneQueryFinished(func_name, result_dict)`；
    - `oneRoundFinished()`。

- `PassiveListener`：
  - 监听第二个 `SerialPortWorker` 的 `frameReceived` 信号；
  - 每接收一帧，调用 `FrameParser.parse` 解析；
  - 仅更新 `DATAS.write_last_frame("passive_rx", ...)`，不写 `all_data_dict`。

### 4.4 应用入口：`TrainGroupReaderApp`

- 构造：
  - `TrainGroupReaderApp(active_port: str, passive_port: str, baudrate: int = 9600)`
  - 内部创建：
    - `SerialPortWorker(active_port, baudrate)`
    - `SerialPortWorker(passive_port, baudrate)`
    - `ModbusClient` / `FrameParser` / `Analyzer` / `GroupQueryScheduler` / `PassiveListener`
  - 将函数集合（如 `read_coils_0_13`, `read_holding_registers_0_13` 等）注册到调度器。

- 方法：
  - `start()`：启动主动 & 被动串口并开始轮询。
  - `stop()`：停止串口与调度器。

- 使用建议（示意）：

```python
from PyQt5.QtWidgets import QApplication
from train_group_reader_oop import TrainGroupReaderApp, DATAS

app = QApplication([])

backend = TrainGroupReaderApp(active_port="COM5", passive_port="COM6", baudrate=9600)
backend.start()

def on_snapshot(snap: dict):
    print("最新快照:", snap["function_name"], snap["RxData"])

DATAS.snapshotUpdated.connect(on_snapshot)

app.exec_()
backend.stop()
```

---

## 5. 实时监控与相机

### 5.1 相机线程：`camera.py`

- `CameraThread(QThread)`：
  - 构造参数：`device_index=0, width=None, height=None, fps=30, parent=None`
  - 信号：
    - `frameReady(QImage)`：每帧图像发射，供 UI 显示。
    - `startedOk()`：摄像头成功初始化。
    - `error(str)`：错误信息。
  - 方法：
    - `run()`：主循环，使用 `cv2.VideoCapture` 读取帧并转成 `QImage`。
    - `stop(wait_timeout_ms=1000)`：请求线程停止并等待退出。

### 5.2 实时帧查看器：`live_frame_viewer.py`

- `SnapshotReader`：
  - 在独立 `QThread` 内运行，周期性调用 `DATAS.snapshot()`。
  - 信号：
    - `snapshotReady(dict)`：向 UI 发射最新快照。

- `LiveFrameWindow(QMainWindow)`：
  - 展示：
    - 顶部：最近一帧的 `function_name / timestamp / Addr / FuncID / DataLen / 状态 / Data`；
    - 下方表格：`all_data_dict` 中所有功能项的最终结果。

- `AppWithReader(QApplication)`：
  - 若 `START_BACKEND = True`：
    - 内部创建并启动 `TrainGroupReaderApp`（主动+被动采集）。
  - 创建 `LiveFrameWindow` 窗口并启动 `SnapshotReader` 线程。

- 运行方式（示例）：

```bash
cd 上位机代码与资料4.0
conda activate <你的环境>
python Back_end\live_frame_viewer.py
```

---

## 6. 数据库访问

### 6.1 新版通用封装：`database.py`

- `TrainDatabaseManager`：
  - 构造参数：`server, database, username, password, driver="{ODBC Driver 17 for SQL Server}", timeout=5`
  - 方法：
    - `query_all(schema, table)`：`SELECT * FROM [schema].[table]`
    - `query_by_id(schema, table, id_column, value)`：按列精确查询。
    - `insert_row(schema, table, data: dict)`：根据 `data` 插入记录。
    - `update_row_by_id(schema, table, id_column, id_value, data: dict)`：按主键更新部分字段。

### 6.2 旧版示例：`data12.py`

- 同名 `TrainDatabaseManager`，但设计偏向于：
  - 针对具体表（如 `[Train Model Table]`, `[Train Arrival Table]` 等）提供专用方法：
    - `get_all_train_models()` / `add_train_model(...)`
    - `get_train_arrivals()` / `update_train_arrival_status(...)`
    - `get_train_speeds()` / `add_speed_record(...)`
    - `get_inventory_records()` / `add_inventory_record(...)`
    - `get_layoff_history()` / `add_layoff_record(...)`
- 适合作为理解数据库结构和业务流程的参考实现。

---

## 7. 环境自检脚本：`env_test.py`

简单脚本用于检查当前解释器与依赖是否正确安装：

```bash
cd 上位机代码与资料4.0
conda activate <你的环境>
python Back_end\env_test.py
```

将输出：

- Python 可执行文件路径与版本；
- 平台信息；
- 尝试导入 `PyQt5`, `PyQt5.QtWidgets`, `PyQt5.QtSerialPort`, `pyodbc`, `cv2` 等模块的结果（[OK]/[FAIL]）。

如某模块为 `[FAIL]`，请根据提示安装对应包后重试。


