## 火车下料自动化装置上位机（Automatic Feeding System for Locomotives）

本仓库为“火车下料自动化装置”上位机软件 4.0 版本的源码与资料，主要功能包括：

- 与 **PLC** 通过 **Modbus RTU** 通信，实时采集牵引车、下料机、仓位等状态数据；
- 采集 **传感器数据**（速度、料位、装载进度等），并在前端进行可视化；
- 与 **SQL Server 数据库** 交互，存储火车信息、出入库记录、下料历史等业务数据；
- 提供 **数字孪生/上位机 UI**，包括主界面、火车控制、仓库管理、历史查询等；
- 提供技术文档与调试工具，方便部署与二次开发。

---

## 目录结构概览

- `UI/`：Qt Designer 设计的各类 `.ui` 界面文件，以及对应的 Python 绑定代码。
- `Back_end/`：后端核心逻辑（Modbus 通信、数据采集、多线程、数据库访问、相机等）。
- `SQL/`：SQL Server 数据库脚本（建库、建表、触发器、测试数据等）。
- `参考文档/`：总体架构、数据库设计、通信协议、技术日志等 Word/PDF 文档。
- `软件工具/`：串口 & Modbus 调试工具（如 MODBUS 调试助手、sscom）。
- `setup.py`：项目安装/打包相关脚本（如有需要可扩展）。
- `readme.txt`：早期简要说明（已被本 `README.md` 覆盖，保留兼容）。

---

## 运行环境与依赖

### 操作系统

- 推荐：**Windows 10 / 11**（当前项目路径与工具均以 Windows 为主）。

### Python & Conda（推荐）

- Python 版本：建议 **3.8–3.10**
- 建议使用 Anaconda / Miniconda 管理虚拟环境：

```bash
conda create -n locomotives python=3.10 -y
conda activate locomotives
```

### 主要第三方依赖

后端模块中用到的核心依赖：

- `PyQt5`：GUI、串口通信（`QtWidgets`, `QtSerialPort`, `QtCore`, `QtGui`）
- `pyodbc`：连接 SQL Server 数据库
- `opencv-python`（`cv2`）：相机视频采集与图像处理

示例安装命令（conda 为主，pip 备选）：

```bash
# 使用 conda
conda install pyqt pyodbc -y
conda install -c conda-forge opencv -y

# 或使用 pip
pip install PyQt5 pyodbc opencv-python
```

---

## 项目模块说明

### 1. UI 前端（`UI/`）

#### 1.1 Qt 界面文件

- `main.ui`：主界面（总体入口）
- `train.ui`：火车/车厢信息相关界面
- `train_control.ui`：火车运行与下料控制界面
- `train_warehouse_management.ui`：仓库/车厢出入库管理
- `train_warehouse_update.ui`：仓库配置更新界面
- `train_label.ui`：车厢标识/标签管理
- `machine_history.ui`：下料历史记录、日志展示

> `.ui` 文件可以用 Qt Designer 打开修改，保存后通过 `pyuic5` 生成对应 Python 文件。

#### 1.2 生成的 UI Python 文件

由 `pyuic` 生成，供业务逻辑直接继承或组合使用：

- `Ui_main.py`
- `Ui_train.py`
- `Ui_train_control.py`
- `Ui_train_warehouse_management.py`
- `Ui_train_warehouse_update.py`
- `Ui_train_label.py`
- `Ui_machine_history.py`

#### 1.3 窗口组织与多窗口管理

- `multi_windows.py`：负责多窗口之间的切换和管理（例如主界面跳转到火车控制界面、仓库管理界面等）。
- `qt_test.py`：用于快速测试 UI 与基本交互的示例脚本。

#### 1.4 资源与图片

- `pictures.qrc` / `pictures_rc.py`：Qt 资源文件（图标、图片等），由 `pyrcc5` 生成。
- `下煤机.jpg`、`火车.jpg`：界面中使用的背景或图示资源。

> 前端 UI 通过信号/槽或轮询方式，调用 `Back_end` 中的数据接口（例如数据库查询、实时采集的 Modbus 数据），实现数字孪生效果。

---

### 2. 后端核心逻辑（`Back_end/`）

后端采用 **模块化 + 线程化 + OOP 数据仓库** 的设计，主要负责：

- 通过串口与 PLC 通讯（Modbus RTU）
- 集群式轮询读取多组线圈/寄存器
- 被动监听上位系统/设备的 Modbus 帧
- 数据解析与分析，并提供线程安全的数据快照给 UI
- 与 SQL Server 数据库交互
- 相机图像采集与实时监控窗口

