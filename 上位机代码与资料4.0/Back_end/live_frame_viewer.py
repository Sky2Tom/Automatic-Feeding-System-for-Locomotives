# -*- coding: utf-8 -*-
"""
live_frame_viewer.py
---------------------------------
单开一个线程，定时读取“最近一帧”数据，并用 Qt 窗口实时展示。
数据来源：train_group_reader_oop.py 中的 DATAS（SharedDataStore 单例）

两种使用方式：
1) 与后端同进程（推荐调试）：把 START_BACKEND = True，并在下面配置你的串口参数；
   这样一个进程里既启动采集（主动+被动串口），又启动本窗口。
2) 已有后端在同进程里运行：把 START_BACKEND = False，此窗口只读 DATAS 来展示。

如需跨进程展示（独立运行后端与前端），需要引入 IPC/网络通讯，这不在本文件范围。
"""

import sys
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QGroupBox, QFrame, QSpacerItem, QSizePolicy
)


# ====== 是否在同进程内启用后端采集（主动串口 + 被动串口） ======
START_BACKEND = True  # 如需同进程采集改为 True
ACTIVE_PORT   = "COM4"
PASSIVE_PORT  = "COM2"
BAUDRATE      = 9600

# ====== 导入后端数据仓库（DATAS）及可选：后端应用（TrainGroupReaderApp） ======
from train_group_reader_oop import DATAS  # 单例数据仓库：含 snapshot(), oneFuncUpdated/snapshotUpdated 信号

if START_BACKEND:
    from train_group_reader_oop import TrainGroupReaderApp


# ------------------------------------------------------------------------------------
# 读取线程：运行在独立 QThread 中，定时（QTimer）拉取 DATAS.snapshot() 并向 UI 发射信号
# ------------------------------------------------------------------------------------
# 替换 live_frame_viewer.py 中的 SnapshotReader 类

class SnapshotReader(QObject):
    snapshotReady = pyqtSignal(dict)  # 向 UI 发射最新快照

    def __init__(self, interval_ms=200):
        super().__init__()
        self._interval_ms = interval_ms
        self._timer = None   # 注意：不要在 __init__ 里建 QTimer（此时还在主线程）

    def start(self):
        # 现在 self 已经在子线程（由 moveToThread 完成），此时创建 QTimer 才会隶属于子线程
        if self._timer is None:
            self._timer = QTimer(self)       # 让 QObject parent= self（已在子线程）
            self._timer.setInterval(self._interval_ms)
            self._timer.setSingleShot(False)
            self._timer.timeout.connect(self._tick)
        self._timer.start()

    def stop(self):
        if self._timer:
            self._timer.stop()

    def _tick(self):
        snap = DATAS.snapshot()  # 线程安全快照
        # 给个兜底：如果后台还没跑起来，至少让 UI 有反馈
        if not snap.get("timestamp"):
            snap["timestamp"] = "no data yet"
        self.snapshotReady.emit(snap)

        # ！！！非常重要：如果想要具体的plc和传感器数据显示，请使用线程安全的形式（快照）
        # print(snap['all_data_dict']['read_coils_0_13'])
        """ 结果：{
                    'RxAddr': 1,
                    'RxFuncID': 3,
                    'RxDataLen': 14,
                    'RxData': [...],         # ← 你想要的数据
                    'Mdbs_state': 128,
                    'function_name': 'read_coils_0_13',
                    'all_data_dict': {...},  # ← 你想要的字典副本
                    'timestamp': '2024-06-16 14:55:12'
                }"""


