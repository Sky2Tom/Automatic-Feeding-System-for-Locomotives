# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'train_control.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Traincontrol(object):
    def setupUi(self, Traincontrol):
        Traincontrol.setObjectName("Traincontrol")
        Traincontrol.resize(1690, 1250)
        self.centralwidget = QtWidgets.QWidget(Traincontrol)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.frame_window = QtWidgets.QFrame(self.centralwidget)
        self.frame_window.setMaximumSize(QtCore.QSize(250, 16777215))
        self.frame_window.setStyleSheet("QFrame{\n"
"    background-color:rgb(206, 206, 206);\n"
"}")
        self.frame_window.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_window.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_window.setObjectName("frame_window")
        self.pushButton = QtWidgets.QPushButton(self.frame_window)
        self.pushButton.setGeometry(QtCore.QRect(60, 1180, 112, 34))
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("QPushButton{\n"
"background-color:rgb(255, 135, 163)\n"
"}")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_5 = QtWidgets.QPushButton(self.frame_window)
        self.pushButton_5.setGeometry(QtCore.QRect(20, 760, 201, 91))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_5.setFont(font)
        self.pushButton_5.setStyleSheet("QPushButton{\n"
"background-color:rgb(243, 255, 189)\n"
"}")
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(self.frame_window)
        self.pushButton_6.setGeometry(QtCore.QRect(20, 610, 201, 91))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_6.setFont(font)
        self.pushButton_6.setStyleSheet("QPushButton{\n"
"background-color:rgb(243, 255, 189)\n"
"}")
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_7 = QtWidgets.QPushButton(self.frame_window)
        self.pushButton_7.setGeometry(QtCore.QRect(20, 460, 201, 91))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_7.setFont(font)
        self.pushButton_7.setStyleSheet("QPushButton{\n"
"background-color:rgb(243, 255, 189)\n"
"}")
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_8 = QtWidgets.QPushButton(self.frame_window)
        self.pushButton_8.setGeometry(QtCore.QRect(20, 300, 201, 91))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.pushButton_8.setFont(font)
        self.pushButton_8.setStyleSheet("QPushButton{\n"
"background-color:rgb(243, 255, 189)\n"
"}")
        self.pushButton_8.setObjectName("pushButton_8")
        self.horizontalLayout.addWidget(self.frame_window)
        self.frame_menu = QtWidgets.QFrame(self.centralwidget)
        self.frame_menu.setStyleSheet("QFrame{\n"
"    background-color:rgb(255, 255, 255)\n"
"}")
        self.frame_menu.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_menu.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_menu.setObjectName("frame_menu")
        self.frame_menu_2 = QtWidgets.QFrame(self.frame_menu)
        self.frame_menu_2.setGeometry(QtCore.QRect(0, 0, 1440, 1250))
        self.frame_menu_2.setStyleSheet("QFrame{\n"
"    background-color:rgb(225, 255, 253)\n"
"}")
        self.frame_menu_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_menu_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_menu_2.setObjectName("frame_menu_2")
        self.System_name_2 = QtWidgets.QLabel(self.frame_menu_2)
        self.System_name_2.setGeometry(QtCore.QRect(310, 10, 721, 81))
        font = QtGui.QFont()
        font.setPointSize(19)
        font.setBold(True)
        font.setWeight(75)
        self.System_name_2.setFont(font)
        self.System_name_2.setTextFormat(QtCore.Qt.AutoText)
        self.System_name_2.setAlignment(QtCore.Qt.AlignCenter)
        self.System_name_2.setObjectName("System_name_2")
        self.label = QtWidgets.QLabel(self.frame_menu_2)
        self.label.setGeometry(QtCore.QRect(140, 160, 201, 441))
        self.label.setStyleSheet("border-image:url(:/machine/下煤机.jpg)")
        self.label.setText("")
        self.label.setObjectName("label")
        self.frame = QtWidgets.QFrame(self.frame_menu_2)
        self.frame.setGeometry(QtCore.QRect(450, 150, 861, 461))
        self.frame.setStyleSheet("QFrame{\n"
"    background-color:rgb(225, 225, 225)\n"
"}")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label_wh_2 = QtWidgets.QLabel(self.frame)
        self.label_wh_2.setGeometry(QtCore.QRect(70, 140, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_2.setFont(font)
        self.label_wh_2.setObjectName("label_wh_2")
        self.label_wh_3 = QtWidgets.QLabel(self.frame)
        self.label_wh_3.setGeometry(QtCore.QRect(70, 230, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_3.setFont(font)
        self.label_wh_3.setObjectName("label_wh_3")
        self.label_wh_4 = QtWidgets.QLabel(self.frame)
        self.label_wh_4.setGeometry(QtCore.QRect(70, 320, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_4.setFont(font)
        self.label_wh_4.setObjectName("label_wh_4")
        self.label_wh_6 = QtWidgets.QLabel(self.frame)
        self.label_wh_6.setGeometry(QtCore.QRect(480, 50, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_6.setFont(font)
        self.label_wh_6.setObjectName("label_wh_6")
        self.label_wh_7 = QtWidgets.QLabel(self.frame)
        self.label_wh_7.setGeometry(QtCore.QRect(480, 170, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_7.setFont(font)
        self.label_wh_7.setObjectName("label_wh_7")
        self.label_wh_5 = QtWidgets.QLabel(self.frame)
        self.label_wh_5.setGeometry(QtCore.QRect(480, 290, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_5.setFont(font)
        self.label_wh_5.setObjectName("label_wh_5")
        self.label_wh_8 = QtWidgets.QLabel(self.frame)
        self.label_wh_8.setGeometry(QtCore.QRect(60, 50, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_8.setFont(font)
        self.label_wh_8.setObjectName("label_wh_8")
        self.textBrowser_chk_2 = QtWidgets.QTextBrowser(self.frame)
        self.textBrowser_chk_2.setGeometry(QtCore.QRect(220, 60, 160, 50))
        self.textBrowser_chk_2.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_2.setObjectName("textBrowser_chk_2")
        self.textBrowser_chk_3 = QtWidgets.QTextBrowser(self.frame)
        self.textBrowser_chk_3.setGeometry(QtCore.QRect(220, 160, 160, 50))
        self.textBrowser_chk_3.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_3.setObjectName("textBrowser_chk_3")
        self.textBrowser_chk_4 = QtWidgets.QTextBrowser(self.frame)
        self.textBrowser_chk_4.setGeometry(QtCore.QRect(220, 250, 160, 50))
        self.textBrowser_chk_4.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_4.setObjectName("textBrowser_chk_4")
        self.textBrowser_chk_5 = QtWidgets.QTextBrowser(self.frame)
        self.textBrowser_chk_5.setGeometry(QtCore.QRect(220, 340, 160, 50))
        self.textBrowser_chk_5.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_5.setObjectName("textBrowser_chk_5")
        self.textBrowser_chk_6 = QtWidgets.QTextBrowser(self.frame)
        self.textBrowser_chk_6.setGeometry(QtCore.QRect(610, 310, 160, 50))
        self.textBrowser_chk_6.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_6.setObjectName("textBrowser_chk_6")
        self.textBrowser_chk_7 = QtWidgets.QTextBrowser(self.frame)
        self.textBrowser_chk_7.setGeometry(QtCore.QRect(610, 190, 160, 50))
        self.textBrowser_chk_7.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_7.setObjectName("textBrowser_chk_7")
        self.textBrowser_chk_8 = QtWidgets.QTextBrowser(self.frame)
        self.textBrowser_chk_8.setGeometry(QtCore.QRect(610, 70, 160, 50))
        self.textBrowser_chk_8.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_8.setObjectName("textBrowser_chk_8")
        self.pushButton_3 = QtWidgets.QPushButton(self.frame_menu_2)
        self.pushButton_3.setGeometry(QtCore.QRect(650, 770, 161, 51))
        self.pushButton_3.setStyleSheet("QpushButton{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.pushButton_3.setObjectName("pushButton_3")
        self.spinBox = QtWidgets.QSpinBox(self.frame_menu_2)
        self.spinBox.setGeometry(QtCore.QRect(1130, 770, 161, 51))
        self.spinBox.setStyleSheet("QspinBox{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.spinBox.setObjectName("spinBox")
        self.label_wh_9 = QtWidgets.QLabel(self.frame_menu_2)
        self.label_wh_9.setGeometry(QtCore.QRect(480, 680, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_9.setFont(font)
        self.label_wh_9.setObjectName("label_wh_9")
        self.textBrowser_chk_9 = QtWidgets.QTextBrowser(self.frame_menu_2)
        self.textBrowser_chk_9.setGeometry(QtCore.QRect(640, 690, 160, 50))
        self.textBrowser_chk_9.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_9.setObjectName("textBrowser_chk_9")
        self.textBrowser_chk_10 = QtWidgets.QTextBrowser(self.frame_menu_2)
        self.textBrowser_chk_10.setGeometry(QtCore.QRect(1130, 690, 160, 50))
        self.textBrowser_chk_10.viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.textBrowser_chk_10.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_10.setObjectName("textBrowser_chk_10")
        self.label_wh_10 = QtWidgets.QLabel(self.frame_menu_2)
        self.label_wh_10.setGeometry(QtCore.QRect(980, 670, 131, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_10.setFont(font)
        self.label_wh_10.setObjectName("label_wh_10")
        self.label_wh_11 = QtWidgets.QLabel(self.frame_menu_2)
        self.label_wh_11.setGeometry(QtCore.QRect(480, 880, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_11.setFont(font)
        self.label_wh_11.setObjectName("label_wh_11")
        self.textBrowser_chk_11 = QtWidgets.QTextBrowser(self.frame_menu_2)
        self.textBrowser_chk_11.setGeometry(QtCore.QRect(630, 900, 160, 50))
        self.textBrowser_chk_11.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_11.setObjectName("textBrowser_chk_11")
        self.label_wh_12 = QtWidgets.QLabel(self.frame_menu_2)
        self.label_wh_12.setGeometry(QtCore.QRect(990, 880, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_wh_12.setFont(font)
        self.label_wh_12.setObjectName("label_wh_12")
        self.textBrowser_chk_12 = QtWidgets.QTextBrowser(self.frame_menu_2)
        self.textBrowser_chk_12.setGeometry(QtCore.QRect(1140, 900, 160, 50))
        self.textBrowser_chk_12.setStyleSheet("QTextBrowser{\n"
"background-color:rgb(217, 255, 187)\n"
"}")
        self.textBrowser_chk_12.setObjectName("textBrowser_chk_12")
        self.spinBox_2 = QtWidgets.QSpinBox(self.frame_menu_2)
        self.spinBox_2.setGeometry(QtCore.QRect(640, 980, 161, 51))
        self.spinBox_2.setObjectName("spinBox_2")
        self.spinBox_3 = QtWidgets.QSpinBox(self.frame_menu_2)
        self.spinBox_3.setGeometry(QtCore.QRect(1140, 980, 161, 51))
        self.spinBox_3.setObjectName("spinBox_3")
        self.horizontalLayout.addWidget(self.frame_menu)
        Traincontrol.setCentralWidget(self.centralwidget)

        self.retranslateUi(Traincontrol)
        QtCore.QMetaObject.connectSlotsByName(Traincontrol)

    def retranslateUi(self, Traincontrol):
        _translate = QtCore.QCoreApplication.translate
        Traincontrol.setWindowTitle(_translate("Traincontrol", "Traincontrol"))
        self.pushButton.setText(_translate("Traincontrol", "退出"))
        self.pushButton_5.setText(_translate("Traincontrol", "火车视觉识别"))
        self.pushButton_6.setText(_translate("Traincontrol", "下料机控制"))
        self.pushButton_7.setText(_translate("Traincontrol", "下料历史查询"))
        self.pushButton_8.setText(_translate("Traincontrol", "火车型号尺寸"))
        self.System_name_2.setText(_translate("Traincontrol", "下料机控制主系统"))
        self.label_wh_2.setText(_translate("Traincontrol", "阀门开度"))
        self.label_wh_3.setText(_translate("Traincontrol", "升降高度"))
        self.label_wh_4.setText(_translate("Traincontrol", "翻板高度"))
        self.label_wh_6.setText(_translate("Traincontrol", "是否装满"))
        self.label_wh_7.setText(_translate("Traincontrol", "装料进度"))
        self.label_wh_5.setText(_translate("Traincontrol", "料面高度"))
        self.label_wh_8.setText(_translate("Traincontrol", "下煤机状态"))
        self.textBrowser_chk_2.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">正常</span></p></body></html>"))
        self.textBrowser_chk_3.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">30度</span></p></body></html>"))
        self.textBrowser_chk_4.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">20cm</span></p></body></html>"))
        self.textBrowser_chk_5.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">10cm</span></p></body></html>"))
        self.textBrowser_chk_6.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">2.7米</span></p></body></html>"))
        self.textBrowser_chk_7.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">40%</span></p></body></html>"))
        self.textBrowser_chk_8.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">否</span></p></body></html>"))
        self.pushButton_3.setText(_translate("Traincontrol", "PushButton"))
        self.label_wh_9.setText(_translate("Traincontrol", "下煤机状态"))
        self.textBrowser_chk_9.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">正常</span></p></body></html>"))
        self.textBrowser_chk_10.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">30度</span></p></body></html>"))
        self.label_wh_10.setText(_translate("Traincontrol", "阀门开度"))
        self.label_wh_11.setText(_translate("Traincontrol", "升降高度"))
        self.textBrowser_chk_11.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">20cm</span></p></body></html>"))
        self.label_wh_12.setText(_translate("Traincontrol", "翻板高度"))
        self.textBrowser_chk_12.setHtml(_translate("Traincontrol", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt;\">10cm</span></p></body></html>"))

import pictures_rc
