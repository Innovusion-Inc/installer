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

""" Handle uninstall task"""
import re
import os
import subprocess
import time
import json
import shutil
# import stat
from PyQt5.QtCore import (
    QThread,
    pyqtSignal)

# import sys
# sys.path.append("/home/demo/code-repo/smart_city_installer")

from common.const import (
    SUCCESS_HEAD,
    INFO_HEAD,
    END_HEAD,
    ERROR_HEAD,
    START_HEAD,
    WEB_REPOS_DOCKER_PATH,
    WEB_REPOS_OMNISENSE_PATH,
    WEB_DOCKER_FILE_PATH,
    WEB_REPOS_PATH,
    DATA_REMAIN_PATH,
    NGINX_WEB_DOCKER_NAME,
    WEB_CITY_DOCKER_NAMES,
    WEB_BASE_DOCKER_NAMES,
    WEB_DOCKER_NET_NAME,
    OD_DOCKER_PATH,
    OD_DOCKER_NAME
)
from common.function import (
    exec_cmd,
    is_container_exited,
    is_docker_network_exist,
    remove_docker_network,
    remove_dir, is_x86,
    remove_docker_container,
    stop_docker_container,
    change_mode_to_full_permission
)
IS_X86 = is_x86()
if IS_X86:
    from common.const import (
        WEB_DOCKER_IMAGE_NAMES_X86 as WEB_DOCKER_IMAGES,
        CUDA_BASE_IMAGE_TAG_NAME_X86 as CUDA_BASE_IMAGE_TAG,
    )
else:
    from common.const import (
        WEB_DOCKER_IMAGE_NAMES_ARM as WEB_DOCKER_IMAGES,
        CUDA_BASE_IMAGE_TAG_NAME_ARM as CUDA_BASE_IMAGE_TAG,
    )