# ------------------------------------------------------------------------------------
# 窗口：展示最近一帧的关键字段 + 汇总 all_data_dict
# ------------------------------------------------------------------------------------
class LiveFrameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚄 Live Frame Viewer")
        self.resize(960, 640)

        # —— 清爽浅色主题 + 顶部加大字号 —— #
        self.setStyleSheet("""
            QMainWindow { background-color: #fdfdfd; color: #222; }
            QLabel { font-size: 15px; color: #333; }
            QLabel[role='title'] { font-size: 20px; font-weight: 700; color: #0078d7; }
            QLabel[role='badge'] { font-size: 14px; font-weight: 700; padding: 2px 8px; border-radius: 10px; }
            QGroupBox { 
                border: 1px solid #dcdcdc; border-radius: 8px; margin-top: 18px;
                background: #ffffff;
            }
            QGroupBox::title { 
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 6px; color: #0078d7; font-weight: 700; font-size: 16px;
            }
            QFrame#TopBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #e9f3ff, stop:1 #f4fbff);
                border-bottom: 1px solid #d3e6ff;
            }
            QTableWidget {
                background: #ffffff; alternate-background-color: #f7f7f7;
                gridline-color: #bbb; color: #222;
                selection-background-color: #cce5ff; selection-color: #000;
            }
            QHeaderView::section {
                background-color: #eef2f7; color: #333;
                padding: 6px; border: 1px solid #d7dde5; font-weight: 600;
            }
            QPushButton {
                background-color: #0078d7; color: #fff; padding: 8px 14px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #3399ff; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(12)

        # ===== 顶部信息组（带浅色背景条） =====
        top_group = QGroupBox("最近一帧")
        top_group_layout = QVBoxLayout(top_group)
        top_group_layout.setContentsMargins(10, 10, 10, 10)
        top_group_layout.setSpacing(10)

        # 顶部彩色条
        top_bar = QFrame()
        top_bar.setObjectName("TopBar")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(10, 8, 10, 8)
        top_bar_layout.setSpacing(10)

        self.lb_fn = QLabel("function_name: ")
        self.lb_fn.setProperty("role", "title")
        self.lb_ts = QLabel("timestamp: ")
        self.lb_ts.setProperty("role", "title")

        top_bar_layout.addWidget(self.lb_fn, 1)
        top_bar_layout.addWidget(self.lb_ts, 0)
        top_group_layout.addWidget(top_bar)

        # 关键信息行
        row2 = QHBoxLayout()
        row2.setSpacing(16)
        self.lb_addr  = QLabel("Addr: ")
        self.lb_func  = QLabel("FuncID: ")
        self.lb_len   = QLabel("DataLen: ")
        self.lb_state = QLabel("State: ")
        self.lb_data  = QLabel("Data: ")

        # 状态加“胶囊色块”
        self.badge_state = QLabel("STATE")
        self.badge_state.setProperty("role", "badge")
        self.badge_state.setStyleSheet("QLabel[role='badge']{ background:#ffdede; color:#b00020; }")

        # 第二行：地址/功能码/长度/状态Badge
        row2.addWidget(self.lb_addr, 1)
        row2.addWidget(self.lb_func, 1)
        row2.addWidget(self.lb_len, 1)
        row2.addSpacerItem(QSpacerItem(12, 12, QSizePolicy.Expanding, QSizePolicy.Minimum))
        row2.addWidget(self.badge_state, 0)

        top_group_layout.addLayout(row2)
        top_group_layout.addWidget(self.lb_state)
        top_group_layout.addWidget(self.lb_data)

        root.addWidget(top_group)

        # ===== 下方表格（汇总） =====
        self.tbl = QTableWidget(0, 2)
        self.tbl.setHorizontalHeaderLabels(["function_name", "final_result"])
        self.tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tbl.setAlternatingRowColors(True)
        root.addWidget(self.tbl, stretch=1)

        # ===== 底部按钮 =====
        bottom = QHBoxLayout()
        bottom.addSpacerItem(QSpacerItem(12, 12, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_clear = QPushButton("清空表格")
        self.btn_clear.clicked.connect(self._clear_table)
        bottom.addWidget(self.btn_clear)
        root.addLayout(bottom)

        self._seen_funcs = set()

    # —— 数据刷新（含彩色状态） —— #
    def on_snapshot(self, snap: dict):
        fn   = snap.get("function_name", "")
        ts   = snap.get("timestamp", "")
        addr = snap.get("RxAddr", 0)
        fid  = snap.get("RxFuncID", 0)
        dlen = snap.get("RxDataLen", 0)
        state= snap.get("Mdbs_state", 0)
        data = snap.get("RxData", [])

        self.lb_fn.setText(f"function_name: {fn}")
        self.lb_ts.setText(f"timestamp: {ts}")
        self.lb_addr.setText(f"Addr: {addr}")
        self.lb_func.setText(f"FuncID: {fid}")
        self.lb_len.setText(f"DataLen: {dlen}")

        # ✅/❌ + 胶囊色块
        if state:  # 这里按你后端的判定使用非零即 OK；如需严格按 Frame_OK，可改 (state & 0x01)
            self.lb_state.setText("State: ✅ 收发正常")
            self.lb_state.setStyleSheet("color: #2e7d32; font-weight: 700;")
            self.badge_state.setText("OK")
            self.badge_state.setStyleSheet("QLabel[role='badge']{ background:#e5f7ea; color:#1b5e20; }")
        else:
            self.lb_state.setText(f"State: ❌ {state}")
            self.lb_state.setStyleSheet("color: #b00020; font-weight: 700;")
            self.badge_state.setText("NG")
            self.badge_state.setStyleSheet("QLabel[role='badge']{ background:#ffdede; color:#b00020; }")

        # Data 更醒目（有值蓝色，无值灰色）
        if data:
            self.lb_data.setText(f"Data: {data}")
            self.lb_data.setStyleSheet("color:#0057b8; font-weight:600;")
        else:
            self.lb_data.setText("Data: (暂无数据)")
            self.lb_data.setStyleSheet("color:#888; font-weight:400;")

        # 汇总
        all_dict = snap.get("all_data_dict", {})
        self._refresh_table(all_dict)

    # —— 表格逻辑不变 —— #
    def _refresh_table(self, all_dict: dict):
        for fn, final_res in all_dict.items():
            text_val = str(final_res)
            row = self._find_row_by_fn(fn)
            if row is None:
                r = self.tbl.rowCount()
                self.tbl.insertRow(r)
                self.tbl.setItem(r, 0, QTableWidgetItem(fn))
                self.tbl.setItem(r, 1, QTableWidgetItem(text_val))
                self._seen_funcs.add(fn)
            else:
                self.tbl.setItem(row, 1, QTableWidgetItem(text_val))

    def _find_row_by_fn(self, fn: str):
        if fn not in self._seen_funcs:
            return None
        for r in range(self.tbl.rowCount()):
            item = self.tbl.item(r, 0)
            if item and item.text() == fn:
                return r
        return None

    def _clear_table(self):
        self.tbl.setRowCount(0)
        self._seen_funcs.clear()

# ------------------------------------------------------------------------------------
# 应用启动
# ------------------------------------------------------------------------------------
class AppWithReader(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # （可选）在同进程内启动后端
        self.backend = None
        if START_BACKEND:
            self.backend = TrainGroupReaderApp(ACTIVE_PORT, PASSIVE_PORT, BAUDRATE)
            self.backend.start()

        # GUI
        self.win = LiveFrameWindow()
        self.win.show()

        # 读取线程
        self.reader_thread = QThread()
        self.reader = SnapshotReader(interval_ms=200)  # 200ms 刷新一次
        self.reader.moveToThread(self.reader_thread)

        # 连接信号
        self.reader_thread.started.connect(self.reader.start)
        self.reader.snapshotReady.connect(self.win.on_snapshot)

        self.aboutToQuit.connect(self._cleanup)

        # 启动线程
        self.reader_thread.start()

    def _cleanup(self):
        try:
            self.reader.stop()
        except Exception:
            pass
        self.reader_thread.quit()
        self.reader_thread.wait()

        if self.backend is not None:
            self.backend.stop()


if __name__ == "__main__":
    app = AppWithReader(sys.argv)
    sys.exit(app.exec_())
