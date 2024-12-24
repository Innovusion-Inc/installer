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
import subprocess
import webbrowser
import argparse
import colorama
import threading
import time
import getpass
import re

from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QDesktopWidget,
    QLabel,
    QFileDialog,
    QWidget,
    QVBoxLayout,
    QMessageBox,
    qApp)
from PyQt5.QtCore import (
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    pyqtSignal,
)
from PyQt5.QtGui import (
    QPixmap,
    QIcon,
    QFontDatabase,
    QFont,
    QTextCursor,
)

# pylint:disable=wildcard-import,unused-wildcard-import
from common.const import *
# pylint:enable=wildcard-import,unused-wildcard-import
import common.version as installer_version
from common.function import (
    find_od_tgz,
    get_full_version_from_od,
    find_web_tgz,
    show_error_msg,
    show_success_msg,
    show_normal_msg,
    msg_with_color,
    get_local_ips,
    remove_ansi_codes,
    clone_label,
    get_free_space,
    check_ip,
    make_dir,
    get_ssd_paths,
    zoom_label_font,
    check_docker,
    check_nvidia_tool,
    check_ssh,
    is_x86,
    get_largest_nvme_mountpoint,
    MD5Checker,
)
from common.logger import get_logger, save_log_as
from common.dialog import PasswdDialog, CudaDialog
from common.eth_widget import EthWidget
from ui.installer_ui import Ui_MainWindow
from handler.install_handle import CityInstall


if getattr(sys, 'frozen', False):
    # 如果是 PyInstaller 打包的程序
    PACKAGE_DIR = os.path.dirname(sys.executable) + "/package/"
else:
    PACKAGE_DIR = os.path.dirname(__file__) + "/smart_city/package/"

LOGGER = get_logger(os.path.join(
    PACKAGE_DIR.replace("/package", ""), "log"), "installer")

PIC_DIR = f"{os.path.dirname(__file__)}/ui/imgs/"
WINDOW_ICON_PATH = PIC_DIR + "window_icon.png"
LOGO_PATH = PIC_DIR + "pic_logo.png"
LOGO_TEXT_PATH = PIC_DIR + "pic_logo_text.png"
ARROW_LEFT_PATH = PIC_DIR + "arrow_left.png"
ARROW_DOWN_PATH = PIC_DIR + "arrow_down.png"
BG1_PIC_PATH = PIC_DIR + "pic_bg1.png"
BG2_PIC_PATH = PIC_DIR + "pic_bg2.png"
BG3_PIC_PATH = PIC_DIR + "pic_bg3.png"
BG4_PIC_PATH = PIC_DIR + "pic_bg4.png"
BTN_CANCEL = PIC_DIR + "cancel_pic.png"
BTN_OK = PIC_DIR + "ok_pic.png"
FILE_ICON_PATH = PIC_DIR + "file.png"
SELECTED_ICON_PATH = PIC_DIR + "selected.png"
DOWNLOAD_ICON_PATH = PIC_DIR + "download.png"

FONT_FILE = f"{os.path.dirname(__file__)}/ui/font/Exo-Medium.ttf"