class CityUninstallTask():
    """Self-explanatory"""
    basedir = ""
    user_passwd = ""

    def uninstall_web(self):
        """Uninstall web component"""
        yield f"{START_HEAD}uninstall WEB ..... "
        # step 1 . remove web docker and reset network
        for output in self.__remove_web_docker():
            yield output
        yield f"{INFO_HEAD}Remove web service and rel network"
        # step2. delete seyond_user
        for output in self.__del_inno_user():
            yield output
        yield f"{INFO_HEAD}Delete seyond_user"
        # step3. remove docker volume directory
        self.__remove_web_docker_volume()
        yield f"{INFO_HEAD}Remove docker volume directory"
        # step4. remove web docker images
        for output in self.__remove_web_docker_images():
            yield output

    def uninstall_od(self):
        """Uninstall od component"""
        # remove docker container
        yield "Uninstall od ..... "
        yield "stop crontab"
        for line in self.__stop_crontab():
            yield line
        yield "stop crontab done"
        if is_container_exited(OD_DOCKER_NAME, self.user_passwd):
            msg = f"{INFO_HEAD}Find container: {OD_DOCKER_NAME}"
            yield msg
            print("Container stoped: " +
                  stop_docker_container(OD_DOCKER_NAME, self.user_passwd))
            print("Container removed: " +
                  remove_docker_container(OD_DOCKER_NAME, self.user_passwd))
        remove_dir(OD_DOCKER_PATH, self.user_passwd)
        yield f"Remove od data path: {OD_DOCKER_PATH}"
        output = subprocess.getoutput(
            f"echo {self.user_passwd} | sudo -S -k docker rmi {CUDA_BASE_IMAGE_TAG}")
        yield output
        yield f"Remove OD docker image: {CUDA_BASE_IMAGE_TAG}"
        yield "Uninstall od done."

    def __remove_web_docker(self):
        """Remove web docker"""
        web_docker_containers = [
            *WEB_CITY_DOCKER_NAMES, *WEB_BASE_DOCKER_NAMES]
        # remove container
        for name in web_docker_containers:
            if is_container_exited(name, self.user_passwd):
                msg = f"{INFO_HEAD}Find container: {name}"
                yield msg
                print("Container stoped: " +
                      stop_docker_container(name, self.user_passwd))
                print("Container removed: " +
                      remove_docker_container(name, self.user_passwd))
        # remove docker network omisense_net
        if is_docker_network_exist(WEB_DOCKER_NET_NAME, self.user_passwd):
            yield f"{INFO_HEAD}Find docker network: {WEB_DOCKER_NET_NAME}, remove it"
            print(remove_docker_network(WEB_DOCKER_NET_NAME, self.user_passwd))

    def __del_inno_user(self):
        """Delete seyond_user"""
        if 'seyond_user' in os.popen('getent passwd').read():
            for output in exec_cmd(
                    "sudo -S -k deluser seyond_user", [self.user_passwd]):
                yield output
        for output in exec_cmd(
            "sudo -S -k sed -i '/seyond_user ALL = (ALL) NOPASSWD: ALL/d' /etc/sudoers",
                [self.user_passwd]):
            yield output

    def __remove_web_docker_volume(self):
        """Remove web docker volume"""
        remove_dir(WEB_REPOS_DOCKER_PATH, self.user_passwd)
        remove_dir(WEB_REPOS_OMNISENSE_PATH, self.user_passwd)
        remove_dir(WEB_REPOS_PATH, self.user_passwd)
        remove_dir(WEB_DOCKER_FILE_PATH, self.user_passwd)

    def __remove_web_docker_images(self):
        """remove web docker images
        """
        for image in WEB_DOCKER_IMAGES:
            cmd = f"sudo -S docker rmi {image}"
            for output in exec_cmd(cmd, [self.user_passwd]):
                print(output)
        yield "Remove web docker images. Done."
    
    def __stop_crontab(self):
        watch_log=os.path.join(OD_DOCKER_PATH, "SW/watch_log.sh")
        temp_cron = "current_cron"
        
        cmd_get_cron = f"echo {self.user_passwd} | sudo -S crontab -l > {temp_cron}"
        output = subprocess.getoutput(cmd_get_cron)
        yield output
            
        cmd = f"echo {self.user_passwd} | sudo -S sed -i '\\|{watch_log}|d' {temp_cron}"
        result = subprocess.getoutput(cmd)
        yield result
        
        cmd_stop_cron = f"echo {self.user_passwd} | sudo -S crontab \"{temp_cron}\""
        output = subprocess.getoutput(cmd_stop_cron)
        yield output
        
        cmd = f"rm {temp_cron}"
        result = subprocess.getoutput(cmd)
        yield result


