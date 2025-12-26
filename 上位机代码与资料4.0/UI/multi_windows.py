import sys
from typing import Dict, Any, Optional, Union
from PyQt5.QtWidgets import (QMainWindow, QDialog, QApplication, QMessageBox, 
                            QLineEdit, QVBoxLayout, QLabel, QPushButton, QWidget)
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer, Qt, QCoreApplication
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton,
    QGroupBox, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication
from Ui_train import Ui_MainWindow  # 主界面
from Ui_main import Ui_Dialog       # 子界面
from Ui_machine_history import Ui_layoff_history  # 下料历史界面
from Ui_train_warehouse_management import Ui_TrainQuery  # 火车型号管理界面
from Ui_train_warehouse_update import Ui_TrainQuery as Ui_TrainUpdate  # 火车型号更新界面
from Ui_train_control import Ui_Traincontrol  # 下料机控制界面
from Ui_train_label import Ui_Trainlabel  # 火车视觉识别界面
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QSizePolicy, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import QRectF
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices, QFont, QScreen
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QTextBrowser, QTextEdit
import csv
from pathlib import Path
# ====== 是否在同进程内启用后端采集（主动串口 + 被动串口） ======
START_BACKEND = True  # 如需同进程采集改为 True
ACTIVE_PORT   = "COM4"
PASSIVE_PORT  = "COM2"
BAUDRATE      = 9600

import os
# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（即 abc 和 backend 的父目录）
project_root = os.path.dirname(current_dir)
# 将 backend 所在目录添加到 Python 路径
sys.path.append(os.path.join(project_root, "Back_end"))

# ====== 导入后端数据仓库（DATAS）及可选：后端应用（TrainGroupReaderApp） ======
from train_group_reader_oop import DATAS  # 单例数据仓库：含 snapshot(), oneFuncUpdated/snapshotUpdated 信号
from camera import CameraThread
from data12 import TrainDatabaseManager
if START_BACKEND:
    from train_group_reader_oop import TrainGroupReaderApp

# PaddleOCR 可选导入（如果导入失败，OCR功能将不可用）
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError as e:
    print(f"警告: PaddleOCR导入失败，OCR功能将不可用: {e}")
    PaddleOCR = None
    PADDLEOCR_AVAILABLE = False
except Exception as e:
    print(f"警告: PaddleOCR初始化错误，OCR功能将不可用: {e}")
    PaddleOCR = None
    PADDLEOCR_AVAILABLE = False
