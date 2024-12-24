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

"""Const functions"""
import sys
import ipaddress
import re
import glob
import os
import subprocess
import colorama
import docker
import shutil
import time
import pathlib
import hashlib
import yaml

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QCoreApplication, QThread, pyqtSignal, QObject

from .const import (
    OD_FILE_PREFIX,
    WEB_FILE_PREFIX,
    SCENE_FILE_SUFFIX,
    WEB_BASE_DOCKER_NAMES,
    WEB_CITY_DOCKER_NAMES,
    OD_DOCKER_NAME,
    ERROR_HEAD,
    INFO_HEAD,
    TRACE_HEAD,
    WARNING_HEAD
)

WEB_DOCKER_NAMES = [*WEB_BASE_DOCKER_NAMES, *WEB_CITY_DOCKER_NAMES]


class MD5Checker(QObject):
    def __init__(self, logger, output_txt=None):
        super().__init__()
        self.logger = logger
        self.output_txt = output_txt

    def calculate_md5_excluding_last_line(self, file_path):
        """Calculate the MD5 checksum of a file excluding its last line."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                lines = f.readlines()
                if len(lines) < 2:  # Ensure there's more than one line to avoid issues
                    msg = ERROR_HEAD + "The file must contain at least two lines."
                    print(msg)
                    self.logger.error(msg)
                    if self.output_txt:
                        self.output_txt.emit(msg)  # Emit the message
                    return

                for line in lines[:-1]:
                    hash_md5.update(line)
            return hash_md5.hexdigest()
        except FileNotFoundError:
            msg = ERROR_HEAD + f"The file {file_path} does not exist."
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return
        except PermissionError:
            msg = ERROR_HEAD + f"Permission denied for file {file_path}."
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return
        except Exception as e:
            msg = ERROR_HEAD + f"An unexpected error occurred while reading {file_path}: {e}"
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return

    def calculate_md5(self, file_path):
        """Calculate the MD5 checksum of a file."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except FileNotFoundError:
            msg = ERROR_HEAD + f"The file {file_path} does not exist."
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return
        except PermissionError:
            msg = ERROR_HEAD + f"Permission denied for file {file_path}."
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return
        except Exception as e:
            msg = ERROR_HEAD + f"An unexpected error occurred while reading {file_path}: {e}"
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return

    def check_md5(self, folder_path):    
        """Check MD5 checksums of files in the given folder against those in install_config.yaml."""
        msg = INFO_HEAD+ f"Start checking md5 for {folder_path}."
        print(msg)
        self.logger.info(msg)
        if self.output_txt:
            self.output_txt.emit(msg)  # Emit the message

        yaml_file_path = os.path.join(folder_path, "package/install_config.yaml")
        
        try:
            with open(yaml_file_path, 'r') as file:
                config = yaml.safe_load(file)
        except FileNotFoundError:
            msg = ERROR_HEAD + f"The file {yaml_file_path} does not exist."
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return False
        except PermissionError:
            msg = ERROR_HEAD + f"Permission denied for file {yaml_file_path}."
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return False
        except yaml.YAMLError as e:
            msg = ERROR_HEAD + f"Failed to parse YAML file {yaml_file_path}: {e}"
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return False
        except Exception as e:
            msg = ERROR_HEAD + f"An unexpected error occurred while reading {yaml_file_path}: {e}"
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return False

        md5_checksums = config.get('md5_checksums', {})
        install_config_md5 = config.get('package/install_config_md5')

        files_to_check = []

        installer_file_path = os.path.join(folder_path, "installer")
        uninstaller_file_path = os.path.join(folder_path, "uninstaller")
        files_to_check.append(installer_file_path)
        files_to_check.append(uninstaller_file_path)

        package_directories_path = os.path.join(folder_path, "package")

        for root, dirs, files in os.walk(package_directories_path):
            for file in files:
                if (not file.endswith('.tar') and file != "install_config.yaml"):
                    files_to_check.append(os.path.join(root, file))
        
        for file_path in files_to_check:
            filename = os.path.relpath(file_path, folder_path)
            
            calculated_md5 = self.calculate_md5(file_path)
            expected_md5 = md5_checksums.get(filename)

            if expected_md5 and calculated_md5 != expected_md5:
                msg = ERROR_HEAD + f"MD5 mismatch for {file_path}: calculated {calculated_md5}, expected {expected_md5}"
                print(msg)
                self.logger.error(msg)
                if self.output_txt:
                    self.output_txt.emit(msg)  # Emit the message
                return False
            else:
                msg = INFO_HEAD + f"MD5 match for {file_path}: calculated {calculated_md5}, expected {expected_md5}"
                print(msg)
                self.logger.info(msg)
                if self.output_txt:
                    self.output_txt.emit(msg)  # Emit the message
        
        expected_files_set = {file for file in md5_checksums.keys() if not file.endswith('.tar')}
        actual_files_set = {os.path.relpath(file, folder_path) for file in files_to_check}

        if expected_files_set != actual_files_set:
            missing_files = expected_files_set - actual_files_set
            extra_files = actual_files_set - expected_files_set

            if missing_files:
                msg = ERROR_HEAD +  f"Missing files in the directory: {', '.join(missing_files)}"
                print(msg)
                self.logger.error(msg)
                if self.output_txt:
                    self.output_txt.emit(msg)  # Emit the message
            if extra_files:
                msg = ERROR_HEAD + f"Extra files found in the directory: {', '.join(extra_files)}"
                print(msg)
                self.logger.error(msg)
                if self.output_txt:
                    self.output_txt.emit(msg)  # Emit the message
            return False
        
        calculated_yaml_md5 = self.calculate_md5_excluding_last_line(yaml_file_path)
        
        if calculated_yaml_md5 != install_config_md5:
            msg = ERROR_HEAD + f"MD5 mismatch for install_config.yaml (excluding last line): calculated {calculated_yaml_md5}, expected {install_config_md5}"
            print(msg)
            self.logger.error(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message
            return False
        else:
            msg = INFO_HEAD + f"MD5 match for install_config.yaml (excluding last line): calculated {calculated_yaml_md5}, expected {install_config_md5}"
            print(msg)
            self.logger.info(msg)
            if self.output_txt:
                self.output_txt.emit(msg)  # Emit the message

        success_msg = INFO_HEAD + "All checksums match successfully."
        print(success_msg)
        self.logger.info(success_msg)
        if self.output_txt:
            self.output_txt.emit(success_msg)  # Emit the success message
        return True



def apt_install(user_password, packages, logger):
    """install packages in apt
    """
    cmd = f"echo -S {user_password} | sudo apt-get update"
    output = subprocess.getoutput(cmd)
    print(output)
    logger.info(output)
    cmd = f"echo -S {user_password} | sudo apt-get install --fix-broken"
    output = subprocess.getoutput(cmd)
    print(output)
    logger.info(output)
    cmd = "sudo -S apt-get install -y " + " ".join(packages)
    for output in exec_cmd(cmd, [user_password]):
        print(output)
        logger.info(output)


def has_app_in_dpkg(user_password, app):
    """check if the application is installed in dpkg
    """
    cmd = "sudo -S dpkg -l | grep " + app
    for output in exec_cmd(cmd, [user_password]):
        if "ii" in output:
            return True
    return False


def get_free_space(fie_directory):
    """get free space (MB) in the specified directory
    """
    try:
        total, used, free = shutil.disk_usage(fie_directory)
        free_mb = free / (1024 ** 2)  # MB
    except Exception as e:
        print(e)
        free_mb = subprocess.getoutput(
            "df -m $(pwd) | awk 'NR==2 { print $4 }'")
    return free_mb


def convert_size_to_gb(size_str):
    number = float(re.findall(r'\d+', size_str)[0])
    if 'T' in size_str:
        return number * 1024
    elif 'G' in size_str:
        return number
    elif 'M' in size_str:
        return number / 1024
    else:
        return number / (1024**2)
    
def get_largest_nvme_mountpoint():
    """ get largest nvme-ssd device mountpoint
    """
    result = subprocess.run(['lsblk', '-nlo', 'NAME,MOUNTPOINT,SIZE'], capture_output=True, text=True)
    lines = result.stdout.splitlines()

    largest_size = 0
    largest_device = None
    largest_mountpoint = None

    for line in lines:
        if 'nvme' in line:
            parts = line.split()
            if len(parts) >= 3:
                name, mountpoint, size_str = parts[0], parts[1], parts[2]
                size = convert_size_to_gb(size_str)
                if mountpoint != "" and size > largest_size:
                    largest_size = size
                    largest_device = name
                    largest_mountpoint = mountpoint

    return largest_mountpoint

def append_line(content, file_path, delete_content):
    """ if content not in file, append line to file
    """
    try:
        file_path = os.path.expanduser(file_path)
        with open(file_path, 'r+') as file:
            lines = file.readlines()
            file.seek(0)  # set file pointer to the beginning of the file
            lines = [line for line in lines if delete_content not in line]
            # check if `content` is already in the remaining lines
            if not any(content in line for line in lines):
                lines.append(content + '\n')
            file.writelines(lines)
            file.truncate()  # write back
            return 0
    except FileNotFoundError:
        return 1
    except PermissionError:
        return 2
    except:
        return -1

def set_core_pattern(user_password, pattern="core"):
    """Config core_pattern to generate core_dump file with process name."""
    try:
        change_mode_to_full_permission("/etc/sysctl.conf", user_password)
        ret = append_line(f"kernel.core_pattern={pattern}", "/etc/sysctl.conf", "kernel.core_pattern")
        if ret == 0:
            os.system(f"echo {user_password} |sudo -S sysctl -p")
        else:
            return ret
        return 0
    except FileNotFoundError:
        return 1
    except PermissionError:
        return 2
    except:
        return -1

def get_ssd_paths():
    """get all path in SSD
    """
    ssd_cmd = "lsblk -d -o name,rota | grep ' 0' | awk '{print $1}' "
    ssd_names = subprocess.getoutput(ssd_cmd).split()
    ssd_names = [("/dev/" + ele) for ele in ssd_names]
    get_path_cmd = "df -h --output=source,target "
    path_result = subprocess.getoutput(get_path_cmd).split("\n")
    path_dict = {}
    for path in path_result:
        pieces = path.split()
        if len(pieces) < 2:
            continue
        path_dict[pieces[0]] = pieces[1]
    res = []
    for name, path in path_dict.items():
        for ssd_name in ssd_names:
            if ssd_name in name:
                res.append(path)
                break
    no_ssd = [path for path in path_dict.values() if path not in res]
    return res, no_ssd


def check_ip(ip):
    """ Check ipv4 address"""
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False


def is_port_vaild(port_str, invalid_ports: list) -> bool:
    """check if port vaild, or not in invaild

    Returns:
        bool: _description_
    """
    if port_str == "":
        return "Port number cannot be empty"
    port_int = 0
    try:
        port_int = int(port_str)
    except Exception:
        return "Invalid port number"

    if (port_str in invalid_ports) or (port_int in invalid_ports):
        return "Port are be occupied"

    if port_int <= 0 or port_int > 65535:
        return "Invalid port number"

    return ""


def get_occupied_ports(only_tcp=True):
    """get occupied ports in the system
    """
    if only_tcp:
        cmd = "ss -tln | awk 'NR>1 {print $4}'"
    else:
        cmd = "ss -tlnp | awk 'NR>1 {print $4}'"
    ports = subprocess.getoutput(cmd).split()
    ports = [port.rsplit(":", 1)[1].strip() for port in ports]
    ports = [port for port in ports if port != ""]
    return ports


def find_od_tgz(basedir):
    """Self-explanatory"""
    pattern = os.path.join(basedir, OD_FILE_PREFIX+"*.tgz")
    files = glob.glob(pattern)
    if len(files) > 0:
        return files[0]
    return ""


def find_web_tgz(basedir):
    """Self-explanatory"""
    pattern = os.path.join(basedir, WEB_FILE_PREFIX+"*.tgz")
    files = glob.glob(pattern)
    if len(files) > 0:
        return files[0]
    return ""


def get_file_path(basedir, filename):
    """Self-explanatory"""
    pattern = os.path.join(basedir, filename)
    files = glob.glob(pattern)
    if len(files) > 0:
        return files[0]
    return ""


def find_scene_tgz(basedir):
    """Self-explanatory"""
    pattern = os.path.join(basedir, OD_FILE_PREFIX +
                           "*" + SCENE_FILE_SUFFIX+"*.zip")
    files = glob.glob(pattern)
    if len(files) > 0:
        return files[0]
    return ""


def get_cuda_version(path):
    """Self-explanatory"""
    filename = os.path.basename(path)
    keys = filename.split("cuda_")
    try:
        return keys[1].split(".")[0]
    except Exception as e:
        print(e)
        return ""


def style_to_html(style):
    """将colorama样式映射为HTML标签"""
    if style == colorama.Style.BRIGHT:
        return "<b>", "</b>"
    if style == colorama.Style.DIM:
        return "<i>", "</i>"
    # 对于未知或未处理的样式，直接返回无标签
    return "", ""


def get_color_from(color):
    """Self-explanatory"""
    color_dict = {
        colorama.Fore.RED: 'color:red',
        colorama.Fore.GREEN: 'color:green',
        colorama.Fore.YELLOW: 'color:yellow',
        colorama.Fore.BLUE: 'color:blue',
        colorama.Fore.MAGENTA: 'color:magenta',
        colorama.Fore.CYAN: 'color:cyan',
        colorama.Fore.WHITE: 'color:white'
    }
    return color_dict.get(color, f"color:{color}")  # 如果没有匹配的颜色，返回本身


def msg_with_color(msg, color):
    """ 将colorama颜色映射为HTML颜色属性"""
    msgs = msg.split('\n')
    span_str = ""
    for m in msgs:
        span_str += f'<span style="{get_color_from(color)}">{m}</span><br>'
    return span_str[:-4]


def ansi_to_html(ansi_str):
    """Convert ANSI codes to HTML"""
    # 使用colorama.Fore定义的ANSI颜色代码进行解析
    result = ""  # 最终的HTML字符串
    current_color = ""  # 当前的颜色代码
    current_style_open, current_style_close = "", ""  # 当前的样式代码

    color_codes = [
        colorama.Fore.BLACK,
        colorama.Fore.RED,
        colorama.Fore.GREEN,
        colorama.Fore.YELLOW,
        colorama.Fore.BLUE,
        colorama.Fore.MAGENTA,
        colorama.Fore.CYAN,
        colorama.Fore.WHITE
    ]

    style_codes = [colorama.Style.BRIGHT, colorama.Style.DIM]

    for word in ansi_str.split():  # 分割字符串
        if word in color_codes:  # 检查单词是否为颜色代码
            current_color = get_color_from(word)
        elif word in style_codes:  # 检查单词是否为样式代码
            current_style_open, current_style_close = style_to_html(word)
        else:  # 如果单词既不是颜色代码也不是样式代码，它应该是普通文本
            result += f'<span style="{current_color}">{current_style_open}'\
                f'{word}{current_style_close}</span> '

    return result


def remove_ansi_codes(s):
    """ ANSI转义序列的正则表达式"""
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', s)


def show_error_msg(label: QLabel, msg: str):
    """show error msg in red color"""
    label.setText(QCoreApplication.translate("MainWindow", msg))
    label.setStyleSheet("color: #E24183")
    label.show()


def show_success_msg(label: QLabel, msg: str):
    """show success msg in green color"""
    label.setText(QCoreApplication.translate("MainWindow", msg))
    label.setStyleSheet("color: green")
    label.show()
    return


def show_normal_msg(label: QLabel, msg: str):
    """show normal msg in black color"""
    label.setText(QCoreApplication.translate("MainWindow", msg))
    label.setStyleSheet("color: black")
    label.show()
    return


def zoom_label_font(label: QLabel, zoom_ratio: float):
    """zoom label font"""
    font = label.font()
    font.setPointSize(int(font.pointSize() * zoom_ratio))
    label.setFont(font)


def zoom_label_font_auto(label: QLabel):
    """auto zoom label font to avoid font oversize label width"""
    font = label.font()
    width = label.width()
    point_size = width * 0.1
    font.setPointSize(point_size)
    label.setFont(font)


def remove_dir(directory, sudo_pw):
    """remove directory
    """
    err_msg = ""
    if os.path.exists(directory):
        try:
            shutil.rmtree(directory)
        except Exception as e:
            err_msg = f"{WARNING_HEAD} remove {directory} failed: {e}"
            os.system(f"echo {sudo_pw} | sudo -S rm -rf {directory}")
    if os.path.exists(directory):
        if err_msg != "":
            print(err_msg)
        else:
            print(f"{WARNING_HEAD} remove {directory} failed")
        return False
    return True


def get_local_ip():
    """ Get local ip"""
    try:
        result = subprocess.getoutput("ifconfig")
        resutl_list = result.split("\n\n")
        net_dict = {}
        for r in resutl_list:
            net_name = r.split(": ")[0]
            if r.split('\n')[1].split()[0].strip() != "inet":
                continue
            inet_addr = r.split('\n')[1].split()[1]
            net_dict[net_name] = inet_addr
        for name, addr in net_dict.items():
            if name.startswith("en") or name.startswith("eth"):
                return addr
        for name, addr in net_dict.items():
            if name.startswith("wl") or name.startswith("wlan"):
                return addr
    except Exception as e:
        print("ERROR: get local ip failed! ")
        print(e)
    print("Not found a good ip address")
    return ""


def get_local_ips(user_pw, exclude_ipv6=True, interface_type=0) -> dict:
    """get all of local network interface IP address
        return : {
           eno1:["ipv4","ipv6"],
           wlo1:["ipv4"],
           docker0:["ipv6"]
        }

    Args:
        exclude_ipv6 (bool, optional): if exclude ipv6 address. Defaults to True.
        type (int ,optional): if 0 ,return only en; if 1 ,return en and wl; if 2, return all.
    """
    # it means no need to get network logical name
    if user_pw != "":
        logical_name_list = get_network_logical_name(user_pw, interface_type)
    else:
        logical_name_list = []

    cmd = "ip -br a | awk '{print $1, $3, $4}'"
    result = subprocess.getoutput(cmd)
    result_list = result.split("\n")
    net_dict = {}
    for r in result_list:
        if len(r.split()) < 2:
            continue
        net = r.split()
        if exclude_ipv6:
            if len(net) < 2:
                continue
            if ":" in net[1]:
                continue
            net_dict[net[0]] = [net[1]]
        else:
            net_dict[net[0]] = net[1:]
    filter_dict = {}
    for k, v in net_dict.items():
        if interface_type == 0 and (k in logical_name_list):
            filter_dict[k] = v
        elif interface_type == 1 and (k in logical_name_list):
            filter_dict[k] = v
        elif interface_type == 2:
            filter_dict[k] = v
    return filter_dict


def get_network_logical_name(user_pw, interface_type) -> list:
    """get network logical name

    Returns:
        list: serial list
    """
    cmd = f"echo {user_pw} | sudo -S lshw -class network"
    result = subprocess.getoutput(cmd)
    network_list = result.split("*-network")
    # filter out ele if not have description field
    network_list = [
        ele for ele in network_list if "description" in ele and "product" in ele and "serial" in ele]
    serial_list = []
    needed_networks = []
    for ele in network_list:
        infos = ele.split("\n")
        needed_network = ["", ""]
        for info in infos:
            if "description" in info:
                needed_network[0] = info.split(": ")[1].strip(" ")
            elif "logical name" in info:
                needed_network[1] = info.split(": ")[1].strip(" ")
        needed_networks.append(needed_network)
    for n in needed_networks:
        if interface_type == 0 and "Ethernet" in n[0]:
            serial_list.append(n[1])
        elif interface_type == 1 and ("Ethernet" in n[0] or "Wireless" in n[0]):
            serial_list.append(n[1])
    return serial_list


def grant_docker() -> bool:
    """add current user to docker group"""
    # do not grant current user to docker group
    return False
    try:
        groups = subprocess.getoutput("groups")
        if "docker" in groups:
            return True
        os.system("sudo usermod -aG docker $USER")
        groups = subprocess.getoutput("groups")
        if "docker" not in groups:
            print("add current user to docker group failed! \n")
            return False
        print("add current user to docker group successfully! \n")
        return True
    except Exception as err:
        print("add current user to docker group failed! Exception: \n", err)
        return False


def docker_exec(docker_name, cmd):
    """Execute docker command"""
    grant_docker()
    client = docker.from_env()
    # 连接到指定的容器
    container = client.containers.get(docker_name)
    # 执行命令或操作
    result = container.exec_run(cmd)
    client.close()
    return result.output.decode()


def is_docker_image_exist(image_name_with_version, sudo_pw):
    """_summary_

    Args:
        image_name_with_version (_type_): _description_
    """
    try:
        cmd = "sudo -S docker images --format '{{.Repository}}:{{.Tag}}'  "
        res = ""
        for output in exec_cmd(cmd, [sudo_pw]):
            if '[sudo]' in output:
                continue
            res += output.replace(TRACE_HEAD, "")
        # image_name_with_version
        res_list = res.split("\n")
        return image_name_with_version in res_list
    except Exception as err:
        print(err)
    return False


def get_all_docker_image(sudo_pw):
    """get all docker image
    """
    try:
        cmd = "sudo -S -k docker images --format '{{.Repository}}:{{.Tag}}'  "
        res = ""
        for output in exec_cmd(cmd, [sudo_pw]):
            if '[sudo]' in output:
                continue
            res += output.replace(TRACE_HEAD, "")
        res_list = res.split("\n")
        return res_list
    except Exception as err:
        print(err)
        return [err]


def get_docker_version():
    """Get docker version, if not exists, return None"""
    try:
        if not grant_docker():
            output = subprocess.getoutput("docker --version")
            if "Docker version" in output:
                return output.split("Docker version ")[1].split(",")[0]
        client = docker.from_env()
        version = client.version()["Version"]
        return version
    except Exception as err:
        print(err)
        return None


def is_container_up(container_name, sudo_pw):
    """Check if docker container"""
    try:
        if not grant_docker():
            format_str = " '{{.State.Status}}' "
            output = subprocess.getoutput(
                f"echo {sudo_pw} | sudo -S docker inspect --format= {format_str} {container_name}")
            if "running" in output:
                return True
            return False
        client = docker.from_env()
        container = client.containers.get(container_name)  # 获取指定名称的容器
        return container.status == 'running'  # 检查是否运行中
    except docker.errors.NotFound:
        print(f'There is no container with name: {container_name}')
        return False
    except docker.errors.APIError as e:
        print(f'An error occurred: {str(e)}')
        return False


def is_container_exited(container_name, sudo_pw):
    """Check if docker container"""
    try:
        cmd = f"echo {sudo_pw} | sudo -S docker inspect {container_name} | grep {container_name}"
        output = subprocess.getoutput(cmd)
        if "Error" not in output:
            return True
        return False
    except Exception as e:
        print(f'An error occurred: {str(e)}')
        return False


def is_container_created(container_name, sudo_pw):
    """Check if docker container"""
    try:
        if not grant_docker():
            format_str = " '{{.State.Status}}' "
            output = subprocess.getoutput(
                f"echo {sudo_pw} | sudo -S docker inspect --format= {format_str} {container_name}")
            if "created" in output:
                return True
            return False
        client = docker.from_env()
        container = client.containers.get(container_name)  # 获取指定名称的容器
        return container.status == 'created'  # 检查是否运行中
    except docker.errors.NotFound:
        print(f'There is no container with name: {container_name}')
        return False
    except docker.errors.APIError as e:
        print(f'An error occurred: {str(e)}')
        return False


def remove_docker_container(container_name, sudo_pw):
    """remove docker container
    """
    try:
        cmd = f"echo {sudo_pw} | sudo -S docker rm {container_name}"
        output = subprocess.getoutput(cmd)
        return output
    except Exception as err:
        print(err)


def stop_docker_container(container_name, sudo_pw):
    """stop docker container
    """
    try:
        cmd = f"echo {sudo_pw} | sudo -S docker stop {container_name}"
        output = subprocess.getoutput(cmd)
        return output
    except Exception as err:
        print(err)


def is_docker_network_exist(network_name, sudo_pw):
    """check if specified docker network exists
    """
    try:
        cmd = f" echo {sudo_pw} | sudo -S docker network ls | grep -w {network_name}"
        output = subprocess.getoutput(cmd)
        return "omisense_net" in output
    except Exception as err:
        print(err)
        return False


def remove_docker_network(network_name, sudo_pw):
    """remove docker network
    """
    try:
        cmd = f"echo {sudo_pw} | sudo -S docker network rm {network_name}"
        output = subprocess.getoutput(cmd)
        return output
    except Exception as err:
        print(err)
        return None


def get_docker_compose_version():
    """Get docker compose version, if not exists, return None"""
    try:
        cmd = "docker-compose --version"
        output = subprocess.getoutput(cmd)
        return output
    except Exception as err:
        print(err)
        return None


def check_docker():
    """check docker
    return : is_ready, version_info
    """
    version = get_docker_version()
    if not version:
        return False, "docker is not installed"
    return True, "docker is ready: version " + version


def check_ssh(user_pw):
    """check ssh
    return : is_ready, version_info
    """
    cmd = "ssh -V"
    output = subprocess.getoutput(cmd)
    if "OpenSSL" not in output:
        return False, "openssh-client is not installed"

    if not has_app_in_dpkg(user_pw, "openssh-client"):
        return False, "openssh-client is not installed"
    if not has_app_in_dpkg(user_pw, "openssh-server"):
        return False, "openssh-server is not installed"

    return True, "openssh is ready: " + output


def check_nvidia_tool(user_pw):
    """check nvidia toolkit and tools

    Args:
        user_pw (_type_): _description_
    """
    if is_x86():
        return has_app_in_dpkg(user_pw, "nvidia-container")
    return True


def make_dir(directory, user_pw):
    """Create directory if not exists
     if create drectory failed, raise NotADirectoryError
    """
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception:
            # generally user does not have permission to create directory
            os.system(f"echo {user_pw} | sudo -S mkdir -p {directory}")
            change_mode_to_full_permission(directory, user_pw, recursive=False)
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"{directory} is not a directory")
    return directory


