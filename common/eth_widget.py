# <install SIMPL on arm or x86.>
# Copyright (C) <2024> <seyond>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets


class EthWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        layout = QtWidgets.QHBoxLayout(self)

        self.enLabel = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.enLabel.setFont(font)
        self.enLabel.setObjectName("enLabel")
        self.enLabel.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.enLabel.setFixedHeight(36)
        self.enLabel.setFixedWidth(180)

        self.enIP = QtWidgets.QLineEdit(self)
        self.enIP.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.enIP.setFont(font)
        self.enIP.setObjectName("enIP")
        self.enIP.setStyleSheet(
            "border:1px solid #c4c4c4;border-radius: 5px;background-color:white;color:black;")
        self.enIP.setFixedHeight(36)
        self.enIP.setFixedWidth(412)

        self.enSelect = QtWidgets.QPushButton(self)
        self.enSelect.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.enSelect.setObjectName("enSelect")
        self.enSelect.setStyleSheet(
            "border:1px solid #c4c4c4;border-radius: 5px;background-color:white;color:white;")
        self.enSelect.setFlat(False)
        self.enSelect.setFixedHeight(36)
        self.enSelect.setFixedWidth(36)

        layout.addWidget(self.enLabel)
        layout.addWidget(self.enIP)
        layout.addWidget(self.enSelect)

        self.enLabel.setText("Ethernet(eth0) :")