> 详细的后端模块说明和接口表请参考 `Back_end/readme.txt`（中文详细文档），这里只做概要。

#### 2.1 Modbus 通信相关

- `modbus_RTU.py`
  - 提供 `Binary` 进制转换工具。
  - 提供 `CRC` 类，计算 Modbus RTU CRC16 校验（0xA001 多项式）。
  - 被所有 Modbus 发送逻辑使用，用于生成完整合法报文。

- `modbus_send.py`
  - 使用 `QSerialPort` 封装串口发送端（主站）：
    - `Serial_Qthread_function`：在 QThread 中运行，负责打开/关闭串口、发送数据、接收数据。
    - 支持自动按 **T3.5**（沉默间隔）切分 Modbus 帧，并通过 `signal_frameReceived` 发射完整帧。
  - `ModbusSender`：
    - 封装各类 Modbus 功能码的 PDU 构造（`read_holding_registers`、`write_single_coil` 等，不带 CRC）。
  - `modbus_RTU(...)`：
    - 按 Modbus RTU 协议在尾部追加 CRC，返回可直接发送的 `bytes`。
  - `wait_for_last_frame(...)`：
    - 阻塞等待一帧回应（带超时），返回十六进制字符串，方便上层调用。

- `modbus_receive.py`
  - 实现 Modbus RTU 帧解析状态机（`tUartParms` / `ModBusCounters`）：
    - 字节级接收（`ModBus_Rcv_Callback`）、定时器回调（`ModBus_TIM_Callback`）、帧检查（`ModBusCheck`）。
    - 完整的 CRC 校验（表驱动）、地址/功能码/长度校验、错误统计。
  - 提供高层解析接口：
    - `Modbus_receive_Interface(rcv_hex_str)`：输入一帧十六进制字符串，输出（地址、功能码、数据长度、解析后的数据列表、状态位、错误计数）。

#### 2.2 单点查询与集群查询（函数式版本）

- `train_function.py`
  - 为业务含义更清晰的“单项查询”提供包装，例如：
    - `transaction_status_query()`：牵引车运行状态
    - `machine_status()`：下料机状态
    - `valve_open_angel()`：阀门开度
    - `Lifting_height()`：升降高度
    - `Full_ornot()`：仓位满载状态
    - `Load_progress()`：装载进度
  - 底层统一调用 `modbus_query(...)`：
    - 构造帧 → 通过 `modbus_RTU` 加 CRC → 串口发送 → 阻塞等待回应 → 得到 RTU 帧 hex 字符串。
  - 提供 `run_queries_in_sequence(...)`，可以顺序调用一批函数，用于调试或一轮采集。

- `train_function_groupRead.py`
  - 早期版本的“集群读取脚本”，一次读取多个线圈/寄存器区间：
    - `read_coils_0_13()`、`read_coils_16_24()`、`read_holding_registers_0_13()` 等。
  - 全局字典 `all_data_dict`：
    - 保存 `{function_name: {'RxAddr','RxFuncID','RxDataLen','RxData','Mdbs_state'}}` 的解析结果。
  - 提供 `run_queries_in_sequence(...)`：
    - 在一个线程里按顺序执行所有读函数，每轮结束等待数秒后再循环。
  - 适合命令行调试和与 UI 松耦合集成。

#### 2.3 OOP 版集群读取 & 线程安全数据仓库（推荐）