class MainWindow(QMainWindow, Ui_MainWindow):
    """Self-explanatory"""

    ip_checking_signal = pyqtSignal(dict)
    disk_checking_signal = pyqtSignal(list)

    def __init__(self):
        """Self-explanatory"""
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Installer")
        self.set_icons()
        self.set_expand_size()
        self.init_step_page()

        self.ip_address = ""
        self.ip_should_reject = False  # 标识是否应该不显示ip选择项
        self.ip_box_dict = {}
        self.ip_checking_signal.connect(self.goto_ip_chose_form)
        self.disk_checking_signal.connect(self.goto_path_select)
        self.ssd_disk_list = []
        self.no_ssd_disk_list = []

        # self.cmd_task = CommandTask()
        self.city_install = CityInstall()
        self.city_install.logger = LOGGER
        self.city_install.basedir = PACKAGE_DIR
        self.pw_dialog = PasswdDialog(qApp)
        # set password dialog icon
        self.pw_dialog.logoPic.setPixmap(QPixmap(LOGO_PATH))
        self.pw_dialog.logoPic.setScaledContents(True)
        self.pw_dialog.setWindowIcon(QIcon(WINDOW_ICON_PATH))
        self.user_pw = ""

        self.move_to_center()

        self.get_passwd()
        self.confirm_local_ip()

    def set_expand_size(self, expand=False):
        """set expand size
        """
        if expand:
            self.setFixedSize(800, 940)
        else:
            self.setFixedSize(800, 500)

    def set_icons(self):
        """set icons
        """
        self.downloadBtn.setIcon(QIcon(DOWNLOAD_ICON_PATH))

        self.fileIcon.setPixmap(QPixmap(FILE_ICON_PATH))
        self.fileIcon.setScaledContents(True)

        self.en0Select.setIcon(QIcon(SELECTED_ICON_PATH))
        self.en0Select.setIconSize(self.en0Select.size())
        self.en0Select_2.setIcon(QIcon(SELECTED_ICON_PATH))
        self.en0Select_2.setIconSize(self.en0Select_2.size())

        self.cancelPicIC.setPixmap(QPixmap(BTN_CANCEL))
        self.cancelPicIC.setScaledContents(True)
        self.cancelPicIS.setPixmap(QPixmap(BTN_CANCEL))
        self.cancelPicIS.setScaledContents(True)
        self.cancelPicPS.setPixmap(QPixmap(BTN_CANCEL))
        self.cancelPicPS.setScaledContents(True)

        self.okPicIC.setPixmap(QPixmap(BTN_OK))
        self.okPicIC.setScaledContents(True)
        self.okPicIS.setPixmap(QPixmap(BTN_OK))
        self.okPicIS.setScaledContents(True)
        self.okPicPS.setPixmap(QPixmap(BTN_OK))
        self.okPicPS.setScaledContents(True)

        self.arrowPic.setPixmap(QPixmap(ARROW_LEFT_PATH))
        self.arrowPic.setScaledContents(True)
        # set mainwindow icon
        self.logoPic.setPixmap(QPixmap(LOGO_TEXT_PATH))
        self.logoPic.setScaledContents(True)
        self.miniLogoPicIC.setPixmap(QPixmap(LOGO_TEXT_PATH))
        self.miniLogoPicIC.setScaledContents(True)
        self.miniLogoPicIS.setPixmap(QPixmap(LOGO_TEXT_PATH))
        self.miniLogoPicIS.setScaledContents(True)
        self.miniLogoPicPS.setPixmap(QPixmap(LOGO_TEXT_PATH))
        self.miniLogoPicPS.setScaledContents(True)

        self.ipRejectLogo.setPixmap(QPixmap(LOGO_PATH))
        self.ipRejectLogo.setScaledContents(True)

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
        self.white_cover_left: QLabel = QLabel(self)
        self.white_cover_left.setGeometry(0, self.bgPic.geometry().y(),
                                          self.bgPic.geometry().x(), self.bgPic.height())
        self.white_cover_right: QLabel = QLabel(self)
        self.white_cover_right.setGeometry(
            self.bgPic.geometry().x()+self.bgPic.width(),
            self.bgPic.geometry().y(),
            self.bgPic.width(),
            self.bgPic.height()
        )

        self.update_background()

    def download_log(self):
        """download log to local
        """
        # open a file dialog
        # filter txt and log file type
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseCustomDirectoryIcons
        cur_time = time.strftime("%Y%m%d%H%M%S", time.localtime())
        save_file_path = QFileDialog.getSaveFileName(
            self, caption="Save File", directory="installer"+cur_time+".log", options=options, filter='Text files (*.log)')
        flag, msg = save_log_as(save_file_path[0], "installer")
        if flag:
            self.on_append_install_msg(
                SUCCESS_HEAD + "Log saved to "+save_file_path[0])
        else:
            self.on_append_install_msg(
                ERROR_HEAD + "Save failed:  "+msg)

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
        """Bind function to component on all pages."""
        # page ipSelect
        self.cancelBtnIS.clicked.connect(self.close)
        self.okBtnIS.clicked.connect(self.on_ip_chosed)
        # page ipConfirm
        self.cancelBtnIC.clicked.connect(self.close)
        self.okBtnIC.clicked.connect(self.on_ip_chosed)
        # page ipReject
        self.ipRejectBtn.clicked.connect(self.close)
        # page pathSelect
        self.cancelBtnPS.clicked.connect(self.close)
        self.okBtnPS.clicked.connect(self.pre_install)
        self.pathBrowse.clicked.connect(self.open_file_dialog)
        self.filePath.clicked.connect(self.open_file_dialog)
        self.label_10.hide()
        # page installing
        self.finishBtn.clicked.connect(self.on_finish)
        self.progressBar.setValue(0)
        self.processBarNum.setText("0%")
        self.installMsg.hide()
        self.installDetail.clicked.connect(self.show_install_detail)
        self.finishBtn.hide()
        self.downloadBtn.clicked.connect(self.download_log)
        self.downloadBtn.show()
        self.downloadBtn.setEnabled(True)
        self.label_7.setText(f"Setup will install {PRODUCT_NAME} into the following folder :")

    def show_install_detail(self, move_to_bottom=False):
        """Self-explanatory"""
        self.installMsg.show()
        self.installDetail.clicked.disconnect()
        self.installDetail.clicked.connect(self.hide_install_detail)
        self.arrowPic.setPixmap(QPixmap(ARROW_DOWN_PATH))
        self.set_expand_size(True)
        if move_to_bottom:
            self.installMsg.moveCursor(QTextCursor.End)
            self.installMsg.moveCursor(QTextCursor.StartOfLine)

    def hide_install_detail(self):
        """hide install detail
        """
        self.installMsg.hide()
        self.installDetail.clicked.disconnect()
        self.installDetail.clicked.connect(self.show_install_detail)
        self.arrowPic.setPixmap(QPixmap(ARROW_LEFT_PATH))
        self.set_expand_size(False)

    def get_passwd(self):
        """Check cuda environment"""
        self.pw_dialog.setModal(True)
        self.pw_dialog.password_value.connect(self.set_passwd)
        self.pw_dialog.exec_()

    def set_passwd(self, pw):
        """Set password"""
        self.city_install.set_pw(pw)
        self.user_pw = pw

    def check_od_file(self):
        """Self-explanatory"""
        od_file = find_od_tgz(PACKAGE_DIR)
        # BRAND_NAME = od_file.split('_')[0]
        # PRODUCT_NAME = re.search(r'_(.*?)_OD', od_file).group(1)
        if od_file == "":
            show_error_msg(self.errorMsg, OD_PACKAGE_NOT_FOUND)
            return False, ""
        self.titleMsg.setText(
            PRODUCT_NAME.replace(" ", "_")+"_"+get_full_version_from_od(od_file))
        return True, od_file

    def check_web_file(self):
        """Self-explanatory"""
        web_file = find_web_tgz(PACKAGE_DIR)
        if web_file == "":
            show_error_msg(self.errorMsg, WEB_PACKAGE_NOT_FOUND)
            return False, ""
        return True, web_file

    def goto_ip_chose_form(self, ips: dict):
        """go to ip chose UI 
        """
        if len(ips) == 1:
            self.stepStack.setCurrentWidget(self.ipConfirm)  # ip confirm page
            for k, v in ips.items():
                self.ip_address = v[0].split("/")[0]
                self.ipIC.setText(f"Ethernet({k}) : {v[0]}")
        elif len(ips) == 0:
            # 当没有找到ip的时候
            if self.ip_should_reject:
                self.stepStack.setCurrentWidget(
                    self.ipReject)  # ip reject page
            else:
                self.ip_should_reject = True
                self.show_other_ip()
        elif len(ips) == 2:
            self.stepStack.setCurrentWidget(self.ipSelect)  # ip select page
            self.ethernetListPage.setCurrentWidget(self.two)
            # default first one
            ip_name_list = list(ips.keys())
            ip_name = ip_name_list[0]
            ip = ips[ip_name][0]
            self.ip_address = ip.split("/")[0]
            self.en0Label_2.setText(f"{ip_name} :")
            self.en0IP_2.setText(ip)
            self.en0Select_2.clicked.connect(self.on_selected)
            ip_name = ip_name_list[1]
            ip = ips[ip_name][0]
            self.en1Label_2.setText(f"{ip_name} :")
            self.en1IP_2.setText(ip)
            self.en1Select_2.clicked.connect(self.on_selected)
            self.ip_box_dict = {
                self.en0Select_2: self.en0IP_2, self.en1Select_2: self.en1IP_2}
        elif len(ips) == 3:
            self.stepStack.setCurrentWidget(self.ipSelect)
            self.ethernetListPage.setCurrentWidget(self.three)
            # default first one
            ip_name_list = list(ips.keys())
            ip_name = ip_name_list[0]
            ip = ips[ip_name][0]
            self.ip_address = ip.split("/")[0]
            self.en0Label.setText(
                f"{ip_name} :")
            self.en0IP.setText(ip)
            self.en0Select.clicked.connect(self.on_selected)
            ip_name = ip_name_list[1]
            ip = ips[ip_name][0]
            self.en1Label.setText(
                f"{ip_name} :")
            self.en1IP.setText(ip)
            self.en1Select.clicked.connect(self.on_selected)
            ip_name = ip_name_list[2]
            ip = ips[ip_name][0]
            self.en2Label.setText(
                f"{ip_name} :")
            self.en2IP.setText(ip)
            self.en2Select.clicked.connect(self.on_selected)
            self.ip_box_dict = {
                self.en0Select: self.en0IP, self.en1Select: self.en1IP, self.en2Select: self.en2IP}
        else:
            self.stepStack.setCurrentWidget(self.ipSelect)
            self.ethernetListPage.setCurrentWidget(self.four)
            scroll_content = QWidget(self.enList)
            self.enList.setWidget(scroll_content)
            vbox = QVBoxLayout(scroll_content)
            self.ip_box_dict = {}
            for name, ip in ips.items():
                ip_row = EthWidget()
                ip_row.enLabel.setText(f"{name} :")
                ip_row.enLabel.setLineWidth(180)
                # a  origin line most have 14 chars, zoom the font when line too long
                scale = 14/len(ip_row.enLabel.text())
                if scale < 1:
                    zoom_label_font(ip_row.enLabel, scale)
                ip_row.enIP.setText(ip[0])
                ip_row.enSelect.clicked.connect(self.on_selected)
                vbox.addWidget(ip_row)
                # vbox.setSpacing(0)
                self.ip_box_dict[ip_row.enSelect] = ip_row.enIP
            # select first one
            list(self.ip_box_dict.keys())[0].click()

    def confirm_local_ip(self):
        """find ipv4 address in host computer
        """
        self.stepStack.setCurrentWidget(self.ipChecking)

        def func_get_ip():
            st = time.time()
            # this function may block
            ips = get_local_ips(self.user_pw, interface_type=0)
            ct = time.time() - st
            if ct < 1.5:
                time.sleep(1.5-ct)
            if ct > 20:
                raise OSError("get IP address command timeout !!!")
            self.ip_checking_signal.emit(ips)

        get_ip_thread = threading.Thread(target=func_get_ip)
        get_ip_thread.start()

        # check phyics network devices may cost a lot time couse system IO high,
        # so manul stop it when timeout
        def watch_dog():
            if get_ip_thread.is_alive():
                get_ip_thread.join(20)  # wait 20 seconds
                if get_ip_thread.is_alive():
                    # TODO manual stop target_thread
                    # emit a empty ip dict
                    self.ip_checking_signal.emit({})

        threading.Thread(target=watch_dog).start()

    def show_other_ip(self):
        """_summary_
        """
        self.stepStack.setCurrentWidget(self.ipChecking)
        # self.showOtherIP.hide()

        def func_get_ip():
            st = time.time()
            ips = get_local_ips("", interface_type=2)
            ct = time.time() - st
            if ct < 1.5:
                time.sleep(1.5-ct)
            self.ip_checking_signal.emit(ips)

        get_ip_thread = threading.Thread(target=func_get_ip)
        get_ip_thread.start()

    def on_selected(self):
        """callback when a ip select button is selected
        """
        selected_ip_style = \
            "background-color:#f0f0f0;border:1px solid #3bdbbf;border-radius: 5px;color:black;"
        unselected_ip_style = \
            "border:1px solid #c4c4c4;border-radius: 5px;background-color:white;color:black;"
        for k, v in self.ip_box_dict.items():
            # k.setStyleSheet(unselected_box_style)
            # k.setText("")
            k.setIcon(QIcon())
            v.setStyleSheet(unselected_ip_style)
        button = self.sender()
        ip_box = self.ip_box_dict[button]
        button.setIcon(QIcon(SELECTED_ICON_PATH))
        button.setIconSize(button.size())
        ip_box.setStyleSheet(selected_ip_style)
        self.ip_address = ip_box.text().split("/")[0]

    def on_ip_chosed(self):
        """ after get ip, go to next page

        """
        if not is_x86():
            directory = get_largest_nvme_mountpoint()
            if directory:
                self.filePath.setText("          " + directory + "/seyond_user")
        self.stepStack.setCurrentWidget(self.ssdChecking)

        def func_get_path():
            st = time.time()
            # this function may block
            paths, other_paths = get_ssd_paths()
            paths = [paths, other_paths]
            ct = time.time() - st
            if ct < 1.5:
                time.sleep(1.5-ct)
            if ct > 15:
                print("get paths mount in SSD: ", paths)
                print(
                    "check command : lsblk -d -o name,rota | grep ' 0' | awk '{print $1}'")
                raise OSError("get IP address command timeout !!!")

            self.disk_checking_signal.emit(paths)

        get_path_thread = threading.Thread(target=func_get_path)
        get_path_thread.start()

        # check phyics network devices may cost a lot time couse system IO high,
        # so manul stop it when timeout
        def watch_dog():
            if get_path_thread.is_alive():
                get_path_thread.join(15)  # wait 15 seconds
                if get_path_thread.is_alive():
                    # TODO manual stop target_thread
                    self.disk_checking_signal.emit([[], []])

        threading.Thread(target=watch_dog).start()

    def goto_path_select(self, disk_list):
        """go to path select page
            disk_list:[[ssd_path],[no_ssd_path]]
        """
        self.ssd_disk_list = disk_list[0]
        self.no_ssd_disk_list = disk_list[1]
        self.stepStack.setCurrentWidget(self.pathSelect)
        if self.filePath.text().strip() != "":
            self.check_path_is_ssd()

    def open_file_dialog(self):
        """select a file in a file dialog
        """
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        options |= QFileDialog.DontUseCustomDirectoryIcons
        directory = QFileDialog.getExistingDirectory(
            self, caption="Select The Install Directory", directory="", options=options)
        if directory:
            self.filePath.setText("          "+directory)
        if self.check_file_path_free():
            self.check_path_is_ssd()

    def check_file_path_free(self) -> bool:
        """check file path free space
        """
        dir_path = self.filePath.text().strip()
        free_gb_in_path = float(get_free_space(dir_path))/1024
        if free_gb_in_path < MIN_FREE_GB:
            color_free_gb = f"<span style='color:#3bdbbf;'>{MIN_FREE_GB}</span>"
            show_normal_msg(
                self.label_10, INSTALL_ERROR_NEED_SPACE % color_free_gb)
            self.okBtnPS.setEnabled(False)
            return False
        self.label_10.hide()
        self.okBtnPS.setEnabled(True)
        return True

    def check_path_is_ssd(self) -> bool:
        """check the selected path if in SSD disk

        Returns:
            bool: true or false
        """
        dir_path = self.filePath.text().strip()
        parent_dir = ""
        ssd_flag = True
        for path in self.no_ssd_disk_list:
            if dir_path.startswith(path) and path.startswith(parent_dir):
                parent_dir = path
                ssd_flag = False

        for path in self.ssd_disk_list:
            if dir_path.startswith(path) and path.startswith(parent_dir):
                parent_dir = path
                ssd_flag = True

        if ssd_flag:
            self.label_10.hide()
            return ssd_flag
        # avoid self.label_10 is showing other message
        if self.label_10.isHidden():
            show_normal_msg(self.label_10, INSTALL_ERROR_SSD)
        return ssd_flag

    def pre_install(self):
        """Prepare install"""
        if not self.check_file_path_free():
            return
        self.stepStack.setCurrentWidget(self.installing)
        od_flag, od_file = self.check_od_file()
        web_flag, web_file = self.check_web_file()
        if od_flag and web_flag:
            self.start_install(True, True, od_path=od_file,
                               web_path=web_file)

    def start_install(self, od_enable, web_enable, web_ip=None, od_path="", web_path=""):
        """start install"""
        local_ip = self.ip_address
        file_path = self.filePath.text().strip()
        self.city_install.use_gpu = self.use_gpu_checkbox.isChecked()
        self.city_install.installed_path = file_path
        if local_ip == "":
            show_error_msg(self.errorMsg, INSTALL_ERROR_LOCAL_IP_NOT_FOUND)
            return
        if web_enable:
            self.city_install.web_tgz = web_path
            self.city_install.install_web = True
        else:
            self.city_install.install_web_ip = web_ip
            self.city_install.install_web = False
        if od_enable:
            self.city_install.od_tgz = od_path
            self.city_install.install_local_ip = local_ip
            self.city_install.install_od = True

        self.city_install.progress.connect(self.on_city_install_progress)
        self.city_install.install_msg.connect(self.on_append_install_msg)
        self.check_dependencies()
        self.city_install.start()

    def check_dependencies(self):
        """ Self-explanatory
        """
        confirm_msg = ""
        docker_ready, _ = check_docker()
        if not docker_ready:
            confirm_msg += f"{DOCKER_IS_NOT_INSTAL}\n"
        ssh_ready, _ = check_ssh(self.user_pw)
        if not ssh_ready:
            confirm_msg += f"{OPENSSH_IS_NOT_INSTAL}\n"
        nvidia_ready = check_nvidia_tool(self.user_pw)
        if not nvidia_ready:
            confirm_msg += f"{NVIDIA_TOOLKIT_IS_NOT_INSTAL}\n"
        if confirm_msg:
            confirm_msg += "------------------------------------------------------------- \n"
            confirm_msg += CONTINUE_INSTALL_MSG
            message_box = QMessageBox(self)
            message_box.setWindowTitle("Confirmation")
            message_box.setText(confirm_msg)
            message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            message_box.setDefaultButton(QMessageBox.No)
            result = message_box.exec_()
            if result != QMessageBox.Yes:
                LOGGER.info(confirm_msg + ": user cancel")
                self.close()
            else:
                LOGGER.info(confirm_msg + ": user confirm")

    def on_city_install_progress(self, val):
        """Self-explanatory"""
        self.progressBar.setValue(val)
        self.processBarNum.setText(str(self.progressBar.value())+"%")

    def on_append_install_msg(self, text):
        """Sefl-explanatory"""
        if ERROR_HEAD in text:
            show_error_msg(self.errorMsg, INSTALL_ERROR_EXIT)
            self.finishBtn.show()
            self.finishBtn.setEnabled(True)
            self.installMsg.append(
                msg_with_color(text, colorama.Fore.RED))
            show_error_msg(self.statusMsg, INSTALL_FAILED)
            self.finishBtn.clicked.disconnect()
            self.finishBtn.clicked.connect(self.close)
            self.show_install_detail(move_to_bottom=True)
            return
        # 将ANSI编码移除
        raw_str = remove_ansi_codes(text)
        # render color
        color_msg = raw_str
        if SUCCESS_HEAD in raw_str:
            color_msg = msg_with_color(raw_str, colorama.Fore.GREEN)
        elif INFO_HEAD in raw_str:
            color_msg = msg_with_color(raw_str, colorama.Fore.BLUE)
        elif WARNING_HEAD in raw_str:
            color_msg = msg_with_color(
                raw_str, colorama.Fore.MAGENTA)
        elif TRACE_HEAD in raw_str:
            raw_str = raw_str.replace(TRACE_HEAD, "")
            color_msg = msg_with_color(raw_str, "#aaa")
        else:
            color_msg = msg_with_color(raw_str, colorama.Fore.BLACK)
        self.installMsg.append(color_msg)

        if END_HEAD in text:
            show_success_msg(self.statusMsg, INSTALL_SUCCESS)
            self.finishBtn.show()
            self.finishBtn.setEnabled(True)

    def on_finish(self):
        """finish button clicked callback
        """
        webbrowser.open_new(WEB_URL)
        self.close()

    def close(self):
        """Close"""
        qApp.quit()


