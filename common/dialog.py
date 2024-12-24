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

""" Some common dialogs"""

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSignal

from ui.passwd_dialog import Ui_Dialog as PW_Dialog_UI
from ui.cuda_dialog import Ui_Dialog as CUDA_Dialog_UI
from .function import (
    show_error_msg,
    show_normal_msg,
    CommandTask,
)
import sys


class PasswdDialog(QDialog, PW_Dialog_UI):
    """Get and store current user password"""
    password_value = pyqtSignal(str)

    def __init__(self, q_app):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(800, 450)
        self.setStyleSheet("background-color: white;")
        self.setWindowIconText("Password Confirm")
        self.setWindowTitle("Password Dialog")
        for button in self.confirmBox.buttons():
            button.setFixedSize(120, 40)  # 修改按钮的宽度和高度

        self.check_job = CommandTask()
        self.check_job.set_command(["sudo", "-S", "-k", "uname", "-m"])
        self.check_job.need_input = True
        self.check_job.output_txt.connect(self.check_callback)
        self.q_app = q_app

        self.init()

    def init(self):
        """Self-explanatory"""
        self.confirmBox.accepted.disconnect()
        self.confirmBox.accepted.connect(self.check_pw)
        self.confirmBox.rejected.connect(self.close)
        self.password.setFocus()

    def check_pw(self):
        """ Self-explanatory"""
        pw = self.password.text()
        show_normal_msg(self.infoLabel, "checking ...")
        if pw == "":
            show_error_msg(self.infoLabel, "Password cannot be empty")
        else:
            self.check_job.input_msg = pw
            self.check_job.start()

    def check_callback(self, output):
        """Self"""
        if output == "" or "sudo" in output:
            show_error_msg(self.infoLabel, "Incorrect password")
        else:
            self.password_value.emit(self.password.text())
            self.accept()

    def accept(self) -> None:
        """Done nothing when click confirmBox"""
        return super().accept()

    def reject(self) -> None:
        """ Quit app when reject input password"""
        # self.q_app.quit()
        sys.exit()

    def close(self) -> bool:
        return super().close()


class CudaDialog(QDialog, CUDA_Dialog_UI):
    """Show cuda check result"""
    password_value = pyqtSignal(str)

    def __init__(self, q_app):
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(800, 450)
        self.setStyleSheet("background-color: white;")
        self.setWindowIconText("Confirmation")
        self.setWindowTitle("Confirmation Dialog")

        self.check_job = CommandTask()
        self.check_job.set_command(["nvidia-smi"])
        self.check_job.output_txt.connect(self.check_callback)
        self.q_app = q_app

        self.init()

    def init(self):
        """Self-explanatory"""
        self.confirmBox.accepted.disconnect()
        self.confirmBox.accepted.connect(self.q_app.quit)
        self.confirmBox.rejected.connect(self.q_app.quit)

    def check_callback(self, output):
        """Self"""
        # show details
        print(output)

    def accept(self) -> None:
        """Done nothing when click confirmBox"""
        return super().accept()

    def reject(self) -> None:
        """ Quit app when reject input password"""
        self.q_app.quit()

    def close(self) -> bool:
        return super().close()
