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

""" Main app"""

import sys
import os
import argparse
import subprocess
import getpass

# pylint:disable=import-error,no-name-in-module
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QDesktopWidget,
    QLabel,
    qApp,)

from PyQt5.QtCore import (
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    QPoint,)

from PyQt5.QtGui import (
    QPixmap,
    QIcon,
    QFontDatabase,
    QFont,
)

from ui.uninstaller_ui import Ui_MainWindow
from handler.uninstall_handle import CityUninstall
from common.const import (
    END_HEAD,
    UNINSTALL_ALERT_MSG,
    PLEASE_ENTER_PASSWORD,
    ERROR_PASSWORD,
    UNINSTALL_WINDOW_TEXT,
    UNINSTALL_FAILED,
    UNINSTALL_SUCCESS,
    UNINSTALL_NO_NEED,
)
from common.function import (
    show_error_msg,
    show_normal_msg,
    find_od,
    find_web,
    clone_label,
)
from common.dialog import PasswdDialog
import common.version as installer_version

if getattr(sys, 'frozen', False):
    # 如果是 PyInstaller 打包的程序
    BASE_DIR = os.path.dirname(sys.executable) + "/"
else:
    BASE_DIR = os.path.dirname(__file__) + "/smart_city/"

PIC_DIR = f"{os.path.dirname(__file__)}/ui/imgs/"
WINDOW_ICON_PATH = PIC_DIR + "window_icon.png"
LOGO_PATH = PIC_DIR + "pic_logo.png"
LOGO_TEXT_PATH = PIC_DIR + "pic_logo_text.png"
BG1_PIC_PATH = PIC_DIR + "pic_bg1.png"
BG2_PIC_PATH = PIC_DIR + "pic_bg2.png"
BG3_PIC_PATH = PIC_DIR + "pic_bg3.png"
BG4_PIC_PATH = PIC_DIR + "pic_bg4.png"
BTN_CANCEL = PIC_DIR + "cancel_pic.png"
BTN_OK = PIC_DIR + "ok_pic.png"
SELECTED_ICON_PATH = PIC_DIR + "selected.png"

FONT_FILE = f"{os.path.dirname(__file__)}/ui/font/Exo-Medium.ttf"