- `train_group_reader_oop.py`
  - **核心设计：将全局状态升级为 OOP + 线程安全数据仓库**：
    - `SharedDataStore`（单例）：
      - 存储最近一帧数据：`RxAddr, RxFuncID, RxDataLen, RxData, Mdbs_state, function_name`
      - 存储所有功能函数最终结果：`all_data_dict`
      - 提供 `snapshot()` 方法返回带时间戳的完整快照：
        - `{ "RxAddr", "RxFuncID", "RxDataLen", "RxData", "Mdbs_state", "function_name", "all_data_dict", "timestamp" }`
      - 发射信号：
        - `snapshotUpdated(dict)`：任意数据更新时推送完整快照
        - `oneFuncUpdated(str, dict)`：单个功能函数结果更新时推送
      - 全局别名：
        - `DATAS = SharedDataStore.instance()`，推荐 UI 与其它模块通过 `DATAS` 访问。
    - `SerialPortWorker`：
      - 包装 `Serial_Qthread_function` 与 `SerialThread`，负责某个串口的生命周期管理（启动、停止、发送）。
    - `ModbusClient`：
      - 统一执行一次 Modbus 查询（构帧 + 发送 + 等待响应），返回回应帧 hex。
    - `FrameParser` & `Analyzer`：
      - 解析 RTU 帧为结构化字段，并可在 `Analyzer` 中加入业务含义转换（当前示例为透传）。
    - `GroupQueryScheduler`：
      - 管理 **主动轮询任务**：
        - 按给定函数列表顺序调用（如 `read_coils_0_13` 等），每条之间有间隔。
        - 每一轮结束后，等待一段时间再从头执行下一轮。
      - 每次有效查询会调用 `DATAS.write_last_frame(...)` 与 `DATAS.write_func_result(...)`，并触发信号。
    - `PassiveListener`：
      - 处理**第二路串口**（被动监听）的帧，将解析结果写入“最近一帧”，但不影响 `all_data_dict`。
    - `TrainGroupReaderApp`：
      - 整体装配类：
        - 构造：`TrainGroupReaderApp(active_port, passive_port, baudrate=9600)`
        - 方法：
          - `start()`：启动主动 & 被动串口线程，开始轮询。
          - `stop()`：关闭串口与线程。
      - UI 推荐直接使用此类作为后台采集进程的入口。

#### 2.4 实时监控窗口 & 相机模块

- `camera.py`
  - `CameraThread`：继承自 `QThread`，使用 OpenCV 捕获摄像头图像；
  - 每一帧转换为 `QImage`，通过 `frameReady(QImage)` 信号发给 UI；
  - 提供 `stop()` 方法优雅关闭线程，避免资源泄漏。

- `live_frame_viewer.py`
  - 提供一个独立的 Qt 程序，用于 **实时查看 Modbus 数据帧**：
    - `SnapshotReader`：在子线程中周期性读取 `DATAS.snapshot()` 并发射 `snapshotReady(dict)`；
    - `LiveFrameWindow`：美观的 UI 窗口，展示：
      - 最近一帧的 `function_name / timestamp / Addr / FuncID / DataLen / 状态 / Data`
      - `all_data_dict` 的汇总表格（每行一个功能函数最终结果）。
    - `AppWithReader`：
      - `START_BACKEND = True` 时，会在同一个进程中启动 `TrainGroupReaderApp`（主动+被动采集）；
      - 启动方式：

```bash
cd 上位机代码与资料4.0
conda activate locomotives
python Back_end\live_frame_viewer.py
```

> 这个程序同时展示“最近一帧”和“所有功能结果”，非常适合作为调试和演示入口。

#### 2.5 数据库访问

- `database.py`
  - 新版通用数据库管理器 `TrainDatabaseManager`：
    - 基于 `pyodbc`，面向 SQL Server。
    - 支持：
      - `query_all(schema, table)`：查询整张表，返回 `(columns, rows)`。
      - `query_by_id(schema, table, id_column, value)`：按主键或指定列精确查询。
      - `insert_row(schema, table, data: dict)`：按字典字段插入数据。
      - `update_row_by_id(schema, table, id_column, id_value, data: dict)`：部分字段更新。
  - 适合作为 UI 或业务逻辑访问数据库的统一封装。

- `data12.py`
  - 旧版数据库管理示例，包含针对具体表的业务方法（火车型号表、到位表、速度表、入库表、下料历史表等）。
  - 部分接口已不再推荐直接使用，但对理解业务模型与表结构很有帮助。

#### 2.6 环境测试脚本

- `env_test.py`
  - 简单自检脚本，打印：
    - 当前 Python 可执行文件路径 (`sys.executable`)
    - Python 版本
    - 平台信息
    - 尝试导入 `PyQt5` / `pyodbc` / `cv2` 等模块并打印 `[OK]` 或 `[FAIL]`
  - 运行方式：

```bash
cd 上位机代码与资料4.0
conda activate locomotives   # 或你的环境名
python Back_end\env_test.py
```

---

### 3. 数据库脚本（`SQL/`）

- `创建数据库及表单约束.sql`：创建主数据库与关键表结构。
- `创建日志表单.sql`：与日志/历史记录相关的表结构。
- `插入测试数据.sql`：插入测试用例数据，便于联调与演示。
- `触发器.sql`：定义数据库级触发器，用于自动维护业务一致性或日志。

> 具体字段与业务含义可参考 `参考文档/数据库设计2.x.*` 以及 SQL 脚本中的注释。

