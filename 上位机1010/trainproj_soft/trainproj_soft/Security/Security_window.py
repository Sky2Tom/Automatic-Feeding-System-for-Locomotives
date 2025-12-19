# -*- coding: utf-8 -*-
import sys,json,re,time,unicodedata
from PyQt5.QtWidgets import QWidget,QApplication,QHeaderView,QAbstractItemView,QMessageBox,QFileDialog,QTableWidgetItem,QToolButton
from PyQt5.QtGui import QIcon,QStandardItemModel,QStandardItem,QFont,QColor,QCursor
from PyQt5.QtCore import QSettings,Qt,QThread,QTimer
from functools import partial

from UI import Security_win
from Serial_Security import Serial_Qthread_function
from Sequence_Window_Security import SequenceForm_Security
from Setting_Window_Security import SettingForm
from Security_Firmware_Window import firmwaresetting
from Pass_station_Win import Pass_station_setting
from HTTP_MES import *
import Write2MySQL_update2

class Security_Form(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Security_win.Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon("./Picture/logo.ico"))

        self.stateTest = 1 # 切换页面(本地测试和工单测试)
        self.startTest_1 = False # 本地测试测试状态(由启动按钮来改变)
        self.startTest_2 = False # 工单测试测试状态(由启动按钮来改变)
        self.test_pre = False # 测试项是否已经选择
        self.channel = 1 # 通道数
        self.current_index_1 = 0 # 测试的设置界面切换
        self.current_index_2 = 0
        self.current_index_3 = 0
        self.current_index_4 = 0
        self.SN_1 = ''
        self.SN_2 = ''
        self.SN_3 = ''
        self.SN_4 = ''
        self.current_command_index = 0  # 记录当前需要发送的命令在命令列表中的下标
        self.current_command_index_2 = 0 
        self.current_command_index_3 = 0
        self.current_command_index_4 = 0
        self.test_item_id = 0 # 记录当前产测的项
        self.test_item_id_2 = 0 
        self.test_item_id_3 = 0 
        self.test_item_id_4 = 0 
        self.serial_open_flage_1 = False # 串口连接标志位
        self.serial_open_flage_2 = False # 串口连接标志位
        self.serial_open_flage_3 = False # 串口连接标志位
        self.serial_open_flage_4 = False # 串口连接标志位
        self.serial_open_flage_slave = False 

        self.test_types = "OnlyToken"  # "Remoter"和"OnlyToken"

        self.test_flag = False # 过站标志位
        self.test_flag_2 = False
        self.test_flag_3 = False
        self.test_flag_4 = False

        self.test_flag_ing_1 = False # 测试正在进行
        self.test_flag_ing_2 = False
        self.test_flag_ing_3 = False
        self.test_flag_ing_4 = False

        self.test_button = '' # 传递测试项名字到通过和失败按钮
        self.test_button_2 = ''
        self.test_button_3 = ''
        self.test_button_4 = ''

        self.time_send = 0 # 记录单项测试开始时间
        self.time_record = [] # 记录各项测试时间
        self.test_result = [] # 记录各项测试结果
        self.test_message = [] # 产测信息
        self.commands_rec = [] # 接收产测消息

        self.time_send_2 = 0 
        self.time_record_2 = [] 
        self.test_result_2 = [] 
        self.test_message_2 = []
        self.commands_rec_2 = []

        self.time_send_3 = 0 
        self.time_record_3 = [] 
        self.test_result_3 = [] 
        self.test_message_3 = []
        self.commands_rec_3 = []

        self.time_send_4 = 0 
        self.time_record_4 = [] 
        self.test_result_4 = [] 
        self.test_message_4 = []
        self.commands_rec_4 = []

        self.serial_slave_channel = 1 # 红外控制串口对应哪个主串口

        self.processid = '' # 制令单号
        self.itemcode = '' #  产品编码
        self.protectid = [] # 产线编码和工序名称 [{'CA_ID': 'GMCS2-0', 'PMO_AREA_SN': 'GMCS2', 'GROUP_NAME': '工模测试'}]

        self.UI_Init() # 界面初始化
        self.pushButton_8_3_open_start() # 初始加载json文件
        self.Serial_init() # 串口通信初始化
        self.Serial_init_2()
        self.Serial_init_3()
        self.Serial_init_4() 
        self.Serial_init_slave()

        self.connect_auto = QTimer() # 自动连接串口
        self.connect_auto.timeout.connect(self.connect_auto_func_1)
        self.connect_auto_2 = QTimer() # 自动连接串口
        self.connect_auto_2.timeout.connect(self.connect_auto_func_2)
        self.connect_auto_3 = QTimer() # 自动连接串口
        self.connect_auto_3.timeout.connect(self.connect_auto_func_3)
        self.connect_auto_4 = QTimer() # 自动连接串口
        self.connect_auto_4.timeout.connect(self.connect_auto_func_4)
        self.connect_auto_slave = QTimer() # 自动连接串口
        self.connect_auto_slave.timeout.connect(self.connect_auto_slave_func)

        self.receive_time_out = QTimer() # 接收定时器
        self.receive_time_out.timeout.connect(self.receive_time_out_func)
        self.rec_buff = bytearray()
        self.receive_time_out_2 = QTimer() # 接收定时器
        self.receive_time_out_2.timeout.connect(self.receive_time_out_func_2)
        self.rec_buff_2 = bytearray()
        self.receive_time_out_3 = QTimer() # 接收定时器
        self.receive_time_out_3.timeout.connect(self.receive_time_out_func_3)
        self.rec_buff_3 = bytearray()
        self.receive_time_out_4 = QTimer() # 接收定时器
        self.receive_time_out_4.timeout.connect(self.receive_time_out_func_4)
        self.rec_buff_4 = bytearray()

        self.receive_time_out_slave = QTimer() # 控制串口接收定时器
        self.receive_time_out_slave.timeout.connect(self.receive_time_out_slave_func)
        self.rec_buff_slave = bytearray()

        self.infrared = QTimer() # 红外接收测试
        self.infrared.timeout.connect(self.infrared_func)
        self.infrared_2 = QTimer() # 红外接收测试
        self.infrared_2.timeout.connect(self.infrared_func_2)
        self.infrared_3 = QTimer() # 红外接收测试
        self.infrared_3.timeout.connect(self.infrared_func_3)
        self.infrared_4 = QTimer() # 红外接收测试
        self.infrared_4.timeout.connect(self.infrared_func_4)

        self.infrared_emit = QTimer() # 红外发射测试
        self.infrared_emit.timeout.connect(self.infrared_emit_func)
        self.infrared_emit_2 = QTimer() # 红外发射测试
        self.infrared_emit_2.timeout.connect(self.infrared_emit_func_2)
        self.infrared_emit_3 = QTimer() # 红外发射测试
        self.infrared_emit_3.timeout.connect(self.infrared_emit_func_3)
        self.infrared_emit_4 = QTimer() # 红外发射测试
        self.infrared_emit_4.timeout.connect(self.infrared_emit_func_4)

        self.testMode_flage_time_1 = QTimer() # 发送产测命令
        self.testMode_flage_time_1.timeout.connect(self.testMode_flage_time_fun_1)
        self.testMode_flage_time_2 = QTimer() # 发送产测命令
        self.testMode_flage_time_2.timeout.connect(self.testMode_flage_time_fun_2)
        self.testMode_flage_time_3 = QTimer() # 发送产测命令
        self.testMode_flage_time_3.timeout.connect(self.testMode_flage_time_fun_3)
        self.testMode_flage_time_4 = QTimer() # 发送产测命令
        self.testMode_flage_time_4.timeout.connect(self.testMode_flage_time_fun_4)

        self.slave_control = False # 控制串口是否占用
        self.slave_control_chan_1 = 1 # 1接收 2发射
        self.slave_control_chan_2 = 1
        self.slave_control_chan_3 = 1
        self.slave_control_chan_4 = 1
        self.channel_control_1 = QTimer()
        self.channel_control_1.timeout.connect(self.channel_control_fun_1)
        self.channel_control_2 = QTimer()
        self.channel_control_2.timeout.connect(self.channel_control_fun_2)
        self.channel_control_3 = QTimer()
        self.channel_control_3.timeout.connect(self.channel_control_fun_3)
        self.channel_control_4 = QTimer()
        self.channel_control_4.timeout.connect(self.channel_control_fun_4)

        self.infrared_ng_1 = QTimer()
        self.infrared_ng_1.timeout.connect(self.infrared_ng_fun_1)
        self.infrared_ng_2 = QTimer()
        self.infrared_ng_2.timeout.connect(self.infrared_ng_fun_2)
        self.infrared_ng_3 = QTimer()
        self.infrared_ng_3.timeout.connect(self.infrared_ng_fun_3)
        self.infrared_ng_4 = QTimer()
        self.infrared_ng_4.timeout.connect(self.infrared_ng_fun_4)
    
    def UI_Init(self):
        self.ui.groupBox_4.setVisible(False) # 测试窗口
        self.ui.groupBox_5.setVisible(False)
        self.ui.groupBox_6.setVisible(False)
        self.ui.groupBox_7.setVisible(False)

        self.ui.pushButton_101.setEnabled(False) # 运行按钮
        self.ui.pushButton_201.setEnabled(False)
        self.ui.pushButton_301.setEnabled(False)
        self.ui.pushButton_401.setEnabled(False)

        self.ui.pushButton_103.setVisible(False) # 通过与失败
        self.ui.pushButton_104.setVisible(False)
        self.ui.pushButton_203.setVisible(False)
        self.ui.pushButton_204.setVisible(False)
        self.ui.pushButton_303.setVisible(False)
        self.ui.pushButton_304.setVisible(False)
        self.ui.pushButton_403.setVisible(False)
        self.ui.pushButton_404.setVisible(False)

        self.ui.label_103.setVisible(False) # 测试项提示
        self.ui.label_203.setVisible(False)
        self.ui.label_303.setVisible(False)
        self.ui.label_403.setVisible(False)
        self.ui.label_3_2.setStyleSheet('border-width:2px;border-style:dotted;border-bottom-color:rgb(0,0,0);border-top-color:rgb(240,240,240);border-left-color:rgb(240,240,240);border-right-color:rgb(240,240,240);')
        self.ui.label_4_8.setStyleSheet('border-width:2px;border-style:dotted;border-bottom-color:rgb(0,0,0);border-top-color:rgb(240,240,240);border-left-color:rgb(240,240,240);border-right-color:rgb(240,240,240);')
        self.ui.label_4_9.setStyleSheet('border-width:2px;border-style:dotted;border-bottom-color:rgb(0,0,0);border-top-color:rgb(240,240,240);border-left-color:rgb(240,240,240);border-right-color:rgb(240,240,240);')
        
        self.ui.pushButton_102.clicked.connect(self.next_page) # 测试界面的菜单按钮
        self.ui.pushButton_202.clicked.connect(self.next_page)
        self.ui.pushButton_302.clicked.connect(self.next_page)
        self.ui.pushButton_402.clicked.connect(self.next_page)

        self.ui.pushButton_10.setStyleSheet("background-color: rgb(30, 144, 255);border: none; color: white;") # 设置启动按钮的颜色 
        self.ui.tableView_12.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 设置通道的表格
        self.ui.tableView_12.horizontalHeader().setVisible(False) # 去掉水平和垂直表头
        self.ui.tableView_12.verticalHeader().setVisible(False)

        self.ui.pushButton_1_1.clicked.connect(self.pushButton_1_1_open) # 本地测试按钮
        self.ui.pushButton_1_2.clicked.connect(self.pushButton_1_2_open) # 工单测试按钮
        self.ui.pushButton_10.clicked.connect(self.pushButton_10_open)   # 启动测试按钮
        self.ui.pushButton_8_3.clicked.connect(self.pushButton_8_3_open) # 导入按钮
        self.ui.pushButton_8_4.clicked.connect(self.pushButton_8_4_open) # 编辑按钮
        self.ui.pushButton_101.clicked.connect(self.Test_start) # 测试界面运行按钮
        self.ui.pushButton_103.clicked.connect(partial(self.pushButton_10_34, 'test'))    # 测试界面通过按钮
        self.ui.pushButton_104.clicked.connect(partial(self.pushButton_10_34, 'cancel'))    # 测试界面取消按钮

        self.ui.pushButton_201.clicked.connect(self.Test_start_2) # 测试界面运行按钮
        self.ui.pushButton_203.clicked.connect(partial(self.pushButton_20_34, 'test'))    # 测试界面通过按钮
        self.ui.pushButton_204.clicked.connect(partial(self.pushButton_20_34, 'cancel'))    # 测试界面取消按钮

        self.ui.pushButton_301.clicked.connect(self.Test_start_3) # 测试界面运行按钮
        self.ui.pushButton_303.clicked.connect(partial(self.pushButton_30_34, 'test'))    # 测试界面通过按钮
        self.ui.pushButton_304.clicked.connect(partial(self.pushButton_30_34, 'cancel'))    # 测试界面取消按钮
    
        self.ui.pushButton_401.clicked.connect(self.Test_start_4) # 测试界面运行按钮
        self.ui.pushButton_403.clicked.connect(partial(self.pushButton_40_34, 'test'))    # 测试界面通过按钮
        self.ui.pushButton_404.clicked.connect(partial(self.pushButton_40_34, 'cancel'))    # 测试界面取消按钮
        
        self.ui.pushButton.clicked.connect(self.select_process) # 选择工序
        self.ui.lineEdit_2_3.returnPressed.connect(self.select_process) # 选择工序
    
    def Serial_init(self):
        self.Serial_QThread_1  = QThread()
        self.Serial_Qthread_function_1 = Serial_Qthread_function()
        self.Serial_Qthread_function_1.moveToThread(self.Serial_QThread_1)
        self.Serial_Qthread_function_1.signal_Serial_qthread_function_Init.connect(self.Serial_Qthread_function_1.Serial_qthread_function_Init)
        self.Serial_Qthread_function_1.signal_pushButton_Open.connect(self.Serial_Qthread_function_1.slot_pushButton_Open)
        self.Serial_Qthread_function_1.signal_SendData.connect(self.Serial_Qthread_function_1.slot_SendData)
        self.Serial_Qthread_function_1.signal_pushButton_Open_flage.connect(self.slot_pushButton_Open_flage)
        self.Serial_Qthread_function_1.signal_readyRead.connect(self.slot_readyRead)

    def Serial_init_2(self):
        self.Serial_QThread_2  = QThread()
        self.Serial_Qthread_function_2 = Serial_Qthread_function()
        self.Serial_Qthread_function_2.moveToThread(self.Serial_QThread_2)
        self.Serial_Qthread_function_2.signal_Serial_qthread_function_Init.connect(self.Serial_Qthread_function_2.Serial_qthread_function_Init)
        self.Serial_Qthread_function_2.signal_pushButton_Open.connect(self.Serial_Qthread_function_2.slot_pushButton_Open)
        self.Serial_Qthread_function_2.signal_SendData.connect(self.Serial_Qthread_function_2.slot_SendData)
        self.Serial_Qthread_function_2.signal_pushButton_Open_flage.connect(self.slot_pushButton_Open_flage_2)
        self.Serial_Qthread_function_2.signal_readyRead.connect(self.slot_readyRead_2)
    
    def Serial_init_3(self):
        self.Serial_QThread_3  = QThread()
        self.Serial_Qthread_function_3 = Serial_Qthread_function()
        self.Serial_Qthread_function_3.moveToThread(self.Serial_QThread_3)
        self.Serial_Qthread_function_3.signal_Serial_qthread_function_Init.connect(self.Serial_Qthread_function_3.Serial_qthread_function_Init)
        self.Serial_Qthread_function_3.signal_pushButton_Open.connect(self.Serial_Qthread_function_3.slot_pushButton_Open)
        self.Serial_Qthread_function_3.signal_SendData.connect(self.Serial_Qthread_function_3.slot_SendData)
        self.Serial_Qthread_function_3.signal_pushButton_Open_flage.connect(self.slot_pushButton_Open_flage_3)
        self.Serial_Qthread_function_3.signal_readyRead.connect(self.slot_readyRead_3)
    
    def Serial_init_4(self):
        self.Serial_QThread_4  = QThread()
        self.Serial_Qthread_function_4 = Serial_Qthread_function()
        self.Serial_Qthread_function_4.moveToThread(self.Serial_QThread_4)
        self.Serial_Qthread_function_4.signal_Serial_qthread_function_Init.connect(self.Serial_Qthread_function_4.Serial_qthread_function_Init)
        self.Serial_Qthread_function_4.signal_pushButton_Open.connect(self.Serial_Qthread_function_4.slot_pushButton_Open)
        self.Serial_Qthread_function_4.signal_SendData.connect(self.Serial_Qthread_function_4.slot_SendData)
        self.Serial_Qthread_function_4.signal_pushButton_Open_flage.connect(self.slot_pushButton_Open_flage_4)
        self.Serial_Qthread_function_4.signal_readyRead.connect(self.slot_readyRead_4)
    
    def Serial_init_slave(self):
        self.Serial_QThread_slave  = QThread()
        self.Serial_Qthread_function_slave = Serial_Qthread_function()
        self.Serial_Qthread_function_slave.moveToThread(self.Serial_QThread_slave)
        self.Serial_Qthread_function_slave.signal_Serial_qthread_function_Init.connect(self.Serial_Qthread_function_slave.Serial_qthread_function_Init)
        self.Serial_Qthread_function_slave.signal_pushButton_Open.connect(self.Serial_Qthread_function_slave.slot_pushButton_Open)
        self.Serial_Qthread_function_slave.signal_SendData.connect(self.Serial_Qthread_function_slave.slot_SendData)
        self.Serial_Qthread_function_slave.signal_pushButton_Open_flage.connect(self.slot_pushButton_Open_flage_slave)
        self.Serial_Qthread_function_slave.signal_readyRead.connect(self.slot_readyRead_slave)

    
    def connect_auto_func_1(self):
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        parameter = {}
        parameter['PortName_master'] = settings.value("Security_serial/master_PortName_1")
        parameter['BaudRate_master'] = int(settings.value("Security_serial/master_BaudRate_1"))
        self.Serial_Qthread_function_1.signal_pushButton_Open.emit(parameter)
        
    
    def connect_auto_func_2(self):
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        parameter = {}
        parameter['PortName_master'] = settings.value("Security_serial/master_PortName_2")
        parameter['BaudRate_master'] = int(settings.value("Security_serial/master_BaudRate_2"))
        self.Serial_Qthread_function_2.signal_pushButton_Open.emit(parameter)
        
    
    def connect_auto_func_3(self):
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        parameter = {}
        parameter['PortName_master'] = settings.value("Security_serial/master_PortName_3")
        parameter['BaudRate_master'] = int(settings.value("Security_serial/master_BaudRate_3"))
        self.Serial_Qthread_function_3.signal_pushButton_Open.emit(parameter)
        
    
    def connect_auto_func_4(self):
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        parameter = {}
        parameter['PortName_master'] = settings.value("Security_serial/master_PortName_4")
        parameter['BaudRate_master'] = int(settings.value("Security_serial/master_BaudRate_4"))
        self.Serial_Qthread_function_4.signal_pushButton_Open.emit(parameter)
    
    def connect_auto_slave_func(self):
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        parameter = {}
        parameter['PortName_master'] = settings.value("Security_serial/slave_PortName")
        parameter['BaudRate_master'] = int(settings.value("Security_serial/slave_BaudRate"))
        self.Serial_Qthread_function_slave.signal_pushButton_Open.emit(parameter)
    
    def testMode_flage_time_fun_1(self):
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        send_list = []
        send_text = settings.value(f"{self.test_types}_command/conmmand_1")
        while send_text != '':
            try:
                num = int(send_text[0:2],16)
            except:
                return
            send_text = send_text[2:].strip()
            send_list.append(num)
        Byte_data = bytes(send_list)
        parameter = {}
        parameter['data'] = Byte_data
        self.Serial_Qthread_function_1.signal_SendData.emit(parameter)
    
    def testMode_flage_time_fun_2(self):
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        send_list = []
        send_text = settings.value(f"{self.test_types}_command/conmmand_1")
        while send_text != '':
            try:
                num = int(send_text[0:2],16)
            except:
                return
            send_text = send_text[2:].strip()
            send_list.append(num)
        Byte_data = bytes(send_list)
        parameter = {}
        parameter['data'] = Byte_data
        self.Serial_Qthread_function_2.signal_SendData.emit(parameter)    

    def testMode_flage_time_fun_3(self):
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        send_list = []
        send_text = settings.value(f"{self.test_types}_command/conmmand_1")
        while send_text != '':
            try:
                num = int(send_text[0:2],16)
            except:
                return
            send_text = send_text[2:].strip()
            send_list.append(num)
        Byte_data = bytes(send_list)
        parameter = {}
        parameter['data'] = Byte_data
        self.Serial_Qthread_function_3.signal_SendData.emit(parameter)    

    def testMode_flage_time_fun_4(self):
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        send_list = []
        send_text = settings.value(f"{self.test_types}_command/conmmand_1")
        while send_text != '':
            try:
                num = int(send_text[0:2],16)
            except:
                return
            send_text = send_text[2:].strip()
            send_list.append(num)
        Byte_data = bytes(send_list)
        parameter = {}
        parameter['data'] = Byte_data
        self.Serial_Qthread_function_4.signal_SendData.emit(parameter) 

    def slot_pushButton_Open_flage_slave(self,state):
        if state == 1:
            print("控制串口打开")
            self.serial_open_flage_slave = True
            self.connect_auto_slave.stop()
        elif state != 1:
            print("控制串口关闭")
            self.serial_open_flage_slave = False
            if self.stateTest == 1 and self.startTest_1:
                self.connect_auto_slave.start(2000)
            elif self.stateTest == 2 and self.startTest_2:
                self.connect_auto_slave.start(2000)
    
    def slot_pushButton_Open_flage(self, state):
        if state == 1:
            print("串口打开")
            self.serial_open_flage_1 = True
            self.connect_auto.stop()
            self.ui.label_101.setStyleSheet("QLabel {background-color : rgb(0,145,234); color : black; }")
            if self.current_command_index == 0:
                self.ui.label_101.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
            for pos in self.connect_position:
                item = self.ui.tableWidget_101.item(pos, 3) # 修改串口连接状态
                item.setText("已就绪")
                item.setForeground(QColor(255, 165, 0))  # 修改字体颜色为橙色
            self.ui.pushButton_101.setEnabled(True)
            self.ui.lineEdit_101.setEnabled(True)
            if self.ui.comboBox_5_2.currentText()=="扫码运行" and self.stateTest==1 or self.ui.comboBox_6_3.currentText()=="扫码运行" and self.stateTest==2:
                self.ui.lineEdit_101.returnPressed.connect(self.Test_start) # 扫码运行
        elif state != 1:
            print("串口关闭")
            self.serial_open_flage_1 = False
            if self.current_command_index != 0:
                QMessageBox.warning(self, '警告', '通道1 连接断开，请检查线路') 
            self.test_reset()
            self.ui.label_101.setStyleSheet("QLabel { background-color : gray; color : black; }")
            self.ui.label_101.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
            if self.stateTest == 1 and self.startTest_1:
                self.connect_auto.start(2000)
            elif self.stateTest == 2 and self.startTest_2:
                self.connect_auto.start(2000)
            for pos in self.connect_position:
                item = self.ui.tableWidget_101.item(pos, 3) # 修改串口连接状态
                item.setText("未就绪")
                item.setForeground(QColor(0, 0, 0))  # 修改字体颜色为黑色
            self.ui.pushButton_101.setEnabled(False)
            self.ui.lineEdit_101.setEnabled(True)
            try:
                self.ui.lineEdit_101.returnPressed.disconnect(self.Test_start) # 扫码运行
            except:pass
    
    def slot_pushButton_Open_flage_2(self, state):
        if state == 1:
            print("串口打开")
            self.serial_open_flage_2 = True
            self.connect_auto_2.stop()
            self.ui.label_201.setStyleSheet("QLabel {background-color : rgb(0,145,234); color : black; }")
            if self.current_command_index_2 == 0:
                self.ui.label_201.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
            for pos in self.connect_position:
                item = self.ui.tableWidget_201.item(pos, 3) # 修改串口连接状态
                item.setText("已就绪")
                item.setForeground(QColor(255, 165, 0))  # 修改字体颜色为橙色
            self.ui.pushButton_201.setEnabled(True)
            self.ui.lineEdit_201.setEnabled(True)
            if self.ui.comboBox_5_2.currentText()=="扫码运行" and self.stateTest==1 or self.ui.comboBox_6_3.currentText()=="扫码运行" and self.stateTest==2:
                self.ui.lineEdit_201.returnPressed.connect(self.Test_start_2) # 扫码运行
        elif state != 1:
            print("串口关闭")
            self.serial_open_flage_2 = False
            if self.current_command_index_2 != 0:
                QMessageBox.warning(self, '警告', '通道1 连接断开，请检查线路') 
            self.test_reset_2()
            self.ui.label_201.setStyleSheet("QLabel { background-color : gray; color : black; }")
            self.ui.label_201.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
            if self.stateTest == 1 and self.startTest_1:
                self.connect_auto_2.start(2000)
            elif self.stateTest == 2 and self.startTest_2:
                self.connect_auto_2.start(2000)
            for pos in self.connect_position:
                item = self.ui.tableWidget_201.item(pos, 3) # 修改串口连接状态
                item.setText("未就绪")
                item.setForeground(QColor(0, 0, 0))  # 修改字体颜色为黑色
            self.ui.pushButton_201.setEnabled(False)
            self.ui.lineEdit_201.setEnabled(True)
            try:
                self.ui.lineEdit_201.returnPressed.disconnect(self.Test_start_2) # 扫码运行
            except:pass

    def slot_pushButton_Open_flage_3(self, state):
        if state == 1:
            print("串口打开")
            self.serial_open_flage_3 = True
            self.connect_auto_3.stop()
            self.ui.label_301.setStyleSheet("QLabel {background-color : rgb(0,145,234); color : black; }")
            if self.current_command_index_3 == 0:
                self.ui.label_301.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
            for pos in self.connect_position:
                item = self.ui.tableWidget_301.item(pos, 3) # 修改串口连接状态
                item.setText("已就绪")
                item.setForeground(QColor(255, 165, 0))  # 修改字体颜色为橙色
            self.ui.pushButton_301.setEnabled(True)
            self.ui.lineEdit_301.setEnabled(True)
            if self.ui.comboBox_5_2.currentText()=="扫码运行" and self.stateTest==1 or self.ui.comboBox_6_3.currentText()=="扫码运行" and self.stateTest==2:
                self.ui.lineEdit_301.returnPressed.connect(self.Test_start_3) # 扫码运行
        elif state != 1:
            print("串口关闭")
            self.serial_open_flage_3 = False
            if self.current_command_index_3 != 0:
                QMessageBox.warning(self, '警告', '通道1 连接断开，请检查线路') 
            self.test_reset_3()
            self.ui.label_301.setStyleSheet("QLabel { background-color : gray; color : black; }")
            self.ui.label_301.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
            if self.stateTest == 1 and self.startTest_1:
                self.connect_auto_3.start(2000)
            elif self.stateTest == 2 and self.startTest_2:
                self.connect_auto_3.start(2000)
            for pos in self.connect_position:
                item = self.ui.tableWidget_301.item(pos, 3) # 修改串口连接状态
                item.setText("未就绪")
                item.setForeground(QColor(0, 0, 0))  # 修改字体颜色为黑色
            self.ui.pushButton_301.setEnabled(False)
            self.ui.lineEdit_301.setEnabled(True)
            try:
                self.ui.lineEdit_301.returnPressed.disconnect(self.Test_start_3) # 扫码运行
            except:pass

    def slot_pushButton_Open_flage_4(self, state):
        if state == 1:
            print("串口打开")
            self.serial_open_flage_4 = True
            self.connect_auto_4.stop()
            self.ui.label_401.setStyleSheet("QLabel {background-color : rgb(0,145,234); color : black; }")
            if self.current_command_index_4 == 0:
                self.ui.label_401.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
            for pos in self.connect_position:
                item = self.ui.tableWidget_401.item(pos, 3) # 修改串口连接状态
                item.setText("已就绪")
                item.setForeground(QColor(255, 165, 0))  # 修改字体颜色为橙色
            self.ui.pushButton_401.setEnabled(True)
            self.ui.lineEdit_401.setEnabled(True)
            if self.ui.comboBox_5_2.currentText()=="扫码运行" and self.stateTest==1 or self.ui.comboBox_6_3.currentText()=="扫码运行" and self.stateTest==2:
                self.ui.lineEdit_401.returnPressed.connect(self.Test_start_4) # 扫码运行
        elif state != 1:
            print("串口关闭")
            self.serial_open_flage_4 = False
            if self.current_command_index_4 != 0:
                QMessageBox.warning(self, '警告', '通道1 连接断开，请检查线路') 
            self.test_reset_4()
            self.ui.label_401.setStyleSheet("QLabel { background-color : gray; color : black; }")
            self.ui.label_401.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
            if self.stateTest == 1 and self.startTest_1:
                self.connect_auto_4.start(2000)
            elif self.stateTest == 2 and self.startTest_2:
                self.connect_auto_4.start(2000)
            for pos in self.connect_position:
                item = self.ui.tableWidget_401.item(pos, 3) # 修改串口连接状态
                item.setText("未就绪")
                item.setForeground(QColor(0, 0, 0))  # 修改字体颜色为黑色
            self.ui.pushButton_401.setEnabled(False)
            self.ui.lineEdit_401.setEnabled(True)
            try:
                self.ui.lineEdit_401.returnPressed.disconnect(self.Test_start_4) # 扫码运行
            except:pass

    
    def select_process(self): # 选中工序
        self.processid = self.ui.lineEdit_2_3.text()
        if self.processid != '':
            data = {"M_MO_NUMBER":self.processid}
            response_data = GetGroupInfo(data)
            print(response_data)
            if response_data == None:
                QMessageBox.warning(self, '警告', '网络异常') 
                return
            if response_data['MSG'] == '获取数据成功':
                self.protectid = response_data['DETAIL']
                self.ui.comboBox_5_4.clear()
                for key in self.protectid:
                    self.ui.comboBox_5_4.addItem(key['GROUP_NAME']) 
            else:
                self.ui.pushButton_10.setEnabled(False)
                self.ui.pushButton_10.setStyleSheet("background-color: rgb(169, 213, 255);border: none; color: white;")
                QMessageBox.warning(self,'警告','工单号输入有误！')
                return
            
            data = {'INTERFACENO':'001','INTERFACEDATA':self.processid}
            response_data = ProcessGet(data)
            print(response_data)
            if response_data == None:
                QMessageBox.warning(self, '警告', '网络异常') 
                return
            if response_data['Message'] == 'OK:执行成功':
                data = response_data['Data'][0]['PM_TARGET_QTY']
                self.ui.label_4_8.setText(str(data))
                data = response_data['Data'][0]['PM_FINISH_COUNT']
                self.ui.label_4_9.setText(str(data))
                self.itemcode = response_data['Data'][0]['PM_MODEL_CODE']

            self.ui.pushButton_10.setEnabled(True) # 启动按钮打开
            self.ui.pushButton_10.setStyleSheet("background-color: rgb(30, 144, 255);border: none; color: white;")
        
        else:
            self.ui.pushButton_10.setEnabled(False) # ****
            self.ui.pushButton_10.setStyleSheet("background-color: rgb(169, 213, 255);border: none; color: white;")
            QMessageBox.warning(self,'警告','请输入工单号！')



    def MES_http_upload(self, channel, sn, time1, time2, test_message, time_record, test_result):
        print(test_message) 
        mac_upload = None
        for mes in test_message:
            if mes.get("mac",None) != None:
                mac_upload = mes["mac"]
                break
        print(mac_upload) 

        new_message = [str(d) if d else None for d in test_message] 
        print(new_message)
        
        print(time_record)
        total_time = 0
        for i in time_record:
            total_time = total_time+i
        total_time = total_time //1000
        print(self.items_text)
        print(test_result)
        
        sn = unicodedata.normalize('NFKC', sn).strip()
        mac = '-'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0,6)][::-1]) # 获取MAC地址
        
        settings = QSettings("../config_update.ini", QSettings.IniFormat)
        usr_name = settings.value("login info/username",'None')
        print("用户名：",usr_name)
        test_upload_params = {
            "fix_id": "firstTest",
            "dut_order_code": self.processid,
            "is_misdetect": "False",
            "dut_number_value": sn,
            "token": getTime(),
            "dut_number_name": self.ui.comboBox_8_3.currentText(),
            "elapsed": total_time,
            "retry_cnt": "1",
            "station": self.ui.comboBox_5_4.currentText(),
            "model": self.itemcode,
            "is_pass": "True",
            "user": usr_name,
            "pc_mac": mac
        }

        defect_code = None # 不良代码
        if not self.check_all_pass(test_result): # 测试项没有全部通过
            test_upload_params["is_pass"] = "False"
            defect_code = '000'
        test_upload_data = self.data_case(self.items_text, new_message, time_record, test_result)
        print(test_upload_data)