class MainWindow(QMainWindow, Ui_MainWindow):
    """Self-explanatory"""

    def __init__(self):
        """Self-explanatory"""
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Uninstaller")
        self.setFixedSize(800, 500)
        self.set_icons()
        self.stackedWidget.setCurrentIndex(0)

        self.city_uninstall = CityUninstall()
        self.city_uninstall.basedir = BASE_DIR
        self.pw_dialog = PasswdDialog(qApp)
        self.pw_dialog.logoPic.setPixmap(QPixmap(LOGO_PATH))
        self.pw_dialog.logoPic.setScaledContents(True)
        self.pw_dialog.setWindowIcon(QIcon(WINDOW_ICON_PATH))
        self.pw_dialog.setWindowIconText(UNINSTALL_WINDOW_TEXT)

        self.move_to_center()

        self.user_pw = ""
        self.has_od = False
        self.has_web = False

        self.init_step_page()

        self.check_installed()

    def __on_preserve_select(self):
        """callback when preserve select
        """
        is_selected = self.sender().property("selected")
        if is_selected:
            self.sender().setIcon(QIcon())
            self.sender().setProperty("selected", False)
        else:
            self.sender().setIcon(QIcon(SELECTED_ICON_PATH))
            self.sender().setProperty("selected", True)

    def set_icons(self):
        """set icons
        """
        self.logoPic.setPixmap(QPixmap(LOGO_PATH))
        self.logoPic.setScaledContents(True)
        self.miniLogoPic.setPixmap(QPixmap(LOGO_TEXT_PATH))
        self.miniLogoPic.setScaledContents(True)
        self.cancelPic.setPixmap(QPixmap(BTN_CANCEL))
        self.okPic.setPixmap(QPixmap(BTN_OK))

        self.preserveSel.setIcon(QIcon(SELECTED_ICON_PATH))
        self.preserveSel.setIconSize(self.preserveSel.size())
        self.preserveSel.setProperty("selected", True)
        self.preserveSel.clicked.connect(self.__on_preserve_select)

        # 设置轮播的图片
        self.pixmaps = [BG1_PIC_PATH, BG2_PIC_PATH, BG3_PIC_PATH, BG4_PIC_PATH]
        self.pixmap_labels = [clone_label(
            self.bgPic), clone_label(self.bgPic)]
        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_background)
        self.timer.start(5000)  # 切换频率（毫秒）

        # 创建动画效果
        self.pixmap_labels[1].setGeometry(
            self.bgPic.geometry().x()+self.bgPic.width(),
            self.bgPic.geometry().y(),
            self.bgPic.width(),
            self.bgPic.height()
        )

        self.pic_animation = QPropertyAnimation(self.pixmap_labels[0], b'pos')
        self.pic_animation.setDuration(2000)  # 动画持续时间（毫秒）

        self.pic_animation2 = QPropertyAnimation(self.pixmap_labels[1], b'pos')
        self.pic_animation2.setDuration(2000)  # 动画持续时间（毫秒）

        # add two white cover
        self.white_cover_left: QLabel = clone_label(self.bgPic)
        self.white_cover_left.setGeometry(0, self.bgPic.geometry().y(),
                                          self.bgPic.geometry().x(), self.bgPic.height())

        self.white_cover_right: QLabel = clone_label(self.bgPic)
        self.white_cover_right.setGeometry(self.bgPic.geometry().x()+self.bgPic.width(),
                                           self.bgPic.geometry().y(), self.bgPic.width(), self.bgPic.height())

        self.update_background()

    def update_background(self):
        """update background pic
        """
        self.pixmap_labels[0].setPixmap(QPixmap(self.pixmaps[0]))
        self.pixmap_labels[1].setPixmap(QPixmap(self.pixmaps[1]))

        # 触发平移动画
        self.pic_animation.setStartValue(self.bgPic.pos())
        self.pic_animation.setEndValue(
            QPoint(self.bgPic.pos().x() - self.bgPic.width(), self.bgPic.pos().y()))
        self.pic_animation.setEasingCurve(QEasingCurve.InOutQuad)  # 设置动画缓动曲线
        self.pic_animation.start()

        self.pic_animation2.setStartValue(
            QPoint(self.bgPic.geometry().x()+self.bgPic.width(), self.bgPic.y()))
        self.pic_animation2.setEndValue(self.bgPic.pos())
        self.pic_animation2.setEasingCurve(QEasingCurve.InOutQuad)  # 设置动画缓动曲线
        self.pic_animation2.start()

        # 循环切换图片
        self.pixmaps.append(self.pixmaps.pop(0))

    def move_to_center(self):
        """Self-explanatory"""
        qt_rect = self.frameGeometry()
        c_point = QDesktopWidget().availableGeometry().center()
        qt_rect.moveCenter(c_point)
        self.move(qt_rect.topLeft())

    def init_step_page(self):
        """Bind function to component on pages"""

        self.okBtn.clicked.connect(self.start_uninstall)
        self.cancelBtn.clicked.connect(self.close)
        # set style sheet
        self.progressBar.setValue(0)
        self.processBarNum.setText("0%")
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: 0px solid grey;
                border-radius: 5px;
                text-align: center;
                background-color: #e1e1e0;
            }
            QProgressBar::chunk {
                background-color: #3bdbbf;
                width: 10px;
            }
            """)
        self.delMsg.setStyleSheet("""
            color:red;
        """)
        show_error_msg(self.delMsg, UNINSTALL_ALERT_MSG)

    def set_passwd(self, pw):
        """Set password"""
        self.city_uninstall.set_pw(pw)
        self.user_pw = pw

    def start_uninstall(self):
        """ handle when nextButton was clicked"""
        # hide preserve widgets
        self.preserveLabel.hide()
        self.preserveSel.hide()
        # switch to uninstall page
        self.stackedWidget.setCurrentIndex(1)
        self.city_uninstall.uninstall_web = self.has_web
        self.city_uninstall.uninstall_od = self.has_od
        self.city_uninstall.preserve_data = self.preserveSel.property(
            "selected")
        self.city_uninstall.progress.connect(self.on_city_uninstall_progress)
        self.city_uninstall.start()
        self.city_uninstall.message.connect(self.on_uninstall_progress)

    def on_city_uninstall_progress(self, val):
        """city uninstall progress callback

        Args:
            val (_type_): _description_
        """
        self.progressBar.setValue(self.progressBar.value() + val)
        self.processBarNum.setText(str(self.progressBar.value())+"%")

    def od_checked(self):
        """Handle when od box option checked"""
        if self.odCheck.isChecked():
            self.nextButton.setEnabled(True)
        elif not self.webCheck.isChecked():
            self.nextButton.setEnabled(False)

    def web_checked(self):
        """Handle when web box option checked"""
        if self.webCheck.isChecked():
            self.nextButton.setEnabled(True)
        elif not self.odCheck.isChecked():
            self.nextButton.setEnabled(False)

    def on_uninstall_progress(self, text):
        """Self-explanatory"""
        if END_HEAD in text:
            self.on_uninstall_success()

    def on_uninstall_failed(self, failed_msg):
        """Self-explanatory"""
        show_normal_msg(self.label,  UNINSTALL_FAILED)
        show_error_msg(self.delMsg, failed_msg)

        self.stackedWidget.setCurrentIndex(0)
        self.okBtn.clicked.disconnect()
        self.cancelBtn.clicked.disconnect()
        self.okBtn.clicked.connect(self.close)
        self.cancelBtn.clicked.connect(self.close)

    def on_uninstall_success(self):
        """Self-explanatory"""
        self.delMsg.hide()
        show_normal_msg(self.label, UNINSTALL_SUCCESS)
        self.label.setGeometry(QRect(230, 230, 321, 42))
        self.stackedWidget.setCurrentIndex(0)
        self.okBtn.clicked.disconnect()
        self.cancelBtn.clicked.disconnect()
        self.okBtn.clicked.connect(self.close)
        self.cancelBtn.clicked.connect(self.close)
        self._hide_cancel()

    def close(self):
        """Close"""
        qApp.quit()

    def check_installed(self):
        """Check if OD or WEB installed"""
        # get password
        self.pw_dialog.setModal(True)
        self.pw_dialog.password_value.connect(self.set_passwd)
        self.pw_dialog.exec_()
        # check od or web exists
        self.has_od = find_od(self.user_pw)
        self.has_web = find_web(self.user_pw)

        if not self.has_od and not self.has_web:
            self.delMsg.hide()
            show_normal_msg(self.label, UNINSTALL_NO_NEED)
            self.label.setGeometry(QRect(230, 230, 321, 42))
            self.okBtn.clicked.connect(self.close)
            self.cancelBtn.clicked.connect(self.close)
            self._hide_cancel()
            # hide preserve widgets
            self.preserveLabel.hide()
            self.preserveSel.hide()
            return

    def _hide_cancel(self):
        """Hide cancel
        """
        self.cancelBtn.hide()
        self.cancelPic.hide()


def get_parse():
    """parse args from commonds
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--no-ui', action='store_true',
                        help='No graphical user interface')
    parser.add_argument('--clean',  action='store_true', required=False, default=False,
                        help='Do not preserve any data, and clean historical data')
    parser.add_argument('-v', '--version', action='store_true',
                        help="The version of uninstaller")
    return parser