# ============================================================================
# UI样式系统和响应式布局工具类
# ============================================================================
class UIStyleManager:
    """
    统一的UI样式管理器
    提供科技感界面样式和深度的响应式缩放支持
    """
    
    @staticmethod
    def get_modern_style() -> str:
        """
        获取黑白灰简约风格UI样式表
        """
        return """
        /* ========== 全局样式 - 黑白灰色调 ========== */
        QMainWindow, QDialog, QWidget {
            background-color: #f5f5f5; /* 浅灰色背景 */
            color: #000000;            /* 纯黑色文字 */
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif;
        }
        
        /* ========== 按钮样式 - 简约灰色 ========== */
        QPushButton {
            background-color: #e0e0e0; /* 灰色按钮 */
            color: #000000;            /* 黑色文字 */
            border: 1px solid #999999;
            border-radius: 4px;
            padding: 5px 15px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #d0d0d0;
            border: 1px solid #666666;
        }
        
        QPushButton:pressed {
            background-color: #c0c0c0;
        }
        
        /* 退出按钮 - 深灰色警示 */
        QPushButton[objectName="pushButton"] {
            background-color: #d32f2f;
            color: #ffffff;
            border: 1px solid #b71c1c;
        }
        
        QPushButton[objectName="pushButton"]:hover {
            background-color: #f44336;
        }
        
        /* ========== 输入与显示框 - 白色背景+黑色文字 ========== */
        QLineEdit, QTextEdit, QTextBrowser, QTableWidget {
            background-color: #ffffff; /* 框内纯白 */
            border: 1px solid #cccccc; /* 灰色边框 */
            border-radius: 2px;
            color: #000000;            /* 黑色文字/数字 */
            gridline-color: #eeeeee;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border: 1px solid #000000;
            background-color: #ffffff;
        }
        
        /* ========== 表格头样式 ========== */
        QHeaderView::section {
            background-color: #e0e0e0;
            color: #000000;
            padding: 5px;
            border: 1px solid #cccccc;
            font-weight: bold;
        }
        
        /* ========== 滚动条 - 简约灰 ========== */
        QScrollBar:vertical {
            border: none;
            background: #f5f5f5;
            width: 8px;
        }
        QScrollBar::handle:vertical {
            background: #cccccc;
            min-height: 20px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover {
            background: #999999;
        }
        
        /* ========== 分组框与面板 ========== */
        QGroupBox {
            border: 1px solid #cccccc;
            margin-top: 1.5ex;
            font-weight: bold;
            color: #000000;
            background-color: #ffffff;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
        }
        
        QFrame#frame_window {
            background-color: #e0e0e0;
            border-right: 1px solid #cccccc;
        }
        
        QLabel {
            color: #333333; /* 深灰色文本 */
        }

        /* 系统标题特殊样式 - 黑色加粗 */
        QLabel#System_name, QLabel#System_name_2 {
            color: #000000;
            font-size: 24px;
            font-weight: bold;
        }
        
        /* 数据显示大数字特效 - 确保黑色加粗 */
        QTextBrowser[techRole="data"] {
            font-family: "Consolas", "Monaco", monospace;
            font-size: 18px;
            font-weight: bold;
            border: 1px solid #999999;
            background: #ffffff;
            color: #000000; /* 数字黑色 */
        }
        """

    @staticmethod
    def apply_smart_scaling(window, base_width=1690, base_height=1250):
        """
        根据屏幕分辨率智能缩放整个窗口及内部所有元素
        """
        try:
            # 开启高DPI自适应后，逻辑坐标和物理坐标会有所不同
            # 这里针对绝对定位的UI进行手动缩放
            screen = QApplication.primaryScreen().availableGeometry()
            s_width = screen.width()
            s_height = screen.height()
            
            # 计算缩放比例 (基于宽和高，取较小值确保不超出屏幕)
            # 预留 50 像素的余量
            factor_w = (s_width - 50) / base_width
            factor_h = (s_height - 50) / base_height
            scale_factor = min(factor_w, factor_h, 1.0) # 不放大，只缩小或保持
            
            new_w = int(base_width * scale_factor)
            new_h = int(base_height * scale_factor)
            
            # 1. 调整窗口尺寸并设置为固定大小或根据需要调整
            window.resize(new_w, new_h)
            
            # 2. 递归调整所有子控件
            def scale_widget(widget):
                # 调整位置和尺寸
                if not widget.isWindow():
                    r = widget.geometry()
                    widget.setGeometry(
                        int(r.x() * scale_factor),
                        int(r.y() * scale_factor),
                        int(r.width() * scale_factor),
                        int(r.height() * scale_factor)
                    )
                
                # 调整字体
                f = widget.font()
                ps = f.pointSize()
                if ps > 0:
                    # 字体缩放系数设为 0.9，防止数字溢出框
                    new_ps = max(int(ps * scale_factor * 0.9), 7)
                    f.setPointSize(new_ps)
                    widget.setFont(f)
                
                # 处理容器类控件的内部间距
                if hasattr(widget, 'setContentsMargins'):
                    m = widget.contentsMargins()
                    widget.setContentsMargins(
                        int(m.left() * scale_factor),
                        int(m.top() * scale_factor),
                        int(m.right() * scale_factor),
                        int(m.bottom() * scale_factor)
                    )

            # 遍历所有控件进行缩放
            for child in window.findChildren(QWidget):
                scale_widget(child)
            
            # 3. 屏幕居中
            window.move((s_width - new_w) // 2, (s_height - new_h) // 2)
            
        except Exception as e:
            print(f"UI 缩放系统异常: {e}")

    @staticmethod
    def center_window(window: QMainWindow):
        """
        将窗口居中显示在屏幕上
        """
        try:
            screen = QApplication.primaryScreen().availableGeometry()
            size = window.geometry()
            window.move((screen.width() - size.width()) // 2, 
                        (screen.height() - size.height()) // 2)
        except Exception:
            pass


# ------------------------------------------------------------------------------------
# 读取线程：运行在独立 QThread 中，定时（QTimer）拉取 DATAS.snapshot() 并向 UI 发射信号
# ------------------------------------------------------------------------------------
# 替换 live_frame_viewer.py 中的 SnapshotReader 类
import cv2
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
    """
    登录对话框
    使用极致科技感样式和智能深度缩放
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("系统登录 [身份验证]")
        
        # 应用科技感样式
        self.setStyleSheet(UIStyleManager.get_modern_style())
        
        # 智能缩放处理
        UIStyleManager.apply_smart_scaling(self, base_width=450, base_height=320)
        
        # 创建控件
        self.label_username = QLabel("USER ID:")
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("ENTER USERNAME")
        
        self.label_password = QLabel("PASSCODE:")
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("ENTER PASSWORD")
        self.input_password.setEchoMode(QLineEdit.Password)
        
        self.button_login = QPushButton("ACCESS SYSTEM")
        self.button_login.clicked.connect(self.check_login)
        
        # 布局
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("SECURITY CLEARANCE")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
        
        layout.addWidget(title)
        layout.addWidget(self.label_username)
        layout.addWidget(self.input_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addSpacing(10)
        layout.addWidget(self.button_login)
        
        self.setLayout(layout)
        
        # 居中
        UIStyleManager.center_window(self)

        self.backend = None
        if START_BACKEND:
            self.backend = TrainGroupReaderApp(ACTIVE_PORT, PASSIVE_PORT, BAUDRATE)
            self.backend.start()

        self.MainWindow = MainWindow()

        # 读取线程
        self.reader_thread = QThread()
        self.reader = SnapshotReader(interval_ms=200)  # 200ms 刷新一次
        self.reader.moveToThread(self.reader_thread)

        # 连接信号
        self.reader_thread.started.connect(self.reader.start)
        self.reader.snapshotReady.connect(self.MainWindow.on_snapshot)

        QCoreApplication.instance().aboutToQuit.connect(self._cleanup)

        # 启动线程
        self.reader_thread.start()

    def check_login(self):
        username = self.input_username.text()
        password = self.input_password.text()
        
        # 验证用户名和密码
        if username == "1" and password == "1":
            self.MainWindow.show()
            self.hide()  # 隐藏登录窗口（而不是 accept()）
        else:
            QMessageBox.warning(self, "警告", "用户名或密码错误！")
            self.input_password.clear()

    def _cleanup(self):
        try:
            self.reader.stop()
        except Exception:
            pass
        self.reader_thread.quit()
        self.reader_thread.wait()

        if self.backend is not None:
            self.backend.stop()

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    主窗口类
    包含系统的主要功能界面，使用极致科技感样式和智能深度缩放
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 设置窗口标题
        self.setWindowTitle("火车加料智能监控系统 - 主界面 [系统在线]")
        
        # 应用科技感样式
        self.setStyleSheet(UIStyleManager.get_modern_style())
        
        # 应用深度智能缩放（处理绝对定位控件，确保不被切断）
        UIStyleManager.apply_smart_scaling(self, base_width=1690, base_height=1250)
        
        # 业务逻辑变量
        self.liechehao = "None"
        self.chexianggaodu = 1
        
        # === 窗口内轮询定时器 ===
        self._timer = QTimer(self)
        self._timer.setInterval(200)  # 200ms 一次，用于定时更新数据
        self._timer.timeout.connect(self._poll_snapshot)
        
        # === 绑定按钮点击事件 ===
        self.pushButton_8.clicked.connect(self.open_train_management)  # "火车型号尺寸"按钮
        self.pushButton_7.clicked.connect(self.open_machine_history)   # "下料历史查询"按钮
        self.pushButton_6.clicked.connect(self.open_train_control)  # "下料机控制"按钮
        self.pushButton_5.clicked.connect(self.open_train_label)   # "火车视觉识别"按钮
        
        # 为数据显示框设置特殊标识（用于应用大数字QSS）
        self._tag_data_browsers()
        
        # 主窗口关闭时退出整个应用
        self.destroyed.connect(lambda: QApplication.instance().quit())

        self._cam_thread = None
    
    def _tag_data_browsers(self):
        """
        为所有用于数据显示的QTextBrowser打上标签
        """
        data_widgets = [
            'textBrowser_xtzt', 'textBrowser_chk', 'textBrowser_czy', 'textBrowser_lch',
            'textBrowser_chk_2', 'textBrowser_chk_3', 'textBrowser_chk_4', 'textBrowser_chk_5',
            'textBrowser_chk_6', 'textBrowser_chk_7', 'textBrowser_chk_8'
        ]
        for name in data_widgets:
            if hasattr(self, name):
                widget = getattr(self, name)
                widget.setProperty("techRole", "data")
                # 重新应用样式以使属性生效
                widget.setStyle(widget.style())
        
        # --- 初始化视觉显示组件 ---
        if hasattr(self, 'Train_graph'):
            self.scene = QGraphicsScene(self.Train_graph)
            self.Train_graph.setScene(self.scene)
            self.Train_graph.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
            self.Train_graph.setTransformationAnchor(self.Train_graph.AnchorViewCenter)
            self.Train_graph.setResizeAnchor(self.Train_graph.AnchorViewCenter)
            self.Train_graph.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.Train_graph.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

            self._pix_item = QGraphicsPixmapItem()
            self.scene.addItem(self._pix_item)
            self.Train_graph.setBackgroundBrush(self.Train_graph.palette().base())
        else:
            self._pix_item = None

    def _style_buttons(self):
        """
        已由全局QSS统一处理
        """
        pass
    
    def _style_text_browsers(self):
        """
        已由全局QSS统一处理
        """
        pass

        self.timer_ocr = None
        self.ocr = None
        self.cap = None
        self.is_camera_running = False
        
        # 只有在PaddleOCR可用时才初始化OCR
        if PADDLEOCR_AVAILABLE and PaddleOCR is not None:
            try:
                self.timer_ocr = QTimer()
                self.ocr = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=True, use_doc_unwarping=False , use_doc_orientation_classify=False)
                self.timer_ocr.timeout.connect(self.process_frame)
            except Exception as e:
                print(f"OCR模型初始化失败: {e}")
                self.ocr = None
        else:
            print("OCR功能不可用（PaddleOCR未安装或导入失败）")

        try:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            if not self.cap.isOpened():
                print("摄像头无法打开")
                return

            self.is_camera_running = True
            if self.timer_ocr:
                self.timer_ocr.start(300)  # 约30fps
        except Exception as e:
            print(f"摄像头打开失败: {e}")

    def process_frame(self):
        """处理每一帧图像 - 这是主要的OCR函数"""
        if not self.cap or not self.is_camera_running or not self.ocr:
            return

        ret, frame = self.cap.read()
        if not ret:
            # 如果无法获取摄像头画面，只打印错误信息
            print("无法获取摄像头画面")
            return

        # 执行OCR识别
        filtered_texts = self.perform_ocr(frame)

    def perform_ocr(self, frame):
        """
        OCR识别函数 - 这是您原始代码转换的函数
        返回: 识别到的文本列表
        """
        if not self.ocr:
            return []
        
        # 将BGR图像转换为RGB（PaddleOCR需要RGB格式）
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        filtered_texts = []

        try:
            # 执行OCR识别
            result = self.ocr.ocr(rgb_frame)

            # 提取所有识别结果中的文本和置信度
            # PaddleOCR返回格式: [[[坐标], ('文本', 置信度)], ...]
            if result and result[0]:
                for line in result[0]:
                    if line and len(line) >= 2:
                        # line[1] 是 ('文本', 置信度) 的元组
                        text_info = line[1]
                        if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                            texta = text_info[0]  # 提取文本
                            confidence = text_info[1]  # 提取置信度
                            # 检查置信度≥0.7
                            if confidence >= 0.7:
                                filtered_texts.append(texta)

            # 如果有识别到的数字，打印出来
            if filtered_texts:
                final_result = ''.join(filtered_texts)
                print(f"识别到的数字: {final_result}")
                if final_result == 'C64':
                    print("车厢信息：120,240,15,20,17")

        except Exception as e:
            print(f"OCR处理错误: {e}")

        return filtered_texts

    # 打开摄像头（注意：不再创建 QLabel）
    def open_with_camera(self, device_index=0, width=640, height=480, fps=30):
        # 启动摄像头线程
        self._cam_thread = CameraThread(
            device_index=device_index, width=width, height=height, fps=fps, parent=self
        )
        self._cam_thread.frameReady.connect(self.on_frame)
        self._cam_thread.error.connect(self.on_camera_error)
        self._cam_thread.start()

    def _fit_view(self):
        """
        让视口自适应当前 pixmap 尺寸
        """
        if not hasattr(self, '_pix_item') or self._pix_item is None:
            return
            
        pix = self._pix_item.pixmap()
        if pix.isNull():
            return
            
        rect = QRectF(pix.rect())
        if hasattr(self, 'scene') and self.scene is not None:
            self.scene.setSceneRect(rect)
        
        # 尝试自适应不同的视图控件名
        if hasattr(self, 'Train_graph'):
            self.Train_graph.fitInView(rect, Qt.KeepAspectRatio)
        elif hasattr(self, 'train_picture'):
            self.train_picture.fitInView(rect, Qt.KeepAspectRatio)
    
    def on_frame(self, qimg):
        """
        CameraThread 发来的帧是 QImage；更新到 pixmap item 并自适应视口
        """
        if qimg is None or not hasattr(self, '_pix_item') or self._pix_item is None:
            return
        pix = QPixmap.fromImage(qimg)
        self._pix_item.setPixmap(pix)
        self._fit_view()

    def resizeEvent(self, ev):
        """
        窗口或 QGraphicsView 尺寸变化时，保持自适应
        """
        super().resizeEvent(ev)
        self._fit_view()

    def on_camera_error(self, msg: str):
        # 也可以在 scene 里显示错误文字，这里简单使用窗口标题提示
        self.setWindowTitle(f"火车视觉识别主界面 - Camera error: {msg}")

    def closeEvent(self, event):
        if self._timer.isActive():
            self._timer.stop()
        if self._cam_thread:
            try:
                self._cam_thread.frameReady.disconnect(self.on_frame)
                self._cam_thread.error.disconnect(self.on_camera_error)
            except Exception:
                pass
            self._cam_thread.stop()
            self._cam_thread.wait()
            self._cam_thread = None
        # event.accept()  # 只关闭当前窗口，避免退出整个应用
        self.is_camera_running = False
        if self.timer_ocr and self.timer_ocr.isActive():
            self.timer_ocr.stop()
        if self.cap:
            self.cap.release()
        event.accept()

    def showEvent(self, e):
        super().showEvent(e)
        if not self._timer.isActive():
            self._timer.start()
        # if self._cam_thread is None:
        #     self.open_with_camera(device_index=0, width=1280, height=720, fps=30)

    def open_train_management(self):
        # 创建火车型号管理子窗口
        self.train_management_window = TrainManagementWindow()
        self.train_management_window.show()
        
    def open_machine_history(self):
        # 创建下料历史子窗口
        self.machine_history_window = MachineHistoryWindow()
        self.machine_history_window.show()

    def open_train_control(self):
        # 创建下料机控制子窗口
        self.train_control_window = TrainControlWindow()
        self.train_control_window.show()
        
    def open_train_label(self):
        # 创建火车视觉识别子窗口
        a=1
        # self.train_label_window = TrainLabelWindow()
        # self.train_label_window.attach_camera_source(self._cam_thread)
        # self.train_label_window.show()
        # 打开子界面时启动摄像头（调用代码写在这里）
        # self.train_label_window.open_with_camera(device_index=0, width=1280, height=720, fps=30)
        
    
    
    def _poll_snapshot(self):
        """定时拉取 DATAS 的快照，并取出 all_dict"""
        try:
            snap = DATAS.snapshot()  # 线程安全
            all_dict = snap.get("all_data_dict", {}) or {}
            read_coils_0_13=all_dict["read_coils_0_13"]["RxData"]
            read_coils_16_24=all_dict["read_coils_16_24"]["RxData"]
            read_coils_27_31=all_dict["read_coils_27_31"]["RxData"]
            read_holding_registers_0_13=all_dict["read_holding_registers_0_13"]["RxData"]
            read_holding_registers_16_24=all_dict["read_holding_registers_16_24"]["RxData"]
            read_holding_registers_32_39=all_dict["read_holding_registers_32_39"]["RxData"]
            # 牵引系统状态
            qianyinxitongzhuangtai = read_coils_0_13[0]
            if qianyinxitongzhuangtai:
                self.textBrowser_xtzt.setPlainText("正常")
            else:
                self.textBrowser_xtzt.setPlainText("故障")
            # 仓库号
            cangkuhao =  "WH111"
            self.textBrowser_chk.setPlainText(cangkuhao)
            # 操作员
            caozuoyuan = "张1三"
            self.textBrowser_czy.setPlainText(caozuoyuan)
            # 列车号
            liechehao = self.liechehao
            self.textBrowser_lch.setPlainText(liechehao)
            # 下煤机状态 
            xiameijizhuangtai = read_coils_0_13[1]
            if xiameijizhuangtai:
                self.textBrowser_chk_2.setPlainText("正常")
            else:
                self.textBrowser_chk_2.setPlainText("故障")
            # 阀门开度
            famenkaidu = read_holding_registers_32_39[0]
            famenkaidu = int(famenkaidu, 16)
            famenkaidu = str(famenkaidu)
            self.textBrowser_chk_3.setPlainText(famenkaidu)
            # 升降高度
            shengjianggaodu = read_holding_registers_32_39[1]
            shengjianggaodu = int(shengjianggaodu, 16)
            shengjianggaodu = str(shengjianggaodu)
            self.textBrowser_chk_4.setPlainText(shengjianggaodu)
            # 翻板高度
            fanbangaodu = read_holding_registers_32_39[2]
            fanbangaodu = int(fanbangaodu, 16)
            fanbangaodu = str(fanbangaodu)
            self.textBrowser_chk_5.setPlainText(fanbangaodu)
            # 是否装载 
            shifouzhuangzai = read_coils_0_13[2]
            if shifouzhuangzai:
                self.textBrowser_chk_8.setPlainText("是")
            else:
                self.textBrowser_chk_8.setPlainText("否")
            # 装料进度
            zhuangliaojindu = read_holding_registers_32_39[3]
            zhuangliaojindu = int(zhuangliaojindu, 16)/self.chexianggaodu
            zhuangliaojindu = str(zhuangliaojindu)
            self.textBrowser_chk_7.setPlainText(zhuangliaojindu)
            # 料面高度
            liaomiangaodu = read_holding_registers_32_39[3]
            liaomiangaodu = int(liaomiangaodu, 16)
            liaomiangaodu = str(liaomiangaodu)
            self.textBrowser_chk_6.setPlainText(liaomiangaodu)
        except Exception as ex:
            # 避免异常把定时器干掉，可在标题或状态区提示
            self.setWindowTitle(f"下料机控制主界面 - 读取异常: {ex}")

    def on_snapshot(self, snap: dict):
        fn   = snap.get("function_name", "")
        ts   = snap.get("timestamp", "")
        addr = snap.get("RxAddr", 0)
        fid  = snap.get("RxFuncID", 0)
        dlen = snap.get("RxDataLen", 0)
        state= snap.get("Mdbs_state", 0)
        data = snap.get("RxData", [])

        # self.lb_fn.setText(f"function_name: {fn}")
        # self.lb_ts.setText(f"timestamp: {ts}")
        # self.lb_addr.setText(f"Addr: {addr}")
        # self.lb_func.setText(f"FuncID: {fid}")
        # self.lb_len.setText(f"DataLen: {dlen}")

        # # ✅/❌ + 胶囊色块
        # if state:  # 这里按你后端的判定使用非零即 OK；如需严格按 Frame_OK，可改 (state & 0x01)
        #     self.lb_state.setText("State: ✅ 收发正常")
        #     self.lb_state.setStyleSheet("color: #2e7d32; font-weight: 700;")
        #     self.badge_state.setText("OK")
        #     self.badge_state.setStyleSheet("QLabel[role='badge']{ background:#e5f7ea; color:#1b5e20; }")
        # else:
        #     self.lb_state.setText(f"State: ❌ {state}")
        #     self.lb_state.setStyleSheet("color: #b00020; font-weight: 700;")
        #     self.badge_state.setText("NG")
        #     self.badge_state.setStyleSheet("QLabel[role='badge']{ background:#ffdede; color:#b00020; }")

        # # Data 更醒目（有值蓝色，无值灰色）
        # if data:
        #     self.lb_data.setText(f"Data: {data}")
        #     self.lb_data.setStyleSheet("color:#0057b8; font-weight:600;")
        # else:
        #     self.lb_data.setText("Data: (暂无数据)")
        #     self.lb_data.setStyleSheet("color:#888; font-weight:400;")

        # 汇总
        all_dict = snap.get("all_data_dict", {})
        a=1
        # self._refresh_table(all_dict)

class TrainManagementWindow(QMainWindow, Ui_TrainQuery):
    """
    火车型号管理窗口
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 数据库配置
        self.TABLE_SCHEMA = "dbo"
        self.TABLE_NAME   = "Train Model Table"
        self.ID_COLUMN    = "TrainTypeID"
        
        self.db_manager = TrainDatabaseManager(
            server="WIN-DNI5FVM376E",
            database="RailwayCoalManagement",
            username="sa",
            password="220242236"
        )
        
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("DATABASE - TRAIN MODELS [DATA MANAGEMENT]")
        
        # 应用科技感样式
        self.setStyleSheet(UIStyleManager.get_modern_style())
        
        # 智能缩放处理
        UIStyleManager.apply_smart_scaling(self, base_width=1690, base_height=1250)
        
        # 绑定按钮点击事件
        self.pushButton_11.clicked.connect(self.open_train_update)  # "新增/修改"按钮
        self.pushButton_9.clicked.connect(self._on_search_clicked)   # 根据 TrainTypeID 查询
        self.pushButton_10.clicked.connect(self._load_all_models)    # 重新显示全部
        
        # 为数据显示框设置特殊标识
        if hasattr(self, 'textBrowser'):
            self.textBrowser.setProperty("techRole", "data")
            self.textBrowser.setStyle(self.textBrowser.style())
        
        self._first_show_done = False

        # 绑定按钮点击事件
        self.pushButton_11.clicked.connect(self.open_train_update)  # "新增/修改"按钮
        # ☆ 新增：绑定查询与重置按钮
        self.pushButton_9.clicked.connect(self._on_search_clicked)   # 根据 TrainTypeID 查询
        self.pushButton_10.clicked.connect(self._load_all_models)    # 重新显示全部
        # ☆ 可选：首次打开就加载所有数据
        self._first_show_done = False

    # --- 窗口第一次显示时加载全表 ---
    def showEvent(self, e):
        super().showEvent(e)
        if not self._first_show_done:
            self._first_show_done = True
            self._load_all_models()

    def open_train_update(self):
        # 创建火车型号更新子窗口
        self.train_update_window = TrainUpdateWindow()
        self.train_update_window.show()

    def _load_all_models(self):
        try:
            cols, rows = self.db_manager.query_all(
                self.TABLE_SCHEMA,
                self.TABLE_NAME
            )
            self._render_to_textbrowser(cols, rows)
        except Exception as ex:
            QMessageBox.critical(self, "错误", f"加载全表失败：\n{ex}")

    def _on_search_clicked(self):
        key = self.textEdit.toPlainText().strip()
        if not key:
            QMessageBox.warning(self, "提示", "请输入 TrainTypeID 再查询。")
            return
        try:
            cols, rows = self.db_manager.query_by_id(
                self.TABLE_SCHEMA,
                self.TABLE_NAME,
                self.ID_COLUMN,
                key
            )
            self._render_to_textbrowser(cols, rows)
            if not rows:
                QMessageBox.information(self, "结果", f"未找到 TrainTypeID = {key} 的记录。")
        except Exception as ex:
            QMessageBox.critical(self, "错误", f"查询失败：\n{ex}")
    
    def _render_to_textbrowser(self, columns, rows):
        """
        以文本表格形式渲染到 textBrowser（等宽对齐）
        """
        if not columns:
            self.textBrowser.setPlainText("No columns.")
            return

        # 将 pyodbc.Row 转成普通字符串列表
        str_rows = []
        for r in rows:
            # r 可能是 pyodbc.Row，可下标访问；也可用 tuple(r)
            str_rows.append([("" if (v is None) else str(v)) for v in r])

        # 计算列宽
        col_widths = [len(col) for col in columns]
        for r in str_rows:
            for i, cell in enumerate(r):
                col_widths[i] = max(col_widths[i], len(cell))

        def fmt_row(cells):
            return " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(cells))

        lines = []
        lines.append(fmt_row(columns))
        lines.append("-+-".join("-" * w for w in col_widths))
        if str_rows:
            for r in str_rows:
                lines.append(fmt_row(r))
        else:
            lines.append("(no records)")

        # 使用等宽字体效果更好（需在 UI 中把 textBrowser 字体设为等宽，
        # 或者在样式里设置 font-family: Consolas, 'Courier New', monospace;）
        self.textBrowser.setPlainText("\n".join(lines))

class TrainUpdateWindow(QMainWindow, Ui_TrainUpdate):
    """
    火车型号更新窗口
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 数据库配置
        self.TABLE_SCHEMA = "dbo"
        self.TABLE_NAME   = "Train Model Table"
        self.ID_COLUMN    = "TrainTypeID"
        
        self.db_manager = TrainDatabaseManager(
            server="WIN-DNI5FVM376E",
            database="RailwayCoalManagement",
            username="sa",
            password="220242236"
        )
        
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("SYSTEM UPDATE - TRAIN PARAMETERS [LOGISTICS]")
        
        # 应用科技感样式
        self.setStyleSheet(UIStyleManager.get_modern_style())
        
        # 智能缩放处理
        UIStyleManager.apply_smart_scaling(self, base_width=1690, base_height=1250)
        
        # 映射：依次对应 textEdit1..textEdit21
        self.COLUMN_ORDER = [
            "textEdit",
            "textEdit_3", "textEdit_4", "textEdit_11", "textEdit_6",
            "textEdit_7", "textEdit_10", "textEdit_8", "textEdit_9", "textEdit_20",
            "textEdit_22","textEdit_21","textEdit_23","textEdit_24"
        ]
        self.FIELD_MAP = {
            "textEdit":   "TrainTypeID",      # 主键
            "textEdit_3": "HoldType",
            "textEdit_4": "ExLength",
            "textEdit_11":"ExWidth",
            "textEdit_6": "ExHeight",
            "textEdit_7": "InLength",
            "textEdit_10":"InWidth",
            "textEdit_8": "InHeight",
            "textEdit_9": "Volume",
            "textEdit_20":"Density",
            "textEdit_22":"LoadWeight",
            "textEdit_21":"FullLength",
            "textEdit_23":"BottomHeight",
            "textEdit_24":"HookType"
        }
        self.pushButton_9.clicked.connect(self._on_add_clicked)      # 新增
        self.pushButton_10.clicked.connect(self._on_update_clicked)  # 修改
        
        # 为数据显示框设置特殊标识
        if hasattr(self, 'textBrowser'):
            self.textBrowser.setProperty("techRole", "data")
            self.textBrowser.setStyle(self.textBrowser.style())

        self._first_show_done = False

        # 映射：依次对应 textEdit1..textEdit21
        self.COLUMN_ORDER = [
            "textEdit",
            "textEdit_3", "textEdit_4", "textEdit_11", "textEdit_6",
            "textEdit_7", "textEdit_10", "textEdit_8", "textEdit_9", "textEdit_20",
            "textEdit_22","textEdit_21","textEdit_23","textEdit_24"
        ]
        self.FIELD_MAP = {
            "textEdit":   "TrainTypeID",      # 主键
            "textEdit_3": "HoldType",
            "textEdit_4": "ExLength",
            "textEdit_11":"ExWidth",
            "textEdit_6": "ExHeight",
            "textEdit_7": "InLength",
            "textEdit_10":"InWidth",
            "textEdit_8": "InHeight",
            "textEdit_9": "Volume",
            "textEdit_20":"Density",
            "textEdit_22":"LoadWeight",
            "textEdit_21":"FullLength",
            "textEdit_23":"BottomHeight",
            "textEdit_24":"HookType"
            # …继续写到所有字段
        }
        # 新增：新增/修改按钮（你提到的 pushButton9 / pushButton10）
        # 这里假设对象名就是 pushButton9 / pushButton10（与上面查询的不同按钮）
        # 若与上面冲突，请换成 pushButton_add / pushButton_update 这样更清晰
        self.pushButton_9.clicked.connect(self._on_add_clicked)      # 新增
        self.pushButton_10.clicked.connect(self._on_update_clicked)  # 修改

        self._first_show_done = False

    # —— 把空串写成 NaN；如需存 NULL，把 USE_NAN_STR 改为 False 即可 ——
    USE_NAN_STR = False  # True: 存字符串 "NaN"；False: 存数据库 NULL

    # --- 窗口第一次显示时加载全表 ---
    def showEvent(self, e):
        super().showEvent(e)
        if not self._first_show_done:
            self._first_show_done = True
            self._load_all_models()

    def _load_all_models(self):
        try:
            cols, rows = self.db_manager.query_all(
                self.TABLE_SCHEMA,
                self.TABLE_NAME
            )
            self._render_to_textbrowser(cols, rows)
        except Exception as ex:
            QMessageBox.critical(self, "错误", f"加载全表失败：\n{ex}")
    
    def _render_to_textbrowser(self, columns, rows):
        """
        以文本表格形式渲染到 textBrowser（等宽对齐）
        """
        if not columns:
            self.textBrowser.setPlainText("No columns.")
            return

        # 将 pyodbc.Row 转成普通字符串列表
        str_rows = []
        for r in rows:
            # r 可能是 pyodbc.Row，可下标访问；也可用 tuple(r)
            str_rows.append([("" if (v is None) else str(v)) for v in r])

        # 计算列宽
        col_widths = [len(col) for col in columns]
        for r in str_rows:
            for i, cell in enumerate(r):
                col_widths[i] = max(col_widths[i], len(cell))

        def fmt_row(cells):
            return " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(cells))

        lines = []
        lines.append(fmt_row(columns))
        lines.append("-+-".join("-" * w for w in col_widths))
        if str_rows:
            for r in str_rows:
                lines.append(fmt_row(r))
        else:
            lines.append("(no records)")

        # 使用等宽字体效果更好（需在 UI 中把 textBrowser 字体设为等宽，
        # 或者在样式里设置 font-family: Consolas, 'Courier New', monospace;）
        self.textBrowser.setPlainText("\n".join(lines))

    def _normalize_cell(self, s: str):
        s = (s or "").strip()
        if s == "":
            return "NaN" if self.USE_NAN_STR else None
        return s

    def _collect_form_values(self):
        data = {}
        for widget_name, col_name in self.FIELD_MAP.items():
            te = getattr(self, widget_name, None)
            if te:
                val = self._normalize_cell(te.toPlainText())
                data[col_name] = val
        return data

    # ========== 新增 ==========
    def _on_add_clicked(self):
        try:
            data = self._collect_form_values()
            # 基本校验：主键不能为空
            pk_val = data.get(self.ID_COLUMN)
            if pk_val is None or (isinstance(pk_val, str) and pk_val.strip() == ""):
                QMessageBox.warning(self, "提示", "TrainTypeID 不能为空。")
                return

            # 插入全部列（含主键）
            self.db_manager.insert_row(self.TABLE_SCHEMA, self.TABLE_NAME, data)
            QMessageBox.information(self, "成功", "新增成功。")
            self._load_all_models()
        except Exception as ex:
            QMessageBox.critical(self, "错误", f"新增失败：\n{ex}")

    # ========== 修改 ==========
    def _on_update_clicked(self):
        """
        读取 textEdit1 作为 TrainTypeID，更新其余列。
        空输入按规则写入 'NaN' 或 NULL
        """
        try:
            data = self._collect_form_values()
            pk_val = data.get(self.ID_COLUMN)
            if pk_val is None or (isinstance(pk_val, str) and pk_val.strip() == ""):
                QMessageBox.warning(self, "提示", "请在 textEdit1 中填写 TrainTypeID。")
                return

            # 准备更新的数据：去掉主键列
            update_data = {k: v for k, v in data.items() if k != self.ID_COLUMN}

            # 如果你希望“只更新有输入的字段”，可以改成下面这行：
            # update_data = {k: v for k, v in data.items() if k != self.ID_COLUMN and v is not None and v != "NaN"}

            self.db_manager.update_row_by_id(
                self.TABLE_SCHEMA,
                self.TABLE_NAME,
                self.ID_COLUMN,
                pk_val,
                update_data
            )
            QMessageBox.information(self, "成功", "更新成功。")
            self._load_all_models()
        except Exception as ex:
            QMessageBox.critical(self, "错误", f"更新失败：\n{ex}")

class MachineHistoryWindow(QMainWindow, Ui_layoff_history):
    """
    下料历史查询窗口
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 数据库配置
        self.TABLE_SCHEMA = "dbo"
        self.TABLE_NAME   = "Layoff History Table"
        self.ID_COLUMN1    = "MaterialID"
        self.ID_COLUMN2    = "WarehouseID"
        self.TIME_COLUMN  = "Time"
        
        self.db_manager = TrainDatabaseManager(
            server="WIN-DNI5FVM376E",
            database="RailwayCoalManagement",
            username="sa",
            password="220242236"
        )
        
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("HISTORY LOGS - DISCHARGE TRENDS [ANALYTICS]")
        
        # 应用科技感样式
        self.setStyleSheet(UIStyleManager.get_modern_style())
        
        # 智能缩放处理
        UIStyleManager.apply_smart_scaling(self, base_width=1690, base_height=1250)
        
        self.pushButton_9.clicked.connect(self._on_search_combined_clicked)
        self.pushButton_11.clicked.connect(lambda: self._load_recent_minutes(10))
        self.pushButton_12.clicked.connect(lambda: self._load_recent_minutes(60))
        self.pushButton_13.clicked.connect(lambda: self._load_recent_minutes(4 * 60))
        self.pushButton_14.clicked.connect(lambda: self._load_recent_minutes(24 * 60))

        self.pushButton_10.clicked.connect(self._export_to_excel)
        self.pushButton_15.clicked.connect(self._open_last_export)
        
        # 为数据显示框设置特殊标识
        if hasattr(self, 'textBrowser'):
            self.textBrowser.setProperty("techRole", "data")
            self.textBrowser.setStyle(self.textBrowser.style())
        
        self._first_show_done = False
        self._last_query_columns = []
        self._last_query_rows = []
        self._last_export_path: Optional[Path] = None

        self.pushButton_9.clicked.connect(self._on_search_combined_clicked)   # 仅按 TrainTypeID
        # 绑定新增控件
        self.pushButton_11.clicked.connect(lambda: self._load_recent_minutes(10))
        self.pushButton_12.clicked.connect(lambda: self._load_recent_minutes(60))
        self.pushButton_13.clicked.connect(lambda: self._load_recent_minutes(4 * 60))
        self.pushButton_14.clicked.connect(lambda: self._load_recent_minutes(24 * 60))

        self.pushButton_10.clicked.connect(self._export_to_excel)
        self.pushButton_15.clicked.connect(self._open_last_export)
        
        self._first_show_done = False
        self._last_query_columns = []
        self._last_query_rows = []
        self._last_export_path: Optional[Path] = None

    # --- 窗口第一次显示时加载全表 ---
    def showEvent(self, e):
        super().showEvent(e)
        if not self._first_show_done:
            self._first_show_done = True
            self._load_all_models()

    def _on_search_combined_clicked(self):
        materialtype = self.textEdit.toPlainText().strip()
        warehouse = self.textEdit_2.toPlainText().strip()

        if not materialtype and not warehouse:
            QMessageBox.information(self, "提示", "请至少填写一个查询条件（下料机号 或 仓库号）。")
            return

        # 组装等值条件
        conditions = {}
        if materialtype:
            conditions[self.ID_COLUMN1] = materialtype
        if warehouse:
            conditions[self.ID_COLUMN2] = warehouse   # ← 仓库号列名，改成你真实的

        try:
            cols, rows = self._select_where_eq(conditions)
            self._render_to_textbrowser(cols, rows)
            if not rows:
                human = " 和 ".join([f"{k}={v}" for k, v in conditions.items()])
                QMessageBox.information(self, "结果", f"未找到满足条件（{human}）的记录。")
        except Exception as ex:
            QMessageBox.critical(self, "错误", f"联合查询失败：\n{ex}")

    def _select_where_eq(self, conditions: Dict[str, Any]):
        # 用已有 manager 的安全转义 + 参数化
        if not conditions:
            raise ValueError("conditions 为空。")

        q = self.db_manager._q
        clause = " AND ".join(f"{q(k)}=?" for k in conditions.keys())
        sql = f"SELECT * FROM {q(self.TABLE_SCHEMA)}.{q(self.TABLE_NAME)} WHERE {clause}"
        params = list(conditions.values())

        with self.db_manager._connect() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]

        # 缓存
        self._last_query_columns = cols
        self._last_query_rows = rows
        return cols, rows
    
    def _export_to_excel(self):
        if not self._last_query_columns:
            QMessageBox.information(self, "提示", "当前没有可导出的数据，请先查询或加载。")
            return

        # 默认路径 & 文件名（CSV）
        default_name = "train_models_export.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, "导出为 CSV", default_name, "CSV Files (*.csv)"
        )
        if not path:
            return  # 用户取消

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                # 写表头
                writer.writerow(self._last_query_columns)
                # 写数据行
                for r in self._last_query_rows:
                    writer.writerow(list(r))

            self._last_export_path = Path(path)
            QMessageBox.information(self, "成功", f"已导出：\n{path}")
        except Exception as ex:
            QMessageBox.critical(self, "错误", f"导出失败：\n{ex}")
    
    def _open_last_export(self):
        if not self._last_export_path:
            QMessageBox.information(self, "提示", "还没有导出的文件。请先执行导出。")
            return
        path = self._last_export_path
        if not path.exists():
            QMessageBox.warning(self, "提示", f"文件不存在：\n{path}")
            return
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))
        except Exception as ex:
            # 兜底：Windows 可退回 os.startfile
            try:
                if os.name == "nt":
                    os.startfile(str(path))  # type: ignore[attr-defined]
                else:
                    raise
            except Exception:
                QMessageBox.critical(self, "错误", f"无法打开文件：\n{ex}")

    def _load_all_models(self):
        try:
            cols, rows = self.db_manager.query_all(
                self.TABLE_SCHEMA,
                self.TABLE_NAME
            )
            self._last_query_columns = cols
            self._last_query_rows = rows
            self._render_to_textbrowser(cols, rows)
        except Exception as ex:
            QMessageBox.critical(self, "错误", f"加载全表失败：\n{ex}")

    def _render_to_textbrowser(self, columns, rows):
        """
        以文本表格形式渲染到 textBrowser（等宽对齐），并缓存结果用于导出
        """
        # 缓存（用于导出）
        self._last_query_columns = list(columns or [])
        self._last_query_rows = list(rows or [])

        if not columns:
            self.textBrowser.setPlainText("No columns.")
            return

        str_rows = []
        for r in rows:
            str_rows.append([("" if (v is None) else str(v)) for v in r])

        col_widths = [len(col) for col in columns]
        for r in str_rows:
            for i, cell in enumerate(r):
                col_widths[i] = max(col_widths[i], len(cell))

        def fmt_row(cells):
            return " | ".join(c.ljust(col_widths[i]) for i, c in enumerate(cells))

        lines = []
        lines.append(fmt_row(columns))
        lines.append("-+-".join("-" * w for w in col_widths))
        if str_rows:
            for r in str_rows:
                lines.append(fmt_row(r))
        else:
            lines.append("(no records)")

        self.textBrowser.setPlainText("\n".join(lines))

    def _load_recent_minutes(self, minutes: int):
        q = self.db_manager._q
        base = (
            f"SELECT * FROM {q(self.TABLE_SCHEMA)}.{q(self.TABLE_NAME)} "
            f"WHERE {q(self.TIME_COLUMN)} >= DATEADD(MINUTE, ?, GETDATE())"
        )
        params = [-minutes]

        # 如果输入框有条件，自动叠加
        materialtype = self.textEdit.toPlainText().strip()
        warehouse = self.textEdit_2.toPlainText().strip()
        if materialtype:
            base += f" AND {q(self.ID_COLUMN1)} = ?"
            params.append(materialtype)
        if warehouse:
            base += f" AND {q(self.ID_COLUMN2)} = ?"  # ← 改成你真实的仓库号列名
            params.append(warehouse)

        try:
            with self.db_manager._connect() as conn:
                cur = conn.cursor()
                cur.execute(base, params)
                rows = cur.fetchall()
                cols = [d[0] for d in cur.description]
            self._last_query_columns = cols
            self._last_query_rows = rows
            self._render_to_textbrowser(cols, rows)
        except Exception as ex:
            QMessageBox.critical(self, "错误", f"加载最近 {minutes} 分钟数据失败：\n{ex}")

