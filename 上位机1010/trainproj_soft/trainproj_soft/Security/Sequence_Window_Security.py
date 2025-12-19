# -*- coding: utf-8 -*-
import json
from PyQt5.QtWidgets import QWidget,QPushButton,QVBoxLayout,QHBoxLayout,QCheckBox,QScrollArea,QFileDialog
from PyQt5.QtCore import pyqtSignal,QSettings
from PyQt5.QtGui import QColor,QIcon,QFont,QPalette


class SequenceForm_Security(QWidget):
    selected_test = pyqtSignal(list)
    def __init__(self, data):
        super().__init__()

        self.setFixedSize(1000, 750)

        # 设置标题栏图标
        self.setWindowTitle("配置测试序列")
        self.setWindowIcon(QIcon("./Picture/logo.ico"))

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(25)  # 设置布局中的间距

        # 创建并添加“全选”QCheckBox
        self.select_all_checkbox = QCheckBox("全选")
        self.select_all_checkbox.setFont(QFont("SimSun", 24))  # 设置字体样式为宋体，x号字
        self.select_all_checkbox.setObjectName("select_all_checkbox")
        self.select_all_checkbox.stateChanged.connect(self.toggle_checkboxes)
        scroll_layout.addWidget(self.select_all_checkbox)

        self.checkboxes = [] # 每一个按钮
        self.box_name = [] # Name
        self.number_names = [] # Text
        self.Paras = [] # Paras

        for item in data:
            text = item.get("Name", "Not Found")  # 获取 "Name" 的内容
            if text == "Not Found":
                text = item.get("name", "")
            self.box_name.append(text)

            text = item.get("Text", "Not Found")  # 获取 "Text" 的内容
            if text == "Not Found":
                text = item.get("text", "")
            self.number_names.append(text)
            
            text = item.get("Paras", "Not Found")  # 获取 "Paras" 的内容
            if text == "Not Found":
                text = item.get("paras", "")
            self.Paras.append(text)


        # 创建并添加QCheckBox，并为它们设置名称
        for i in range(len(self.number_names)):
            checkbox = QCheckBox()
            checkbox.setText(self.number_names[i])
            checkbox.setObjectName(f"checkbox_{i+1}")
            checkbox.stateChanged.connect(self.change_checkbox_color)
            checkbox.setFont(QFont("SimSun", 24))  # 设置字体样式为宋体，14号字
            checkbox.setStyleSheet("background-color: none;border-radius: 9px; padding: 12px;")
            self.checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)
        scroll_layout.addStretch(1)

        scroll_area.setWidget(scroll_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        main_layout.setSpacing(25)  # 设置布局中的间距为20

         # 创建按钮布局
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFont(QFont("SimSun", 18))
        self.cancel_button.setStyleSheet("background-color:#ff1744")
        self.cancel_button.clicked.connect(self.close)
        button_layout.addWidget(self.cancel_button)

        self.save_button = QPushButton("确定")
        self.save_button.setFont(QFont("SimSun", 18))
        self.save_button.setStyleSheet("background-color:#64dd17")
        self.save_button.clicked.connect(self.save_checkbox_state)
        button_layout.addWidget(self.save_button)

        self.export_button = QPushButton("导出")
        self.export_button.setFont(QFont("SimSun", 18))
        self.export_button.setStyleSheet("background-color:#5f9ea0")
        self.export_button.clicked.connect(self.export_to_json)
        button_layout.addWidget(self.export_button)


        self.setAutoFillBackground(True)  # 设置窗口自动填充背景
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))  # 设置窗口的背景颜色为白色
        self.setPalette(palette)

        self.load_checkbox_state()

    def save_checkbox_state(self): # 保存为config.ini文件
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        for checkbox in self.checkboxes:
            name = checkbox.objectName()
            state = 1 if checkbox.isChecked() else 0
            settings.setValue(f'Security_checkbox_state/{name}', state)
        state = 1 if self.select_all_checkbox.isChecked() else 0
        settings.setValue(f'Security_checkbox_state/{self.select_all_checkbox.objectName()}', state)

        selected = [] # 选中按钮数据格式[[Name1,Text1,Paras1],[Name2,Text2,Paras2]...]
        for checkbox in self.checkboxes:
            if checkbox.isChecked():
                selected_alone = []
                selected_alone.append(self.box_name[self.checkboxes.index(checkbox)])
                selected_alone.append(self.number_names[self.checkboxes.index(checkbox)])
                selected_alone.append(self.Paras[self.checkboxes.index(checkbox)])
                selected.append(selected_alone)
        self.selected_test.emit(selected) # 把选中的测试项发送出去
        self.close()


    def export_to_json(self):
        selected_checkboxes = []

        for i in range(len(self.checkboxes)):
            checkbox = self.checkboxes[i]
            if checkbox.isChecked():
                checkbox_info = {
                    "Name": self.box_name[i],
                    "Text": self.number_names[i],
                    "Paras": self.Paras[i]
                }
                selected_checkboxes.append(checkbox_info)

        # 添加顶部固定内容
        output_data = {
            "SequenceName": "VideoTest",
            "ProtocolType": "Linux",
            "PlatformName": "IPC",
            "TestItems": selected_checkboxes
        }

        # 打开文件对话框，选择导出文件的位置
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "选择导出位置", "", "JSON Files (*.json)")

        if file_path:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(output_data, file, indent=2, ensure_ascii=False)


    def closeEvent(self, event):
        # 在关闭窗口时执行清理操作，如保存数据、释放资源等
        event.accept()

    def load_checkbox_state(self):
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        for checkbox in self.checkboxes:
            name = checkbox.objectName()
            state = settings.value(f'Security_checkbox_state/{name}', 0, type=int)
            checkbox.setChecked(bool(state))
        state = settings.value(f'Security_checkbox_state/{self.select_all_checkbox.objectName()}', 0, type=int)
        self.select_all_checkbox.setChecked(bool(state))

    def toggle_checkboxes(self, state):
        for checkbox in self.checkboxes:
            checkbox.setChecked(state == 2)  # 2 表示选中状态

    def change_checkbox_color(self, state):
        checkbox = self.sender()
        if state == 2:  # 选中状态
            checkbox.setStyleSheet("background-color: #e7e7e7;border-radius: 9px; padding: 12px;")
        else:
            checkbox.setStyleSheet("background-color: none;border-radius: 9px; padding: 12px;")