def uninstall_with_ui():
    """uninstall with UI

    """
    app = QApplication([])

    # 设置全局字体
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(FONT_FILE)
    font_name = "EXO MEDIUM"  # 使用实际的字体名称
    font = QFont(font_name)
    app.setFont(font)
    # app.setWindowIcon()
    window = MainWindow()
    window.setStyleSheet("background-color: white;")
    window.setWindowIcon(QIcon(WINDOW_ICON_PATH))
    window.setWindowIconText(UNINSTALL_WINDOW_TEXT)
    window.show()
    # QApplication.processEvents()
    # QTimer.singleShot(200, window.check_env)
    sys.exit(app.exec_())


def uninstall_with_no_ui(preserve_data):
    """uninstall with no UI

    """
    # get user password
    while True:
        password = getpass.getpass(PLEASE_ENTER_PASSWORD)
        print("...... checking")
        # check password
        res = subprocess.getoutput(f"echo {password} |sudo -S -k uname -m")
        if ("x86" not in res) and ("arm" not in res) and ("aarch64" not in res):
            print(f"Error: {ERROR_PASSWORD}")
        else:
            break
    city_uninstall = CityUninstall()
    city_uninstall.basedir = BASE_DIR
    city_uninstall.set_pw(password)
    city_uninstall.uninstall_web = find_web(password)
    city_uninstall.uninstall_od = find_od(password)
    city_uninstall.preserve_data = preserve_data
    city_uninstall.message.connect(print)
    print("--------------------- start uninstalling ---------------------")
    city_uninstall.start()
    city_uninstall.wait()


if __name__ == '__main__':
    args_parser = get_parse()
    args = args_parser.parse_args()
    if args.version:
        print("Uninstaller Version: ", installer_version.VERSION)
        sys.exit(0)
    if args.no_ui:
        uninstall_with_no_ui(not args.clean)
        sys.exit(0)
    uninstall_with_ui()
