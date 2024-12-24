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

import logging
from datetime import datetime
import os
import shutil


def get_logger(log_dir, name):
    """Self-explanatory..."""
    now_date = datetime.now().strftime("%Y-%m-%d-%H:%M")
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    log_path = os.path.join(log_dir, name+"-"+now_date+".log")
    cur_logger = logging.getLogger(name)
    cur_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(
        filename=log_path, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        '[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    cur_logger.addHandler(file_handler)
    return cur_logger


def save_log_to(directory, logger_name):
    """Save log"""
    try:
        if os.path.isdir(directory) is False:
            os.mkdir(directory)
        log_path = logging.getLogger(logger_name).handlers[0].baseFilename
        shutil.copy(log_path, directory)
        return True
    except Exception as err:
        print(err)
        return False


def save_log_as(full_path, logger_name):
    """Save log"""
    try:
        log_path = logging.getLogger(logger_name).handlers[0].baseFilename
        shutil.copy(log_path, full_path)
        return True, ""
    except Exception as err:
        return False, f"{err}"