def find_od(sudo_pw):
    """Find if od exists"""
    if get_docker_version() is None:
        return False
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        for container in containers:
            if OD_DOCKER_NAME in container.name:
                return True
    except Exception as err:
        print(err)
        output = subprocess.getoutput(
            f"echo {sudo_pw} |sudo -S docker ps -a|grep {OD_DOCKER_NAME}")
        if OD_DOCKER_NAME in output:
            return True
    return False


def find_web(sudo_pw):
    """Find if web exists"""
    if get_docker_version() is None:
        return False
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        for container in containers:
            if container.name in WEB_DOCKER_NAMES:
                return True
    except Exception as err:
        print(err)
        output = subprocess.getoutput(
            f"echo {sudo_pw} |sudo -S docker ps -a ")
        if any([name for name in WEB_DOCKER_NAMES if name in output]):
            return True
    return False


def clone_label(origin: QLabel) -> QLabel:
    """clone a label

    Args:
        origin (QLabel): _description_

    Returns:
        QLabel: _description_
    """
    new_label = QLabel(origin.parentWidget())
    # 复制文本和样式
    new_label.setText(origin.text())
    new_label.setStyleSheet(origin.styleSheet())
    # 复制字体
    new_label.setFont(origin.font())
    # 复制位置和大小
    new_label.setGeometry(origin.geometry())
    new_label.setAlignment(origin.alignment())
    return new_label


