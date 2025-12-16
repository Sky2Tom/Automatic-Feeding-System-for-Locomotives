import sys
from PyQt5.QtWidgets import QApplication, QMainWindow  # 使用 QMainWindow
import Ui_train_  # 导入生成的 UI 文件

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 使用 QMainWindow，因为 UI 是基于 QMainWindow 的
    MainWindow = QMainWindow()
    
    # 使用正确的类名（查看 Ui_train.py 确认）
    ui = Ui_train.Ui_MainWindow()  # 可能是 Ui_MainWindow / Ui_Dialog / Ui_Form
    ui.setupUi(MainWindow)  # 设置 UI

    MainWindow.show()
    sys.exit(app.exec_())