import sys
from PyQt5.QtWidgets import (QMainWindow, QDialog, QApplication, QMessageBox, 
                            QLineEdit, QVBoxLayout, QLabel, QPushButton, QWidget)
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QGroupBox, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication
from UI.Ui_train import Ui_MainWindow  # 主界面
from UI.Ui_main import Ui_Dialog       # 子界面
from UI.Ui_machine_history import Ui_layoff_history  # 下料历史界面
from UI.Ui_train_warehouse_management import Ui_TrainQuery  # 火车型号管理界面
from UI.Ui_train_warehouse_update import Ui_TrainQuery as Ui_TrainUpdate  # 火车型号更新界面


# ====== 是否在同进程内启用后端采集（主动串口 + 被动串口） ======
START_BACKEND = True  # 如需同进程采集改为 True
ACTIVE_PORT   = "COM4"
PASSIVE_PORT  = "COM2"
BAUDRATE      = 9600

# ====== 导入后端数据仓库（DATAS）及可选：后端应用（TrainGroupReaderApp） ======
from Back_end.train_group_reader_oop import DATAS  # 单例数据仓库：含 snapshot(), oneFuncUpdated/snapshotUpdated 信号

if START_BACKEND:
    from Back_end.train_group_reader_oop import TrainGroupReaderApp


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


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("登录")
        self.setFixedSize(300, 150)
        
        # 创建控件
        self.label_username = QLabel("用户名:")
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("请输入用户名")
        
        self.label_password = QLabel("密码:")
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("请输入密码")
        self.input_password.setEchoMode(QLineEdit.Password)
        
        self.button_login = QPushButton("登录")
        self.button_login.clicked.connect(self.check_login)
        
        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.label_username)
        layout.addWidget(self.input_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.button_login)
        
        self.setLayout(layout)
    
    def check_login(self):
        username = self.input_username.text()
        password = self.input_password.text()
        
        # 验证用户名和密码
        if username == "123456" and password == "123456":
            self.accept()  # 关闭对话框并返回QDialog.Accepted
        else:
            QMessageBox.warning(self, "警告", "用户名或密码错误！")
            self.input_password.clear()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 绑定按钮点击事件
        self.pushButton_8.clicked.connect(self.open_train_management)  # "火车型号尺寸"按钮
        self.pushButton_7.clicked.connect(self.open_machine_history)   # "下料历史查询"按钮
        
        self.backend = None
        if START_BACKEND:
            self.backend = TrainGroupReaderApp(ACTIVE_PORT, PASSIVE_PORT, BAUDRATE)
            self.backend.start()

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

    def open_train_management(self):
        # 创建火车型号管理子窗口
        self.train_management_window = TrainManagementWindow()
        self.train_management_window.show()
        
    def open_machine_history(self):
        # 创建下料历史子窗口
        self.machine_history_window = MachineHistoryWindow()
        self.machine_history_window.show()
    
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

class TrainManagementWindow(QMainWindow, Ui_TrainQuery):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 设置窗口标题
        self.setWindowTitle("火车型号尺寸信息管理系统")
        
        # 绑定按钮点击事件
        self.pushButton_11.clicked.connect(self.open_train_update)  # "新增/修改"按钮
        
    def open_train_update(self):
        # 创建火车型号更新子窗口
        self.train_update_window = TrainUpdateWindow()
        self.train_update_window.show()


class TrainUpdateWindow(QMainWindow, Ui_TrainUpdate):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 设置窗口标题
        self.setWindowTitle("火车型号尺寸更新系统")


class MachineHistoryWindow(QMainWindow, Ui_layoff_history):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 设置窗口标题
        self.setWindowTitle("下料历史趋势主界面")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 设置应用程序样式
    app.setStyle("Fusion")
    
    # # 创建并显示主窗口
    # window = MainWindow()
    # window.show()
    
    # sys.exit(app.exec_())
        # 设置应用程序样式

    # 显示登录对话框
    login = LoginDialog()
    if login.exec_() == QDialog.Accepted:
        # 登录成功，创建并显示主窗口
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    else:
        # 用户取消登录或关闭对话框
        sys.exit(0)