def install_with_ui():
    """install with UI

    """
    app = QApplication([])

    # 设置全局字体
    fontDB = QFontDatabase()
    fontDB.addApplicationFont(FONT_FILE)
    font_name = "EXO MEDIUM"  # 使用实际的字体名称
    font = QFont(font_name)
    app.setFont(font)
    # app.setWindowIcon()
    # check current path free space
    free_gb = float(get_free_space(PACKAGE_DIR)) / 1024
    needed_free_gb = 8
    if free_gb > needed_free_gb:
        window = MainWindow()
        window.setStyleSheet("background-color: white;")
        window.setWindowIcon(QIcon(WINDOW_ICON_PATH))
        window.setWindowIconText(INSTALL_WINDOW_TEXT)
        window.show()
    else:
        dialog = CudaDialog(qApp)
        # set cuda_dialog icon
        dialog.setWindowIconText("CUDA Msg")
        dialog.setWindowIcon(QIcon(WINDOW_ICON_PATH))
        dialog.logo_pic.setPixmap(QPixmap(LOGO_PATH))
        dialog.logo_pic.setScaledContents(True)
        dialog.show()
        show_error_msg(dialog.cuda_msg, INSTALL_ERROR_NEED_SPACE %
                       needed_free_gb)
    sys.exit(app.exec_())