def is_need_input():
    """_summary_
    check current user if need password when use sudo
    """
    result = subprocess.getoutput("echo 0 | sudo -S -k uname")
    if "Linux" in result:
        return False
    return True


def is_x86():
    """check if x86 cpu
    """
    result = subprocess.getoutput("uname -m")
    if "x86" in result:
        return True
    return False


def get_full_version_from_od(od_file_path):
    """get full version from OD compressed file

    Args:
        od_file_path (str): OD compressed file path

    Returns:
        str: full version string
    """
    try:
        file_name = od_file_path.rsplit("/", 1)[1].rsplit(".", 1)[0]
        # find full version od
        tmp = file_name.split(OD_FILE_PREFIX, 1)[1]
        pieces = tmp.split("_")
        rc = ""
        if 'rc' in pieces[1]:
            rc = "_"+pieces[1]
        return pieces[0] + rc
    except Exception as err:
        print(err)
    return ""


def exec_cmd(cmd, inputs: list = None):
    """Execute command
    如果需要交互,则inputs至少放入一个后续指令,
    后续指令需要按照顺序执行,
    可以在迭代器返回时向inputs增加指令
    """
    if inputs:
        with subprocess.Popen(
                cmd, shell=True,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
            while True:
                if len(inputs) > 0:
                    input_data = f'{inputs.pop(0)}\n'
                    output, error = proc.communicate(input=input_data.encode())
                    output_msg = output.strip().decode('utf-8')
                    # NOTE '[sudo] demo 的密码‘  will output to stderr
                    error_msg = error.strip().decode("utf-8")
                    if output_msg:
                        yield TRACE_HEAD+output_msg
                    if error_msg:
                        if "[sudo]" in error_msg:
                            yield error_msg+"\n"
                        else:
                            yield ERROR_HEAD+f"[cmd: {cmd}] \n"+error_msg
                else:
                    output = proc.stdout.readline()
                    yield TRACE_HEAD + output.strip().decode('utf-8')
                if proc.poll() is not None:
                    break
    else:
        # 创建一个子进程，并连接到其 stdout 和 stderr 管道
        with subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
            while True:
                # 读取一行输出
                output = p.stdout.readline().decode('utf-8')
                error = p.stderr.readline().decode('utf-8')
                # 如果输出为空（或者子进程已经结束），则退出循环
                if not output and not error and p.poll() is not None:
                    break
                # 输出获取到的信息
                if output:
                    yield TRACE_HEAD+output
                if error:
                    if "[sudo]" in error:
                        yield error
                    else:
                        yield ERROR_HEAD+f"[cmd: {cmd}] \n"+error


def change_mode_to_full_permission(path, user_pw, recursive=False):
    """Change the mode of given file path to full permission that all user can read/write/execute."""
    try:
        if recursive:
            os.system(f"echo {user_pw} | sudo -S chmod -R 777 {path}")
        else:
            os.system(f"echo {user_pw} | sudo -S chmod 777 {path}")
        mode = os.stat(path).st_mode & 0o777
        return mode == 0o777
    except Exception as err:
        print(err)
        return False


def directory_test(directory, user_pw):
    """Check whether files can be created under the path and 
        whether the path supports POSIX permissions

    Args:
        path (_type_): _description_
        user_pw (_type_): _description_
    """
    # create a test file in the directory
    test_file_name = f"{time.time_ns()}.test"
    test_file_path = os.path.join(directory, test_file_name)
    try:
        pathlib.Path.touch(test_file_path)
    except Exception:
        os.system(f"echo {user_pw}| sudo -S touch {test_file_path}")

    if not os.path.isfile(test_file_path):
        raise FileNotFoundError(
            f"Cannot create file in directory : {directory}")

    if not change_mode_to_full_permission(test_file_path, user_pw):
        msg = "Unable to modify file permissions in " + directory + \
            "\n Please ensure that the file system where the path is located supports POSIX permissions"
        raise PermissionError(msg)

    # remove the test file
    os.system(f"echo {user_pw}| sudo -S rm -f {test_file_path}")


class CommandTask(QThread):
    """ Do backend shell task"""
    output_txt = pyqtSignal(str)
    commands = []
    need_input = False
    input_msg = ""

    def set_command(self, cmd: list):
        """Set command"""
        self.commands = cmd

    def run(self):
        """Self-explanatory"""
        if self.need_input:
            with subprocess.Popen(
                    " ".join(self.commands), shell=True,
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as proc:
                input_data = f'{self.input_msg}\n'
                output, _ = proc.communicate(input=input_data.encode())
                self.emit_msg(output.strip().decode())
        else:
            # 创建一个子进程，并连接到其 stdout 和 stderr 管道
            with subprocess.Popen(self.commands,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE) as p:
                while True:
                    # 读取一行输出
                    output = p.stdout.readline()
                    # 如果输出为空（或者子进程已经结束），则退出循环
                    if not output and p.poll() is not None:
                        break
                    # 输出获取到的信息
                    if output:
                        self.emit_msg(output.strip().decode('utf-8'))
                # 在所有输出都处理完成后，获取返回码
                # rc = p.poll()
                # if rc != 0:

    def emit_msg(self, msg: str):
        """Self-explanatory"""
        self.output_txt.emit(msg)

def modify_journal_config(config_file, items: dict, user_pw):
    try:
        with open(config_file, 'r') as file:
            lines = file.readlines()
        new_lines = []
        for line in lines:
            found_key = False
            for key in items.keys():
                if key in line:
                    found_key = True
                    continue
            if not found_key:
                new_lines.append(line)
        new_lines.extend([f"{key}={value}\n" for key, value in items.items()])
        with open(config_file, 'w') as file:
            file.writelines(new_lines)
        os.system(f"echo {user_pw} | sudo -S systemctl restart systemd-journald")
        return 0
    except FileNotFoundError:
        return 1
    except PermissionError:
        return 2
    except:
        return -1