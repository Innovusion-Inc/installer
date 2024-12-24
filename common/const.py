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

import os
import glob
import sys
import re
import yaml
# import logger
"""Const variable"""
# region messages
# ***Use spaces instead of underscores to concatenate words***  e.g.  "Virtual Loop"
CUDA_BASE_IMAGE_TAR_X86 = "base_runtime_v2_x86.tar"
CUDA_BASE_IMAGE_TAR_ARM = "base_runtime_v2_arm.tar"
CUDA_BASE_IMAGE_NAME_X86 = "innovusion/omnisense_rt_vl:v1"
CUDA_BASE_IMAGE_TAG_NAME_X86 = "virtual_loop:x86"
CUDA_BASE_IMAGE_NAME_ARM = "innovusion/orin_rt_vl:v1"
CUDA_BASE_IMAGE_TAG_NAME_ARM = "virtual_loop:arm"

OD_FILE_PATTERN = "*_OD_"
SCENE_FILE_SUFFIX = "Conf"
PACKAGE_DIR = os.path.dirname(sys.executable) + "/package/"
pattern = os.path.join(PACKAGE_DIR, OD_FILE_PATTERN+"*.tgz")

config_file = os.path.join(PACKAGE_DIR, "install_config.yaml")
if os.path.exists(config_file):
    try:
        with open(config_file, 'r') as file:
            config_data = yaml.safe_load(file)

        # 获取需要的 key 值
        key_value = config_data.get("CUDA_BASE_IMAGE_TAR_X86")
        if key_value:
            CUDA_BASE_IMAGE_TAR_X86 = key_value
        else:
            print("CUDA_BASE_IMAGE_TAR_X86 do not exist , use default vlue")

        key_value = config_data.get("CUDA_BASE_IMAGE_TAR_ARM")
        if key_value:
            CUDA_BASE_IMAGE_TAR_ARM = key_value
        else:
            print("CUDA_BASE_IMAGE_TAR_ARM do not exist , use default vlue")

        key_value = config_data.get("CUDA_BASE_IMAGE_NAME_X86")
        if key_value:
            CUDA_BASE_IMAGE_NAME_X86 = key_value
        else:
            print("CUDA_BASE_IMAGE_NAME_X86 do not exist , use default vlue")

        key_value = config_data.get("CUDA_BASE_IMAGE_TAG_NAME_X86")
        if key_value:
            CUDA_BASE_IMAGE_TAG_NAME_X86 = key_value
        else:
            print("CUDA_BASE_IMAGE_TAG_NAME_X86 do not exist , use default vlue")

        key_value = config_data.get("CUDA_BASE_IMAGE_NAME_ARM")
        if key_value:
            CUDA_BASE_IMAGE_NAME_ARM = key_value
        else:
            print("CUDA_BASE_IMAGE_NAME_ARM do not exist , use default vlue")

        key_value = config_data.get("CUDA_BASE_IMAGE_TAG_NAME_ARM")
        if key_value:
            CUDA_BASE_IMAGE_TAG_NAME_ARM = key_value
        else:
            print("CUDA_BASE_IMAGE_TAG_NAME_ARM do not exist , use default vlue")

    except yaml.YAMLError as exc:
        print("yaml format wrong , use default values. error:", exc)

    except Exception as e:
        print("other exception when reading yaml abord config , use default values. error::", e)
else:
    print("package/install_config.yaml do not exist , use default values")


files = glob.glob(pattern)
if len(files) > 0:
    od_file_path = files[0]
od_file = od_file_path.rsplit("/", 1)[1].rsplit(".", 1)[0]
# print("od_file", od_file)
# logger.infor("od_file ="+od_file)
BRAND_NAME = od_file.split('_')[0]
# logger.infor("BRAND_NAME ="+BRAND_NAME)
PRODUCT_NAME = re.search(r'_(.*?)_OD', od_file).group(1)
# print("BRAND_NAME", BRAND_NAME)
# print("PRODUCT_NAME", PRODUCT_NAME)
WEB_FILE_PREFIX = BRAND_NAME+"_"+PRODUCT_NAME+"_WEB_"
OD_FILE_PREFIX = BRAND_NAME+"_"+PRODUCT_NAME+"_OD_"
# print("WEB_FILE_PREFIX", WEB_FILE_PREFIX)
# print("OD_FILE_PREFIX", OD_FILE_PREFIX)

