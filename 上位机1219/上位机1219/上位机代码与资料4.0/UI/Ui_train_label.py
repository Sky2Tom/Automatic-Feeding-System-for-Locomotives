# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'train_label.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Trainlabel(object):
    def setupUi(self, Trainlabel):
        Trainlabel.setObjectName("Trainlabel")
        Trainlabel.resize(1690, 1250)
        self.centralwidget = QtWidgets.QWidget(Trainlabel)
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
"    background-color:rgb(225, 255, 253)\n"
"}")
        self.frame_menu.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_menu.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_menu.setObjectName("frame_menu")
        self.System_name = QtWidgets.QLabel(self.frame_menu)
        self.System_name.setGeometry(QtCore.QRect(310, 10, 721, 81))
        font = QtGui.QFont()
        font.setPointSize(19)
        font.setBold(True)
        font.setWeight(75)
        self.System_name.setFont(font)
        self.System_name.setTextFormat(QtCore.Qt.AutoText)
        self.System_name.setAlignment(QtCore.Qt.AlignCenter)
        self.System_name.setObjectName("System_name")
        self.train_picture = QtWidgets.QGraphicsView(self.frame_menu)
        self.train_picture.setGeometry(QtCore.QRect(150, 160, 1051, 621))
        self.train_picture.setStyleSheet("QGraphicsView{\n"
" background-color:rgb(255, 242, 208)\n"
"}")
        self.train_picture.setObjectName("train_picture")
        self.textEdit = QtWidgets.QTextEdit(self.frame_menu)
        self.textEdit.setGeometry(QtCore.QRect(610, 880, 251, 41))
        self.textEdit.setStyleSheet("QTextEdit{\n"
"    background-color:rgb(255, 240, 226)\n"
"}")
        self.textEdit.setObjectName("textEdit")
        self.label_train = QtWidgets.QLabel(self.frame_menu)
        self.label_train.setGeometry(QtCore.QRect(450, 860, 200, 80))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_train.setFont(font)
        self.label_train.setObjectName("label_train")
        self.horizontalLayout.addWidget(self.frame_menu)
        Trainlabel.setCentralWidget(self.centralwidget)

        self.retranslateUi(Trainlabel)
        QtCore.QMetaObject.connectSlotsByName(Trainlabel)

    def retranslateUi(self, Trainlabel):
        _translate = QtCore.QCoreApplication.translate
        Trainlabel.setWindowTitle(_translate("Trainlabel", "MainWindow"))
        self.pushButton.setText(_translate("Trainlabel", "退出"))
        self.pushButton_5.setText(_translate("Trainlabel", "火车视觉识别"))
        self.pushButton_6.setText(_translate("Trainlabel", "下料机控制"))
        self.pushButton_7.setText(_translate("Trainlabel", "下料历史查询"))
        self.pushButton_8.setText(_translate("Trainlabel", "火车型号尺寸"))
        self.System_name.setText(_translate("Trainlabel", "火车视觉识别主系统"))
        self.label_train.setText(_translate("Trainlabel", "火车车厢号"))

