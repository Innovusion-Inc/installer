# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/uninstaller_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from common.const import (
    PRODUCT_NAME
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 500)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 800, 500))
        self.stackedWidget.setObjectName("stackedWidget")
        self.msgPage = QtWidgets.QWidget()
        self.msgPage.setObjectName("msgPage")
        self.logoPic = QtWidgets.QLabel(self.msgPage)
        self.logoPic.setGeometry(QtCore.QRect(342, 50, 100, 70))
        self.logoPic.setText("")
        self.logoPic.setAlignment(QtCore.Qt.AlignCenter)
        self.logoPic.setObjectName("logoPic")
        self.label = QtWidgets.QLabel(self.msgPage)
        self.label.setGeometry(QtCore.QRect(230, 170, 321, 42))
        font = QtGui.QFont()
        font.setPointSize(17)
        self.label.setFont(font)
        self.label.setStyleSheet("color:#E24183;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.delMsg = QtWidgets.QLabel(self.msgPage)
        self.delMsg.setGeometry(QtCore.QRect(20, 250, 741, 64))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.delMsg.setFont(font)
        self.delMsg.setStyleSheet("")
        self.delMsg.setLineWidth(1)
        self.delMsg.setMidLineWidth(0)
        self.delMsg.setScaledContents(False)
        self.delMsg.setAlignment(QtCore.Qt.AlignCenter)
        self.delMsg.setWordWrap(True)
        self.delMsg.setObjectName("delMsg")
        self.okBtn = QtWidgets.QPushButton(self.msgPage)
        self.okBtn.setEnabled(True)
        self.okBtn.setGeometry(QtCore.QRect(640, 410, 120, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.okBtn.setFont(font)
        self.okBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.okBtn.setStyleSheet(
            "border:1px solid #c4c4c4;border-radius: 5px;background-color:white;")
        self.okBtn.setObjectName("okBtn")
        self.cancelBtn = QtWidgets.QPushButton(self.msgPage)
        self.cancelBtn.setEnabled(True)
        self.cancelBtn.setGeometry(QtCore.QRect(510, 410, 120, 40))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.cancelBtn.setFont(font)
        self.cancelBtn.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.cancelBtn.setStyleSheet(
            "border:1px solid #c4c4c4;border-radius: 5px;background-color:white;")
        self.cancelBtn.setObjectName("cancelBtn")
        self.cancelPic = QtWidgets.QLabel(self.msgPage)
        self.cancelPic.setGeometry(QtCore.QRect(600, 423, 16, 16))
        self.cancelPic.setText("")
        self.cancelPic.setObjectName("cancelPic")
        self.okPic = QtWidgets.QLabel(self.msgPage)
        self.okPic.setGeometry(QtCore.QRect(725, 423, 16, 16))
        self.okPic.setText("")
        self.okPic.setObjectName("okPic")
        self.preserveLabel = QtWidgets.QLabel(self.msgPage)
        self.preserveLabel.setGeometry(QtCore.QRect(80, 338, 361, 27))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.preserveLabel.setFont(font)
        self.preserveLabel.setObjectName("preserveLabel")
        self.preserveSel = QtWidgets.QPushButton(self.msgPage)
        self.preserveSel.setGeometry(QtCore.QRect(36, 340, 24, 24))
        self.preserveSel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.preserveSel.setStyleSheet(
            "border:1px solid #c4c4c4;border-radius: 5px;background-color:white;color:white;")
        self.preserveSel.setText("")
        self.preserveSel.setFlat(False)
        self.preserveSel.setObjectName("preserveSel")
        self.stackedWidget.addWidget(self.msgPage)
        self.progressPage = QtWidgets.QWidget()
        self.progressPage.setObjectName("progressPage")
        self.miniLogoPic = QtWidgets.QLabel(self.progressPage)
        self.miniLogoPic.setGeometry(QtCore.QRect(340, 30, 132, 20))
        self.miniLogoPic.setText("")
        self.miniLogoPic.setAlignment(QtCore.Qt.AlignCenter)
        self.miniLogoPic.setObjectName("miniLogoPic")
        self.label2 = QtWidgets.QLabel(self.progressPage)
        self.label2.setGeometry(QtCore.QRect(48, 70, 704, 32))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label2.setFont(font)
        self.label2.setAlignment(QtCore.Qt.AlignCenter)
        self.label2.setObjectName("label2")
        self.bgPic = QtWidgets.QLabel(self.progressPage)
        self.bgPic.setGeometry(QtCore.QRect(32, 128, 736, 241))
        self.bgPic.setText("")
        self.bgPic.setWordWrap(True)
        self.bgPic.setObjectName("bgPic")
        self.progressBar = QtWidgets.QProgressBar(self.progressPage)
        self.progressBar.setGeometry(QtCore.QRect(32, 410, 736, 12))
        self.progressBar.setProperty("value", 40)
        self.progressBar.setTextVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Horizontal)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressBar.setObjectName("progressBar")
        self.statusMsg = QtWidgets.QLabel(self.progressPage)
        self.statusMsg.setGeometry(QtCore.QRect(30, 440, 361, 29))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.statusMsg.sizePolicy().hasHeightForWidth())
        self.statusMsg.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.statusMsg.setFont(font)
        self.statusMsg.setObjectName("statusMsg")
        self.processBarNum = QtWidgets.QLabel(self.progressPage)
        self.processBarNum.setEnabled(True)
        self.processBarNum.setGeometry(QtCore.QRect(700, 440, 71, 29))
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.processBarNum.sizePolicy().hasHeightForWidth())
        self.processBarNum.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.processBarNum.setFont(font)
        self.processBarNum.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.processBarNum.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.processBarNum.setObjectName("processBarNum")
        self.white_cover_left = QtWidgets.QLabel(self.progressPage)
        self.white_cover_left.setGeometry(QtCore.QRect(0, 128, 32, 241))
        self.white_cover_left.setStyleSheet("")
        self.white_cover_left.setText("")
        self.white_cover_left.setObjectName("white_cover_left")
        self.white_cover_right = QtWidgets.QLabel(self.progressPage)
        self.white_cover_right.setGeometry(QtCore.QRect(768, 128, 736, 241))
        self.white_cover_right.setText("")
        self.white_cover_right.setObjectName("white_cover_right")
        self.stackedWidget.addWidget(self.progressPage)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Uninstall "+PRODUCT_NAME))
        self.delMsg.setText(_translate(
            "MainWindow", "The software will be removed from this device and cannot be undone"))
        self.okBtn.setText(_translate("MainWindow", "OK"))
        self.cancelBtn.setText(_translate("MainWindow", "Cancel     "))
        self.preserveLabel.setText(_translate(
            "MainWindow", "Preserve historical data"))
        self.label2.setText(_translate(
            "MainWindow", "Thank you for your support. We hope you return soon. "))
        self.statusMsg.setText(_translate("MainWindow", "Uninstalling"))
        self.processBarNum.setText(_translate("MainWindow", "0%"))