# logger.infor("PRODUCT_NAME ="+PRODUCT_NAME)
# PRODUCT_NAME = "*"
# BRAND_NAME = "*"   # OM
INSTALL_WINDOW_TEXT = PRODUCT_NAME+" Install"
UNINSTALL_WINDOW_TEXT = PRODUCT_NAME+" Uninstall"
INSTALL_FAILED = "Installation failed"
UNINSTALL_FAILED = "Uninstallation failed"
INSTALL_SUCCESS = "Installation successful"
UNINSTALL_SUCCESS = "Uninstallation successful"
INSTALL_ERROR_EXIT = "Aborted"
INSTALL_ERROR_LOCAL_IP_NOT_FOUND = "Network interface controller IP not found!"

UNINSTALL_NO_NEED = "No need to uninstall"

DOCKER_IS_NOT_INSTAL = "Docker is not installed!"
OPENSSH_IS_NOT_INSTAL = "OpenSSH is not installed!"
NVIDIA_TOOLKIT_IS_NOT_INSTAL = "NVIDIA container toolkit is not installed!"
CONTINUE_INSTALL_MSG = "Click Yes to attempt fixing the issues and continue with the installation."


IP_ERROR_MSG = "This is not a valid ipv4 address: %s"


UNINSTALL_ALERT_MSG = "The software will be removed from this device and cannot be undone"

INSTALL_ERROR_NEED_SPACE = "At least %s GB of available disk space is required"
INSTALL_ERROR_NOT_ENOUGH_SPACE = "Please check whether there is enough available space in the path: %s"
INSTALL_ERROR_SSD = "Installation may be slow under the current path."


PLEASE_ENTER_PASSWORD = "Please enter the password for the user:"
ERROR_PASSWORD = "Incorrect password."

OD_PACKAGE_NOT_FOUND = "OD package not found"
WEB_PACKAGE_NOT_FOUND = "Web package not found"

# endregion messages

# region message head
ERROR_HEAD = "[ERROR] "
WARNING_HEAD = "[WARNING] "
INFO_HEAD = "[INFO] "
START_HEAD = "[START] ----  "
SUCCESS_HEAD = "[DONE]  ---- "
END_HEAD = "[END] "
TRACE_HEAD = "[TRACE] "
# endregion message head


# region package files


JDK_TAR_X86 = "jre8_x86.tar"
MYSQL_TAR_X86 = "mysql_x86.tar"
REDIS_TAR_X86 = "redis_x86.tar"
NGINX_TAR_X86 = "nginx_x86.tar"
# BASE_TAR_X86 = "base.tar"

JDK_TAR_ARM = "jre8_arm.tar"
MYSQL_TAR_ARM = "mysql_arm.tar"
REDIS_TAR_ARM = "redis_arm.tar"
NGINX_TAR_ARM = "nginx_arm.tar"
# BASE_TAR_ARM = "base.tar"


DOCKER_DEB_X86 = "containerd.io_1.4.12-1_amd64.deb"
DOCKER_CE_CLI_X86 = "docker-ce-cli_20.10.12~3-0~ubuntu-focal_amd64.deb"
DOCKER_CE_X86 = "docker-ce_20.10.12~3-0~ubuntu-focal_amd64.deb"

DOCKER_DEB_ARM = "containerd.io_1.4.12-1_arm64.deb"
DOCKER_CE_CLI_ARM = "docker-ce-cli_20.10.12_3-0_ubuntu-focal_arm64.deb"
DOCKER_CE_ARM = "docker-ce_20.10.12_3-0_ubuntu-focal_arm64.deb"