#####################################################################################################

        test_items_save = []
        for key in test_upload_data['cases']:
            test_item = []
            test_item.append(key['name'])
            test_item.append(key['value'])
            test_item.append(key['elapsed'])
            test_item.append(key['result'])
            test_items_save.append(test_item)
        print(test_items_save)

        # 上传测试数据
        # response_data = TestUpload(test_upload_params,test_upload_data)
        # print(response_data)

        # 过站
        data = {"M_EMP_NO":usr_name,"M_GROUP_NAME":self.ui.comboBox_5_4.currentText(),"M_SN":sn,"M_MO_NUMBER":self.processid}
        response_data = ProductStation(data)
        print(response_data)
        if response_data == None:
            QMessageBox.warning(self, '警告', '网络异常') 
            return
        resultMsg = response_data['MSG']
        if '过站失败' in resultMsg:
            QMessageBox.warning(self, f'警告 通道{channel}', resultMsg) 
        # 更新产出数量
        data = {'INTERFACENO':'001','INTERFACEDATA':self.processid}
        response_data = ProcessGet(data)
        if response_data == None:
            QMessageBox.warning(self, '警告', '网络异常') 
            return
        if response_data['Message'] == 'OK:执行成功':
            data = response_data['Data'][0]['PM_TARGET_QTY']
            self.ui.label_4_8.setText(str(data))
            data = response_data['Data'][0]['PM_FINISH_COUNT']
            self.ui.label_4_9.setText(str(data))
            self.itemcode = response_data['Data'][0]['PM_MODEL_CODE']

        try:
            Write2MySQL_update2.Write2MySQL(model = test_upload_params["model"],
                                    dut_number_name = test_upload_params["dut_number_name"],
                                    dut_number_value = test_upload_params["dut_number_value"],
                                    station = test_upload_params["station"],
                                    fix_id = test_upload_params["fix_id"],
                                    pc_mac = test_upload_params["pc_mac"],
                                    is_pass = test_upload_params["is_pass"],#测试结果
                                    elapsed = test_upload_params["elapsed"],    #测试总时长
                                    retry_cnt = test_upload_params["retry_cnt"],      #试测次数
                                    is_misdetect = test_upload_params["is_misdetect"],#是否误测
                                    defect_type_code = defect_code,
                                    test_key_value = None,
                                    product_mac = mac_upload,
                                    product_uuid = None,
                                    MES_station_passing_information = resultMsg,
                                    product_type = 'TUYA',
                                    test_start_time = time1,#测试开始时间
                                    Work_order_number = None,
                                    SN = test_upload_params["dut_number_value"],
                                    production_processes = test_upload_params["station"],
                                    product_model = self.itemcode,
                                    test_end_time = time2,#测试结束时间
                                    dut_order_code = test_upload_params["dut_order_code"],
                                    product_quantity = self.ui.label_4_8.text(),#产品数量
                                    test_item_info = test_items_save)
        except:
            print("上传数据库失败")

    def test_reset(self):
        self.current_command_index = 0
        self.test_item_id = 0
        self.ui.label_103.setVisible(False) 
        self.ui.pushButton_103.setVisible(False)
        self.ui.pushButton_104.setVisible(False)
        for index in range(len(self.timeIndex_finish)):
            waiting_item = self.ui.tableWidget_101.item(index, 6) # 修改等待状态
            waiting_item.setText("等待测试")
            waiting_item.setForeground(QColor(0,0,0)) # 黑色字体

            item = self.ui.tableWidget_101.item(index, 7) # 时间表格清零
            item.setText('')
            item = self.ui.tableWidget_101.item(index, 5) # 数据表格清零
            item.setText('')

    
    def test_reset_2(self):
        self.current_command_index_2 = 0
        self.test_item_id_2 = 0
        self.ui.label_203.setVisible(False) 
        self.ui.pushButton_203.setVisible(False)
        self.ui.pushButton_204.setVisible(False)
        for index in range(len(self.timeIndex_finish)):
            waiting_item = self.ui.tableWidget_201.item(index, 6) # 修改等待状态
            waiting_item.setText("等待测试")
            waiting_item.setForeground(QColor(0,0,0)) # 黑色字体

            item = self.ui.tableWidget_201.item(index, 7) # 时间表格清零
            item.setText('')
            item = self.ui.tableWidget_201.item(index, 5) # 数据表格清零
            item.setText('')

    
    def test_reset_3(self):
        self.current_command_index_3 = 0
        self.test_item_id_3 = 0
        self.ui.label_303.setVisible(False) 
        self.ui.pushButton_303.setVisible(False)
        self.ui.pushButton_304.setVisible(False)
        for index in range(len(self.timeIndex_finish)):
            waiting_item = self.ui.tableWidget_301.item(index, 6) # 修改等待状态
            waiting_item.setText("等待测试")
            waiting_item.setForeground(QColor(0,0,0)) # 黑色字体

            item = self.ui.tableWidget_301.item(index, 7) # 时间表格清零
            item.setText('')
            item = self.ui.tableWidget_301.item(index, 5) # 数据表格清零
            item.setText('')

    
    def test_reset_4(self):
        self.current_command_index_4 = 0
        self.test_item_id_4 = 0
        self.ui.label_403.setVisible(False) 
        self.ui.pushButton_403.setVisible(False)
        self.ui.pushButton_404.setVisible(False)
        for index in range(len(self.timeIndex_finish)):
            waiting_item = self.ui.tableWidget_401.item(index, 6) # 修改等待状态
            waiting_item.setText("等待测试")
            waiting_item.setForeground(QColor(0,0,0)) # 黑色字体

            item = self.ui.tableWidget_401.item(index, 7) # 时间表格清零
            item.setText('')
            item = self.ui.tableWidget_401.item(index, 5) # 数据表格清零
            item.setText('')



    def Test_start(self): # 运行按钮
        self.test_flag_ing_1 = True
        self.test_message = [] # 数据清零
        self.time_record = []
        self.test_result = []

        if self.stateTest == 2:
            if self.ui.lineEdit_101.text().strip() == "":
                QMessageBox.warning(self, '警告', '请输入SN') 
                return
        self.ui.pushButton_101.setEnabled(False)
        self.ui.lineEdit_101.setEnabled(False)
        # 获取当前本地时间
        current_time = time.localtime()
        self.time_start_1 = time.strftime('%Y-%m-%d %H:%M:%S', current_time)
        print(f'开始时间：{self.time_start_1}')
        self.test_reset()
        self.pushButton_Send()
    
    def Test_start_2(self): # 运行按钮
        self.test_flag_ing_2 = True
        self.test_message_2 = [] # 数据清零
        self.time_record_2 = []
        self.test_result_2 = []
        
        if self.stateTest == 2:
            if self.ui.lineEdit_201.text().strip() == "":
                QMessageBox.warning(self, '警告', '请输入SN') 
                return
        self.ui.pushButton_201.setEnabled(False)
        self.ui.lineEdit_201.setEnabled(False)
        # 获取当前本地时间
        current_time = time.localtime()
        self.time_start_2 = time.strftime('%Y-%m-%d %H:%M:%S', current_time)
        print(f'开始时间：{self.time_start_2}')
        self.test_reset_2()
        self.pushButton_Send_2()

    def Test_start_3(self): # 运行按钮
        self.test_flag_ing_3 = True
        self.test_message_3 = [] # 数据清零
        self.time_record_3 = []
        self.test_result_3 = []

        if self.stateTest == 2:
            if self.ui.lineEdit_301.text().strip() == "":
                QMessageBox.warning(self, '警告', '请输入SN') 
                return
        self.ui.pushButton_301.setEnabled(False)
        self.ui.lineEdit_301.setEnabled(False)
        # 获取当前本地时间
        current_time = time.localtime()
        self.time_start_3 = time.strftime('%Y-%m-%d %H:%M:%S', current_time)
        print(f'开始时间：{self.time_start_3}')
        self.test_reset_3()
        self.pushButton_Send_3()

    def Test_start_4(self): # 运行按钮
        self.test_flag_ing_4 = True
        self.test_message_4 = [] # 数据清零
        self.time_record_4 = []
        self.test_result_4 = []

        if self.stateTest == 2:
            if self.ui.lineEdit_401.text().strip() == "":
                QMessageBox.warning(self, '警告', '请输入SN') 
                return
        self.ui.pushButton_401.setEnabled(False)
        self.ui.lineEdit_401.setEnabled(False)
        # 获取当前本地时间
        current_time = time.localtime()
        self.time_start_4 = time.strftime('%Y-%m-%d %H:%M:%S', current_time)
        print(f'开始时间：{self.time_start_4}')
        self.test_reset_4()
        self.pushButton_Send_4()

    
    def test_ing(self): # 开始测试
        self.time_send = int(time.time()*1000)
        index = self.timeIndex_start.index(self.current_command_index)
        print(index)
        waiting_item = self.ui.tableWidget_101.item(index, 6) # 修改等待状态
        waiting_item.setText("正在测试")
        waiting_item.setForeground(QColor(255, 165, 0)) # 橙色字体
        # 修改主label
        self.text_show(self.items_text[index],"正在测试","1")
    
    def test_ing_2(self): # 开始测试
        self.time_send_2 = int(time.time()*1000)
        index = self.timeIndex_start.index(self.current_command_index_2)
        print(index)
        waiting_item = self.ui.tableWidget_201.item(index, 6) # 修改等待状态
        waiting_item.setText("正在测试")
        waiting_item.setForeground(QColor(255, 165, 0)) # 橙色字体
        # 修改主label
        self.text_show(self.items_text[index],"正在测试","2")

    def test_ing_3(self): # 开始测试
        self.time_send_3 = int(time.time()*1000)
        index = self.timeIndex_start.index(self.current_command_index_3)
        print(index)
        waiting_item = self.ui.tableWidget_301.item(index, 6) # 修改等待状态
        waiting_item.setText("正在测试")
        waiting_item.setForeground(QColor(255, 165, 0)) # 橙色字体
        # 修改主label
        self.text_show(self.items_text[index],"正在测试","3")

    def test_ing_4(self): # 开始测试
        self.time_send_4 = int(time.time()*1000)
        index = self.timeIndex_start.index(self.current_command_index_4)
        print(index)
        waiting_item = self.ui.tableWidget_401.item(index, 6) # 修改等待状态
        waiting_item.setText("正在测试")
        waiting_item.setForeground(QColor(255, 165, 0)) # 橙色字体
        # 修改主label
        self.text_show(self.items_text[index],"正在测试","4")
    
    def test_end_pass(self): # 测试通过
        receive_time = int(time.time() * 1000)  # 记录接收时间，单位是毫秒
        timedelta = receive_time - self.time_send  # 发送和接收的时间差
        print(f"时间：{timedelta}ms")
        waiting_item = self.ui.tableWidget_101.item(self.test_item_id, 6) # 修改等待状态
        waiting_item.setText("测试完成")
        waiting_item.setForeground(QColor(0,128,0)) # 绿色字体
        # 修改主label
        self.text_show(self.items_text[self.test_item_id],"测试完成","1")

        item = self.ui.tableWidget_101.item(self.test_item_id, 7) # 添加时间到表格
        item.setText(f"{timedelta}ms")
        self.time_record.append(timedelta) # 记录测试时间
        self.test_result.append('pass')

        print('产测消息：')
        print(self.commands_rec)

        b = {}
        for dictionary in self.commands_rec:
            for key in self.test_params[self.test_item_id]:
                if key in dictionary:
                    b[key] = dictionary[key]
        self.test_message.append(b)

        self.commands_rec = []
        self.test_item_id += 1 # 下一个测试项
        if self.test_item_id >= len(self.timeIndex_start):
            self.current_command_index = self.timeIndex_finish[-1]+1
        else: 
            self.current_command_index = self.timeIndex_start[self.test_item_id]
    
    def test_end_pass_2(self): # 测试通过
        receive_time = int(time.time() * 1000)  # 记录接收时间，单位是毫秒
        timedelta = receive_time - self.time_send_2  # 发送和接收的时间差
        print(f"时间：{timedelta}ms")
        waiting_item = self.ui.tableWidget_201.item(self.test_item_id_2, 6) # 修改等待状态
        waiting_item.setText("测试完成")
        waiting_item.setForeground(QColor(0,128,0)) # 绿色字体
        # 修改主label
        self.text_show(self.items_text[self.test_item_id_2],"测试完成","2")

        item = self.ui.tableWidget_201.item(self.test_item_id_2, 7) # 添加时间到表格
        item.setText(f"{timedelta}ms")
        self.time_record_2.append(timedelta) # 记录测试时间
        self.test_result_2.append('pass')

        print('产测消息：')
        print(self.commands_rec_2)

        b = {}
        for dictionary in self.commands_rec_2:
            for key in self.test_params[self.test_item_id_2]:
                if key in dictionary:
                    b[key] = dictionary[key]
        self.test_message_2.append(b)

        self.commands_rec_2 = []
        self.test_item_id_2 += 1 # 下一个测试项
        if self.test_item_id_2 >= len(self.timeIndex_start):
            self.current_command_index_2 = self.timeIndex_finish[-1]+1
        else: 
            self.current_command_index_2 = self.timeIndex_start[self.test_item_id_2]
    
    def test_end_pass_3(self): # 测试通过
        receive_time = int(time.time() * 1000)  # 记录接收时间，单位是毫秒
        timedelta = receive_time - self.time_send_3  # 发送和接收的时间差
        print(f"时间：{timedelta}ms")
        waiting_item = self.ui.tableWidget_301.item(self.test_item_id_3, 6) # 修改等待状态
        waiting_item.setText("测试完成")
        waiting_item.setForeground(QColor(0,128,0)) # 绿色字体
        # 修改主label
        self.text_show(self.items_text[self.test_item_id_3],"测试完成","3")

        item = self.ui.tableWidget_301.item(self.test_item_id_3, 7) # 添加时间到表格
        item.setText(f"{timedelta}ms")
        self.time_record_3.append(timedelta) # 记录测试时间
        self.test_result_3.append('pass')

        print('产测消息：')
        print(self.commands_rec_3)

        b = {}
        for dictionary in self.commands_rec_3:
            for key in self.test_params[self.test_item_id_3]:
                if key in dictionary:
                    b[key] = dictionary[key]
        self.test_message_3.append(b)

        self.commands_rec_3 = []
        self.test_item_id_3 += 1 # 下一个测试项
        if self.test_item_id_3 >= len(self.timeIndex_start):
            self.current_command_index_3 = self.timeIndex_finish[-1]+1
        else: 
            self.current_command_index_3 = self.timeIndex_start[self.test_item_id_3]
    
    def test_end_pass_4(self): # 测试通过
        receive_time = int(time.time() * 1000)  # 记录接收时间，单位是毫秒
        timedelta = receive_time - self.time_send_4  # 发送和接收的时间差
        print(f"时间：{timedelta}ms")
        waiting_item = self.ui.tableWidget_401.item(self.test_item_id_4, 6) # 修改等待状态
        waiting_item.setText("测试完成")
        waiting_item.setForeground(QColor(0,128,0)) # 绿色字体
        # 修改主label
        self.text_show(self.items_text[self.test_item_id_4],"测试完成","4")

        item = self.ui.tableWidget_401.item(self.test_item_id_4, 7) # 添加时间到表格
        item.setText(f"{timedelta}ms")
        self.time_record_4.append(timedelta) # 记录测试时间
        self.test_result_4.append('pass')

        print('产测消息：')
        print(self.commands_rec_4)

        b = {}
        for dictionary in self.commands_rec_4:
            for key in self.test_params[self.test_item_id_4]:
                if key in dictionary:
                    b[key] = dictionary[key]
        self.test_message_4.append(b)

        self.commands_rec_4 = []
        self.test_item_id_4 += 1 # 下一个测试项
        if self.test_item_id_4 >= len(self.timeIndex_start):
            self.current_command_index_4 = self.timeIndex_finish[-1]+1
        else: 
            self.current_command_index_4 = self.timeIndex_start[self.test_item_id_4]
    
    def test_end_ng(self): # 测试失败
        self.test_flag_ing_1 = False
        receive_time = int(time.time() * 1000)  # 记录接收时间，单位是毫秒
        timedelta = receive_time - self.time_send  # 发送和接收的时间差
        print(f"时间：{timedelta}ms")
        waiting_item = self.ui.tableWidget_101.item(self.test_item_id, 6) # 修改等待状态
        waiting_item.setText("测试失败")
        waiting_item.setForeground(QColor(200,0,0)) # 红色字体
        # 修改主label
        self.text_show(self.items_text[self.test_item_id],"测试失败","1")

        item = self.ui.tableWidget_101.item(self.test_item_id, 7) # 添加时间到表格
        item.setText(f"{timedelta}ms")
        self.time_record.append(timedelta) # 记录测试时间
        self.test_result.append('ng')

        print('产测消息：')
        print(self.commands_rec)

        b = {}
        for dictionary in self.commands_rec:
            for key in self.test_params[self.test_item_id]:
                if key in dictionary:
                    b[key] = dictionary[key]
        self.test_message.append(b)

        self.commands_rec = []
        self.test_item_id += 1 # 下一个测试项
        if self.test_item_id >= len(self.timeIndex_start):
            self.current_command_index = self.timeIndex_finish[-1]+1
        else: 
            self.current_command_index = self.timeIndex_start[self.test_item_id]
        self.ui.pushButton_101.setEnabled(True)
        self.ui.lineEdit_101.setEnabled(True)
        self.current_command_index = 0
        self.test_item_id = 0
    
    def test_end_ng_2(self): # 测试失败
        self.test_flag_ing_2 = False
        receive_time = int(time.time() * 1000)  # 记录接收时间，单位是毫秒
        timedelta = receive_time - self.time_send_2  # 发送和接收的时间差
        print(f"时间：{timedelta}ms")
        waiting_item = self.ui.tableWidget_201.item(self.test_item_id_2, 6) # 修改等待状态
        waiting_item.setText("测试失败")
        waiting_item.setForeground(QColor(200,0,0)) # 红色字体
        # 修改主label
        self.text_show(self.items_text[self.test_item_id_2],"测试失败","2")

        item = self.ui.tableWidget_201.item(self.test_item_id_2, 7) # 添加时间到表格
        item.setText(f"{timedelta}ms")
        self.time_record_2.append(timedelta) # 记录测试时间
        self.test_result_2.append('ng')

        print('产测消息：')
        print(self.commands_rec_2)

        b = {}
        for dictionary in self.commands_rec_2:
            for key in self.test_params[self.test_item_id_2]:
                if key in dictionary:
                    b[key] = dictionary[key]
        self.test_message_2.append(b)

        self.commands_rec_2 = []
        self.test_item_id_2 += 1 # 下一个测试项
        if self.test_item_id_2 >= len(self.timeIndex_start):
            self.current_command_index_2 = self.timeIndex_finish[-1]+1
        else: 
            self.current_command_index_2 = self.timeIndex_start[self.test_item_id_2]
        self.ui.pushButton_201.setEnabled(True)
        self.ui.lineEdit_201.setEnabled(True)
        self.current_command_index_2 = 0
        self.test_item_id_2 = 0
    
    def test_end_ng_3(self): # 测试失败
        self.test_flag_ing_3 = False
        receive_time = int(time.time() * 1000)  # 记录接收时间，单位是毫秒
        timedelta = receive_time - self.time_send_3  # 发送和接收的时间差
        print(f"时间：{timedelta}ms")
        waiting_item = self.ui.tableWidget_301.item(self.test_item_id_3, 6) # 修改等待状态
        waiting_item.setText("测试失败")
        waiting_item.setForeground(QColor(200,0,0)) # 红色字体
        # 修改主label
        self.text_show(self.items_text[self.test_item_id_3],"测试失败","3")

        item = self.ui.tableWidget_301.item(self.test_item_id_3, 7) # 添加时间到表格
        item.setText(f"{timedelta}ms")
        self.time_record_3.append(timedelta) # 记录测试时间
        self.test_result_3.append('ng')

        print('产测消息：')
        print(self.commands_rec_3)

        b = {}
        for dictionary in self.commands_rec_3:
            for key in self.test_params[self.test_item_id_3]:
                if key in dictionary:
                    b[key] = dictionary[key]
        self.test_message_3.append(b)

        self.commands_rec_3 = []
        self.test_item_id_3 += 1 # 下一个测试项
        if self.test_item_id_3 >= len(self.timeIndex_start):
            self.current_command_index_3 = self.timeIndex_finish[-1]+1
        else: 
            self.current_command_index_3 = self.timeIndex_start[self.test_item_id_3]
        self.ui.pushButton_301.setEnabled(True)
        self.ui.lineEdit_301.setEnabled(True)
        self.current_command_index_3 = 0
        self.test_item_id_3 = 0
    
    def test_end_ng_4(self): # 测试失败
        self.test_flag_ing_4 = False
        receive_time = int(time.time() * 1000)  # 记录接收时间，单位是毫秒
        timedelta = receive_time - self.time_send_4  # 发送和接收的时间差
        print(f"时间：{timedelta}ms")
        waiting_item = self.ui.tableWidget_401.item(self.test_item_id_4, 6) # 修改等待状态
        waiting_item.setText("测试失败")
        waiting_item.setForeground(QColor(200,0,0)) # 红色字体
        # 修改主label
        self.text_show(self.items_text[self.test_item_id_4],"测试失败","4")

        item = self.ui.tableWidget_401.item(self.test_item_id_4, 7) # 添加时间到表格
        item.setText(f"{timedelta}ms")
        self.time_record_4.append(timedelta) # 记录测试时间
        self.test_result_4.append('ng')

        print('产测消息：')
        print(self.commands_rec_4)

        b = {}
        for dictionary in self.commands_rec_4:
            for key in self.test_params[self.test_item_id_4]:
                if key in dictionary:
                    b[key] = dictionary[key]
        self.test_message_4.append(b)

        self.commands_rec_4 = []
        self.test_item_id_4 += 1 # 下一个测试项
        if self.test_item_id_4 >= len(self.timeIndex_start):
            self.current_command_index_4 = self.timeIndex_finish[-1]+1
        else: 
            self.current_command_index_4 = self.timeIndex_start[self.test_item_id_4]
        self.ui.pushButton_401.setEnabled(True)
        self.ui.lineEdit_401.setEnabled(True)
        self.current_command_index_4 = 0
        self.test_item_id_4 = 0
    
    def channel_control_fun_1(self):
        if self.slave_control == False:
            self.slave_control = True
            self.channel_control_1.stop()
            if self.slave_control_chan_1 == 1: # 接收测试
                self.infrared_ng_1.start(2000)
                self.Infrared_receiving_function(self.Serial_Qthread_function_1,self.infrared)
            elif self.slave_control_chan_1 == 2: # 发射测试
                self.infrared_ng_1.start(2000)
                self.Infrared_emission_function(1, self.pushButton_Send_slave, self.infrared_emit)
        elif self.slave_control == True:
            print("1无权限")

    def channel_control_fun_2(self):
        if self.slave_control == False:
            self.slave_control = True
            self.channel_control_2.stop()
            if self.slave_control_chan_2 == 1: # 接收测试
                self.infrared_ng_2.start(2000)
                self.Infrared_receiving_function(self.Serial_Qthread_function_2,self.infrared_2)
            elif self.slave_control_chan_2 == 2: # 发射测试
                self.infrared_ng_2.start(2000)
                self.Infrared_emission_function(2, self.pushButton_Send_slave, self.infrared_emit_2)
        elif self.slave_control == True:
            print("2无权限")

    def channel_control_fun_3(self):
        if self.slave_control == False:
            self.slave_control = True
            self.channel_control_3.stop()
            if self.slave_control_chan_3 == 1: # 接收测试
                self.infrared_ng_3.start(2000)
                self.Infrared_receiving_function(self.Serial_Qthread_function_3,self.infrared_3)
            elif self.slave_control_chan_3 == 2: # 发射测试
                self.infrared_ng_3.start(2000)
                self.Infrared_emission_function(3, self.pushButton_Send_slave, self.infrared_emit_3)
        elif self.slave_control == True:
            print("3无权限")

    def channel_control_fun_4(self):
        if self.slave_control == False:
            self.slave_control = True
            self.channel_control_4.stop()
            if self.slave_control_chan_4 == 1: # 接收测试
                self.infrared_ng_4.start(2000)
                self.Infrared_receiving_function(self.Serial_Qthread_function_4,self.infrared_4)
            elif self.slave_control_chan_4 == 2: # 发射测试
                self.infrared_ng_4.start(2000)
                self.Infrared_emission_function(4, self.pushButton_Send_slave, self.infrared_emit_4)
        elif self.slave_control == True:
            print("4无权限")

    def Infrared_receiving_function(self, Serial_Qthread_chan, infrared_chan): # 红外接收任务
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        send_list = []
        send_text = settings.value(f'{self.test_types}_command/conmmand_5','') # 红外接收命令
        while send_text != '':
            try:
                num = int(send_text[0:2],16)
            except:
                return
            send_text = send_text[2:].strip()
            send_list.append(num)
        Byte_data = bytes(send_list)
        parameter = {}
        parameter['data'] = Byte_data
        Serial_Qthread_chan.signal_SendData.emit(parameter)
        infrared_chan.start(500)
    
    def Infrared_emission_function(self, serial_chan, pushButton_slave_chan,infrared_emit_chan): # 红外发射任务
        self.serial_slave_channel = serial_chan # 控制串口设置
        # settings = QSettings("config_Security.ini", QSettings.IniFormat)
        # command = settings.value(f'{self.test_types}_command/conmmand_9','') # 红外复位命令
        # pushButton_slave_chan(command) 
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        command = settings.value(f'{self.test_types}_command/conmmand_5','') # 红外接收命令
        pushButton_slave_chan(command) 
        infrared_emit_chan.start(500)
    
    def pushButton_Send(self):
        if self.current_command_index < len(self.commands):
            if self.commands[self.current_command_index] == 'CHECK_SN': # 输入SN检查
                self.test_ing()

                if self.stateTest != 2:
                    self.test_end_ng()
                    return
                
                # 读取输入SN
                self.SN_1 = self.ui.lineEdit_101.text()

                for key in self.protectid:
                    if key['GROUP_NAME'] == self.ui.comboBox_5_4.currentText():
                        ProcessID = key['CRC_GROUP_CODE']
                        break
                data = {"INTERFACENO":"007", "INTERFACEDATA":""}
                data["INTERFACEDATA"] = self.processid[:-3]+",SN,"+self.SN_1+','+ProcessID
                response_data = Check_SN_fun(data)
                try:
                    if response_data.get('Data')[0]['RESULT'] == 1:
                        self.test_end_pass()
                        b = {}
                        b['SN'] = self.SN_1
                        self.test_message[-1] = b
                    else:
                        self.test_end_ng()
                        return
                except:
                    self.test_end_ng()
                    return
            
            elif self.commands[self.current_command_index] == 'CHECK_STATION': # 过站信息检查
                self.test_ing()

                ########
                self.test_flag = False
                settings = QSettings("../config_update.ini", QSettings.IniFormat)
                usr_name = settings.value("login info/username",'None')
                data = {"M_EMP_NO":usr_name,"M_GROUP_NAME":self.ui.comboBox_5_4.currentText(),"M_SN":self.SN_1,"M_MO_NUMBER":self.ui.lineEdit_2_3.text()}
                response_data = ProductCheck(data)
                print(response_data)
                if response_data == None:
                    QMessageBox.warning(self, '警告', '网络异常') 
                    return
                if response_data['MSG'] == '验证成功':
                    self.test_flag = True
                elif response_data['MSG'][:8] == 'NG:该产品SN' and response_data['MSG'][-19:] == '不属于工单SN号段中的SN，请及时维护' or response_data['MSG'][:17] == "NG:当前工序已过站，请勿重复过站":
                    self.PassStationWin = Pass_station_setting()
                    self.PassStationWin.pass_station_signal.connect(self.PassStation)
                    self.setEnabled(False)
                    self.PassStationWin.exec_()
                    self.setEnabled(True)
                ########

                if self.test_flag:
                    self.test_end_pass()

                else:
                    self.test_end_ng()
                    return
            
            elif self.commands[self.current_command_index] == 'SerialPort':
                self.test_ing()
                self.current_command_index += 1
                self.testMode_flage_time_1.start(1000)
                return

            elif self.commands[self.current_command_index] == 'ENTER_TESTMODE':
                self.test_ing()
                self.test_end_pass()

            elif self.commands[self.current_command_index] == 'CHECK_INFO_FIRMWARE': # 固件版本检测
                firmwork = []
                firmwork_test = ['None','None']
                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                firmwork.append(settings.value("Security_firmware/firmName"))
                firmwork.append(settings.value("Security_firmware/firmVer"))
                del settings
                for message in self.commands_rec:
                    if 'firmName' in message:
                        firmwork_test[0] = message['firmName']
                    if 'firmVer' in message:
                        firmwork_test[1] = message['firmVer']
                item = self.ui.tableWidget_101.item(self.test_item_id, 5) # 添加测试值到表格
                item.setText(firmwork_test[0]+' '+firmwork_test[1])
                if firmwork[0] == firmwork_test[0] and firmwork[1] == firmwork_test[1]:
                    self.test_end_pass()
                else:
                    self.test_end_ng()
                    return
            
            elif self.commands[self.current_command_index] == 'EnterReceive': # 红外接收测试
                self.slave_control_chan_1 = 1
                self.channel_control_1.start(200)
                # self.Infrared_receiving_function(self.Serial_Qthread_function_1,self.infrared)

                return
            
            elif self.commands[self.current_command_index] == 'EnterReceive_New': # 红外接收测试
                self.slave_control = False # 取消占用
                
                print("红外接收取消占用")
                self.test_end_pass()

            elif self.commands[self.current_command_index] == 'EnterReceive_check':
                self.slave_control = False # 取消占用
                self.infrared_ng_1.stop()
                # self.infrared.stop()
                signal = None
                for message in self.commands_rec:
                    if 'rec' in message:
                        signal = message['rec']
                if signal == "000000313233":
                    self.test_end_pass() 
                else:
                    self.test_end_ng()
                    return

             
            
            elif self.commands[self.current_command_index] == 'Emission_check':
                self.slave_control = False # 取消占用
                self.infrared_ng_1.stop()
                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                command = settings.value(f'{self.test_types}_command/conmmand_9','')
                self.pushButton_Send_slave(command) # 红外接收复位
                signal = None
                for message in self.commands_rec:
                    if 'rec' in message:
                        signal = message['rec']
                if signal == "000000313233":
                    self.test_end_pass()
                else:
                    self.test_end_ng()
                    return
            
            elif self.commands[self.current_command_index] == 'Emission_check_New':
                print("红外发射取消占用")
                self.slave_control = False # 取消占用
                self.test_end_pass()
            
            elif self.commands[self.current_command_index] == 'LampTest': # 红外灯检测直接跳过
                self.test_ing()
                self.test_end_pass()    

            
            elif self.commands[self.current_command_index] == 'TEST_LED_Normal': # 指示灯测试
                self.test_ing()
                # 打开通过和失败的按钮
                self.ui.label_103.setText('指示灯是否正常')
                self.ui.label_103.setVisible(True) 
                self.ui.pushButton_103.setVisible(True)
                self.ui.pushButton_104.setVisible(True)
                self.test_button = 'TEST_LED_Normal'
                return
            
            elif self.commands[self.current_command_index] == 'TEST_BOOL_IRLamp': # 红外灯测试
                # 打开通过和失败的按钮
                self.ui.label_103.setText('红外灯是否正常')
                self.ui.label_103.setVisible(True) 
                self.ui.pushButton_103.setVisible(True)
                self.ui.pushButton_104.setVisible(True)
                self.test_button = 'TEST_BOOL_IRLamp'
                return

            elif self.commands[self.current_command_index] == 'TEST_SIGNALQUALITY': # WIFI检测
                signal = None
                for message in self.commands_rec:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_101.item(self.test_item_id, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal}')
                try:
                    if self.params_standard['TEST_SIGNAL_WIFI'][0] <= signal <= self.params_standard['TEST_SIGNAL_WIFI'][1]:
                        self.test_end_pass()
                    else:
                        self.test_end_ng()
                        return
                except: 
                    self.test_end_ng()
                    return
            
            elif self.commands[self.current_command_index] == 'TEST_SIGNAL_Subg': # WIFI检测
                signal = 0
                for message in self.commands_rec:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_101.item(self.test_item_id, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal*10/3}%')
                try:
                    if self.params_standard['TEST_SIGNAL_Subg'][0] <= signal/30 <= self.params_standard['TEST_SIGNAL_Subg'][1]:
                        self.test_end_pass()
                    else:
                        self.test_end_ng()
                        return
                except: 
                    self.test_end_ng()
                    return

            elif self.commands[self.current_command_index] == 'TEST_QUALITY_RSSI': # WIFI检测
                signal = 0
                for message in self.commands_rec:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_101.item(self.test_item_id, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal}')
                try:
                    if self.params_standard['TEST_QUALITY_RSSI'][0] <= signal <= self.params_standard['TEST_QUALITY_RSSI'][1]:
                        self.test_end_pass()
                    else:
                        self.test_end_ng()
                        return
                except: 
                    self.test_end_ng()
                    return
        
        if self.current_command_index >= len(self.commands): # 产测结束
            self.current_command_index = 0
            self.test_item_id = 0
            # 获取当前本地时间
            current_time = time.localtime()
            self.time_end_1 = time.strftime('%Y-%m-%d %H:%M:%S', current_time)
            print(f'结束时间：{self.time_end_1}')

            if self.stateTest == 2: # 工单测试
                self.SN_1 = self.ui.lineEdit_101.text()
                self.MES_http_upload("1",self.SN_1,self.time_start_1,self.time_end_1,self.test_message,self.time_record,self.test_result)
            
            self.ui.pushButton_101.setEnabled(True)
            self.ui.lineEdit_101.setEnabled(True)
            self.ui.lineEdit_101.clear() 
            self.ui.lineEdit_101.setFocus()
            return

        if self.commands[self.current_command_index][:4] == '57AA' or self.commands[self.current_command_index][:4] == '55AA':
            Byte_data = bytes()
            send_list = []
            send_text = self.commands[self.current_command_index]  # 发送当前需要发送的命令
            while send_text != '':
                try:
                    num = int(send_text[0:2],16)
                except:
                    return
                send_text = send_text[2:].strip()
                send_list.append(num)
            Byte_data = bytes(send_list)
            parameter = {}
            parameter['data'] = Byte_data
            self.Serial_Qthread_function_1.signal_SendData.emit(parameter)

            if self.current_command_index in self.timeIndex_start:
                self.test_ing()
        else: self.pushButton_Send()
    
    def pushButton_Send_2(self):
        if self.current_command_index_2 < len(self.commands):
            if self.commands[self.current_command_index_2] == 'CHECK_SN': # 输入SN检查
                self.test_ing_2()

                if self.stateTest != 2:
                    self.test_end_ng_2()
                    return

                # 读取输入SN
                self.SN_2 = self.ui.lineEdit_201.text()

                for key in self.protectid:
                    if key['GROUP_NAME'] == self.ui.comboBox_5_4.currentText():
                        ProcessID = key['CRC_GROUP_CODE']
                        break
                data = {"INTERFACENO":"007", "INTERFACEDATA":""}
                data["INTERFACEDATA"] = self.processid[:-3]+",SN,"+self.SN_2+','+ProcessID
                response_data = Check_SN_fun(data)
                try:
                    if response_data.get('Data')[0]['RESULT'] == 1:
                        self.test_end_pass_2()
                        b = {}
                        b['SN'] = self.SN_2
                        self.test_message_2[-1] = b
                    else:
                        self.test_end_ng_2()
                        return
                except:
                    self.test_end_ng_2()
                    return
            
            elif self.commands[self.current_command_index_2] == 'CHECK_STATION': # 过站信息检查
                self.test_ing_2()

                ########
                self.test_flag_2 = False
                settings = QSettings("../config_update.ini", QSettings.IniFormat)
                usr_name = settings.value("login info/username",'None')
                data = {"M_EMP_NO":usr_name,"M_GROUP_NAME":self.ui.comboBox_5_4.currentText(),"M_SN":self.SN_2,"M_MO_NUMBER":self.ui.lineEdit_2_3.text()}
                response_data = ProductCheck(data)
                print(response_data)
                if response_data == None:
                    QMessageBox.warning(self, '警告', '网络异常') 
                    return
                if response_data['MSG'] == '验证成功':
                    self.test_flag_2 = True
                elif response_data['MSG'][:8] == 'NG:该产品SN' and response_data['MSG'][-19:] == '不属于工单SN号段中的SN，请及时维护' or response_data['MSG'][:17] == "NG:当前工序已过站，请勿重复过站":
                    self.PassStationWin_2 = Pass_station_setting()
                    self.PassStationWin_2.pass_station_signal.connect(self.PassStation_2)
                    self.setEnabled(False)
                    self.PassStationWin_2.exec_()
                    self.setEnabled(True)
                ########

                if self.test_flag_2:
                    self.test_end_pass_2()
                else:
                    self.test_end_ng_2()
                    return
            
            elif self.commands[self.current_command_index_2] == 'SerialPort':
                self.test_ing_2()
                self.current_command_index_2 += 1

                self.testMode_flage_time_2.start(1000)
                return
            
            elif self.commands[self.current_command_index_2] == 'ENTER_TESTMODE':
                self.test_ing_2()
                self.test_end_pass_2()

            elif self.commands[self.current_command_index_2] == 'CHECK_INFO_FIRMWARE': # 固件版本检测
                firmwork = []
                firmwork_test = ['None','None']
                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                firmwork.append(settings.value("Security_firmware/firmName"))
                firmwork.append(settings.value("Security_firmware/firmVer"))
                del settings
                for message in self.commands_rec_2:
                    if 'firmName' in message:
                        firmwork_test[0] = message['firmName']
                    if 'firmVer' in message:
                        firmwork_test[1] = message['firmVer']
                item = self.ui.tableWidget_201.item(self.test_item_id_2, 5) # 添加测试值到表格
                item.setText(firmwork_test[0]+' '+firmwork_test[1])
                if firmwork[0] == firmwork_test[0] and firmwork[1] == firmwork_test[1]:
                    self.test_end_pass_2()
                else:
                    self.test_end_ng_2()
                    return
            
            elif self.commands[self.current_command_index_2] == 'EnterReceive': # 红外接收测试
                self.slave_control_chan_2 = 1
                self.channel_control_2.start(200)
                # self.Infrared_receiving_function(self.Serial_Qthread_function_2,self.infrared_2)
                return
            
            elif self.commands[self.current_command_index_2] == 'EnterReceive_New': # 红外接收测试
                self.slave_control = False # 取消占用
                
                print("红外接收取消占用")
                self.test_end_pass_2()

            elif self.commands[self.current_command_index_2] == 'EnterReceive_check':
                self.slave_control = False # 取消占用
                self.infrared_ng_2.stop()
                # self.infrared_2.stop()
                signal = None
                for message in self.commands_rec_2:
                    if 'rec' in message:
                        signal = message['rec']
                if signal == "000000313233":
                    self.test_end_pass_2() 
                else:
                    self.test_end_ng_2()
                    return

            elif self.commands[self.current_command_index_2] == 'Emission': # 红外发射测试
                self.test_ing_2()
                self.current_command_index_2 += 1
                
                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                command = settings.value(f'{self.test_types}_command/conmmand_9','') # 红外复位命令
                self.pushButton_Send_slave(command)

                self.slave_control_chan_2 = 2
                self.channel_control_2.start(200)
                # self.Infrared_emission_function(2, self.pushButton_Send_slave, self.infrared_emit_2)

                return
            
            elif self.commands[self.current_command_index_2] == 'Emission_check':
                self.slave_control = False # 取消占用
                self.infrared_ng_2.stop()
                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                command = settings.value(f'{self.test_types}_command/conmmand_9','')
                self.pushButton_Send_slave(command) # 红外接收复位
                signal = None
                for message in self.commands_rec_2:
                    if 'rec' in message:
                        signal = message['rec']
                if signal == "000000313233":
                    self.test_end_pass_2() 
                else:
                    self.test_end_ng_2()
                    return
            
            elif self.commands[self.current_command_index_2] == 'Emission_check_New':
                print("红外发射取消占用")
                self.slave_control = False # 取消占用
                self.test_end_pass_2()
            
            elif self.commands[self.current_command_index_2] == 'LampTest': # 红外灯检测直接跳过
                self.test_ing_2()
                self.test_end_pass_2()    

            
            elif self.commands[self.current_command_index_2] == 'TEST_LED_Normal': # 指示灯测试
                self.test_ing_2()
                # 打开通过和失败的按钮
                self.ui.label_203.setText('指示灯是否正常')
                self.ui.label_203.setVisible(True) 
                self.ui.pushButton_203.setVisible(True)
                self.ui.pushButton_204.setVisible(True)
                self.test_button_2 = 'TEST_LED_Normal'
                return
            
            elif self.commands[self.current_command_index_2] == 'TEST_BOOL_IRLamp': # 红外灯测试
                # 打开通过和失败的按钮
                self.ui.label_203.setText('红外灯是否正常')
                self.ui.label_203.setVisible(True) 
                self.ui.pushButton_203.setVisible(True)
                self.ui.pushButton_204.setVisible(True)
                self.test_button_2 = 'TEST_BOOL_IRLamp'
                return

            elif self.commands[self.current_command_index_2] == 'TEST_SIGNALQUALITY': # WIFI检测
                signal = None
                for message in self.commands_rec_2:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_201.item(self.test_item_id_2, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal}')
                try:
                    if self.params_standard['TEST_SIGNAL_WIFI'][0] <= signal <= self.params_standard['TEST_SIGNAL_WIFI'][1]:
                        self.test_end_pass_2()
                    else:
                        self.test_end_ng_2()
                        return
                except: 
                    self.test_end_ng_2()
                    return
            
            elif self.commands[self.current_command_index_2] == 'TEST_SIGNAL_Subg': # WIFI检测
                signal = 0
                for message in self.commands_rec_2:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_201.item(self.test_item_id_2, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal*10/3}%')
                try:
                    if self.params_standard['TEST_SIGNAL_Subg'][0] <= signal/30 <= self.params_standard['TEST_SIGNAL_Subg'][1]:
                        self.test_end_pass_2()
                    else:
                        self.test_end_ng_2()
                        return
                except: 
                    self.test_end_ng_2()
                    return

            elif self.commands[self.current_command_index_2] == 'TEST_QUALITY_RSSI': # WIFI检测
                signal = 0
                for message in self.commands_rec_2:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_201.item(self.test_item_id_2, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal}')
                try:
                    if self.params_standard['TEST_QUALITY_RSSI'][0] <= signal <= self.params_standard['TEST_QUALITY_RSSI'][1]:
                        self.test_end_pass_2()
                    else:
                        self.test_end_ng_2()
                        return
                except: 
                    self.test_end_ng_2()
                    return
        
        if self.current_command_index_2 >= len(self.commands): # 产测结束
            self.current_command_index_2 = 0
            self.test_item_id_2 = 0

            # 获取当前本地时间
            current_time = time.localtime()
            self.time_end_2 = time.strftime('%Y-%m-%d %H:%M:%S', current_time)
            print(f'结束时间：{self.time_end_2}')

            if self.stateTest == 2: # 工单测试
                self.SN_2 = self.ui.lineEdit_201.text()
                self.MES_http_upload("2", self.SN_2,self.time_start_2,self.time_end_2,self.test_message_2,self.time_record_2,self.test_result_2)
            
            self.ui.pushButton_201.setEnabled(True)
            self.ui.lineEdit_201.setEnabled(True)
            self.ui.lineEdit_201.clear()   
            self.ui.lineEdit_101.setFocus()
            return

        if self.commands[self.current_command_index_2][:4] == '57AA' or self.commands[self.current_command_index_2][:4] == '55AA':
            Byte_data = bytes()
            send_list = []
            send_text = self.commands[self.current_command_index_2]  # 发送当前需要发送的命令
            while send_text != '':
                try:
                    num = int(send_text[0:2],16)
                except:
                    return
                send_text = send_text[2:].strip()
                send_list.append(num)
            Byte_data = bytes(send_list)
            parameter = {}
            parameter['data'] = Byte_data
            self.Serial_Qthread_function_2.signal_SendData.emit(parameter)

            if self.current_command_index_2 in self.timeIndex_start:
                self.test_ing_2()
        else: self.pushButton_Send_2()

    def pushButton_Send_3(self):
        if self.current_command_index_3 < len(self.commands):
            if self.commands[self.current_command_index_3] == 'CHECK_SN': # 输入SN检查
                self.test_ing_3()

                if self.stateTest != 2:
                    self.test_end_ng_3()
                    return

                # 读取输入SN
                self.SN_3 = self.ui.lineEdit_301.text()

                for key in self.protectid:
                    if key['GROUP_NAME'] == self.ui.comboBox_5_4.currentText():
                        ProcessID = key['CRC_GROUP_CODE']
                        break
                data = {"INTERFACENO":"007", "INTERFACEDATA":""}
                data["INTERFACEDATA"] = self.processid[:-3]+",SN,"+self.SN_3+','+ProcessID
                response_data = Check_SN_fun(data)
                try:
                    if response_data.get('Data')[0]['RESULT'] == 1:
                        self.test_end_pass_3()
                        b = {}
                        b['SN'] = self.SN_3
                        self.test_message_3[-1] = b
                    else:
                        self.test_end_ng_3()
                        return
                except:
                    self.test_end_ng_3()
                    return
            
            elif self.commands[self.current_command_index_3] == 'CHECK_STATION': # 过站信息检查
                self.test_ing_3()

                ########
                self.test_flag_3 = False
                settings = QSettings("../config_update.ini", QSettings.IniFormat)
                usr_name = settings.value("login info/username",'None')
                data = {"M_EMP_NO":usr_name,"M_GROUP_NAME":self.ui.comboBox_5_4.currentText(),"M_SN":self.SN_3,"M_MO_NUMBER":self.ui.lineEdit_2_3.text()}
                response_data = ProductCheck(data)
                print(response_data)
                if response_data == None:
                    QMessageBox.warning(self, '警告', '网络异常') 
                    return
                if response_data['MSG'] == '验证成功':
                    self.test_flag_3 = True
                elif response_data['MSG'][:8] == 'NG:该产品SN' and response_data['MSG'][-19:] == '不属于工单SN号段中的SN，请及时维护' or response_data['MSG'][:17] == "NG:当前工序已过站，请勿重复过站":
                    self.PassStationWin_3 = Pass_station_setting()
                    self.PassStationWin_3.pass_station_signal.connect(self.PassStation_3)
                    self.setEnabled(False)
                    self.PassStationWin_3.exec_()
                    self.setEnabled(True)
                ########

                if self.test_flag_3:
                    self.test_end_pass_3()

                else:
                    self.test_end_ng_3()
                    return
            
            elif self.commands[self.current_command_index_3] == 'SerialPort':
                self.test_ing_3()
                self.current_command_index_3 += 1

                self.testMode_flage_time_3.start(1000)
                return
            
            elif self.commands[self.current_command_index_3] == 'ENTER_TESTMODE':
                self.test_ing_3()
                self.test_end_pass_3()

            elif self.commands[self.current_command_index_3] == 'CHECK_INFO_FIRMWARE': # 固件版本检测
                firmwork = []
                firmwork_test = ['None','None']
                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                firmwork.append(settings.value("Security_firmware/firmName"))
                firmwork.append(settings.value("Security_firmware/firmVer"))
                del settings
                for message in self.commands_rec_3:
                    if 'firmName' in message:
                        firmwork_test[0] = message['firmName']
                    if 'firmVer' in message:
                        firmwork_test[1] = message['firmVer']
                item = self.ui.tableWidget_301.item(self.test_item_id_3, 5) # 添加测试值到表格
                item.setText(firmwork_test[0]+' '+firmwork_test[1])
                if firmwork[0] == firmwork_test[0] and firmwork[1] == firmwork_test[1]:
                    self.test_end_pass_3()
                else:
                    self.test_end_ng_3()
                    return
            
            elif self.commands[self.current_command_index_3] == 'EnterReceive': # 红外接收测试
                self.slave_control_chan_3 = 1
                self.channel_control_3.start(200)
                
                # self.Infrared_receiving_function(self.Serial_Qthread_function_3,self.infrared_3)

                return
            
            elif self.commands[self.current_command_index_3] == 'EnterReceive_New': # 红外接收测试
                self.slave_control = False # 取消占用
                
                print("红外接收取消占用")
                self.test_end_pass_3()

            elif self.commands[self.current_command_index_3] == 'EnterReceive_check':
                self.slave_control = False # 取消占用
                self.infrared_ng_3.stop()
                # self.infrared_3.stop()
                signal = None
                for message in self.commands_rec_3:
                    if 'rec' in message:
                        signal = message['rec']
                if signal == "000000313233":
                    self.test_end_pass_3() 
                else:
                    self.test_end_ng_3()
                    return

            elif self.commands[self.current_command_index_3] == 'Emission': # 红外发射测试
                self.test_ing_3()
                self.current_command_index_3 += 1

                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                command = settings.value(f'{self.test_types}_command/conmmand_9','') # 红外复位命令
                self.pushButton_Send_slave(command)

                self.slave_control_chan_3 = 2
                self.channel_control_3.start(200)
                # self.Infrared_emission_function(3, self.pushButton_Send_slave, self.infrared_emit_3)
                return
            
            elif self.commands[self.current_command_index_3] == 'Emission_check':
                self.slave_control = False # 取消占用
                self.infrared_ng_3.stop()
                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                command = settings.value(f'{self.test_types}_command/conmmand_9','')
                self.pushButton_Send_slave(command) # 红外接收复位
                signal = None
                for message in self.commands_rec_3:
                    if 'rec' in message:
                        signal = message['rec']
                if signal == "000000313233":
                    self.test_end_pass_3() 
                else:
                    self.test_end_ng_3()
                    return
            
            elif self.commands[self.current_command_index_3] == 'Emission_check_New':
                print("红外发射取消占用")
                self.slave_control = False # 取消占用
                self.test_end_pass_3()
            
            elif self.commands[self.current_command_index_3] == 'LampTest': # 红外灯检测直接跳过
                self.test_ing_3()
                self.test_end_pass_3()    

            
            elif self.commands[self.current_command_index_3] == 'TEST_LED_Normal': # 指示灯测试
                self.test_ing_3()
                # 打开通过和失败的按钮
                self.ui.label_303.setText('指示灯是否正常')
                self.ui.label_303.setVisible(True) 
                self.ui.pushButton_303.setVisible(True)
                self.ui.pushButton_304.setVisible(True)
                self.test_button_3 = 'TEST_LED_Normal'
                return
            
            elif self.commands[self.current_command_index_3] == 'TEST_BOOL_IRLamp': # 红外灯测试
                # 打开通过和失败的按钮
                self.ui.label_303.setText('红外灯是否正常')
                self.ui.label_303.setVisible(True) 
                self.ui.pushButton_303.setVisible(True)
                self.ui.pushButton_304.setVisible(True)
                self.test_button_3 = 'TEST_BOOL_IRLamp'
                return

            elif self.commands[self.current_command_index_3] == 'TEST_SIGNALQUALITY': # WIFI检测
                signal = None
                for message in self.commands_rec_3:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_301.item(self.test_item_id_3, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal}')
                try:
                    if self.params_standard['TEST_SIGNAL_WIFI'][0] <= signal <= self.params_standard['TEST_SIGNAL_WIFI'][1]:
                        self.test_end_pass_3()
                    else:
                        self.test_end_ng_3()
                        return
                except: 
                    self.test_end_ng_3()
                    return
            
            elif self.commands[self.current_command_index_3] == 'TEST_SIGNAL_Subg': # WIFI检测
                signal = 0
                for message in self.commands_rec_3:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_301.item(self.test_item_id_2, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal*10/3}%')
                try:
                    if self.params_standard['TEST_SIGNAL_Subg'][0] <= signal/30 <= self.params_standard['TEST_SIGNAL_Subg'][1]:
                        self.test_end_pass_3()
                    else:
                        self.test_end_ng_3()
                        return
                except: 
                    self.test_end_ng_3()
                    return

            elif self.commands[self.current_command_index_3] == 'TEST_QUALITY_RSSI': # WIFI检测
                signal = 0
                for message in self.commands_rec_3:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_301.item(self.test_item_id_3, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal}')
                try:
                    if self.params_standard['TEST_QUALITY_RSSI'][0] <= signal <= self.params_standard['TEST_QUALITY_RSSI'][1]:
                        self.test_end_pass_3()
                    else:
                        self.test_end_ng_3()
                        return
                except: 
                    self.test_end_ng_3()
                    return
        
        if self.current_command_index_3 >= len(self.commands): # 产测结束
            self.current_command_index_3 = 0
            self.test_item_id_3 = 0

            # 获取当前本地时间
            current_time = time.localtime()
            self.time_end_3 = time.strftime('%Y-%m-%d %H:%M:%S', current_time)
            print(f'结束时间：{self.time_end_3}')

            if self.stateTest == 2: # 工单测试
                self.SN_3 = self.ui.lineEdit_301.text()
                self.MES_http_upload("3",self.SN_3,self.time_start_3,self.time_end_3,self.test_message_3,self.time_record_3,self.test_result_3)
            
            self.ui.pushButton_301.setEnabled(True)
            self.ui.lineEdit_301.setEnabled(True)
            self.ui.lineEdit_301.clear() 
            self.ui.lineEdit_101.setFocus()
            return

        if self.commands[self.current_command_index_3][:4] == '57AA' or self.commands[self.current_command_index_3][:4] == '55AA':
            Byte_data = bytes()
            send_list = []
            send_text = self.commands[self.current_command_index_3]  # 发送当前需要发送的命令
            while send_text != '':
                try:
                    num = int(send_text[0:2],16)
                except:
                    return
                send_text = send_text[2:].strip()
                send_list.append(num)
            Byte_data = bytes(send_list)
            parameter = {}
            parameter['data'] = Byte_data
            self.Serial_Qthread_function_3.signal_SendData.emit(parameter)

            if self.current_command_index_3 in self.timeIndex_start:
                self.test_ing_3()
        else: self.pushButton_Send_3()

    def pushButton_Send_4(self):
        if self.current_command_index_4 < len(self.commands):
            if self.commands[self.current_command_index_4] == 'CHECK_SN': # 输入SN检查
                self.test_ing_4()

                if self.stateTest != 2:
                    self.test_end_ng_4()
                    return

                # 读取输入SN
                self.SN_4 = self.ui.lineEdit_401.text()

                for key in self.protectid:
                    if key['GROUP_NAME'] == self.ui.comboBox_5_4.currentText():
                        ProcessID = key['CRC_GROUP_CODE']
                        break
                data = {"INTERFACENO":"007", "INTERFACEDATA":""}
                data["INTERFACEDATA"] = self.processid[:-3]+",SN,"+self.SN_4+','+ProcessID
                response_data = Check_SN_fun(data)
                try:
                    if response_data.get('Data')[0]['RESULT'] == 1:
                        self.test_end_pass_4()
                        b = {}
                        b['SN'] = self.SN_4
                        self.test_message_4[-1] = b
                    else:
                        self.test_end_ng_4()
                        return
                except:
                    self.test_end_ng_4()
                    return
            
            elif self.commands[self.current_command_index_4] == 'CHECK_STATION': # 过站信息检查
                self.test_ing_4()

                ########
                self.test_flag_4 = False
                settings = QSettings("../config_update.ini", QSettings.IniFormat)
                usr_name = settings.value("login info/username",'None')
                data = {"M_EMP_NO":usr_name,"M_GROUP_NAME":self.ui.comboBox_5_4.currentText(),"M_SN":self.SN_4,"M_MO_NUMBER":self.ui.lineEdit_2_3.text()}
                response_data = ProductCheck(data)
                print(response_data)
                if response_data == None:
                    QMessageBox.warning(self, '警告', '网络异常') 
                    return
                if response_data['MSG'] == '验证成功':
                    self.test_flag_4 = True
                elif response_data['MSG'][:8] == 'NG:该产品SN' and response_data['MSG'][-19:] == '不属于工单SN号段中的SN，请及时维护' or response_data['MSG'][:17] == "NG:当前工序已过站，请勿重复过站":
                    self.PassStationWin_4 = Pass_station_setting()
                    self.PassStationWin_4.pass_station_signal.connect(self.PassStation_4)
                    self.setEnabled(False)
                    self.PassStationWin_4.exec_()
                    self.setEnabled(True)
                ########

                if self.test_flag_4:
                    self.test_end_pass_4()

                else:
                    self.test_end_ng_4()
                    return
            
            elif self.commands[self.current_command_index_4] == 'SerialPort':
                self.test_ing_4()
                self.current_command_index_4 += 1

                self.testMode_flage_time_4.start(1000)
                return
            
            elif self.commands[self.current_command_index_4] == 'ENTER_TESTMODE':
                self.test_ing_4()
                self.test_end_pass_4()

            elif self.commands[self.current_command_index_4] == 'CHECK_INFO_FIRMWARE': # 固件版本检测
                firmwork = []
                firmwork_test = ['None','None']
                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                firmwork.append(settings.value("Security_firmware/firmName"))
                firmwork.append(settings.value("Security_firmware/firmVer"))
                del settings
                for message in self.commands_rec_4:
                    if 'firmName' in message:
                        firmwork_test[0] = message['firmName']
                    if 'firmVer' in message:
                        firmwork_test[1] = message['firmVer']
                item = self.ui.tableWidget_401.item(self.test_item_id_4, 5) # 添加测试值到表格
                item.setText(firmwork_test[0]+' '+firmwork_test[1])
                if firmwork[0] == firmwork_test[0] and firmwork[1] == firmwork_test[1]:
                    self.test_end_pass_4()
                else:
                    self.test_end_ng_4()
                    return
            
            elif self.commands[self.current_command_index_4] == 'EnterReceive': # 红外接收测试
                self.slave_control_chan_4 = 1
                self.channel_control_4.start(200)
                
                # self.Infrared_receiving_function(self.Serial_Qthread_function_4,self.infrared_4)

                return
            
            elif self.commands[self.current_command_index_4] == 'EnterReceive_New': # 红外接收测试
                self.slave_control = False # 取消占用
                
                print("红外接收取消占用")
                self.test_end_pass_4()

            elif self.commands[self.current_command_index_4] == 'EnterReceive_check':
                self.slave_control = False # 取消占用
                self.infrared_ng_4.stop()
                # self.infrared_4.stop()
                signal = None
                for message in self.commands_rec_4:
                    if 'rec' in message:
                        signal = message['rec']
                if signal == "000000313233":
                    self.test_end_pass_4() 
                else:
                    self.test_end_ng_4()
                    return

            elif self.commands[self.current_command_index_4] == 'Emission': # 红外发射测试
                self.test_ing_4()
                self.current_command_index_4 += 1

                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                command = settings.value(f'{self.test_types}_command/conmmand_9','') # 红外复位命令
                self.pushButton_Send_slave(command)

                self.slave_control_chan_4 = 2
                self.channel_control_4.start(200)
                # self.Infrared_emission_function(4, self.pushButton_Send_slave, self.infrared_emit_4)
                return
            
            elif self.commands[self.current_command_index_4] == 'Emission_check':
                self.slave_control = False # 取消占用
                self.infrared_ng_4.stop()
                settings = QSettings("config_Security.ini", QSettings.IniFormat)
                command = settings.value(f'{self.test_types}_command/conmmand_9','')
                self.pushButton_Send_slave(command) # 红外接收复位
                signal = None
                for message in self.commands_rec_4:
                    if 'rec' in message:
                        signal = message['rec']
                if signal == "000000313233":
                    self.test_end_pass_4() 
                else:
                    self.test_end_ng_4()
                    return
            
            elif self.commands[self.current_command_index_4] == 'Emission_check_New':
                print("红外发射取消占用")
                self.slave_control = False # 取消占用
                self.test_end_pass_4()
            
            elif self.commands[self.current_command_index_4] == 'LampTest': # 红外灯检测直接跳过
                self.test_ing_4()
                self.test_end_pass_4()    

            
            elif self.commands[self.current_command_index_4] == 'TEST_LED_Normal': # 指示灯测试
                self.test_ing_4()
                # 打开通过和失败的按钮
                self.ui.label_403.setText('指示灯是否正常')
                self.ui.label_403.setVisible(True) 
                self.ui.pushButton_403.setVisible(True)
                self.ui.pushButton_404.setVisible(True)
                self.test_button_4 = 'TEST_LED_Normal'
                return
            
            elif self.commands[self.current_command_index_4] == 'TEST_BOOL_IRLamp': # 红外灯测试
                # 打开通过和失败的按钮
                self.ui.label_403.setText('红外灯是否正常')
                self.ui.label_403.setVisible(True) 
                self.ui.pushButton_403.setVisible(True)
                self.ui.pushButton_404.setVisible(True)
                self.test_button_4 = 'TEST_BOOL_IRLamp'
                return

            elif self.commands[self.current_command_index_4] == 'TEST_SIGNALQUALITY': # WIFI检测
                signal = None
                for message in self.commands_rec_4:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_401.item(self.test_item_id_4, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal}')
                try:
                    if self.params_standard['TEST_SIGNAL_WIFI'][0] <= signal <= self.params_standard['TEST_SIGNAL_WIFI'][1]:
                        self.test_end_pass_4()
                    else:
                        self.test_end_ng_4()
                        return
                except: 
                    self.test_end_ng_4()
                    return
            
            elif self.commands[self.current_command_index_4] == 'TEST_SIGNAL_Subg': # WIFI检测
                signal = 0
                for message in self.commands_rec_4:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_401.item(self.test_item_id_4, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal*10/3}%')
                try:
                    if self.params_standard['TEST_SIGNAL_Subg'][0] <= signal/30 <= self.params_standard['TEST_SIGNAL_Subg'][1]:
                        self.test_end_pass_4()
                    else:
                        self.test_end_ng_4()
                        return
                except: 
                    self.test_end_ng_4()
                    return

            elif self.commands[self.current_command_index_4] == 'TEST_QUALITY_RSSI': # WIFI检测
                signal = 0
                for message in self.commands_rec_4:
                    if 'rssi' in message:
                        signal = message['rssi']
                        print(f'信号值：{signal}')
                item = self.ui.tableWidget_401.item(self.test_item_id_4, 5) # 添加测试值到表格
                item.setText(f'RSSI 信号强度:{signal}')
                try:
                    if self.params_standard['TEST_QUALITY_RSSI'][0] <= signal <= self.params_standard['TEST_QUALITY_RSSI'][1]:
                        self.test_end_pass_4()
                    else:
                        self.test_end_ng_4()
                        return
                except: 
                    self.test_end_ng_4()
                    return
        
        if self.current_command_index_4 >= len(self.commands): # 产测结束
            self.current_command_index_4 = 0
            self.test_item_id_4 = 0

            # 获取当前本地时间
            current_time = time.localtime()
            self.time_end_4 = time.strftime('%Y-%m-%d %H:%M:%S', current_time)
            print(f'结束时间：{self.time_end_4}')

            if self.stateTest == 2: # 工单测试
                self.SN_4 = self.ui.lineEdit_401.text()
                self.MES_http_upload("4",self.SN_4,self.time_start_4,self.time_end_4,self.test_message_4,self.time_record_4,self.test_result_4)
            
            self.ui.pushButton_401.setEnabled(True)
            self.ui.lineEdit_401.setEnabled(True)
            self.ui.lineEdit_401.clear() 
            self.ui.lineEdit_101.setFocus()
            return

        if self.commands[self.current_command_index_4][:4] == '57AA' or self.commands[self.current_command_index_4][:4] == '55AA':
            Byte_data = bytes()
            send_list = []
            send_text = self.commands[self.current_command_index_4]  # 发送当前需要发送的命令
            while send_text != '':
                try:
                    num = int(send_text[0:2],16)
                except:
                    return
                send_text = send_text[2:].strip()
                send_list.append(num)
            Byte_data = bytes(send_list)
            parameter = {}
            parameter['data'] = Byte_data
            self.Serial_Qthread_function_4.signal_SendData.emit(parameter)

            if self.current_command_index_4 in self.timeIndex_start:
                self.test_ing_4()
        else: self.pushButton_Send_4()
           
    def pushButton_Send_slave(self, command):
        Byte_data = bytes()
        send_list = []
        send_text = command
        while send_text != '':
            try:
                num = int(send_text[0:2],16)
            except:
                return
            send_text = send_text[2:].strip()
            send_list.append(num)
        Byte_data = bytes(send_list)
        parameter = {}
        parameter['data'] = Byte_data
        self.Serial_Qthread_function_slave.signal_SendData.emit(parameter)


    def receive_time_out_func(self):
        self.receive_time_out.stop()
        
        View_data = ''
        Byte_data = bytes(self.rec_buff)

        self.rec_buff.clear() # 清除缓存

        if self.test_flag_ing_1 == True:  # 正在进行测试

            for i in range(0,len(Byte_data)):
                View_data = View_data + '{:02X}'.format(Byte_data[i]) + ' '
            # 判断回应是否是指定的命令
            response_command = View_data.replace(" ", "").upper()  # 去除空格并大写

            # 去掉多余接收的命令
            first_occurrence = response_command.find("57AA00")  # 找到第一次出现的位置
            second_occurrence = response_command.find("57AA00", first_occurrence + 1)  # 找到第二次出现的位置
            if second_occurrence != -1:  # 如果找到第二次出现的位置
                response_command = response_command[:second_occurrence]  # 截取第二次出现之前的部分
            print(response_command)

            
            if response_command == "57AA000000010406" or response_command == '55AA000000010404': # 开始产测
                self.testMode_flage_time_1.stop()
            elif response_command[:12] == "57AA00210006": # 红外接收
                response_command_trans = {}
                response_command_trans["rec"] = response_command[12:-2]
                self.commands_rec.append(response_command_trans)
                print("红外接收成功")
            elif response_command == "57AA0020000C7B22726574223A747275657DAE": # 红外发射
                return
            elif response_command == '55AA00F0000F01000C7B22726574223A747275657D8C': # 新红外发射 
                return
            elif response_command[:18] == "55AA00F00019010101": # Subg433测试
                try:
                    response_command = self.HEX_to_ASCII(response_command,18) # 转换为字典(** 要判断是否为字典)
                    self.commands_rec.append(response_command)
                except:
                    pass
            elif response_command[:18] == "55AA00F0000F01000D": # 红外接收
                print("红外接收正常")
            elif response_command[:4] == "57AA" or response_command[:4] == "55AA":
                try: 
                    response_command = self.HEX_to_ASCII(response_command) # 转换为字典(** 要判断是否为字典)
                    self.commands_rec.append(response_command)
                except:
                    pass
            else:
                return
    
            if self.current_command_index in self.timeIndex_finish:  # 每个测试项执行完成
                self.test_end_pass()
            else:self.current_command_index += 1
            self.pushButton_Send()

    def slot_readyRead(self,data): # 主串口接收
        self.receive_time_out.start(120)
        self.rec_buff += data["buf"]
    
    def receive_time_out_func_2(self):
        self.receive_time_out_2.stop()
        
        View_data = ''
        Byte_data = bytes(self.rec_buff_2)

        self.rec_buff_2.clear() # 清除缓存

        if self.test_flag_ing_2 == True:

            for i in range(0,len(Byte_data)):
                View_data = View_data + '{:02X}'.format(Byte_data[i]) + ' '
            # 判断回应是否是指定的命令
            response_command = View_data.replace(" ", "").upper()  # 去除空格并大写
            
            # 去掉多余接收的命令
            first_occurrence = response_command.find("57AA00")  # 找到第一次出现的位置
            second_occurrence = response_command.find("57AA00", first_occurrence + 1)  # 找到第二次出现的位置
            if second_occurrence != -1:  # 如果找到第二次出现的位置
                response_command = response_command[:second_occurrence]  # 截取第二次出现之前的部分
            print(response_command)

            if response_command == "57AA000000010406" or response_command == '55AA000000010404': # 开始产测
                self.testMode_flage_time_2.stop()
            elif response_command[:12] == "57AA00210006": # 红外接收
                response_command_trans = {}
                response_command_trans["rec"] = response_command[12:-2]
                self.commands_rec_2.append(response_command_trans)
            elif response_command == "57AA0020000C7B22726574223A747275657DAE": # 红外发射
                return
            elif response_command == '55AA00F0000F01000C7B22726574223A747275657D8C': # 新红外发射 
                return
            elif response_command[:18] == "55AA00F00019010101": # Subg433测试
                try:
                    response_command = self.HEX_to_ASCII(response_command,18) # 转换为字典(** 要判断是否为字典)
                    self.commands_rec_2.append(response_command)
                except:
                    pass
            elif response_command[:18] == "55AA00F0000F01000D": # 红外接收
                print("红外接收正常")
            elif response_command[:4] == "57AA" or response_command[:4] == "55AA":
                try: 
                    response_command = self.HEX_to_ASCII(response_command) # 转换为字典(** 要判断是否为字典)
                    self.commands_rec_2.append(response_command)
                except:
                    pass
            else:
                return
    
            if self.current_command_index_2 in self.timeIndex_finish:  # 每个测试项执行完成
                self.test_end_pass_2()
            else:self.current_command_index_2 += 1
            self.pushButton_Send_2()
   
    def slot_readyRead_2(self,data): # 主串口接收
        self.receive_time_out_2.start(120)
        self.rec_buff_2 += data["buf"]
    
    def receive_time_out_func_3(self):
        self.receive_time_out_3.stop()
        
        View_data = ''
        Byte_data = bytes(self.rec_buff_3)

        self.rec_buff_3.clear() # 清除缓存

        if self.test_flag_ing_3 == True:

            for i in range(0,len(Byte_data)):
                View_data = View_data + '{:02X}'.format(Byte_data[i]) + ' '
            # 判断回应是否是指定的命令
            response_command = View_data.replace(" ", "").upper()  # 去除空格并大写
            
            # 去掉多余接收的命令
            first_occurrence = response_command.find("57AA00")  # 找到第一次出现的位置
            second_occurrence = response_command.find("57AA00", first_occurrence + 1)  # 找到第二次出现的位置
            if second_occurrence != -1:  # 如果找到第二次出现的位置
                response_command = response_command[:second_occurrence]  # 截取第二次出现之前的部分
            print(response_command)

            if response_command == "57AA000000010406" or response_command == '55AA000000010404': # 开始产测
                self.testMode_flage_time_3.stop()
            elif response_command[:12] == "57AA00210006": # 红外接收
                response_command_trans = {}
                response_command_trans["rec"] = response_command[12:-2]
                self.commands_rec_3.append(response_command_trans)
            elif response_command == "57AA0020000C7B22726574223A747275657DAE": # 红外发射
                return
            elif response_command == '55AA00F0000F01000C7B22726574223A747275657D8C': # 新红外发射 
                return
            elif response_command[:18] == "55AA00F00019010101": # Subg433测试
                try:
                    response_command = self.HEX_to_ASCII(response_command,18) # 转换为字典(** 要判断是否为字典)
                    self.commands_rec_3.append(response_command)
                except:
                    pass
            elif response_command[:18] == "55AA00F0000F01000D": # 红外接收
                print("红外接收正常")
            elif response_command[:4] == "57AA" or response_command[:4] == "55AA":
                try: 
                    response_command = self.HEX_to_ASCII(response_command) # 转换为字典(** 要判断是否为字典)
                    self.commands_rec_3.append(response_command)
                except:
                    pass
            else:
                return
    
            if self.current_command_index_3 in self.timeIndex_finish:  # 每个测试项执行完成
                self.test_end_pass_3()
            else:self.current_command_index_3 += 1
            self.pushButton_Send_3()

    def slot_readyRead_3(self,data): # 主串口接收
        self.receive_time_out_3.start(120)
        self.rec_buff_3 += data["buf"]
    
    def receive_time_out_func_4(self):
        self.receive_time_out_4.stop()
        
        View_data = ''
        Byte_data = bytes(self.rec_buff_4)

        self.rec_buff_4.clear() # 清除缓存

        if self.test_flag_ing_4 == True:

            for i in range(0,len(Byte_data)):
                View_data = View_data + '{:02X}'.format(Byte_data[i]) + ' '
            # 判断回应是否是指定的命令
            response_command = View_data.replace(" ", "").upper()  # 去除空格并大写

            # 去掉多余接收的命令
            first_occurrence = response_command.find("57AA00")  # 找到第一次出现的位置
            second_occurrence = response_command.find("57AA00", first_occurrence + 1)  # 找到第二次出现的位置
            if second_occurrence != -1:  # 如果找到第二次出现的位置
                response_command = response_command[:second_occurrence]  # 截取第二次出现之前的部分
            print(response_command)

            if response_command == "57AA000000010406" or response_command == '55AA000000010404': # 开始产测
                self.testMode_flage_time_4.stop()
            elif response_command[:12] == "57AA00210006": # 红外接收
                response_command_trans = {}
                response_command_trans["rec"] = response_command[12:-2]
                self.commands_rec_4.append(response_command_trans)
            elif response_command == "57AA0020000C7B22726574223A747275657DAE": # 红外发射
                return
            elif response_command == '55AA00F0000F01000C7B22726574223A747275657D8C': # 新红外发射 
                return
            elif response_command[:18] == "55AA00F00019010101": # Subg433测试
                try:
                    response_command = self.HEX_to_ASCII(response_command,18) # 转换为字典(** 要判断是否为字典)
                    self.commands_rec_4.append(response_command)
                except:
                    pass
            elif response_command[:18] == "55AA00F0000F01000D": # 红外接收
                print("红外接收正常")
            elif response_command[:4] == "57AA" or response_command[:4] == "55AA":
                try: 
                    response_command = self.HEX_to_ASCII(response_command) # 转换为字典(** 要判断是否为字典)
                    self.commands_rec_4.append(response_command)
                except:
                    pass
            else:
                return
    
            if self.current_command_index_4 in self.timeIndex_finish:  # 每个测试项执行完成
                self.test_end_pass_4()
            else:self.current_command_index_4 += 1
            self.pushButton_Send_4()

    def slot_readyRead_4(self,data): # 主串口接收
        self.receive_time_out_4.start(120)
        self.rec_buff_4 += data["buf"]
    

    def receive_time_out_slave_func(self):
        self.receive_time_out_slave.stop()

        View_data = ''
        Byte_data = bytes(self.rec_buff_slave)
        self.rec_buff_slave.clear() # 清除缓存
        for i in range(0,len(Byte_data)):
            View_data = View_data + '{:02X}'.format(Byte_data[i]) + ' '
        # 判断回应是否是指定的命令
        response_command = View_data.replace(" ", "").upper()  # 去除空格并大写
        print("控制串口")

        # 去掉多余接收的命令
        first_occurrence = response_command.find("57AA00")  # 找到第一次出现的位置
        second_occurrence = response_command.find("57AA00", first_occurrence + 1)  # 找到第二次出现的位置
        if second_occurrence != -1:  # 如果找到第二次出现的位置
            response_command = response_command[:second_occurrence]  # 截取第二次出现之前的部分
        print(response_command)

        if response_command[:12] == "57AA00210006": # 红外接收
            response_command_trans = {}
            response_command_trans["rec"] = response_command[12:-2]
            if self.serial_slave_channel == 1:# 控制串口设置
                self.commands_rec.append(response_command_trans)
                self.pushButton_Send()
            elif self.serial_slave_channel == 2:# 控制串口设置
                self.commands_rec_2.append(response_command_trans)
                self.pushButton_Send_2()
            elif self.serial_slave_channel == 3:# 控制串口设置
                self.commands_rec_3.append(response_command_trans)
                self.pushButton_Send_3()
            elif self.serial_slave_channel == 4:# 控制串口设置
                self.commands_rec_4.append(response_command_trans)
                self.pushButton_Send_4()

        elif response_command[:18] == "55AA00F0000F01000D": # 新红外接收
            if self.serial_slave_channel == 1:# 控制串口设置
                self.pushButton_Send()
            elif self.serial_slave_channel == 2:# 控制串口设置
                self.pushButton_Send_2()
            elif self.serial_slave_channel == 3:# 控制串口设置
                self.pushButton_Send_3()
            elif self.serial_slave_channel == 4:# 控制串口设置
                self.pushButton_Send_4()

    def slot_readyRead_slave(self,data): # 控制串口接收
        self.receive_time_out_slave.start(100)
        self.rec_buff_slave += data["buf"]
    
    def infrared_ng_fun_1(self):
        self.infrared_ng_1.stop()
        self.test_end_ng()
        self.slave_control = False
    
    def infrared_ng_fun_2(self):
        self.infrared_ng_2.stop()
        self.test_end_ng_2()
        self.slave_control = False
    
    def infrared_ng_fun_3(self):
        self.infrared_ng_3.stop()
        self.test_end_ng_3()
        self.slave_control = False
    
    def infrared_ng_fun_4(self):
        self.infrared_ng_4.stop()
        self.test_end_ng_4()
        self.slave_control = False


    def infrared_func(self):
        self.infrared.stop()
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        command = settings.value(f'{self.test_types}_command/conmmand_4','')
        self.pushButton_Send_slave(command) # 红外发送命令

    def infrared_emit_func(self):
        self.infrared_emit.stop()
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        command = settings.value(f'{self.test_types}_command/conmmand_4','') # 红外发射命令
        Byte_data = bytes() 
        send_list = []
        send_text = command  # 发送当前需要发送的命令
        while send_text != '':
            try:
                num = int(send_text[0:2],16)
            except:
                return
            send_text = send_text[2:].strip()
            send_list.append(num)
        Byte_data = bytes(send_list)
        parameter = {}
        parameter['data'] = Byte_data
        self.Serial_Qthread_function_1.signal_SendData.emit(parameter)
    
    def infrared_func_2(self):
        self.infrared_2.stop()
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        command = settings.value(f'{self.test_types}_command/conmmand_4','')
        self.pushButton_Send_slave(command) # 红外发送命令

    def infrared_emit_func_2(self):
        self.infrared_emit_2.stop()
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        command = settings.value(f'{self.test_types}_command/conmmand_4','') # 红外发射命令
        Byte_data = bytes() 
        send_list = []
        send_text = command  # 发送当前需要发送的命令
        while send_text != '':
            try:
                num = int(send_text[0:2],16)
            except:
                return
            send_text = send_text[2:].strip()
            send_list.append(num)
        Byte_data = bytes(send_list)
        parameter = {}
        parameter['data'] = Byte_data
        self.Serial_Qthread_function_2.signal_SendData.emit(parameter)
    
    def infrared_func_3(self):
        self.infrared_3.stop()
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        command = settings.value(f'{self.test_types}_command/conmmand_4','')
        self.pushButton_Send_slave(command) # 红外发送命令

    def infrared_emit_func_3(self):
        self.infrared_emit_3.stop()
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        command = settings.value(f'{self.test_types}_command/conmmand_4','') # 红外发射命令
        Byte_data = bytes() 
        send_list = []
        send_text = command  # 发送当前需要发送的命令
        while send_text != '':
            try:
                num = int(send_text[0:2],16)
            except:
                return
            send_text = send_text[2:].strip()
            send_list.append(num)
        Byte_data = bytes(send_list)
        parameter = {}
        parameter['data'] = Byte_data
        self.Serial_Qthread_function_3.signal_SendData.emit(parameter)
    
    def infrared_func_4(self):
        self.infrared_4.stop()
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        command = settings.value(f'{self.test_types}_command/conmmand_4','')
        self.pushButton_Send_slave(command) # 红外发送命令

    def infrared_emit_func_4(self):
        self.infrared_emit_4.stop()
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        command = settings.value(f'{self.test_types}_command/conmmand_4','') # 红外发射命令
        Byte_data = bytes() 
        send_list = []
        send_text = command  # 发送当前需要发送的命令
        while send_text != '':
            try:
                num = int(send_text[0:2],16)
            except:
                return
            send_text = send_text[2:].strip()
            send_list.append(num)
        Byte_data = bytes(send_list)
        parameter = {}
        parameter['data'] = Byte_data
        self.Serial_Qthread_function_4.signal_SendData.emit(parameter)

    def pushButton_10_34(self, action):
        if self.test_button == 'TEST_LED_Normal':
            self.ui.label_103.setVisible(False) 
            self.ui.pushButton_103.setVisible(False)
            self.ui.pushButton_104.setVisible(False)

            if action == 'test':
                self.test_end_pass()
                self.pushButton_Send()

            elif action == 'cancel':
                self.test_end_ng()
        
        elif self.test_button == 'TEST_BOOL_IRLamp':
            self.ui.label_103.setVisible(False) 
            self.ui.pushButton_103.setVisible(False)
            self.ui.pushButton_104.setVisible(False)

            if action == 'test':
                self.test_end_pass()
                self.pushButton_Send()

            elif action == 'cancel':
                self.test_end_ng()

    
    def pushButton_20_34(self, action):
        if self.test_button_2 == 'TEST_LED_Normal':
            self.ui.label_203.setVisible(False) 
            self.ui.pushButton_203.setVisible(False)
            self.ui.pushButton_204.setVisible(False)

            if action == 'test':
                self.test_end_pass_2()
                self.pushButton_Send_2()

            elif action == 'cancel':
                self.test_end_ng_2()
        
        elif self.test_button_2 == 'TEST_BOOL_IRLamp':
            self.ui.label_203.setVisible(False) 
            self.ui.pushButton_203.setVisible(False)
            self.ui.pushButton_204.setVisible(False)

            if action == 'test':
                self.test_end_pass_2()
                self.pushButton_Send_2()

            elif action == 'cancel':
                self.test_end_ng_2()
                

    def pushButton_30_34(self, action):
        if self.test_button_3 == 'TEST_LED_Normal':
            self.ui.label_303.setVisible(False) 
            self.ui.pushButton_303.setVisible(False)
            self.ui.pushButton_304.setVisible(False)

            if action == 'test':
                self.test_end_pass_3()
                self.pushButton_Send_3()

            elif action == 'cancel':
                self.test_end_ng_3()
        
        elif self.test_button_3 == 'TEST_BOOL_IRLamp':
            self.ui.label_303.setVisible(False) 
            self.ui.pushButton_303.setVisible(False)
            self.ui.pushButton_304.setVisible(False)

            if action == 'test':
                self.test_end_pass_3()
                self.pushButton_Send_3()

            elif action == 'cancel':
                self.test_end_ng_3()

    def pushButton_40_34(self, action):
        if self.test_button_4 == 'TEST_LED_Normal':
            self.ui.label_403.setVisible(False) 
            self.ui.pushButton_403.setVisible(False)
            self.ui.pushButton_404.setVisible(False)

            if action == 'test':
                self.test_end_pass_4()
                self.pushButton_Send_4()

            elif action == 'cancel':
                self.test_end_ng_4()

        elif self.test_button_4 == 'TEST_BOOL_IRLamp':
            self.ui.label_403.setVisible(False) 
            self.ui.pushButton_403.setVisible(False)
            self.ui.pushButton_404.setVisible(False)

            if action == 'test':
                self.test_end_pass_4()
                self.pushButton_Send_4()

            elif action == 'cancel':
                self.test_end_ng_4()        

    def pushButton_8_3_open_start(self):
        try:
            with open("file.json", "r", encoding="utf-8-sig") as file:
                json_data = file.read()
                pattern = r',\s*}'   
                replacement = "\r\n    }"
                data = re.sub(pattern, replacement, json_data)
                pattern = r',\s*]'   
                replacement = "\r\n    ]"
                data = re.sub(pattern, replacement, data)
                pattern = r'//.*'   
                replacement = " "
                data = re.sub(pattern, replacement, data)
                with open("file.json", "w", encoding="utf-8") as file:
                    file.write(data)

            with open("file.json", "r", encoding="utf-8-sig") as file:    
                try:
                    data = json.load(file)  # 加载 JSON 数据

                    types_choose = data.get("PlatformName", []) # 获取协议类型
                    if types_choose == []:
                        types_choose = data.get("platformName", [])
                    if types_choose.lower() == "onlytoken":
                        self.test_types = "OnlyToken"
                    elif types_choose.lower() == "remoter":
                        self.test_types = "Remoter"
                    print("协议类型：", self.test_types)

                    test_items = data.get("TestItems", [])  # 获取 "TestItems" 的内容
                    if test_items == []:
                        test_items = data.get("testItems", [])

                    self.Sequence_1 = SequenceForm_Security(test_items)
                    self.Sequence_1.selected_test.connect(self.handle_selected_changed) # 接收产测序列的信号
                    self.Sequence_1.save_checkbox_state()
                except json.JSONDecodeError:
                    QMessageBox.warning(self, '警告', '无法解析JSON文件')
        except:
            pass 
    
    def pushButton_8_3_open(self): # 导入按钮
        file_dialog = QFileDialog(self)  # 创建文件对话框
        file_dialog.setNameFilter("JSON Files (*.json)")  # 设置文件过滤器
        if file_dialog.exec_():
            file_name = file_dialog.selectedFiles()[0]  # 获取选择的文件名

            with open(file_name, "r", encoding="utf-8-sig") as file:
                json_data = file.read()
                pattern = r',\s*}'   
                replacement = "\r\n    }"
                data = re.sub(pattern, replacement, json_data)
                pattern = r',\s*]'   
                replacement = "\r\n    ]"
                data = re.sub(pattern, replacement, data)
                pattern = r'//.*'   
                replacement = " "
                data = re.sub(pattern, replacement, data)
                with open("file.json", "w", encoding="utf-8") as file:
                    file.write(data)

            with open("file.json", "r", encoding="utf-8-sig") as file:    
                try:
                    data = json.load(file)  # 加载 JSON 数据
                    
                    types_choose = data.get("PlatformName", []) # 获取协议类型
                    if types_choose == []:
                        types_choose = data.get("platformName", [])
                    if types_choose.lower() == "onlytoken":
                        self.test_types = "OnlyToken"
                    elif types_choose.lower() == "remoter":
                        self.test_types = "Remoter"
                    print("协议类型：", self.test_types)

                    test_items = data.get("TestItems", [])  # 获取 "TestItems" 的内容
                    if test_items == []:
                        test_items = data.get("testItems", [])
                    self.Sequence_1 = SequenceForm_Security(test_items)
                    self.Sequence_1.selected_test.connect(self.handle_selected_changed) # 接收产测序列的信号
                except json.JSONDecodeError:
                    QMessageBox.warning(self, '警告', '无法解析JSON文件') 
    
    def pushButton_8_4_open(self): # 编辑按钮
        try:
            self.Sequence_1.show()
        except:pass
    
    def handle_selected_changed(self, selected): # 对接收到的selected值进行处理
        self.items_text = [] # text
        self.items_name = [] # name
        self.commands = [] # 产测命令
        timeIndex_count = [] # 记录每一个测试项命令的个数
        self.test_params = []  # 记录要接收的参数
        self.params_standard = {'TEST_SIGNAL_WIFI':[],'TEST_SIGNAL_Subg':[],'TEST_QUALITY_RSSI':[]}

        self.connect_position = [] # 记录表格中TCP设置按钮的位置
        self.firmware_check = [] # 记录固件版本按钮的位置

        select_name = [] # name和paras
        for i in range(len(selected)):
            select_name.append([selected[i][0],selected[i][2]])
            
        # 产测命令添加
        settings = QSettings("config_Security.ini", QSettings.IniFormat)
        for name in select_name:
            if name[0] == "CHECK_CODE": # 输入SN检查
                if name[1]['CodeType'] == "InputSn":
                    self.items_name.append("CHECK_SN")
                    self.commands.append('CHECK_SN')
                    timeIndex_count.append(1)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append([])
            elif name[0] == "CHECK_STATION": # 过站信息检查
                self.items_name.append("CHECK_STATION")
                self.commands.append('CHECK_STATION')
                timeIndex_count.append(1)
                self.items_text.append(selected[select_name.index(name)][1])
                self.test_params.append([])        
            elif name[0] == 'CONNECT' or name[0] == 'CONNECT_DOUBLE_SERIALPORT': # 建立连接
                if name[1]['ConnectType'] == "SerialPort":
                    self.items_name.append("SerialPort")
                    self.commands.append("SerialPort")
                    timeIndex_count.append(1)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append([])
            elif name[0] == 'ENTER_TESTMODE': # 进入测试模式
                print('进入测试模式TRUE')
                self.items_name.append("ENTER_TESTMODE")
                self.commands.append('ENTER_TESTMODE')
                timeIndex_count.append(1)
                self.items_text.append(selected[select_name.index(name)][1])
                self.test_params.append([])
            elif name[0] == "CHECK_INFO_FIRMWARE": # 固件版本检测
                self.items_name.append("CHECK_INFO_FIRMWARE")
                self.commands.append(settings.value(f'{self.test_types}_command/conmmand_3',""))
                self.commands.append('CHECK_INFO_FIRMWARE')
                timeIndex_count.append(2)
                self.items_text.append(selected[select_name.index(name)][1])
                self.test_params.append(['firmName','firmVer'])
            elif name[0] == 'TEST_INFRARE':
                if name[1]['InfrareType'] == "EnterReceive": # 红外接收测试
                    self.items_name.append("EnterReceive")
                    self.commands.append(settings.value(f'{self.test_types}_command/conmmand_9',""))
                    self.commands.append("EnterReceive")
                    self.commands.append("EnterReceive_check")
                    timeIndex_count.append(3)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append([])
                elif name[1]['InfrareType'] == "Emission": # 红外发射测试
                    self.items_name.append("Emission")
                    self.commands.append("Emission")
                    self.commands.append("Emission_check")
                    timeIndex_count.append(2)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append([])
                elif name[1]['InfrareType'] == "LampTest": # 红外灯测试(直接跳过)
                    self.items_name.append("LampTest")
                    self.commands.append('LampTest')
                    timeIndex_count.append(1)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append([])
            elif name[0] == 'TEST_GPIO' or name[0] == 'TEST_KEY': # 按键测试
                self.items_name.append('TEST_GPIO')
                self.commands.append(settings.value(f'{self.test_types}_command/conmmand_6',""))
                timeIndex_count.append(1)
                self.items_text.append(selected[select_name.index(name)][1])
                self.test_params.append([])
            elif name[0] == 'TEST_LED':
                if name[1]['LEDType'] == "Normal": # 指示灯测试
                    self.items_name.append("TEST_LED_Normal")
                    self.commands.append('TEST_LED_Normal')
                    timeIndex_count.append(1)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append([])
            elif name[0] == 'PROMPT': # 指示灯测试
                self.items_name.append("TEST_LED_Normal")
                self.commands.append('TEST_LED_Normal')
                timeIndex_count.append(1)
                self.items_text.append(selected[select_name.index(name)][1])
                self.test_params.append([])
            elif name[0] == 'TEST_SIGNALQUALITY':
                if name[1]['TestType'] == "RSSI": # wifi性能测试
                    self.items_name.append("TEST_SIGNALQUALITY")
                    message = {}
                    message['ssid'] = name[1]['SSID']
                    head = '57AA0003'
                    settings.setValue(f'{self.test_types}_command/conmmand_8',self.ASCII_to_HEX(message,head))
                    self.commands.append(settings.value(f'{self.test_types}_command/conmmand_8',""))
                    self.commands.append('TEST_SIGNALQUALITY')
                    timeIndex_count.append(2)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append(["rssi"])
                    params = []
                    params.append(name[1]['LowLimit'])
                    params.append(name[1]['HighLimit'])
                    self.params_standard['TEST_SIGNAL_WIFI'] = params
            elif name[0] == 'TEST_QUALITY_SIGNAL':
                if name[1]['TestType'] == "Subg433RSSI": # Subg433 RSSI信号强度测试
                    self.items_name.append("TEST_SIGNAL_Subg")
                    self.commands.append(settings.value(f'{self.test_types}_command/conmmand_8',""))
                    self.commands.append('TEST_SIGNAL_Subg')
                    timeIndex_count.append(2)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append(["rssi"])
                    params = []
                    params.append(name[1]['LowLimit'])
                    params.append(name[1]['HighLimit'])
                    self.params_standard['TEST_SIGNAL_Subg'] = params
                elif name[1]['TestType'] == "RSSI": # RSSI信号强度测试
                    self.items_name.append("TEST_QUALITY_RSSI")
                    self.commands.append(settings.value(f'{self.test_types}_command/conmmand_15',""))
                    self.commands.append('TEST_QUALITY_RSSI')
                    timeIndex_count.append(2)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append(["rssi"])
                    params = []
                    params.append(name[1]['LowLimit'])
                    params.append(name[1]['HighLimit'])
                    self.params_standard['TEST_QUALITY_RSSI'] = params
            elif name[0] == 'WR_CODE':
                if name[1]['WRType'] == "Read": # 读取mac
                    self.items_name.append("WR_CODE_MAC")
                    self.commands.append(settings.value(f'{self.test_types}_command/conmmand_10',""))
                    timeIndex_count.append(1)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append(['mac'])
            elif name[0] == 'TEST_BOOL':
                if name[1]['TestItem'] == "IRLamp": # 红外灯测试
                    self.items_name.append("TEST_BOOL_IRLamp")
                    self.commands.append(settings.value(f'{self.test_types}_command/conmmand_11',""))
                    self.commands.append("TEST_BOOL_IRLamp")
                    timeIndex_count.append(2)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append([])
            elif name[0] == 'TEST_INFRARE_NEW':
                if name[1]['InfrareType'] == "EnterReceive": # 红外接收测试
                    self.items_name.append("EnterReceive")
                    self.commands.append(settings.value(f'{self.test_types}_command/conmmand_9',""))
                    self.commands.append("EnterReceive")
                    self.commands.append("EnterReceive_New")
                    timeIndex_count.append(3)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append([])
                elif name[1]['InfrareType'] == "Emission": # 红外发射测试
                    self.items_name.append("Emission")
                    self.commands.append("Emission")
                    self.commands.append("Emission_check_New")
                    timeIndex_count.append(2)
                    self.items_text.append(selected[select_name.index(name)][1])
                    self.test_params.append([])
        
        del settings
        self.timeIndex_start = [0] # 开始的序列
        self.timeIndex_finish = [] # 结束的序列
        for i in range(len(timeIndex_count)-1):
            self.timeIndex_start.append(self.timeIndex_start[i] + timeIndex_count[i])
        for i in range(len(self.timeIndex_start)):
            try: self.timeIndex_finish.append(self.timeIndex_start[i] + timeIndex_count[i] -1)
            except: pass

        print(f'命令数：{timeIndex_count}') # 每个测试项有几个命令
        print(f'开始序列：{self.timeIndex_start}') # 开始的序列
        print(f'结束序列：{self.timeIndex_finish}') # 结束的序列
        print(f'text：{self.items_text}') # text
        print(f'name：{self.items_name}') # name
        print(f'paras：{self.test_params}') # paras
        print(f'标准值：{self.params_standard}') # 填入表格的标准值
        print(f'command：{self.commands}')

        self.connect_position = self.get_all_indexes(self.items_name,'SerialPort')
        self.firmware_check = self.get_all_indexes(self.items_name,'CHECK_INFO_FIRMWARE')
        self.test_pre = True


    def get_all_indexes(self, input_list, target): # 返回指定元素所有下标
        indexes = [index for index, value in enumerate(input_list) if value == target]
        return indexes if indexes else []

    def ASCII_to_HEX(self,message,head): # ASCII转16进制
        message = json.dumps(message).replace(' ','').encode().hex()  # 转化为字符串 16进制
        message_len = hex(len(bytes.fromhex(message))) # 计算数据长度
        if len(message_len) == 3:
            len_mes = '0'+ message_len[-1]
        else: 
            len_mes = message_len[-2:]
        message = head + '00' + len_mes + message
        hex_list = [message[i:i+2] for i in range(0, len(message), 2)] # 计算校验位
        decimal_sum = sum(int(hex_num, 16) for hex_num in hex_list)

        message = message + hex(decimal_sum)[-2:]
        # message = ' '.join([message[i:i+2] for i in range(0, len(message), 2)]) # 2字符分割
        return message
    
    def HEX_to_ASCII(self, hex_str, flag=12): # 16进制转ASCII
        ascii_str = ""
        for i in range(flag, len(hex_str)-2, 2):
            ascii_str += chr(int(hex_str[i:i+2], 16))
        ascii = json.loads(ascii_str)
        return ascii

    def data_case(self, name, value, time, result): 
        cases = [{"name": name[i], "value": value[i], "elapsed": time[i], "result": result[i]} for i in range(len(name))]
        return {"cases": cases}

    def check_all_pass(self, lst): # 判断是否全部通过
        for item in lst:
            if item != "pass":
                return False
        return True
    
    def text_show(self, item, state, channel): # 测试状态
        state_color_dict = {'等待测试':'rgb(0,145,234)',
                            '正在测试':'rgb(255,165,0)',
                            '测试完成':'rgb(50,205,50)',
                            '测试失败':'rgb(255,0,0)'}
        state_color = state_color_dict[state]
        label_name = "label_" + channel + "01"
        label = getattr(self.ui, label_name)
        label.setStyleSheet(f"QLabel {{background-color : {state_color}; color : black;}}")
        label.setText(f"<p style='font-size:{self.show_size[0]}'>{item}</p><p style='font-size:{self.show_size[1]}'>{state}</p>")

    def next_page(self):
        sender = self.sender()
        button_name = sender.objectName()
        label_name = "stackedWidget_" + button_name[-3]
        label = getattr(self.ui, label_name)
        label_index = f"self.current_index_{button_name[-3]}"
        exec(f"{label_index} = ({label_index} + 1) % label.count()")
        exec(f"label.setCurrentIndex({label_index})")
    
    def init_table(self, channel):
        row_count = len(self.items_text) # 行数由产测序列个数决定
        column_count = 8 # 列数固定
        label_name = "tableWidget_" + channel + "01" # 对应通道的表格
        label = getattr(self.ui, label_name)
        label.setRowCount(row_count)
        label.setColumnCount(column_count)
        label.verticalHeader().setVisible(False)
        label.horizontalHeader().setDefaultSectionSize(100) # 表格默认列宽
        label.verticalHeader().setDefaultSectionSize(50) # 表格默认列高
        label.setColumnWidth(0, 60) # 列宽
        label.setColumnWidth(1, 80)
        label.setColumnWidth(2, 200)
        label.setColumnWidth(4, 120)
        label.setColumnWidth(5, 200)
        label.setEditTriggers(QAbstractItemView.NoEditTriggers) # 禁止对表格进行编辑
        label.setSelectionMode(QAbstractItemView.NoSelection) # 禁止对表格进行选中
        label.setWordWrap(False) # 不自动换行

        # 设置表头
        header_labels = ['序号','配置','测试项','状态','标准','数据','结果','用时']
        label.setHorizontalHeaderLabels(header_labels)
        label.horizontalHeader().setStyleSheet("QHeaderView::section{font:11pt}")

        for i, item in enumerate(self.items_text): # 每一行配置
            squ_item = QTableWidgetItem(str(i+1)) # 序号
            squ_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) # 居中
            squ_item.setFont(QFont('微软雅黑', 11))

            test_item = QTableWidgetItem(item) # 测试序列
            test_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter) # 居中
            test_item.setFont(QFont('微软雅黑', 11))

            status_item = QTableWidgetItem('已就绪') # 状态序列
            status_item.setForeground(QColor(255, 165, 0))
            status_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) # 居中
            status_item.setFont(QFont('微软雅黑', 11))

            param_item = QTableWidgetItem("") # 标准
            param_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) # 居中
            param_item.setFont(QFont('微软雅黑', 11))

            data_item = QTableWidgetItem("") # 数据
            data_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) # 居中
            data_item.setFont(QFont('微软雅黑', 11))

            waiting_item = QTableWidgetItem('等待测试') # 结果
            waiting_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) # 居中
            waiting_item.setFont(QFont('微软雅黑', 11))

            time_item = QTableWidgetItem("") # 用时
            time_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) # 居中
            time_item.setFont(QFont('微软雅黑', 11))

            label.setItem(i, 0, squ_item)
            label.setItem(i, 2, test_item)
            label.setItem(i, 3, status_item)
            label.setItem(i, 4, param_item)
            label.setItem(i, 5, data_item)
            label.setItem(i, 6, waiting_item)
            label.setItem(i, 7, time_item)

            label.setCellWidget(i, 1, None) # 清除按钮

        # 添加测试标准值
        if self.params_standard['TEST_SIGNAL_WIFI'] != []:
            item = label.item(self.items_name.index('TEST_SIGNALQUALITY'), 4)
            item.setText(str(self.params_standard['TEST_SIGNAL_WIFI']))
        
        if self.params_standard['TEST_SIGNAL_Subg'] != []:
            item = label.item(self.items_name.index('TEST_SIGNAL_Subg'), 4)
            item.setText(str(self.params_standard['TEST_SIGNAL_Subg']))

        if self.params_standard['TEST_QUALITY_RSSI'] != []:
            item = label.item(self.items_name.index('TEST_QUALITY_RSSI'), 4)
            item.setText(str(self.params_standard['TEST_QUALITY_RSSI']))
        
        for pos in self.connect_position: # 串口连接按钮
            waiting_item = label.item(pos, 3) # 修改等待状态
            waiting_item.setText("未就绪")
            waiting_item.setForeground(QColor(0,0,0))
            button = QToolButton()
            button.setStyleSheet("background-color: white; border: none;")
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.setIcon(QIcon("./Picture/setting1.ico"))
            button.setObjectName("button_tcpcon_" + channel)
            label.setCellWidget(pos, 1, button)
            button.clicked.connect(partial(self.connect_settings, button.objectName()))
        
        for pos in self.firmware_check: # 固件检测按钮
            button = QToolButton()
            button.setStyleSheet("background-color: white; border: none;")
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.setIcon(QIcon("./Picture/setting1.ico"))
            button.setObjectName("button_firm_" + channel)
            label.setCellWidget(pos, 1, button)
            button.clicked.connect(partial(self.firm_settings, button.objectName()))

    def connect_settings(self,state): # 串口连接按钮
        if state == 'button_tcpcon_1':
            self.settingWindow1 = SettingForm('button_1',2)
            self.setEnabled(False)
            self.settingWindow1.exec_()
            self.setEnabled(True)
     
        elif state == 'button_tcpcon_2':
            self.settingWindow2 = SettingForm('button_2',2)
            self.setEnabled(False)
            self.settingWindow2.exec_()
            self.setEnabled(True)

        elif state == 'button_tcpcon_3':
            self.settingWindow3 = SettingForm('button_3',2)
            self.setEnabled(False)
            self.settingWindow3.exec_()
            self.setEnabled(True)
        
        elif state == 'button_tcpcon_4':
            self.settingWindow4 = SettingForm('button_4',2)
            self.setEnabled(False)
            self.settingWindow4.exec_()
            self.setEnabled(True)