def install_without_ui(local_ip, installed_path, use_gpu):
    """install without UI

    """
    # check installed_path is valid
    try:
        os.path.abspath(installed_path)
    except Exception as e:
        LOGGER.error(e)
        print(f"Install path invaild: {e}")
        sys.exit(1)
    # check current path free space
    free_gb = float(get_free_space(PACKAGE_DIR)) / 1024
    needed_free_gb = 8
    if free_gb < needed_free_gb:
        print(f"Error:  {INSTALL_ERROR_NOT_ENOUGH_SPACE%PACKAGE_DIR}")
        print(INSTALL_ERROR_NEED_SPACE % needed_free_gb)
        sys.exit(1)
    # check IP valid
    if not check_ip(local_ip):
        print(f"Error: {IP_ERROR_MSG%local_ip}")
        LOGGER.error(IP_ERROR_MSG, local_ip)
        sys.exit(1)
    # get user password
    while True:
        password = getpass.getpass(PLEASE_ENTER_PASSWORD)
        print("...... checking")
        # check password
        res = subprocess.getoutput(f"echo {password} |sudo -S -k uname -m")
        if ("x86" not in res) and ("arm" not in res) and ("aarch64" not in res):
            LOGGER.error(res)
            print(f"Error: {ERROR_PASSWORD}")
        else:
            break
    # check install path has enough free space
    try:
        make_dir(installed_path, password)
    except Exception as err:
        err_msg = f"Cannot create the directory : {installed_path}, {err}"
        LOGGER.error(err_msg)
        print(err_msg)
        sys.exit(1)

    free_gb = float(get_free_space(installed_path)) / 1024
    if free_gb < MIN_FREE_GB:
        print(f"Error: {INSTALL_ERROR_NOT_ENOUGH_SPACE%installed_path}.")
        print(INSTALL_ERROR_NOT_ENOUGH_SPACE % MIN_FREE_GB)
        LOGGER.error(INSTALL_ERROR_NOT_ENOUGH_SPACE, installed_path)
        sys.exit(1)
    print("--------------------- start installing ---------------------")
    city_install = CityInstall()
    city_install.logger = LOGGER
    city_install.basedir = PACKAGE_DIR
    city_install.set_pw(password)
    city_install.installed_path = installed_path
    city_install.install_local_ip = local_ip
    city_install.use_gpu = use_gpu
    # check tgz exist
    od_file = find_od_tgz(PACKAGE_DIR)
    if od_file == "":
        print(f"Error:  {OD_PACKAGE_NOT_FOUND} in {PACKAGE_DIR}")
        LOGGER.error(OD_PACKAGE_NOT_FOUND, PACKAGE_DIR)
        sys.exit(1)
    web_file = find_web_tgz(PACKAGE_DIR)
    if web_file == "":
        print(f"Error:  {WEB_PACKAGE_NOT_FOUND} in {PACKAGE_DIR}")
        LOGGER.error(WEB_PACKAGE_NOT_FOUND, PACKAGE_DIR)
        sys.exit(1)
    city_install.web_tgz = web_file
    city_install.od_tgz = od_file
    city_install.install_web = True
    city_install.install_od = True
    city_install.install_msg.connect(echo_install_msg)
    city_install.start()
    city_install.wait()