class CityUninstall(QThread):
    """Uninstall smartcity od or web."""
    message = pyqtSignal(str)
    progress = pyqtSignal(int)
    progress_total = 0
    basedir = ""
    user_passwd = ""
    task = CityUninstallTask()
    uninstall_web = False
    uninstall_od = False
    installed_path = ""
    preserve_data = False

    def set_pw(self, pw):
        """Set user password"""
        self.user_passwd = pw
        self.task.user_passwd = pw

    def increase_progress(self, length):
        """Self-explanatory"""
        if (self.progress_total + length) > 99:
            length = 99 - self.progress_total
        self.progress.emit(length)
        self.progress_total += length

    def increase_progress_to_end(self):
        """Self-explanatory"""
        if self.progress_total < 100:
            self.progress.emit(100 - self.progress_total)
            self.progress_total = 100

    def emit_msg(self, msg):
        """Emit message"""
        print(msg)
        self.message.emit(msg)
        self.increase_progress(2)

    def _find_docker_mount(self, docker_name, dest_key, path_tail):
        """find docker mount path
        """
        cmd = f"echo {self.user_passwd} | sudo -S docker inspect {docker_name}" + \
            " --format '{{json .Mounts}}' "
        bind_json_str = subprocess.getoutput(cmd)
        mount_path = ""
        try:
            bind_json_str = re.sub(r'\[\w+\] password.*?: ', '', bind_json_str)
            bind_array = json.loads(bind_json_str)
            for mount in bind_array:
                if mount["Destination"] == dest_key:
                    print(mount["Source"])
                    mount_path = mount["Source"][:-
                                                 len(dest_key)]
                    if not mount_path.endswith(path_tail):
                        mount_path = ""
                    else:
                        mount_path = mount_path[:-len(
                            path_tail)]
                    break
        except json.decoder.JSONDecodeError:
            print("json deserialize failed")
        except Exception as err:
            print(err)
        return mount_path

    def get_installed_path(self):
        """Get installed path"""
        # find web nginx config path
        self.installed_path = self._find_docker_mount(
            NGINX_WEB_DOCKER_NAME, "/docker/nginx/html", "/web")
        if self.installed_path != "":
            return True
        # find od file
        self.installed_path = self._find_docker_mount(
            OD_DOCKER_NAME, "/apollo", "/od")
        if self.installed_path != "":
            return True
        return False

    def compress_and_move(self, src_dir, dest_dir, archive_name):
        """
        压缩 src_dir 目录并将压缩文件移动到 dest_dir。
        :param src_dir: 要压缩的源目录。
        :param dest_dir: 压缩文件的目标目录。
        :param archive_name: 压缩文件的名称（不包含扩展名）。
        """
        # 创建压缩文件（默认为 .zip 格式）
        archive_path = shutil.make_archive(archive_name, 'zip', src_dir)
        # 构造最终的目标路径（包括文件名）
        final_path = os.path.join(dest_dir, os.path.basename(archive_path))
        # 移动压缩文件到目标目录
        shutil.move(archive_path, final_path)
        # print(f"Archive moved to {final_path}")

    def copy_backup(self, source_path, sub_folder, need_cmps=False):

        # cmd = f" sudo -S -k cp -r {source_path}/* {DATA_REMAIN_PATH}/ai_model/"
        # for output in exec_cmd(cmd, [self.user_passwd]):
        #     yield output
        # self.emit_msg("cmd:"+cmd)
        if os.path.exists(source_path):
            self.emit_msg("source path:"+source_path)
            self.emit_msg("backup path:" +
                          DATA_REMAIN_PATH+"/"+sub_folder+"/")
            # if not change_mode_to_full_permission(source_path, self.user_passwd):
            #     yield ERROR_HEAD + "Unable to modify file permissions for " + source_path
            os.system(
                f"echo {self.user_passwd} | sudo -S chmod -R 777 {source_path}")

            os.system(
                f"echo {self.user_passwd} | sudo -S chmod -R 777 {DATA_REMAIN_PATH}")

            if not os.path.exists(DATA_REMAIN_PATH+"/"+sub_folder+"/"):
                os.makedirs(DATA_REMAIN_PATH+"/"+sub_folder+"/")

            destination_path = DATA_REMAIN_PATH+"/"+sub_folder+"/"
            if need_cmps:
                self.compress_and_move(
                    source_path, destination_path, sub_folder)
            else:
                for item in os.listdir(source_path):
                    source_item = os.path.join(source_path, item)
                    destination_item = os.path.join(destination_path, item)
                    if os.path.isfile(source_item):
                        # os.chmod(source_item, stat.S_IWRITE)
                        shutil.copy2(source_item, destination_item)
                    elif os.path.isdir(source_item):
                        shutil.copytree(
                            source_item, destination_item, dirs_exist_ok=True)
            self.emit_msg(destination_path+" backup finish .")
        else:
            self.emit_msg(source_path + " do not exist!")

    # def copy_matrix(self, matrix_path):
    #     # cmd = f"echo {user_pw} | sudo -S -k cp -r {matrix_path}/* {DATA_REMAIN_PATH}/matrix/"
    #     # for output in exec_cmd(cmd, [self.user_passwd]):
    #     #     yield output
    #     if os.path.exists(matrix_path):
    #         self.emit_msg("matrix path :"+matrix_path)
    #         destination_path = DATA_REMAIN_PATH+"/matrix/"
    #         # if not change_mode_to_full_permission(matrix_path, self.user_passwd):
    #         #     yield ERROR_HEAD + "Unable to modify file permissions for " + matrix_path
    #         os.system(
    #             f"echo {self.user_passwd} | sudo -S chmod -R 777 {matrix_path}")
    #         if not os.path.exists(destination_path):
    #             os.makedirs(destination_path)
    #         self.emit_msg("matrix backup path :"+destination_path)
    #         for item in os.listdir(matrix_path):
    #             source_item = os.path.join(matrix_path, item)
    #             destination_item = os.path.join(destination_path, item)
    #             if os.path.isfile(source_item):
    #                 # os.chmod(source_item, stat.S_IWRITE)
    #                 # cmd = f"echo {self.user_passwd} | sudo chmod  777 {source_item}"
    #                 # self.emit_msg("check here ***  cmd: "+cmd)
    #                 # result = subprocess.getoutput(cmd)
    #                 # self.emit_msg("check here ***  result: "+result)
    #                 shutil.copy2(source_item, destination_item)
    #             elif os.path.isdir(source_item):
    #                 shutil.copytree(
    #                     source_item, destination_item, dirs_exist_ok=True)
    #         self.emit_msg("matrix backuped .")

    def run(self):
        """uninstall start run"""
        try:
            global OD_DOCKER_PATH
            global WEB_DOCKER_FILE_PATH
            global WEB_REPOS_OMNISENSE_PATH
            global WEB_REPOS_DOCKER_PATH
            global WEB_REPOS_PATH
            global DATA_REMAIN_PATH
            if self.get_installed_path():
                OD_DOCKER_PATH = f"{self.installed_path}/od"
                WEB_DOCKER_FILE_PATH = f"{self.installed_path}/web"
                WEB_REPOS_PATH = f"{self.installed_path}/repos"
                WEB_REPOS_OMNISENSE_PATH = f"{self.installed_path}/repos/omisense"
                WEB_REPOS_DOCKER_PATH = f"{self.installed_path}/repos/omisense/docker"
                DATA_REMAIN_PATH = f"{self.installed_path}/data"
            self.copy_backup(
                f"{OD_DOCKER_PATH}/SW/modules/omnisense/segmentation/v2x_mvp_ai_model/model/centerpoint_pillar_sightnet/", "ai_model")
            self.copy_backup(
                f"{OD_DOCKER_PATH}/SW/modules/omnisense/launch/calib_matrices/", "matrix")
            self.copy_backup(
                f"{WEB_DOCKER_FILE_PATH}/docker/mysql/", "mysql", True)
            time.sleep(1)
            if self.uninstall_od:
                self.emit_msg(f"{INFO_HEAD}Uninstall OD start ..... ")
                for echo_msg in self.task.uninstall_od():
                    self.emit_msg(echo_msg)
                self.emit_msg(SUCCESS_HEAD + "Uninstall OD done. ")
                if not self.preserve_data:
                    remove_dir(DATA_REMAIN_PATH, self.user_passwd)
            if self.progress_total < 34:
                self.increase_progress(34-self.progress_total)
            if self.uninstall_web:
                self.emit_msg(f"{INFO_HEAD}Uninstall WEB  start ..... ")
                for echo_msg in self.task.uninstall_web():
                    self.emit_msg(echo_msg)
                self.emit_msg(SUCCESS_HEAD+"Uninstall WEB done.")
            if self.progress_total < 68:
                self.increase_progress(68-self.progress_total)
            if self.uninstall_web and self.uninstall_od and (not self.preserve_data):
                remove_dir("/home/seyond_user", self.user_passwd)
            self.emit_msg(END_HEAD + "Uninstall finish ")
            self.increase_progress_to_end()
        except Exception as err:
            self.emit_msg(ERROR_HEAD + str(err))


if __name__ == "__main__":
    ct = CityUninstallTask()
    ct.user_passwd = "demo"
    for out in ct.uninstall_web():
        print(out)