####################################################################################    

    def firm_settings(self,state):
        if state == 'button_firm_1':
            self.firmWin1 = firmwaresetting('button_firm_1')
            self.setEnabled(False)
            self.firmWin1.exec_()
            self.setEnabled(True)
        
        elif state == 'button_firm_2':
            self.firmWin2 = firmwaresetting('button_firm_1')
            self.setEnabled(False)
            self.firmWin2.exec_()
            self.setEnabled(True)
        
        elif state == 'button_firm_3':
            self.firmWin3 = firmwaresetting('button_firm_1')
            self.setEnabled(False)
            self.firmWin3.exec_()
            self.setEnabled(True)
        
        elif state == 'button_firm_4':
            self.firmWin4 = firmwaresetting('button_firm_1')
            self.setEnabled(False)
            self.firmWin4.exec_()
            self.setEnabled(True)
    
    def PassStation(self,state):
        self.test_flag = state # 是否成功标志位

    def PassStation_2(self,state):
        self.test_flag_2 = state # 是否成功标志位
    
    def PassStation_3(self,state):
        self.test_flag_3 = state # 是否成功标志位
    
    def PassStation_4(self,state):
        self.test_flag_4 = state # 是否成功标志位

    def pushButton_1_1_open(self): # 本地测试按钮
        self.ui.stackedWidget.setCurrentIndex(0)
        self.stateTest = 1
        self.ui.pushButton_10.setEnabled(True)
        self.ui.pushButton_10.setStyleSheet("background-color: rgb(30, 144, 255);border: none; color: white;")

    def pushButton_1_2_open(self): # 工单测试按钮
        self.ui.stackedWidget.setCurrentIndex(1)
        self.stateTest = 2
        self.ui.pushButton_10.setEnabled(False)
        self.ui.pushButton_10.setStyleSheet("background-color: rgb(169, 213, 255);border: none; color: white;")

    def pushButton_10_open(self): # 启动按钮
        if self.stateTest == 1: # 本地测试
            if self.startTest_1:
                self.ui.groupBox_2.setEnabled(True)
                self.ui.pushButton_1_1.setEnabled(True)
                self.ui.pushButton_1_2.setEnabled(True)
                self.ui.pushButton_10.setText("启动测试")
                self.ui.pushButton_10.setStyleSheet("background-color: rgb(30, 144, 255);border: none; color: white;")
                self.ui.groupBox_4.setVisible(False)
                self.ui.groupBox_5.setVisible(False)
                self.ui.groupBox_6.setVisible(False)
                self.ui.groupBox_7.setVisible(False)
                self.ui.tableView_12.setModel(QStandardItemModel()) # 清空表格数据
                self.ui.stackedWidget_1.setCurrentIndex(0)
                self.ui.stackedWidget_2.setCurrentIndex(0)
                self.ui.stackedWidget_3.setCurrentIndex(0)
                self.ui.stackedWidget_4.setCurrentIndex(0)
                self.current_index_1 = 0
                self.current_index_2 = 0
                self.current_index_3 = 0
                self.current_index_4 = 0

                self.slave_control = False # 取消占用
                self.channel_control_1.stop()
                self.channel_control_2.stop()
                self.channel_control_3.stop()
                self.channel_control_4.stop()

                self.infrared_ng_1.stop()
                self.infrared_ng_2.stop()
                self.infrared_ng_3.stop()
                self.infrared_ng_4.stop()

                self.ui.label_103.setVisible(False) # 隐藏测试提示框
                self.ui.label_203.setVisible(False)
                self.ui.label_303.setVisible(False)
                self.ui.label_403.setVisible(False)

                self.ui.pushButton_103.setVisible(False) # 隐藏通过失败按钮
                self.ui.pushButton_104.setVisible(False)
                self.ui.pushButton_203.setVisible(False)
                self.ui.pushButton_204.setVisible(False)
                self.ui.pushButton_303.setVisible(False)
                self.ui.pushButton_304.setVisible(False)
                self.ui.pushButton_403.setVisible(False)
                self.ui.pushButton_404.setVisible(False)

                self.ui.lineEdit_101.setEnabled(True) # 输入SN框
                self.ui.lineEdit_201.setEnabled(True)
                self.ui.lineEdit_301.setEnabled(True)
                self.ui.lineEdit_401.setEnabled(True)

                try:
                    self.ui.lineEdit_101.returnPressed.disconnect(self.Test_start)
                    self.ui.lineEdit_201.returnPressed.disconnect(self.Test_start_2)
                    self.ui.lineEdit_301.returnPressed.disconnect(self.Test_start_3)
                    self.ui.lineEdit_401.returnPressed.disconnect(self.Test_start_4)
                except:
                    pass

                self.current_command_index = 0
                self.current_command_index_2 = 0
                self.current_command_index_3 = 0
                self.current_command_index_4 = 0
                self.test_item_id = 0
                self.test_item_id_2 = 0
                self.test_item_id_3 = 0
                self.test_item_id_4 = 0
                self.ui.lineEdit_101.clear() 
                self.ui.lineEdit_201.clear() 
                self.ui.lineEdit_301.clear() 
                self.ui.lineEdit_401.clear() 

                if self.serial_open_flage_1 == True:
                    self.Serial_Qthread_function_1.signal_pushButton_Open.emit(1)
                    self.serial_open_flage_1 = False
                if self.serial_open_flage_2 == True:
                    self.Serial_Qthread_function_2.signal_pushButton_Open.emit(1)
                    self.serial_open_flage_2 = False
                if self.serial_open_flage_3 == True:
                    self.Serial_Qthread_function_3.signal_pushButton_Open.emit(1)
                    self.serial_open_flage_3 = False
                if self.serial_open_flage_4 == True:
                    self.Serial_Qthread_function_4.signal_pushButton_Open.emit(1)
                    self.serial_open_flage_4 = False
                if self.serial_open_flage_slave == True:
                    self.Serial_Qthread_function_slave.signal_pushButton_Open.emit(1)
                    self.serial_open_flage_slave = False
                
                self.connect_auto.stop()
                self.connect_auto_2.stop()
                self.connect_auto_3.stop()
                self.connect_auto_4.stop()
                self.connect_auto_slave.stop()

                self.receive_time_out.stop()
                self.receive_time_out_2.stop()
                self.receive_time_out_3.stop()
                self.receive_time_out_4.stop()
                self.receive_time_out_slave.stop()

                self.infrared.stop()
                self.infrared_2.stop()
                self.infrared_3.stop()
                self.infrared_4.stop()

                self.infrared_emit.stop()
                self.infrared_emit_2.stop()
                self.infrared_emit_3.stop()
                self.infrared_emit_4.stop()

                self.testMode_flage_time_1.stop()
                self.testMode_flage_time_2.stop()
                self.testMode_flage_time_3.stop()
                self.testMode_flage_time_4.stop()

            else:
                if not self.test_pre:
                    QMessageBox.warning(self, '提示', '先选择测试项')
                    return
                
                self.ui.groupBox_2.setEnabled(False)
                self.ui.pushButton_1_1.setEnabled(False)
                self.ui.pushButton_1_2.setEnabled(False)
                self.ui.lineEdit_101.setFocus() # 设置焦点在第一个输入框
                self.ui.pushButton_10.setText("停止测试")
                self.ui.pushButton_10.setStyleSheet("background-color: rgb(255, 0, 0);border: none; color: white;")

                # 创建表格数据
                self.channel = int(self.ui.comboBox_6_2.currentText())
                model = QStandardItemModel(self.channel, 1)
                for i in range(self.channel):
                    item = QStandardItem("通道"+str(i+1))
                    model.setItem(i, 0, item)
                self.ui.tableView_12.setModel(model)

                if self.channel == 1:
                    self.ui.groupBox_4.setGeometry(370, 0, 1550, 990)
                    self.ui.groupBox_4.setVisible(True)
                    self.init_table('1')
                    self.show_size = ['100px','60px']
                    self.Serial_QThread_1.start()
                    self.Serial_Qthread_function_1.signal_Serial_qthread_function_Init.emit()
                    self.Serial_QThread_slave.start()
                    self.Serial_Qthread_function_slave.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto.start(2000)
                    self.connect_auto_slave.start(2000)
                    self.ui.label_101.setStyleSheet("QLabel {background-color : gray; color : black; }")
                    self.ui.label_101.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                elif self.channel == 2:
                    self.ui.groupBox_4.setGeometry(370, 0, 775, 990)
                    self.ui.groupBox_5.setGeometry(1145, 0, 775, 990)
                    self.ui.groupBox_4.setVisible(True)
                    self.ui.groupBox_5.setVisible(True)
                    self.ui.lineEdit_101.returnPressed.connect(self.ui.lineEdit_201.setFocus)
                    self.ui.lineEdit_201.returnPressed.connect(self.ui.lineEdit_201.clearFocus)
                    self.init_table('1')
                    self.init_table('2')
                    self.show_size = ['60px','40px']
                    self.Serial_QThread_1.start()
                    self.Serial_Qthread_function_1.signal_Serial_qthread_function_Init.emit()
                    self.Serial_QThread_slave.start()
                    self.Serial_Qthread_function_slave.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto.start(2000)
                    self.connect_auto_slave.start(2000)
                    self.Serial_QThread_2.start()
                    self.Serial_Qthread_function_2.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto_2.start(2000)
                    self.ui.label_101.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_101.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                    self.ui.label_201.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_201.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                elif self.channel == 4:
                    self.ui.groupBox_4.setGeometry(370, 0, 775, 495)
                    self.ui.groupBox_5.setGeometry(1145, 0, 775, 495)
                    self.ui.groupBox_6.setGeometry(370, 495, 775, 495)
                    self.ui.groupBox_7.setGeometry(1145, 495, 775, 495)
                    self.ui.groupBox_4.setVisible(True)
                    self.ui.groupBox_5.setVisible(True)
                    self.ui.groupBox_6.setVisible(True)
                    self.ui.groupBox_7.setVisible(True)
                    self.ui.lineEdit_101.returnPressed.connect(self.ui.lineEdit_201.setFocus)
                    self.ui.lineEdit_201.returnPressed.connect(self.ui.lineEdit_301.setFocus)
                    self.ui.lineEdit_301.returnPressed.connect(self.ui.lineEdit_401.setFocus)
                    self.ui.lineEdit_401.returnPressed.connect(self.ui.lineEdit_401.clearFocus)
                    self.init_table('1')
                    self.init_table('2')
                    self.init_table('3')
                    self.init_table('4')
                    self.show_size = ['60px','40px']
                    self.Serial_QThread_1.start()
                    self.Serial_Qthread_function_1.signal_Serial_qthread_function_Init.emit()
                    self.Serial_QThread_slave.start()
                    self.Serial_Qthread_function_slave.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto.start(2000)
                    self.connect_auto_slave.start(2000)
                    self.Serial_QThread_2.start()
                    self.Serial_Qthread_function_2.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto_2.start(2000)
                    self.Serial_QThread_3.start()
                    self.Serial_Qthread_function_3.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto_3.start(2000)
                    self.Serial_QThread_4.start()
                    self.Serial_Qthread_function_4.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto_4.start(2000)
                    self.ui.label_101.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_101.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                    self.ui.label_201.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_201.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                    self.ui.label_301.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_301.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                    self.ui.label_401.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_401.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
        
            self.startTest_1 = not self.startTest_1 # 改变测试状态

        elif self.stateTest == 2: # 本地测试
            if self.startTest_2:
                self.ui.groupBox_3.setEnabled(True)
                self.ui.pushButton_1_1.setEnabled(True)
                self.ui.pushButton_1_2.setEnabled(True)
                self.ui.pushButton_10.setText("启动测试")
                self.ui.pushButton_10.setStyleSheet("background-color: rgb(30, 144, 255);border: none; color: white;")
                self.ui.groupBox_4.setVisible(False)
                self.ui.groupBox_5.setVisible(False)
                self.ui.groupBox_6.setVisible(False)
                self.ui.groupBox_7.setVisible(False)
                self.ui.tableView_12.setModel(QStandardItemModel()) # 清空表格数据
                self.ui.stackedWidget_1.setCurrentIndex(0)
                self.ui.stackedWidget_2.setCurrentIndex(0)
                self.ui.stackedWidget_3.setCurrentIndex(0)
                self.ui.stackedWidget_4.setCurrentIndex(0)
                self.current_index_1 = 0
                self.current_index_2 = 0
                self.current_index_3 = 0
                self.current_index_4 = 0

                self.slave_control = False # 取消占用
                self.channel_control_1.stop()
                self.channel_control_2.stop()
                self.channel_control_3.stop()
                self.channel_control_4.stop()

                self.infrared_ng_1.stop()
                self.infrared_ng_2.stop()
                self.infrared_ng_3.stop()
                self.infrared_ng_4.stop()

                self.ui.label_103.setVisible(False) # 隐藏测试提示框
                self.ui.label_203.setVisible(False)
                self.ui.label_303.setVisible(False)
                self.ui.label_403.setVisible(False)

                self.ui.pushButton_103.setVisible(False) # 隐藏通过失败按钮
                self.ui.pushButton_104.setVisible(False)
                self.ui.pushButton_203.setVisible(False)
                self.ui.pushButton_204.setVisible(False)
                self.ui.pushButton_303.setVisible(False)
                self.ui.pushButton_304.setVisible(False)
                self.ui.pushButton_403.setVisible(False)
                self.ui.pushButton_404.setVisible(False)

                self.ui.lineEdit_101.setEnabled(True) # 输入SN框
                self.ui.lineEdit_201.setEnabled(True)
                self.ui.lineEdit_301.setEnabled(True)
                self.ui.lineEdit_401.setEnabled(True)

                try:
                    self.ui.lineEdit_101.returnPressed.disconnect(self.Test_start)
                    self.ui.lineEdit_201.returnPressed.disconnect(self.Test_start_2)
                    self.ui.lineEdit_301.returnPressed.disconnect(self.Test_start_3)
                    self.ui.lineEdit_401.returnPressed.disconnect(self.Test_start_4)
                except:
                    pass

                self.current_command_index = 0
                self.current_command_index_2 = 0
                self.current_command_index_3 = 0
                self.current_command_index_4 = 0
                self.test_item_id = 0
                self.test_item_id_2 = 0
                self.test_item_id_3 = 0
                self.test_item_id_4 = 0
                self.ui.lineEdit_101.clear() 
                self.ui.lineEdit_201.clear() 
                self.ui.lineEdit_301.clear() 
                self.ui.lineEdit_401.clear() 


                if self.serial_open_flage_1 == True:
                    self.Serial_Qthread_function_1.signal_pushButton_Open.emit(1)
                    self.serial_open_flage_1 = False
                if self.serial_open_flage_2 == True:
                    self.Serial_Qthread_function_2.signal_pushButton_Open.emit(1)
                    self.serial_open_flage_2 = False
                if self.serial_open_flage_3 == True:
                    self.Serial_Qthread_function_3.signal_pushButton_Open.emit(1)
                    self.serial_open_flage_3 = False
                if self.serial_open_flage_4 == True:
                    self.Serial_Qthread_function_4.signal_pushButton_Open.emit(1)
                    self.serial_open_flage_4 = False
                if self.serial_open_flage_slave == True:
                    self.Serial_Qthread_function_slave.signal_pushButton_Open.emit(1)
                    self.serial_open_flage_slave = False
                
                self.connect_auto.stop()
                self.connect_auto_2.stop()
                self.connect_auto_3.stop()
                self.connect_auto_4.stop()
                self.connect_auto_slave.stop()

                self.receive_time_out.stop()
                self.receive_time_out_2.stop()
                self.receive_time_out_3.stop()
                self.receive_time_out_4.stop()
                self.receive_time_out_slave.stop()

                self.infrared.stop()
                self.infrared_2.stop()
                self.infrared_3.stop()
                self.infrared_4.stop()

                self.infrared_emit.stop()
                self.infrared_emit_2.stop()
                self.infrared_emit_3.stop()
                self.infrared_emit_4.stop()

                self.testMode_flage_time_1.stop()
                self.testMode_flage_time_2.stop()
                self.testMode_flage_time_3.stop()
                self.testMode_flage_time_4.stop()

            else:
                # 获取JSON文件
                for key in self.protectid:
                    if key['GROUP_NAME'] == self.ui.comboBox_5_4.currentText():
                        ProcessID = key['CRC_GROUP_CODE']
                        break
                data = {"ProductID":self.itemcode,"ProcessID":ProcessID} 
                response_data = TuyaDataGet(data)
                if response_data == None:
                    QMessageBox.warning(self, '警告', '网络异常') 
                    return
                data = response_data['data']
                if data != '':
                    data = data.lstrip('\ufeff')
                    pattern = r',\s*}'   
                    replacement = "\r\n    }"
                    data = re.sub(pattern, replacement, data)
                    pattern = r',\s*]'   
                    replacement = "\r\n    ]"
                    data = re.sub(pattern, replacement, data)
                    pattern = r'//.*'   
                    replacement = " "
                    data = re.sub(pattern, replacement, data)
                    file_path = "file.json"  
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(data)
                    print('获取json文件成功')

                    with open('file.json', "r", encoding="utf-8-sig") as file:
                        try:
                            data = json.load(file)  # 加载 JSON 数据

                            types_choose = data.get("PlatformName", []) # 获取协议类型
                            if types_choose == []:
                                types_choose = data.get("platformName", [])
                            if types_choose.lower() == "onlytoken":
                                self.test_types = "OnlyToken"
                            elif types_choose.lower() == "remoter":
                                self.test_types = "Remoter"
                            print("协议类型：", self.test_types)

                            test_items = data.get("TestItems", "Not Found")  # 获取 "TestItems" 的内容
                            if test_items == "Not Found":
                                test_items = data.get("testItems")
                            print(test_items)
                            selected = [] # [[Name1,Text1,Paras1],[Name2,Text2,Paras2]...]
                            for item in test_items:
                                selected_alone = []
                                text = item.get("Name", "Not Found")  # 获取 "Name" 的内容
                                if text == "Not Found":
                                    text = item.get("name", "")
                                selected_alone.append(text)

                                text = item.get("Text", "Not Found")  # 获取 "Text" 的内容
                                if text == "Not Found":
                                    text = item.get("text", "")
                                selected_alone.append(text)

                                text = item.get("Paras", "Not Found")  # 获取 "Paras" 的内容
                                if text == "Not Found":
                                    text = item.get("paras", "")
                                selected_alone.append(text)
                                selected.append(selected_alone)
                            self.handle_selected_changed(selected)

                        except :
                            QMessageBox.warning(self, '警告', '无法解析JSON文件')
                            return
                        
                else:
                    print('获取失败')
                    QMessageBox.warning(self,'警告','获取测试项失败')
                    return

                self.ui.groupBox_3.setEnabled(False)
                self.ui.pushButton_1_1.setEnabled(False)
                self.ui.pushButton_1_2.setEnabled(False)
                self.ui.lineEdit_101.setFocus() # 设置焦点在第一个输入框
                self.ui.pushButton_10.setText("停止测试")
                self.ui.pushButton_10.setStyleSheet("background-color: rgb(255, 0, 0);border: none; color: white;")


                # 创建表格数据
                self.channel = int(self.ui.comboBox_7_3.currentText())
                model = QStandardItemModel(self.channel, 1)
                for i in range(self.channel):
                    item = QStandardItem("通道"+str(i+1))
                    model.setItem(i, 0, item)
                self.ui.tableView_12.setModel(model)

                if self.channel == 1:
                    self.ui.groupBox_4.setGeometry(370, 0, 1550, 990)
                    self.ui.groupBox_4.setVisible(True)
                    self.init_table('1')
                    self.show_size = ['100px','60px']
                    self.Serial_QThread_1.start()
                    self.Serial_Qthread_function_1.signal_Serial_qthread_function_Init.emit()
                    self.Serial_QThread_slave.start()
                    self.Serial_Qthread_function_slave.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto.start(2000)
                    self.connect_auto_slave.start(2000)
                    self.ui.label_101.setStyleSheet("QLabel {background-color : gray; color : black; }")
                    self.ui.label_101.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                elif self.channel == 2:
                    self.ui.groupBox_4.setGeometry(370, 0, 775, 990)
                    self.ui.groupBox_5.setGeometry(1145, 0, 775, 990)
                    self.ui.groupBox_4.setVisible(True)
                    self.ui.groupBox_5.setVisible(True)
                    self.ui.lineEdit_101.returnPressed.connect(self.ui.lineEdit_201.setFocus)
                    self.ui.lineEdit_201.returnPressed.connect(self.ui.lineEdit_201.clearFocus)
                    self.init_table('1')
                    self.init_table('2')
                    self.show_size = ['60px','40px']
                    self.Serial_QThread_1.start()
                    self.Serial_Qthread_function_1.signal_Serial_qthread_function_Init.emit()
                    self.Serial_QThread_slave.start()
                    self.Serial_Qthread_function_slave.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto.start(2000)
                    self.connect_auto_slave.start(2000)
                    self.Serial_QThread_2.start()
                    self.Serial_Qthread_function_2.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto_2.start(2000)
                    self.ui.label_101.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_101.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                    self.ui.label_201.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_201.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                elif self.channel == 4:
                    self.ui.groupBox_4.setGeometry(370, 0, 775, 495)
                    self.ui.groupBox_5.setGeometry(1145, 0, 775, 495)
                    self.ui.groupBox_6.setGeometry(370, 495, 775, 495)
                    self.ui.groupBox_7.setGeometry(1145, 495, 775, 495)
                    self.ui.groupBox_4.setVisible(True)
                    self.ui.groupBox_5.setVisible(True)
                    self.ui.groupBox_6.setVisible(True)
                    self.ui.groupBox_7.setVisible(True)
                    self.ui.lineEdit_101.returnPressed.connect(self.ui.lineEdit_201.setFocus)
                    self.ui.lineEdit_201.returnPressed.connect(self.ui.lineEdit_301.setFocus)
                    self.ui.lineEdit_301.returnPressed.connect(self.ui.lineEdit_401.setFocus)
                    self.ui.lineEdit_401.returnPressed.connect(self.ui.lineEdit_401.clearFocus)
                    self.init_table('1')
                    self.init_table('2')
                    self.init_table('3')
                    self.init_table('4')
                    self.show_size = ['60px','40px']
                    self.Serial_QThread_1.start()
                    self.Serial_Qthread_function_1.signal_Serial_qthread_function_Init.emit()
                    self.Serial_QThread_slave.start()
                    self.Serial_Qthread_function_slave.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto.start(2000)
                    self.connect_auto_slave.start(2000)
                    self.Serial_QThread_2.start()
                    self.Serial_Qthread_function_2.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto_2.start(2000)
                    self.Serial_QThread_3.start()
                    self.Serial_Qthread_function_3.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto_3.start(2000)
                    self.Serial_QThread_4.start()
                    self.Serial_Qthread_function_4.signal_Serial_qthread_function_Init.emit()
                    self.connect_auto_4.start(2000)
                    self.ui.label_101.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_101.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                    self.ui.label_201.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_201.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                    self.ui.label_301.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_301.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                    self.ui.label_401.setStyleSheet("QLabel { background-color : gray; color : black; }")
                    self.ui.label_401.setText(f"<p style='font-size:{self.show_size[0]}'>{self.items_text[0]}</p><p style='font-size:{self.show_size[1]}'>等待测试</p>")
                
            self.startTest_2 = not self.startTest_2 # 改变测试状态

    def keyPressEvent(self, event): # 快捷键
        if event.key() == Qt.Key_Space:
            if  self.ui.pushButton_103.isVisible():
                 self.ui.pushButton_103.click()
            if  self.ui.pushButton_203.isVisible():
                 self.ui.pushButton_203.click()
            if  self.ui.pushButton_303.isVisible():
                 self.ui.pushButton_303.click()
            if  self.ui.pushButton_403.isVisible():
                 self.ui.pushButton_403.click()            
    
    def closeEvent(self, event): # 关闭窗口
        print("安防窗体关闭")
        self.Serial_QThread_1.quit() #回收线程
        self.Serial_QThread_1.wait()
        del self.Serial_QThread_1
        self.Serial_QThread_2.quit() #回收线程
        self.Serial_QThread_2.wait()
        del self.Serial_QThread_2
        self.Serial_QThread_3.quit() #回收线程
        self.Serial_QThread_3.wait()
        del self.Serial_QThread_3
        self.Serial_QThread_4.quit() #回收线程
        self.Serial_QThread_4.wait()
        del self.Serial_QThread_4

        self.connect_auto.stop()
        self.connect_auto_2.stop()
        self.connect_auto_3.stop()
        self.connect_auto_4.stop()
        self.connect_auto_slave.stop()

        self.receive_time_out.stop()
        self.receive_time_out_2.stop()
        self.receive_time_out_3.stop()
        self.receive_time_out_4.stop()
        self.receive_time_out_slave.stop()

        self.infrared.stop()
        self.infrared_2.stop()
        self.infrared_3.stop()
        self.infrared_4.stop()

        self.infrared_emit.stop()
        self.infrared_emit_2.stop()
        self.infrared_emit_3.stop()
        self.infrared_emit_4.stop()

        self.testMode_flage_time_1.stop()
        self.testMode_flage_time_2.stop()
        self.testMode_flage_time_3.stop()
        self.testMode_flage_time_4.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Security_Form()
    window.show()
    window.showMaximized()
    sys.exit(app.exec_())