def echo_install_msg(text):
    """_summary_

    Args:
        text (_type_): _description_
    """
    print(text)


def str_to_bool(value):
    """Convert a string to a boolean value."""
    if isinstance(value, bool):
        return value
    if value.lower() in {'yes', 'true', 't', 'y', '1'}:
        return True
    elif value.lower() in {'no', 'false', 'f', 'n', '0'}:
        return False
    raise argparse.ArgumentTypeError('Boolean value expected.')

def get_parse():
    """parse args from commonds
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--no-ui', action='store_true',
                        help='No graphical user interface')
    parser.add_argument('-p', '--path', metavar='PATH', type=str, required=False,
                        help='The installation path')
    parser.add_argument('--host-ip', metavar='IP', type=str, required=False,
                        help='The IP address of the local network interface, do not use the 172.30.0.xxx network segment')
    parser.add_argument('--use-gpu', type=str_to_bool, nargs='?', const=True, default=True,
                        help='Enable or disable GPU usage (default: True)')
    parser.add_argument('-v', '--version', action='store_true',
                        help="The version of installer")
    return parser


if __name__ == '__main__':
    args_parser = get_parse()
    args = args_parser.parse_args()

    if args.version:
        print("Installer Version: ", installer_version.VERSION)
        sys.exit(0)
    if args.no_ui:
        # check if --lidar-ip and --install-path is set
        if not (args.host_ip and args.path):
            print(
                "Params Error: --host-ip and --install-path are required when --no-ui is set")
            # print help message
            args_parser.print_help()
            sys.exit(1)
        # install without UI
        install_without_ui(local_ip=args.host_ip,
                           installed_path=args.path,
                           use_gpu=args.use_gpu)
        sys.exit(0)
    elif args.path or args.host_ip:
        print("Params Error: --no-ui is required when --install-path or --local-ip is set")
        # print help message
        args_parser.print_help()
        sys.exit(1)
    if len(sys.argv) != 1:
        args_parser.print_help()
        sys.exit(0)
    # install with UI
    install_with_ui()