---

### 4. 文档与工具

#### 4.1 参考文档（`参考文档/`）

包含整个系统重要的技术文档：

- 通信协议与数据映射：
  - `COM1工控机与PLC间Modbus通信数据地址定义与数据库变量对应.*`
  - `COM1工控机与数字孪生软件之间数据API口定义.*`
  - `modbus协议帧格式.png`
  - `plc通信.docx`
- 上位机产品 & 数字孪生：
  - `火车下料自动化装置上位机产品文档.docx`
  - `数字孪生软件1.0.docx`
- 数据库设计：
  - `数据库设计2.0.docx` / `数据库设计2.1.docx` / `数据库设计2.2.*`
  - `火车下料上位机数据库技术文档.pdf`
- 其他：
  - `技术日志6.28.docx`
  - `用例设计.docx`
  - `装车系统架构.docx`
  - `架构图.vsdx`

> 在理解/扩展代码前，建议先快速浏览 **协议文档** 与 **数据库设计文档**，可帮助快速对齐业务语义。

#### 4.2 软件工具（`软件工具/`）

- `MODBUS调试助手10/`：
  - 包含 `MODBUS调试助手.exe` 与配置文件；
  - 可用于在没有实际 PLC 或上位机时模拟 Modbus 主站/从站，验证通信是否正常。
- `sscom/`：
  - 串口调试助手 `sscom5.13.1.exe`，可直接收发串口数据包。

---

## 快速上手与运行示例

### 1. 准备数据库（可选，但推荐）

1. 在 SQL Server 中执行 `SQL/创建数据库及表单约束.sql`，创建数据库与表结构。
2. 如需测试数据，执行 `SQL/插入测试数据.sql`。
3. 确认数据库连接信息与 `database.py` / `data12.py` 中配置一致。

### 2. 准备 Python 环境

```bash
conda create -n locomotives python=3.10 -y
conda activate locomotives
conda install pyqt pyodbc -y
conda install -c conda-forge opencv -y
```

运行环境自检：

```bash
cd 上位机代码与资料4.0
python Back_end\env_test.py
```

确保大部分依赖 `[OK]`。

### 3. 启动后端集群采集 + 实时监控

1. 确认与你实际 PLC 相连的串口号，例如：
   - 主动轮询口：`COM5`
   - 被动监听口：`COM6`
2. 修改 `Back_end/train_group_reader_oop.py` / `live_frame_viewer.py` 中默认端口（如有需要）。
3. 在终端中运行：

```bash
cd 上位机代码与资料4.0
conda activate locomotives
python Back_end\live_frame_viewer.py
```

若 `START_BACKEND = True`，将：

- 启动后台 Modbus 集群采集（主动轮询 + 被动监听）；
- 打开实时监控窗口，动态显示 Modbus 帧与解析结果。

### 4. 启动 UI 主界面（示意）

根据你的实际入口脚本（例如你自己的 `main.py` 或 `multi_windows.py` 中的入口），示意运行方式可能类似：

```bash
cd 上位机代码与资料4.0
conda activate locomotives
python UI\multi_windows.py
```

> 具体 UI 入口会依你项目实际主程序为准；若需要，我可以再为你整理一份专门的“UI 启动说明”，包括信号如何连接 `Back_end`。

---

## 开发与二次扩展建议

- **新增 PLC 变量/传感器读取：**
  - 在 `train_group_reader_oop.py` 中新增一个形如 `read_xxx()` 的函数，返回 `(slave, func_id, start_addr, qty)`。
  - 将该函数加入 `functions` 列表中，使其被 `GroupQueryScheduler` 轮询。
  - 在 `Analyzer.analyze()` 中针对该函数名进行业务含义转换（如单位、阈值、状态枚举等）。
- **UI 展示新数据：**
  - 在 UI 代码中订阅 `DATAS.snapshotUpdated` 或 `DATAS.oneFuncUpdated` 信号；
  - 在回调里解析 `snap["all_data_dict"][function_name]` 并刷新界面控件。
- **数据库联动：**
  - 使用 `database.py` 中的 `TrainDatabaseManager` 统一访问数据库；
  - 将实时采集到的关键事件（如下料开始/结束、报警状态）写入数据库表中，便于历史追溯。

---

## License & 说明

本项目包含大量企业/项目级技术文档与专用协议，**请在遵守所属单位/项目的保密与使用规范前提下使用本仓库代码**。  
如需对外发布或商用集成，请根据所在单位规范进行审批与脱敏处理。