SSH_CLI_DEB_X86 = "openssh-client_8.2p1-4ubuntu0.9_amd64.deb"
SSH_SERVER_DEB_X86 = "openssh-server_8.2p1-4ubuntu0.9_amd64.deb"
SSH_SFTP_DEB_X86 = "openssh-sftp-server_8.2p1-4ubuntu0.9_amd64.deb"

SSH_CLI_DEB_ARM = "openssh-client_8.2p1-4ubuntu0.10_arm64.deb"
SSH_SERVER_DEB_ARM = "openssh-server_8.2p1-4ubuntu0.10_arm64.deb"
SSH_SFTP_DEB_ARM = "openssh-sftp-server_8.2p1-4ubuntu0.10_arm64.deb"

# endregion package files

# region path configs
WEB_REPOS_OMNISENSE_PATH = "/home/seyond_user/repos/omisense"
WEB_REPOS_DOCKER_PATH = "/home/seyond_user/repos/omisense/docker"
WEB_REPOS_PATH = "/home/seyond_user/repos"
OD_DOCKER_PATH = "/home/seyond_user/od"

WEB_DOCKER_FILE_PATH = "/home/seyond_user/web"
# WEB_DOCKER_FILE_PATH = ""

#  keep the directory when uninstall
DATA_REMAIN_PATH = "/home/seyond_user/data"

# endregion path configs


# region docker
WEB_CITY_DOCKER_NAMES = [
    "city-admin",
]
WEB_BASE_DOCKER_NAMES = [
    "mysql-sc",
    "nginx-web-sc",
    "redis-sc"
]
NGINX_WEB_DOCKER_NAME = "nginx-web-sc"  # use for uninstall

WEB_DOCKER_NET_NAME = "omisense_net"


OD_DOCKER_NAME = "OmniVidi_VL"

WEB_DOCKER_BASE_IMAGE_NAMES = [
    "redis:6.2.6",
    "mysql:8.0.27",
    "nginx:1.21.3",
    "anapsix/alpine-java:8u202b08_jdk",
]

REMOVE_IMG_BEFORE_DEPLOY_ARM = [
    "docker-nginx-web:latest",
    "vom-nginx-web:latest",
]

REMOVE_IMG_BEFORE_DEPLOY_X86 = [
    "docker_nginx-web:latest",
    "vom_nginx-web:latest",
]

WEB_DOCKER_IMAGE_NAMES_ARM = [
    "city-admin:latest",
    "redis:6.2.6",
    "mysql:8.0.27",
    "nginx:1.21.3",
    "anapsix/alpine-java:8u202b08_jdk",
    "vom-nginx-web:latest",
]

WEB_DOCKER_IMAGE_NAMES_X86 = [
    "city-admin:latest",
    "redis:6.2.6",
    "mysql:8.0.27",
    "nginx:1.21.3",
    "anapsix/alpine-java:8u202b08_jdk",
    "vom_nginx-web:latest",
]
# endregion docker

WEB_PING_URL = "http://localhost:80/prod-api/getRsaPrivateKey"
WEB_URL = "http://localhost/#/login"

MIN_FREE_GB = 16

# region log
DOCKER_MAX_SIZE = "10m"
DOCKER_MAX_FILE = "5"

WATCH_LOG_SYS_DIRS = ["/var/log"]
WATCH_LOG_SYS_DIRS_DAYS_TO_KEEPS = [30]
WATCH_LOG_SYS_DIRS_MAX_SIZES = [2147483648] # 2GB
WATCH_LOG_INSTALL_DIRS = ["data/cron", "data/log", "data/running_output"]
WATCH_LOG_INSTALL_DIRS_DAYS_TO_KEEP = [15, 15, 15]
WATCH_LOG_INSTALL_DIRS_MAX_SIZE = [1073741824, 5368709120, 1073741824] # 1GB
# endregion log

# region core
CORE_MAX_SIZE = 2097152
CORE_FILEPATH = "/apollo/data/core/core"
#endregion

# region journal
JOURNAL_CONFIG = {"Storage": "persistent",
                  "SystemMaxUse": "1G",
                  "SystemKeepFree": "500M",
                  "MaxFileSec": "1month"}
# endregion