class TrainControlWindow(QMainWindow, Ui_Traincontrol):
    """
    下料机控制窗口
    使用极致科技感样式和智能深度缩放
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 业务逻辑变量
        self.chexianggaodu = 1
        
        # 设置窗口属性
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("CONTROL CENTER - DISCHARGE SYSTEM [OPERATIONS]")
        
        # 应用科技感样式
        self.setStyleSheet(UIStyleManager.get_modern_style())
        
        # 智能缩放处理 (处理绝对定位)
        UIStyleManager.apply_smart_scaling(self, base_width=1690, base_height=1250)
        
        # === 窗口内轮询定时器 ===
        self._timer = QTimer(self)
        self._timer.setInterval(200)  # 200ms 一次，用于定时更新数据
        self._timer.timeout.connect(self._poll_snapshot)
        
        # 为数据显示框设置特殊标识（用于应用大数字QSS）
        self._tag_data_browsers()
    
    def _tag_data_browsers(self):
        """
        为数据显示的QTextBrowser打上标签
        """
        data_widgets = [
            'textBrowser_chk_2', 'textBrowser_chk_3', 'textBrowser_chk_4', 'textBrowser_chk_5',
            'textBrowser_chk_6', 'textBrowser_chk_7', 'textBrowser_chk_8', 'textBrowser_chk_9',
            'textBrowser_chk_10', 'textBrowser_chk_11', 'textBrowser_chk_12'
        ]
        for name in data_widgets:
            if hasattr(self, name):
                widget = getattr(self, name)
                widget.setProperty("techRole", "data")
                widget.setStyle(widget.style())
    
    def _style_text_browsers(self):
        """
        已由全局QSS处理
        """
        pass

    def showEvent(self, e):
        super().showEvent(e)
        if not self._timer.isActive():
            self._timer.start()

    def closeEvent(self, e):
        # 关闭时一定停掉
        if self._timer.isActive():
            self._timer.stop()
        super().closeEvent(e)
    
    def _poll_snapshot(self):
        """定时拉取 DATAS 的快照，并取出 all_dict"""
        try:
            snap = DATAS.snapshot()  # 线程安全
            all_dict = snap.get("all_data_dict", {}) or {}
            read_coils_0_13=all_dict["read_coils_0_13"]["RxData"]
            read_coils_16_24=all_dict["read_coils_16_24"]["RxData"]
            read_coils_27_31=all_dict["read_coils_27_31"]["RxData"]
            read_holding_registers_0_13=all_dict["read_holding_registers_0_13"]["RxData"]
            read_holding_registers_16_24=all_dict["read_holding_registers_16_24"]["RxData"]
            read_holding_registers_32_39=all_dict["read_holding_registers_32_39"]["RxData"]
            # 下煤机状态 
            xiameijizhuangtaikz = read_coils_0_13[0]
            if xiameijizhuangtaikz:
                self.textBrowser_chk_9.setPlainText("运行")
            else:
                self.textBrowser_chk_9.setPlainText("关闭")
            # 下煤机状态 
            xiameijizhuangtai = read_coils_0_13[1]
            if xiameijizhuangtai:
                self.textBrowser_chk_2.setPlainText("正常")
            else:
                self.textBrowser_chk_2.setPlainText("故障")
            # 阀门开度
            famenkaidu = read_holding_registers_32_39[0]
            famenkaidu = int(famenkaidu, 16)
            famenkaidu = str(famenkaidu)
            self.textBrowser_chk_3.setPlainText(famenkaidu)
            self.textBrowser_chk_10.setPlainText(famenkaidu)
            # 升降高度
            shengjianggaodu = read_holding_registers_32_39[1]
            shengjianggaodu = int(shengjianggaodu, 16)
            shengjianggaodu = str(shengjianggaodu)
            self.textBrowser_chk_4.setPlainText(shengjianggaodu)
            self.textBrowser_chk_11.setPlainText(shengjianggaodu)
            # 翻板高度
            fanbangaodu = read_holding_registers_32_39[2]
            fanbangaodu = int(fanbangaodu, 16)
            fanbangaodu = str(fanbangaodu)
            self.textBrowser_chk_5.setPlainText(fanbangaodu)
            self.textBrowser_chk_12.setPlainText(fanbangaodu)
            # 是否装载 
            shifouzhuangzai = read_coils_0_13[2]
            if shifouzhuangzai:
                self.textBrowser_chk_8.setPlainText("是")
            else:
                self.textBrowser_chk_8.setPlainText("否")
            # 装料进度
            zhuangliaojindu = read_holding_registers_32_39[3]
            zhuangliaojindu = int(zhuangliaojindu, 16)/self.chexianggaodu
            zhuangliaojindu = str(zhuangliaojindu)
            self.textBrowser_chk_7.setPlainText(zhuangliaojindu)
            # 料面高度
            liaomiangaodu = read_holding_registers_32_39[3]
            liaomiangaodu = int(liaomiangaodu, 16)
            liaomiangaodu = str(liaomiangaodu)
            self.textBrowser_chk_6.setPlainText(liaomiangaodu)
        except Exception as ex:
            # 避免异常把定时器干掉，可在标题或状态区提示
            self.setWindowTitle(f"CONTROL CENTER - ERROR: {ex}")

class TrainLabelWindow(QMainWindow, Ui_Trainlabel):
    """
    火车视觉识别窗口
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 设置窗口属性
        self.setWindowTitle("VISUAL RECOGNITION - SYSTEM MONITOR")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        
        # 应用科技感样式
        self.setStyleSheet(UIStyleManager.get_modern_style())
        
        # 智能缩放处理
        UIStyleManager.apply_smart_scaling(self, base_width=1690, base_height=1250)
        
        self._cam_thread = None

        # --- 在 QGraphicsView 上准备 Scene 和 PixmapItem ---
        self.scene = QGraphicsScene(self.train_picture)
        self.train_picture.setScene(self.scene)

        # 可选：优化与观感
        self.train_picture.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform
        )
        self.train_picture.setTransformationAnchor(self.train_picture.AnchorViewCenter)
        self.train_picture.setResizeAnchor(self.train_picture.AnchorViewCenter)
        self.train_picture.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.train_picture.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 用于承载每帧图像的 item
        self._pix_item = QGraphicsPixmapItem()
        self.scene.addItem(self._pix_item)

        # 背景色(可选，与你 ui 中的样式一致即可)
        self.train_picture.setBackgroundBrush(self.train_picture.palette().base())

    def attach_camera_source(self, cam_thread):
        # """复用外部 CameraThread（不持有所有权，不负责 stop）"""
        # self._cam_thread = cam_thread
        # if self._cam_thread:
        #     # 连接即可
        #     self._cam_thread.frameReady.connect(self.on_frame)
        #     self._cam_thread.error.connect(self.on_camera_error)
        if self._cam_thread is cam_thread:
            return
        self.detach_camera_source()
        self._cam_thread = cam_thread
        if self._cam_thread:
            self._cam_thread.frameReady.connect(self.on_frame, Qt.QueuedConnection)
            self._cam_thread.error.connect(self.on_camera_error, Qt.QueuedConnection)

    def detach_camera_source(self):
        # """断开连接，不停止线程"""
        # if self._cam_thread:
        #     try:
        #         self._cam_thread.frameReady.disconnect(self.on_frame)
        #         self._cam_thread.error.disconnect(self.on_camera_error)
        #     except Exception:
        #         pass
        # self._cam_thread = None
        if self._cam_thread:
            try:
                self._cam_thread.frameReady.disconnect(self.on_frame)
            except Exception:
                pass
            try:
                self._cam_thread.error.disconnect(self.on_camera_error)
            except Exception:
                pass
        self._cam_thread = None

    def closeEvent(self, event):
        # 这里改为仅断开连接，不 stop
        self.detach_camera_source()
        event.accept()

    # 打开摄像头（注意：不再创建 QLabel）
    def open_with_camera(self, device_index=0, width=640, height=480, fps=30):
        # 启动摄像头线程
        self._cam_thread = CameraThread(
            device_index=device_index, width=width, height=height, fps=fps, parent=self
        )
        self._cam_thread.frameReady.connect(self.on_frame)
        self._cam_thread.error.connect(self.on_camera_error)
        self._cam_thread.start()

    def _fit_view(self):
        """
        让视口自适应当前 pixmap 尺寸
        """
        if not hasattr(self, '_pix_item') or self._pix_item is None:
            return
            
        pix = self._pix_item.pixmap()
        if pix.isNull():
            return
            
        rect = QRectF(pix.rect())
        if hasattr(self, 'scene') and self.scene is not None:
            self.scene.setSceneRect(rect)
            
        if hasattr(self, 'train_picture'):
            self.train_picture.fitInView(rect, Qt.KeepAspectRatio)
        elif hasattr(self, 'Train_graph'):
            self.Train_graph.fitInView(rect, Qt.KeepAspectRatio)
    
    def on_frame(self, qimg):
        if qimg is None or qimg.isNull() or not hasattr(self, '_pix_item') or self._pix_item is None:
            return
        try:
            pix = QPixmap.fromImage(qimg)
        except Exception:
            return
        self._pix_item.setPixmap(pix)
        self._fit_view()

    def resizeEvent(self, ev):
        """
        窗口或 QGraphicsView 尺寸变化时，保持自适应
        """
        super().resizeEvent(ev)
        self._fit_view()

    def on_camera_error(self, msg: str):
        # 也可以在 scene 里显示错误文字，这里简单使用窗口标题提示
        self.setWindowTitle(f"火车视觉识别主界面 - Camera error: {msg}")

    # def closeEvent(self, event):
    #     if self._cam_thread:
    #         try:
    #             self._cam_thread.frameReady.disconnect(self.on_frame)
    #             self._cam_thread.error.disconnect(self.on_camera_error)
    #         except Exception:
    #             pass
    #         self._cam_thread.stop()
    #         self._cam_thread.wait()
    #         self._cam_thread = None
    #     event.accept()  # 只关闭当前窗口，避免退出整个应用

if __name__ == "__main__":
    # 启用高DPI缩放支持
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    # 设置应用程序整体风格
    app.setStyle("Fusion")
    
    # 创建并显示登录窗口
    window = LoginDialog()
    window.show()
    
    sys.exit(app.exec_())

