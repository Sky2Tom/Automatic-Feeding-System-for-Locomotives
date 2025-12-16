import sys
from PyQt5.QtWidgets import QMainWindow, QDialog, QApplication
from Ui_train import Ui_MainWindow  # 主界面
from Ui_main import Ui_Dialog       # 子界面
from Ui_machine_history import Ui_layoff_history  # 下料历史界面
from Ui_train_warehouse_management import Ui_TrainQuery  # 火车型号管理界面
from Ui_train_warehouse_update import Ui_TrainQuery as Ui_TrainUpdate  # 火车型号更新界面

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 绑定按钮点击事件
        self.pushButton_8.clicked.connect(self.open_train_management)  # "火车型号尺寸"按钮
        self.pushButton_7.clicked.connect(self.open_machine_history)   # "下料历史查询"按钮
        
    def open_train_management(self):
        # 创建火车型号管理子窗口
        self.train_management_window = TrainManagementWindow()
        self.train_management_window.show()
        
    def open_machine_history(self):
        # 创建下料历史子窗口
        self.machine_history_window = MachineHistoryWindow()
        self.machine_history_window.show()

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
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())