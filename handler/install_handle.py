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

"""Handle install"""

import os
import re
from time import sleep
import shutil
import subprocess
import requests
import yaml
import json
import sys

from PyQt5.QtCore import (
    QThread,
    pyqtSignal)

# import sys
# sys.path.append("/home/demo/code-repo/smart_city_installer")

from common.const import (
    PRODUCT_NAME,
    SUCCESS_HEAD,
    WARNING_HEAD,
    END_HEAD,
    INFO_HEAD,
    ERROR_HEAD,
    START_HEAD,
    WEB_REPOS_OMNISENSE_PATH,
    WEB_REPOS_DOCKER_PATH,
    OD_DOCKER_PATH,
    WEB_CITY_DOCKER_NAMES,
    WEB_BASE_DOCKER_NAMES,
    WEB_PING_URL,
    OD_DOCKER_NAME,
    TRACE_HEAD,
    WEB_DOCKER_FILE_PATH,
    SCENE_FILE_SUFFIX,
    WEB_FILE_PREFIX,
    OD_FILE_PREFIX,
    DATA_REMAIN_PATH,
    WEB_DOCKER_BASE_IMAGE_NAMES,
    WEB_DOCKER_NET_NAME,
    DOCKER_MAX_SIZE,
    DOCKER_MAX_FILE,
    WATCH_LOG_SYS_DIRS,
    WATCH_LOG_SYS_DIRS_DAYS_TO_KEEPS,
    WATCH_LOG_SYS_DIRS_MAX_SIZES,
    WATCH_LOG_INSTALL_DIRS,
    WATCH_LOG_INSTALL_DIRS_DAYS_TO_KEEP,
    WATCH_LOG_INSTALL_DIRS_MAX_SIZE,
    CORE_FILEPATH,
    CORE_MAX_SIZE,
    JOURNAL_CONFIG,
)
from common.function import (
    find_od_tgz,
    get_full_version_from_od,
    find_web_tgz,
    find_scene_tgz,
    is_need_input,
    exec_cmd,
    make_dir,
    directory_test,
    is_container_up,
    remove_dir,
    is_container_exited,
    remove_docker_container,
    stop_docker_container,
    is_docker_image_exist,
    get_all_docker_image,
    is_x86,
    check_docker,
    check_ssh,
    change_mode_to_full_permission,
    get_file_path,
    apt_install,
    is_container_created,
    append_line,
    set_core_pattern,
    modify_journal_config,
    MD5Checker)

IS_X86 = is_x86()
if IS_X86:
    from common.const import (
        JDK_TAR_X86 as JDK_TAR,
        MYSQL_TAR_X86 as MYSQL_TAR,
        REDIS_TAR_X86 as REDIS_TAR,
        NGINX_TAR_X86 as NGINX_TAR,
        CUDA_BASE_IMAGE_TAR_X86 as CUDA_BASE_TAR_NAME,
        CUDA_BASE_IMAGE_NAME_X86 as CUDA_BASE_IMAGE_NAME,
        CUDA_BASE_IMAGE_TAG_NAME_X86 as CUDA_BASE_IMAGE_TAG_NAME,
        DOCKER_DEB_X86 as DOCKER_DEB,
        DOCKER_CE_CLI_X86 as DOCKER_CE_CLI,
        DOCKER_CE_X86 as DOCKER_CE,
        SSH_CLI_DEB_X86 as SSH_CLI_DEB,
        SSH_SERVER_DEB_X86 as SSH_SERVER_DEB,
        SSH_SFTP_DEB_X86 as SSH_SFTP_DEB,
        REMOVE_IMG_BEFORE_DEPLOY_X86 as RM_IMG)
else:
    from common.const import (
        JDK_TAR_ARM as JDK_TAR,
        MYSQL_TAR_ARM as MYSQL_TAR,
        REDIS_TAR_ARM as REDIS_TAR,
        NGINX_TAR_ARM as NGINX_TAR,
        CUDA_BASE_IMAGE_TAR_ARM as CUDA_BASE_TAR_NAME,
        CUDA_BASE_IMAGE_NAME_ARM as CUDA_BASE_IMAGE_NAME,
        CUDA_BASE_IMAGE_TAG_NAME_ARM as CUDA_BASE_IMAGE_TAG_NAME,
        DOCKER_DEB_ARM as DOCKER_DEB,
        DOCKER_CE_CLI_ARM as DOCKER_CE_CLI,
        DOCKER_CE_ARM as DOCKER_CE,
        SSH_CLI_DEB_ARM as SSH_CLI_DEB,
        SSH_SERVER_DEB_ARM as SSH_SERVER_DEB,
        SSH_SFTP_DEB_ARM as SSH_SFTP_DEB,
        REMOVE_IMG_BEFORE_DEPLOY_ARM as RM_IMG)

LOGGER = None


def restart_docker(user_pw):
    """restart docker"""
    cmd = "sudo -S systemctl restart docker"
    for output in exec_cmd(cmd, [user_pw]):
        print(output)
        LOGGER.debug(output)
    cmd = "systemctl is-active docker"
    wait_count = 10
    while subprocess.getoutput(cmd) != "active":
        print("Docker restarting ...")
        LOGGER.debug("Docker restarting ...")
        sleep(2)
        wait_count -= 1
        if wait_count <= 0:
            return f"{ERROR_HEAD} Docker restart failed."
    return f"{INFO_HEAD} Docker has restarted successfully."


def check_nvidia_smi(base_image, user_pw):
    """Check if nvidia-toolkit is ready

    Args:
        user_pw (_type_): _description_
    """
    cmd = f"sudo -S docker run --gpus all --rm {base_image} nvidia-smi 2>&1"
    results = ""
    for output in exec_cmd(cmd, [user_pw]):
        results += output
        print(output)
    LOGGER.debug(results)
    if "Error" in results:
        return False
    return True


def install_nvidia_smi(base_env_dir, base_image, user_pw):
    """Check if nvidia-smi is available in the specified Docker image"""
    yield "check nvidia-smi ...."
    if check_nvidia_smi(base_image, user_pw):
        yield f"{SUCCESS_HEAD} nvidia-smi for docker is ready."
        return
    yield f"{INFO_HEAD} gpus not support, start install nvidia-cuda-toolkit......"
    # get ubuntu version
    cmd = "lsb_release -d"
    version_info = subprocess.getoutput(cmd)
    if "20.04" not in version_info:
        yield f"{INFO_HEAD} apt installation for nvidia-toolkit will be attempted ...... \n {version_info}"
        apt_install(user_pw,
                    ["nvidia-container-toolkit",
                     "libnvidia-container-tools",
                     "nvidia-container-toolkit-base",
                     "libnvidia-container1"], LOGGER)
    else:
        # install nvidia-cuda-toolkit offline
        cmd = f"sudo -S dpkg -i {base_env_dir}libnvidia-container1_1.13.4-1_amd64.deb"
        for output in exec_cmd(cmd, [user_pw]):
            print(output)
            LOGGER.debug(output)
        cmd = f"sudo -S dpkg -i {base_env_dir}nvidia-container-toolkit-base_1.13.4-1_amd64.deb"
        for output in exec_cmd(cmd, [user_pw]):
            print(output)
            LOGGER.debug(output)
        cmd = f"sudo -S dpkg -i {base_env_dir}libnvidia-container-tools_1.13.4-1_amd64.deb"
        for output in exec_cmd(cmd, [user_pw]):
            print(output)
            LOGGER.debug(output)
        cmd = f"sudo -S dpkg -i {base_env_dir}nvidia-container-toolkit_1.13.4-1_amd64.deb"
        for output in exec_cmd(cmd, [user_pw]):
            print(output)
            LOGGER.debug(output)
    yield f"{INFO_HEAD} install nvidia-cuda-toolkit done. Restarting docker ..."
    yield restart_docker(user_pw)
    # check nvidia-smi again
    if not check_nvidia_smi(base_image, user_pw):
        yield f"{ERROR_HEAD} nvidia-smi for docker is not ready ! \n Please check log and  your nvidia drivers!"
    else:
        yield f"{SUCCESS_HEAD} nvidia-smi for docker is ready."


def install_ssh(base_env_dir, user_pw):
    """remove ssh if exists, and install the given SSH."""
    cmd = f"echo  {user_pw}| sudo -S apt-get remove openssh-client -y"
    os.system(cmd)
    cmd = f"echo  {user_pw}| sudo -S apt-get remove openssh-server -y"
    os.system(cmd)

    # get ubuntu version
    cmd = "lsb_release -d"
    version_info = subprocess.getoutput(cmd)
    if "20.04" not in version_info:
        yield f"{INFO_HEAD} apt installation for openssh will be attempted ...... \n {version_info}"
        apt_install(user_pw, ["openssh-client",
                    "openssh-server", "openssh-sftp-server"], LOGGER)
    else:
        # install offline
        yield "start install openssh-client ......"
        cmd = f"sudo -S dpkg -i {base_env_dir}{SSH_CLI_DEB}"
        for output in exec_cmd(cmd, [user_pw]):
            print(output)
            LOGGER.debug(output)

        yield "start install openssh-sftp-server ......"
        cmd = f"sudo -S dpkg -i {base_env_dir}{SSH_SFTP_DEB}"
        for output in exec_cmd(cmd, [user_pw]):
            print(output)
            LOGGER.debug(output)

        yield "start install openssh-server ......"
        cmd = f"sudo -S dpkg -i {base_env_dir}{SSH_SERVER_DEB}"
        for output in exec_cmd(cmd, [user_pw]):
            print(output)
            LOGGER.debug(output)

    # check ssh again
    is_ssh_ready, msg = check_ssh(user_pw)
    if not is_ssh_ready:
        yield ERROR_HEAD+msg+"\n Please check log and install openssh manually! "
        return

    cmd = f"echo  {user_pw}| sudo -S systemctl restart ssh"
    os.system(cmd)

    yield f"{INFO_HEAD} install openssh. Done."


def install_docker(base_env_dir, user_pw, installed_path):
    """install docker """
    # get ubuntu version
    cmd = "lsb_release -d"
    version_info = subprocess.getoutput(cmd)
    if "20.04" not in version_info:
        yield f"{INFO_HEAD} apt installation for docker will be attempted ...... \n {version_info}"
        apt_install(user_pw,
                    ["containerd.io",
                     "docker-ce",
                     "docker-ce-cli"], LOGGER)
    else:
        yield f"start load {DOCKER_DEB}..."
        cmd = f"sudo -S dpkg -i {base_env_dir}{DOCKER_DEB}"
        for output in exec_cmd(cmd, [user_pw]):
            print(output)
            LOGGER.debug(output)
        yield f"load {DOCKER_DEB}.Done."

        yield f"start load {DOCKER_CE_CLI}."
        cmd = f"sudo -S dpkg -i {base_env_dir}{DOCKER_CE_CLI}"
        for output in exec_cmd(cmd, [user_pw]):
            print(output)
            LOGGER.debug(output)
        yield f"load {DOCKER_CE_CLI}.Done."

        yield f"start load {DOCKER_CE}."
        cmd = f"sudo -S dpkg -i {base_env_dir}{DOCKER_CE}"
        for output in exec_cmd(cmd, [user_pw]):
            print(output)
            LOGGER.debug(output)
        yield f"load {DOCKER_CE}.Done."

    flag, msg = check_docker()
    if not flag:
        yield f"{ERROR_HEAD} docker installation failed!"
        return
    yield INFO_HEAD + msg

    yield "start modify docker config"
    for line in modify_docker_config(user_pw, installed_path):
        yield line
    yield "modify docker config Done"

def modify_docker_config(user_pw, installed_path):
    """set docker dataroot and logging driver """
    if os.path.exists(installed_path):
        yield f"{INFO_HEAD}try to change docker data-root to {installed_path}/docker_data/"
        os.system(f"echo {user_pw}|sudo -S systemctl stop docker.socket")
        os.system(f"echo {user_pw}|sudo -S systemctl stop docker")
        if not os.path.exists("/etc/docker/daemon.json"):
            yield "create a new /etc/docker/daemon.json"
            os.system(
                f"echo {user_pw}|sudo -S touch /etc/docker/daemon.json")
            os.system(f"(echo '{user_pw}'; echo ' " + "{}' " +
                      " ) |sudo -S -k tee -a /etc/docker/daemon.json")
        change_mode_to_full_permission("/etc/docker/daemon.json", user_pw)
        # read daemon.json
        with open("/etc/docker/daemon.json", "r") as f:
            # modify docker dataroot
            daemon_json = json.load(f)
            daemon_json["data-root"] = f"{installed_path}/docker_data/"
            # modify docker logging
            daemon_json["log-driver"] = "json-file"
            daemon_json["log-opts"] = {
                "max-size": DOCKER_MAX_SIZE,
                "max-file": DOCKER_MAX_FILE
                }
        json.dump(daemon_json, open("/etc/docker/daemon.json", "w"), indent=4)
        yield restart_docker(user_pw)

def base_environment_install(base_env_dir, user_pw, installed_path):
    """Self-explanatroy"""
    yield "start check Docker ......"
    is_ready, version_info = check_docker()
    if not is_ready:
        for output in install_docker(base_env_dir, user_pw, installed_path):
            yield output
        yield "add seyond_user to docker group ......"
        cmd = "sudo -S usermod -aG docker seyond_user"
        for output in exec_cmd(cmd, [user_pw]):
            yield output
        yield "add seyond_user to docker group. Done"
    else:
        yield version_info
        yield "start modify docker config"
        if (not IS_X86) and os.path.exists(installed_path):
            yield "start modify docker config"
            for line in modify_docker_config(user_pw, installed_path):
                yield line
            yield "modify docker config Done"
    yield restart_docker(user_pw)
    yield "start check SSH ......"
    is_ready, version_info = check_ssh(user_pw)
    if not is_ready:
        for output in install_ssh(base_env_dir, user_pw):
            yield output
    else:
        yield version_info


def prepare_od_env(package_dir, user_pw, use_gpu):
    """prepare OD envirment

    Args:
        package_dir (_type_): _description_
        user_pw (_type_): _description_

    Yields:
        _type_: _description_
    """
    # check docker image exist
    yield f"start load OD base docker images ...... {CUDA_BASE_TAR_NAME}"
    yield "Please wait, this may take some time ...... "
    if is_docker_image_exist(CUDA_BASE_IMAGE_TAG_NAME, user_pw):
        yield f"{INFO_HEAD}CUDA base image already exist, removing the old image ..."
        yield TRACE_HEAD+stop_docker_container(OD_DOCKER_NAME, user_pw)
        yield TRACE_HEAD+remove_docker_container(OD_DOCKER_NAME, user_pw)
        output = subprocess.getoutput(
            f"echo {user_pw} | sudo -S -k docker rmi {CUDA_BASE_IMAGE_TAG_NAME}")
        # yield output
        yield f"Remove old OD docker image cuda base image"
    # else:
    cuda_base_img_path = f"{package_dir}base_imgs/{CUDA_BASE_TAR_NAME}"
    if not os.path.exists(cuda_base_img_path):
        yield WARNING_HEAD + cuda_base_img_path + " not exist, start find in parent directory ..."
        cuda_base_img_path = f"{package_dir}{CUDA_BASE_TAR_NAME}"
        if not os.path.exists(cuda_base_img_path):
            yield ERROR_HEAD + "OD docker images not exist!"
            return
    result = ""
    for output in exec_cmd(f"sudo -S -k docker load -i {cuda_base_img_path} -q", [user_pw]):
        if '[sudo]' in output:
            continue
        result += output.replace(TRACE_HEAD, "")
    print(result)
    # the 'innovusion' may in output, so do not print
    # get the image name
    image_name = CUDA_BASE_IMAGE_NAME
    try:
        lines = result.split('\n')
        last_line = lines[len(lines)-1]
        image_name = last_line.split(": ", 1)[1].strip()
        if image_name != CUDA_BASE_IMAGE_NAME:
            LOGGER.info(
                "use OD docker image name from load : %s", image_name)
        if ":" not in image_name:
            yield ERROR_HEAD + "load OD docker image failed: \n"+output
            return
    except Exception as e:
        LOGGER.error(e)
        yield ERROR_HEAD + "load OD docker image failed: \n"+output
        return
    yield "load OD base docker images. Done."
    yield "tag the image with a new name ......"
    cmd = f"sudo -S -k docker tag {image_name} {CUDA_BASE_IMAGE_TAG_NAME}"
    # LOGGER.debug(cmd)
    for output in exec_cmd(cmd, [user_pw]):
        LOGGER.info("cmd executed ")
    cmd = f"echo {user_pw} | sudo -S -k docker rmi {image_name}"
    output = subprocess.getoutput(cmd)
    # LOGGER.info(output)
    yield f"tag new name. Done."
    if not is_docker_image_exist(CUDA_BASE_IMAGE_TAG_NAME, user_pw):
        yield f"{ERROR_HEAD}Load image {CUDA_BASE_IMAGE_TAG_NAME} failed! Please check docker!"
    if IS_X86 and use_gpu:
        for output in install_nvidia_smi(package_dir+"base_env/", CUDA_BASE_IMAGE_TAG_NAME, user_pw):
            yield output


def prepare_scene(package_dir, web_base_path, user_pw):
    """check scene if exist and copy scene to webAndGL directory"""
    scene_tgz_file = find_scene_tgz(package_dir)
    if scene_tgz_file == "":
        yield ERROR_HEAD + SCENE_FILE_SUFFIX+"*.zip not exists in package"
    change_mode_to_full_permission(scene_tgz_file, user_pw)
    scene_path = os.path.join(web_base_path, "webAndGL/omnisense/scene")
    make_dir(scene_path, user_pw)
    shutil.unpack_archive(scene_tgz_file, scene_path)
    # make sure all files can be read and write by anyone
    change_mode_to_full_permission(scene_path, user_pw, recursive=True)
    yield "check scene. Done."


def get_versions(package_dir):
    """get versions
    return
        {
            od_version: version,
            web_version:version,
            full_version:version
        }
    """
    versions = {}
    try:
        # find od version
        LOGGER.error("package_dir="+package_dir)
        od_file_path = find_od_tgz(package_dir)
        # get file name without dir and suffix
        versions["product_name"] = PRODUCT_NAME
        versions["full_version"] = get_full_version_from_od(od_file_path)

        file_name = od_file_path.rsplit("/", 1)[1].rsplit(".", 1)[0]
        versions["od_version"] = "OD_" + file_name.split(OD_FILE_PREFIX, 1)[1]
        # find web version
        web_file_path = find_web_tgz(package_dir)
        file_name = web_file_path.rsplit("/", 1)[1].rsplit(".", 1)[0]
        versions["web_version"] = "WEB_"+file_name.split(WEB_FILE_PREFIX, 1)[1]
    except Exception as err:
        print(err)
        LOGGER.error(f"{err}")
    return versions


def prepare_web_docker(web_base_path, base_imgs_dir, user_pw, gpu, versions: dict):
    """Self-expanatory
    verisons: include od_version, web_version, full_version
    """
    make_dir(WEB_REPOS_DOCKER_PATH, user_pw)
    change_mode_to_full_permission(WEB_REPOS_DOCKER_PATH, user_pw)
    yield "docker load java base docker images ...... "
    cmd = f"sudo -S -k docker load -i {base_imgs_dir}{MYSQL_TAR}"
    for output in exec_cmd(cmd, [user_pw]):
        yield output
    cmd = f"sudo -S -k docker load -i {base_imgs_dir}{REDIS_TAR}"
    for output in exec_cmd(cmd, [user_pw]):
        yield output
    cmd = f"sudo -S -k docker load -i {base_imgs_dir}{NGINX_TAR}"
    for output in exec_cmd(cmd, [user_pw]):
        yield output
    cmd = f"sudo -S -k docker load -i {base_imgs_dir}{JDK_TAR}"
    for output in exec_cmd(cmd, [user_pw]):
        yield output
    yield TRACE_HEAD + "check image ....."
    image_list = get_all_docker_image(user_pw)
    # LOGGER.debug(f"find images: {image_list}")
    for name in WEB_DOCKER_BASE_IMAGE_NAMES:
        if name not in image_list:
            LOGGER.debug(f"{name} not in {image_list}")
            yield f"{ERROR_HEAD} Load image {name} failed! Please check docker!"
            return
    yield "docker load java base docker images. Done."
    # move project to path
    yield f"copy projet to {WEB_REPOS_DOCKER_PATH}"
    cmd = f"sudo -S -k cp -r {web_base_path}/docker_install/* {WEB_REPOS_DOCKER_PATH}"
    for output in exec_cmd(cmd, [user_pw]):
        yield output
    make_dir(WEB_REPOS_OMNISENSE_PATH+"/upload", user_pw)
    # check scene if exist in webAndGL
    for echo_msg in prepare_scene(base_imgs_dir.rsplit("/base_imgs", 1)[0], web_base_path, user_pw):
        yield echo_msg
    cmd = f"sudo -S -k cp -r {web_base_path}/webAndGL/* {WEB_REPOS_OMNISENSE_PATH}/upload"
    for output in exec_cmd(cmd, [user_pw]):
        yield output
    upload_path = os.path.join(WEB_REPOS_OMNISENSE_PATH, "upload", "omnisense")
    if not change_mode_to_full_permission(upload_path, user_pw):
        yield ERROR_HEAD + "Unable to modify file permissions for " + upload_path

    yield "create omisense_net ......"
    cmd = "sudo -S docker network ls | grep omisense_net"
    output_msg = ""
    for output in exec_cmd(cmd, [user_pw]):
        output_msg += output
    if ERROR_HEAD in output_msg:
        yield output_msg
    if "omisense_net" in output_msg:
        yield f"{WARNING_HEAD} omisense_net is already exist: {output_msg}"
    else:
        LOGGER.info(f"before create omisense_net: {output_msg}")
        cmd = "sudo -S docker network create --driver bridge --subnet=172.30.0.0/24 omisense_net"
        for output in exec_cmd(cmd, [user_pw]):
            yield output
    yield "check docker compose yml file ...... "
    for line in check_docker_compose_yml(user_pw):
        yield line
    yield "modify web dockerfile ...... "
    docker_file_path = f"{WEB_REPOS_OMNISENSE_PATH}/upload/omnisense/Dockerfile"
    if not os.path.exists(docker_file_path):
        yield f"{ERROR_HEAD} web Dockerfile not exist: {docker_file_path}"
    for line in modify_web_dockerfile(user_pw, docker_file_path,gpu,
                                      od_version=versions["od_version"],
                                      web_version=versions["web_version"],
                                      full_version=versions["full_version"],
                                      product_name=versions["product_name"],
                                      ):
        yield line
    yield "web environment is ready."


def modify_web_dockerfile(user_pw, file_path, gpu, od_version, web_version, full_version, product_name):
    """_summary_

    Args:
        user_pw (_type_): _description_
    """
    yield f"od_version: {od_version}, web_version: {web_version}, total_version: {full_version} , gpu:{gpu}"
    if not os.path.exists(file_path):
        yield f"{ERROR_HEAD} file not exist: {file_path}"
    if not change_mode_to_full_permission(file_path, user_pw):
        yield ERROR_HEAD + "Unable to modify file permissions for " + file_path
    # Open Dockerfile and read its lines
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # Now open it in write mode and modify the required line(s)
    with open(file_path, 'w', encoding='utf-8') as file:
        for line in lines:
            # Check if line contains ENTRYPOINT
            if 'ENTRYPOINT' in line:
                # Extract JSON from the line
                json_str = re.search(r'\[.*\]', line).group(0)
                entrypoint_args = json.loads(json_str)
                entrypoint_args.append(f"--od_version={od_version}")
                entrypoint_args.append(f"--web_version={web_version}")
                entrypoint_args.append(f"--total_version={full_version}")
                entrypoint_args.append(f"--product_name={product_name}")
                entrypoint_args.append(f"--od.gpu={gpu}")
                # Convert the args back to JSON and replace in the line
                new_json_str = json.dumps(entrypoint_args)
                line = line.replace(json_str, new_json_str)

            file.write(line)
    yield "modify web dockerfile. Done."


def check_docker_compose_yml(user_pw):
    """check docker compose yml file

    Args:
        user_pw (string): user password
    """
    docker_compose_yml = WEB_REPOS_DOCKER_PATH + "/docker-compose.yml"
    if not os.path.exists(docker_compose_yml):
        yield f"{ERROR_HEAD} docker-compose.yml not exist in :{WEB_REPOS_DOCKER_PATH}"
        return
    if not change_mode_to_full_permission(docker_compose_yml, user_pw):
        yield ERROR_HEAD + "Unable to modify file permissions for " + docker_compose_yml
    with open(docker_compose_yml, 'r', encoding="utf-8") as file:
        doc = yaml.safe_load(file)
    if doc:
        # change docker volumes
        service_name = 'mysql'  # 需要修改的服务名称
        data_volume_path = "/var/lib/mysql/"  # 新的挂载路径
        conf_volume_path = "/etc/mysql/conf.d/"
        if service_name in doc['services']:
            change_yml_volumes(doc, service_name, {
                data_volume_path: WEB_DOCKER_FILE_PATH,
                conf_volume_path: WEB_DOCKER_FILE_PATH})

        service_name = "nginx-web"
        cert_volume_path = "/etc/nginx/cert"
        conf_volume_path = "/etc/nginx/nginx.conf"
        page_volume_path = "/docker/nginx/html"
        meta_volume_path = "/docker/nginx/metaView"
        log_volume_path = "/var/log/nginx"
        if service_name in doc['services']:
            change_yml_volumes(doc, service_name, {
                cert_volume_path: WEB_DOCKER_FILE_PATH,
                page_volume_path: WEB_DOCKER_FILE_PATH,
                meta_volume_path: WEB_DOCKER_FILE_PATH,
                log_volume_path: WEB_DOCKER_FILE_PATH,
                conf_volume_path: WEB_DOCKER_FILE_PATH})

        service_name = "redis"
        conf_volume_path = "/redis/config:rw"
        data_volume_path = "/redis/data/:rw"
        if service_name in doc['services']:
            change_yml_volumes(doc, service_name, {
                data_volume_path: WEB_DOCKER_FILE_PATH,
                conf_volume_path: WEB_DOCKER_FILE_PATH})

        # service_name = 'minio'
        # data_volume_path = "/data"
        # conf_volume_path = "/root/.minio/"
        # if service_name in doc['services']:
        #     change_yml_volumes(doc, service_name, {
        #         data_volume_path: WEB_DOCKER_FILE_PATH,
        #         conf_volume_path: WEB_DOCKER_FILE_PATH})

        service_name = "city-admin"
        html_volume_path = "/docker/nginx/html/"
        log_volume_path = "/omisense/server/logs/"
        update_volume_path = "/home/inno_user/repos/omisense/"
        apollo_pcd_volume_path = "/omisense/server/pcd/"
        apollo_fusion_volume_path = "/omisense/server/fusion/"
        apollo_ai_volume_path = "/omisense/server/ai/"
        if service_name in doc['services']:
            change_yml_volumes(doc, service_name, {
                html_volume_path: WEB_DOCKER_FILE_PATH,
                log_volume_path: WEB_DOCKER_FILE_PATH})
            change_yml_volumes(doc, service_name, {
                update_volume_path: WEB_REPOS_OMNISENSE_PATH,
                apollo_pcd_volume_path: os.path.join(
                    OD_DOCKER_PATH, "SW", "data/calib/"),
                apollo_fusion_volume_path: os.path.join(
                    OD_DOCKER_PATH, "SW", "modules/omnisense/launch/calib_matrices"),
                apollo_ai_volume_path: os.path.join(
                    OD_DOCKER_PATH, "SW", "modules/omnisense/segmentation"),
            }, replace=True)
            change_yml_build(doc, service_name,
                             f"{WEB_REPOS_OMNISENSE_PATH}/upload/omnisense")

    else:
        yield f"{ERROR_HEAD} docker-compose.yml is not correct in {WEB_DOCKER_FILE_PATH}"
        return

    # 写回docker-compose.yml文件
    with open(docker_compose_yml, 'w', encoding="utf-8") as file:
        yaml.safe_dump(doc, file)
    if not change_mode_to_full_permission(docker_compose_yml, user_pw):
        yield ERROR_HEAD + "Unable to modify file permissions for " + docker_compose_yml


def change_yml_volumes(doc, service_name,  new_volumes: dict, replace=False):
    """_summary_

    Args:
        doc (_type_): _description_
        service_name (_type_): _description_
        new_volumes (dict): _description_
    """
    # 确保服务及其volumes字段存在
    if 'volumes' not in doc['services'][service_name]:
        return
    for i, volume in enumerate(doc['services'][service_name]['volumes']):
        # 切割成host和container两部分
        parts = volume.split(':', 1)
        if len(parts) != 2:
            continue
        if parts[1] not in new_volumes:
            continue

        # 修改host部分为新的路径，并重新组合
        if replace:
            parts[0] = new_volumes[parts[1]]
        else:
            parts[0] = new_volumes[parts[1]] + parts[0]
        doc['services'][service_name]['volumes'][i] = ':'.join(
            parts)


def change_yml_build(doc, service_name,  path):
    """change_yml_build
    """
    if 'build' not in doc['services'][service_name]:
        return
    doc['services'][service_name]['build'] = path


def docker_deploy(user_pw, docker_compose_bin, mount=False, base=False):
    """Self-explanatory"""
    docker_compose_yml = WEB_REPOS_DOCKER_PATH + "/docker-compose.yml"
    if mount:
        for line in docker_deploy_mount(user_pw):
            yield line
    elif base:
        cmd = f"sudo -S {docker_compose_bin} -f {docker_compose_yml} up -d mysql redis nginx-web"
        for line in exec_cmd(cmd, [user_pw]):
            yield line
    else:
        cmd = f"sudo -S {docker_compose_bin} -f {docker_compose_yml} build --no-cache city-admin"
        for line in exec_cmd(cmd, [user_pw]):
            yield line
        cmd = f"sudo -S {docker_compose_bin} -f {docker_compose_yml} up -d city-admin"
        for line in exec_cmd(cmd, [user_pw]):
            yield line


def docker_deploy_mount(user_pw):
    """Self-explanatory"""
    yield "start mount web docker path ......."
    make_dir(WEB_DOCKER_FILE_PATH, user_pw)
    change_mode_to_full_permission(WEB_DOCKER_FILE_PATH, user_pw)
    make_dir(WEB_DOCKER_FILE_PATH+"/docker", user_pw)
    # 挂载 nginx 配置文件
    path = f"{WEB_DOCKER_FILE_PATH}/docker/nginx/conf"
    make_dir(path, user_pw)
    if not os.path.isfile(f"{path}/nginx.conf"):
        shutil.copy(f"{WEB_REPOS_DOCKER_PATH}/nginx/nginx.conf",
                    f"{path}/nginx.conf")

    # 挂载 redis 配置文件
    path = f"{WEB_DOCKER_FILE_PATH}/docker/redis/conf"
    make_dir(path, user_pw)
    if not os.path.isfile(f"{path}/redis.conf"):
        shutil.copy(f"{WEB_REPOS_DOCKER_PATH}/redis/redis.conf",
                    f"{path}/redis.conf")

    # 挂载 redis 持久化文件
    path = f"{WEB_DOCKER_FILE_PATH}/docker/redis/data"
    make_dir(path, user_pw)

    # 挂载 mysql 配置文件
    path = f"{WEB_DOCKER_FILE_PATH}/docker/mysql/conf"
    make_dir(path, user_pw)

    # 挂载 mysql数据文件
    path = f"{WEB_DOCKER_FILE_PATH}/docker/mysql/data"
    make_dir(path, user_pw)

    # 挂载 nginx前端文件
    html_path = f"{WEB_DOCKER_FILE_PATH}/docker/nginx/html"
    make_dir(html_path, user_pw)

    # init web
    upload_path = f"{WEB_REPOS_OMNISENSE_PATH}/upload/web/"
    # get file with prefix and suffix
    file_list = [file for file in os.listdir(
        upload_path) if file.endswith(".tgz")]
    if len(file_list) != 1:
        yield f"{ERROR_HEAD} cannot confirm web tgz file in path: {upload_path} \n file_list: {file_list}"
        return
    upload_html_path = f"{upload_path}{file_list[0]}"
    if not change_mode_to_full_permission(upload_html_path, user_pw):
        yield ERROR_HEAD + "Unable to modify file permissions for " + upload_html_path
    shutil.unpack_archive(upload_path + file_list[0], html_path)
    unzip_file_name = file_list[0].rsplit(".", 1)[0]

    web_link = f"{html_path}/web"
    if os.path.islink(web_link):
        yield 'web soft link already exist, update it'
        os.unlink(web_link)
    yield f"create the web soft link : {web_link}"
    # the link used in nginx docker, so the source path is in nginx docker container
    os.system(f"ln -s /docker/nginx/html/{unzip_file_name} {web_link}")

    # make sure the all file can be change
    web_docker_path = os.path.join(WEB_DOCKER_FILE_PATH, "docker")
    if not change_mode_to_full_permission(web_docker_path, user_pw, recursive=True):
        yield ERROR_HEAD + "Unable to modify file permissions for " + web_docker_path
    yield "mount web docker path. Done."


def web_docker_check(user_pw, docker_list):
    """Check all of web docker containers if up"""
    for docker_name in docker_list:
        if is_container_created(docker_name, user_pw):
            os.system(f"echo {user_pw} | sudo -S docker start {docker_name}")
    for docker_name in docker_list:
        # check three times
        check_count = 0
        max_wait_count = 5
        while True:
            if check_count > max_wait_count:
                break
            if not is_container_up(docker_name, user_pw):
                yield f"{WARNING_HEAD} waiting {docker_name} run up .... "
                sleep(2)
            else:
                yield f"{INFO_HEAD} {docker_name} is up."
                break
            check_count += 1
        if check_count > max_wait_count:
            yield f"{ERROR_HEAD} {docker_name} is not up !"


class CityInstallTask():
    """Self-explanatory"""
    basedir = ""
    user_passwd = ""
    docker_compose_bin = ""

    def change_passwd(self) -> str:
        """Change passwd of seyond_user"""
        echo_msg = ""
        is_need_input_flag = is_need_input()
        if 'seyond_user' in os.popen(
                "getent passwd|grep -i '^seyond_user'").read().split('\n'):
            echo_msg = "seyond_user already exists;  continue next step"
            yield echo_msg
            cmd = f"(echo '{self.user_passwd}'; echo 'seyond_user:4321Go') |sudo -S -k chpasswd"
            if not is_need_input_flag:
                cmd = "echo 'seyond_user:4321Go' | sudo chpasswd"
            for line in exec_cmd(cmd):
                yield line
            cmd = "sudo -S -k usermod -a -G adm seyond_user"
            for line in exec_cmd(cmd, [self.user_passwd]):
                yield line
        else:
            # check if seyond_user group exists
            cmd = "cut -d: -f1 /etc/group | sort |grep seyond_user"
            cmd_result = subprocess.getoutput(cmd)
            cmd_adduser = "sudo  -S  useradd -c 'Seyond User' -p '*' -M -r -d /home/seyond_user"
            if "seyond_user" in cmd_result.split():
                echo_msg = "seyond_user group already exists;"
                yield echo_msg
                cmd_adduser += " -g seyond_user"
            cmd_adduser += " seyond_user"
            for line in exec_cmd(cmd_adduser, [self.user_passwd]):
                print(line.replace(ERROR_HEAD, INFO_HEAD))
                LOGGER.debug(line.replace(ERROR_HEAD, INFO_HEAD))
            cmd = f"(echo '{self.user_passwd}'; echo 'seyond_user:4321Go') |sudo -S -k chpasswd"
            if not is_need_input_flag:
                cmd = "echo 'seyond_user:4321Go' | sudo chpasswd"
            for line in exec_cmd(cmd):
                yield line
            cmd = "sudo -S -k usermod -a -G adm seyond_user"
            for line in exec_cmd(cmd, [self.user_passwd]):
                yield line

        cmd = f"(echo {self.user_passwd};echo 'seyond_user ALL = (ALL) NOPASSWD: ALL') | sudo -S -k EDITOR='tee -a' visudo"
        if not is_need_input_flag:
            cmd = "echo 'seyond_user ALL = (ALL) NOPASSWD: ALL' | sudo  EDITOR='tee -a' visudo"
        for line in exec_cmd(cmd):
            yield line

    def __check_base_env_dir(self, base_env_dir, needed_files):
        """check if needed files in base env directory
        return checked message
        """
        for file in needed_files:
            if not os.path.isfile(base_env_dir+file):
                return f"{ERROR_HEAD} :{file} does not exist in {base_env_dir}"
        return "base_env directory is ready"

    def __check_base_imgs_dir(self, base_imgs_dir):
        """check if needed files in base docker images directory
        return checked message
        """
        needed_files = [
            MYSQL_TAR, NGINX_TAR, REDIS_TAR, JDK_TAR, CUDA_BASE_TAR_NAME
        ]
        for file in needed_files:
            if not os.path.isfile(base_imgs_dir+file):
                return f"{ERROR_HEAD} :{file} does not exist in {base_imgs_dir}"
        return "base_imgs directory is ready"

    def __check_docker_compose(self, base_env_dir):
        """check if docker-compose file in base env directory
        return checked message
        """
        self.docker_compose_bin = get_file_path(
            base_env_dir, "docker-compose*")
        if not self.docker_compose_bin:
            return f"{ERROR_HEAD} :docker-compose does not exist in {base_env_dir}"
        if "2." not in subprocess.getoutput(f"{self.docker_compose_bin} --version"):
            return f"{ERROR_HEAD} :docker-compose version in base_env must be 2.x !"
        return "docker-compose is ready"

    def __prepare_dir_in_package(self, dir_name):
        """prepare directory in package"""
        base_env_dir = os.path.join(self.basedir, dir_name)
        if not os.path.isdir(base_env_dir):
            yield f"{WARNING_HEAD} cannot find {dir_name} directory"
            if os.path.isfile(base_env_dir+".tgz"):
                yield f"try to get from {dir_name} compressed file ...... "
                shutil.unpack_archive(base_env_dir + ".tgz", self.basedir)
            else:
                yield ERROR_HEAD + "Please make sure base_env is reachable in the package directory"

    def __start_crontab(self, target_od_dir, user_pw):
        """_summary_
        """
        watch_log = os.path.join(target_od_dir, "watch_log.sh")
        output = subprocess.getoutput(f"echo {user_pw} | sudo -S chmod +x {watch_log}")
        yield(output)
        temp_cron = "current_cron"
        
        cmd_get_cron = f"echo {user_pw} | sudo -S crontab -l > {temp_cron}"
        output = subprocess.getoutput(cmd_get_cron)
        yield output
            
        cmd = f"echo {user_pw} | sudo -S sed -i '\\|{watch_log}|d' {temp_cron}"
        result = subprocess.getoutput(cmd)
        yield(result)
        
        cmd = f"""
            echo {user_pw} | sudo -S echo '*/10 * * * * {watch_log}' >> {temp_cron}
        """
        result = subprocess.getoutput(cmd)
        LOGGER.debug(result)
        if len(WATCH_LOG_SYS_DIRS) != len(WATCH_LOG_SYS_DIRS_DAYS_TO_KEEPS) or \
            len(WATCH_LOG_SYS_DIRS) != len(WATCH_LOG_SYS_DIRS_MAX_SIZES):
            promt = "watch log sys config not valid"
            LOGGER.error(promt)
            yield promt
        if len(WATCH_LOG_INSTALL_DIRS) != len(WATCH_LOG_INSTALL_DIRS_DAYS_TO_KEEP) or \
            len(WATCH_LOG_INSTALL_DIRS) != len(WATCH_LOG_INSTALL_DIRS_MAX_SIZE):
            promt = "watch log install config not valid"
            LOGGER.error(promt)
            yield promt
        for i, dir in enumerate(WATCH_LOG_INSTALL_DIRS):
            sys_dir = os.path.join(target_od_dir, dir)
            WATCH_LOG_SYS_DIRS.append(sys_dir)
            WATCH_LOG_SYS_DIRS_DAYS_TO_KEEPS.append(WATCH_LOG_INSTALL_DIRS_DAYS_TO_KEEP[i])
            WATCH_LOG_SYS_DIRS_MAX_SIZES.append(WATCH_LOG_INSTALL_DIRS_MAX_SIZE[i])
        log_path = os.path.join(target_od_dir, "data/cron")
        with open(watch_log, "a") as file:
            for i in range(len(WATCH_LOG_SYS_DIRS)):
                folder = WATCH_LOG_SYS_DIRS[i]
                days = WATCH_LOG_SYS_DIRS_DAYS_TO_KEEPS[i]
                max_size = WATCH_LOG_SYS_DIRS_MAX_SIZES[i]
                formatted_string = "(" + f'"{folder}"' + ")"
                file.write("\n")
                file.write(f'folder_dirs={formatted_string}\n')
                file.write(f"days_to_keep={days}\n")
                file.write(f"max_size={max_size}\n")
                file.write(f'log_dir="{log_path}"\n')
                file.write('cleanup_log_directory "${folder_dirs[@]}" $days_to_keep $max_size $log_dir\n')
        LOGGER.debug(result)
        
        cmd_start_cron = f"echo {user_pw} | sudo -S crontab \"{temp_cron}\""
        output = subprocess.getoutput(cmd_start_cron)
        yield output
            
        cmd = f"rm {temp_cron}"
        result = subprocess.getoutput(cmd)
        LOGGER.debug(result)

    def install_env(self, installed_path):
        """Install base environment and base docker images
        base environment include:
            docker
            openssh
            docker-compose
        """
        # check base env directory
        for output in self.__prepare_dir_in_package("base_env"):
            yield output
        base_env_dir = os.path.join(self.basedir, "base_env/")
        if not change_mode_to_full_permission(base_env_dir, self.user_passwd, recursive=True):
            yield ERROR_HEAD + "Unable to modify file permissions for " + base_env_dir

        if IS_X86:
            # needed file: docker-ce\docker-ce-cli\containerd.io
            yield self.__check_base_env_dir(base_env_dir,
                                            [
                                                DOCKER_CE, DOCKER_CE_CLI, DOCKER_DEB,
                                                SSH_CLI_DEB, SSH_SERVER_DEB, SSH_SFTP_DEB,
                                            ])
        else:
            # needed file: docker-ce\docker-ce-cli\containerd.io
            yield self.__check_base_env_dir(base_env_dir, [])
        yield self.__check_docker_compose(base_env_dir)

        # check base docker images directory
        for output in self.__prepare_dir_in_package("base_imgs"):
            yield output
        base_images_dir = self.basedir+"base_imgs/"
        if not change_mode_to_full_permission(base_images_dir, self.user_passwd, recursive=True):
            yield ERROR_HEAD + "Unable to modify file permissions for " + base_env_dir
        yield self.__check_base_imgs_dir(base_images_dir)

        for output in base_environment_install(base_env_dir, self.user_passwd, installed_path):
            yield output

    def install_web(self, zip_file,gpu):
        """Install web docker"""
        dir_name, _ = os.path.splitext(zip_file)
        remove_dir(dir_name, self.user_passwd)
        yield "start decompress web files ......"
        shutil.unpack_archive(zip_file, os.path.dirname(zip_file))
        msg = f"web files extract to : {dir_name}"
        yield msg
        yield "prepare web environment ......"
        versions = get_versions(os.path.dirname(zip_file))
        if len(versions) < 3:
            yield f"{ERROR_HEAD} versions info not completed : {versions}"
        yield "remove nginx image before deploy web"
        try:
            for image in RM_IMG:
                cmd_rm_img = f"echo {self.user_passwd} | sudo -S docker rmi {image}"
                output = subprocess.getoutput(cmd_rm_img)
                yield output
                yield f"rm image: {image} success"
        except Exception as e:
            msg = f"An unexpected error occurred while rm image {image}: {e}"
            print(msg)
            LOGGER.error(msg)
            yield(msg)
        for output in prepare_web_docker(dir_name,
                                         os.path.dirname(
                                             zip_file)+"/base_imgs/", self.user_passwd,
                                         gpu,versions):
            yield output
        yield "mount web docker ....."
        for output in docker_deploy(self.user_passwd, self.docker_compose_bin, mount=True):
            yield output
        yield "deploy web base docker containers ....."
        for output in docker_deploy(self.user_passwd, self.docker_compose_bin, base=True):
            print(output.replace(ERROR_HEAD, INFO_HEAD))
            LOGGER.debug(output.replace(ERROR_HEAD, INFO_HEAD))
        yield "check web base docker containers are running ......"
        for output in web_docker_check(self.user_passwd, WEB_BASE_DOCKER_NAMES):
            yield output
        yield "start  city-admin ....."
        for output in docker_deploy(self.user_passwd, self.docker_compose_bin):
            print(output.replace(ERROR_HEAD, INFO_HEAD))
            LOGGER.debug(output.replace(ERROR_HEAD, INFO_HEAD))
        yield "check city dockers are running ......"
        for output in web_docker_check(self.user_passwd, WEB_CITY_DOCKER_NAMES):
            yield output

        remove_dir(dir_name, self.user_passwd)

    def install_od(self, od_file, host_ip, gpu_od,remote_web=""):
        """Install od docker"""
        # check base image and docker images:
        yield "start check OD environment ......"
        for output in prepare_od_env(self.basedir, self.user_passwd, gpu_od):
            yield output
        yield "OD environment prepare. Done"
        target_od_dir = os.path.join(OD_DOCKER_PATH, "SW/")
        make_dir(target_od_dir, self.user_passwd)
        change_mode_to_full_permission(
            target_od_dir, self.user_passwd, recursive=True)
        if not os.path.isdir(DATA_REMAIN_PATH):
            make_dir(DATA_REMAIN_PATH, self.user_passwd)
        yield f"mkdir SW done: {target_od_dir}"
        if is_container_exited(OD_DOCKER_NAME, self.user_passwd):
            msg = f"{INFO_HEAD} OD docker already exists, stop and remove it"
            yield msg
            yield TRACE_HEAD+stop_docker_container(OD_DOCKER_NAME, self.user_passwd)
            yield TRACE_HEAD+remove_docker_container(OD_DOCKER_NAME, self.user_passwd)

        # Unpack the od tar file to the SW directory
        yield f"start unpack OD tgz ...... {target_od_dir}"
        yield "Please wait, this may take some time ...... "
        shutil.unpack_archive(od_file, target_od_dir)
        # prepare crontab excute shell
        change_mode_to_full_permission(os.path.join(
            target_od_dir, "apollo_od.bash"), self.user_passwd)
        # self.__prepare_crontab_shell(target_od_dir, self.user_passwd)
        yield "start crontab"
        for output in self.__start_crontab(target_od_dir, self.user_passwd):
            yield output
        yield "start crontab done"
        use_gpu_str = " "
        yield f"gpu_od = {gpu_od}"
        if IS_X86:
            if gpu_od:
                use_gpu_str = "--gpus all "
            cmd = f"echo {self.user_passwd} | " +\
                f"sudo -S docker run --restart=always --env HOST_IP=172.30.0.1 -it -d " +\
                f"{use_gpu_str}" +\
                f"--net=host -v {target_od_dir}:/apollo/ " +\
                "-v /etc/timezone:/etc/timezone:rw " +\
                "-v /usr/share/zoneinfo:/usr/share/zoneinfo:rw " +\
                f"-v {target_od_dir}data/:/apollo/data/ " +\
                f"--name {OD_DOCKER_NAME} {CUDA_BASE_IMAGE_TAG_NAME} bash /apollo/apollo_od.bash"
        else:
            if gpu_od:
                use_gpu_str = "--runtime=nvidia "
            cmd = f"echo {self.user_passwd} | " +\
                f"sudo -S docker run --restart=always --env HOST_IP=172.30.0.1 -it -d " +\
                f"{use_gpu_str}" +\
                f"--net=host -v {target_od_dir}:/apollo/ " +\
                "-v /etc/timezone:/etc/timezone:rw " +\
                "-v /usr/share/zoneinfo:/usr/share/zoneinfo:rw " +\
                f"-v {target_od_dir}data/:/apollo/data/ " +\
                f"--name {OD_DOCKER_NAME} {CUDA_BASE_IMAGE_TAG_NAME} bash /apollo/apollo_od.bash"
        # yield f"cmd = {cmd}"
        yield "startup OD docker ......"
        for output in exec_cmd(cmd):
            yield output
        yield "startup OD docker. Done."

        if remote_web != "":
            # cmd = f"sed -i 's|redis_server_ip: |redis_server_ip:  '{remote_web}'|' {target_od_dir}REDIS_CONFIG"
            cmd = f"sed -i 's|redis_server_ip: |redis_server_ip:  '{host_ip}'|' {target_od_dir}REDIS_CONFIG"
        else:
            # cmd = f"sed -i 's|redis_server_ip: |redis_server_ip:  '{host_ip}'|' {target_od_dir}REDIS_CONFIG"
            cmd = f"sed -i 's|redis_server_ip: |redis_server_ip:  '{host_ip}'|' {target_od_dir}REDIS_CONFIG"
        output = subprocess.getoutput(cmd)
        yield output
        # config to enable generating core file when od coredump
        yield "enable core pattern"
        file_path = os.path.expanduser("~/.bashrc")
        change_mode_to_full_permission(file_path, self.user_passwd)
        ret = append_line(f"ulimit -c {CORE_MAX_SIZE}", file_path, "ulimit -c")
        if ret != 0:
            yield f"ulimit set failed"
        ret = set_core_pattern(self.user_passwd, CORE_FILEPATH)
        if ret != 0:
            yield "core pattern set failed"
        else:
            yield "enable core pattern done"


class CityInstall(QThread):
    """Install SmartCity"""
    progress = pyqtSignal(int)
    install_msg = pyqtSignal(str)
    basedir = ""
    user_passwd = ""
    task = CityInstallTask()
    install_web = False
    install_od = False
    install_web_ip = ""
    web_tgz = ""
    od_tgz = ""
    install_local_ip = ""
    progress_total = 0
    installed_path = ""  # it is a directory, like : "/home/seyond_user/"
    use_gpu = True
    logger = None
    

    def set_pw(self, pw):
        """Set user password"""
        self.user_passwd = pw
        self.task.user_passwd = pw

    def run(self):
        """install: three big step"""
        try:
            global OD_DOCKER_PATH
            global WEB_DOCKER_FILE_PATH
            global WEB_REPOS_OMNISENSE_PATH
            global WEB_REPOS_DOCKER_PATH
            global DATA_REMAIN_PATH
            global LOGGER
            LOGGER = self.logger

            if 'SIMPL_SKIP_MD5' not in os.environ:
                # Check md5
                md5checker = MD5Checker(LOGGER, self.install_msg)
                TGZ_PACKAGE_DIR = os.path.dirname(sys.executable)
                md5_check_result = md5checker.check_md5(TGZ_PACKAGE_DIR)
                if md5_check_result == False:
                    return
            else:
                self.emit_msg(INFO_HEAD + "Skip MD5 check!")

            if self.installed_path == "":
                self.emit_msg(
                    ERROR_HEAD+PRODUCT_NAME+" installed path is empty!")
                return
            self.installed_path = os.path.abspath(self.installed_path)
            # self.installed_path = os.path.join(
            #     self.installed_path, PRODUCT_NAME)
            OD_DOCKER_PATH = os.path.join(self.installed_path, "od")
            WEB_DOCKER_FILE_PATH = os.path.join(self.installed_path, "web")
            WEB_REPOS_OMNISENSE_PATH = os.path.join(
                self.installed_path, "repos/omisense")
            WEB_REPOS_DOCKER_PATH = os.path.join(
                self.installed_path, "repos/omisense/docker")
            DATA_REMAIN_PATH = os.path.join(self.installed_path, "data")
            LOGGER.info(f"installed_path: {self.installed_path}")
            sleep(1.5)
            self.progress_total = 0
            self.task.basedir = self.basedir
            # check installed path
            make_dir(self.installed_path, self.user_passwd)
            directory_test(self.installed_path, self.user_passwd)

            self.emit_msg(START_HEAD+"create seyond_user")
            for echo_msg in self.task.change_passwd():
                if not self.emit_msg(echo_msg):
                    return
            if self.progress_total < 15:
                self.increase_progress(15-self.progress_total)
            self.emit_msg(SUCCESS_HEAD+"seyond_user is ready")

            self.emit_msg(START_HEAD+"prepare base environment")
            for echo_msg in self.task.install_env(self.installed_path):
                if not self.emit_msg(echo_msg):
                    return
            if self.progress_total < 40:
                self.increase_progress(40-self.progress_total)
            self.emit_msg(SUCCESS_HEAD+"base environment is ready")

            self.emit_msg(INFO_HEAD+"use IP address: " +
                          self.install_local_ip)

            if self.install_web:
                self.emit_msg(f"{START_HEAD}install WEB: {self.web_tgz}")
                for echo_msg in self.task.install_web(self.web_tgz,self.use_gpu):
                    if not self.emit_msg(echo_msg):
                        return
                self.emit_msg(SUCCESS_HEAD+"WEB is ready")

            for echo_msg in self.wait_web_startup():
                self.emit_msg(echo_msg)
            if self.progress_total < 70:
                self.increase_progress(70-self.progress_total)

            if self.install_od:
                self.emit_msg(f"{START_HEAD}install OD: {self.od_tgz}")
                for echo_msg in self.task.install_od(self.od_tgz, self.install_local_ip,
                                                     self.use_gpu,remote_web=self.install_web_ip):
                    if not self.emit_msg(echo_msg):
                        return
                self.emit_msg(SUCCESS_HEAD+"OD is ready")

            self.emit_msg(f"{START_HEAD}modify journal config")
            config_file = "/etc/systemd/journald.conf"
            change_mode_to_full_permission(config_file, self.user_passwd)
            ret = modify_journal_config(config_file, JOURNAL_CONFIG, self.user_passwd)
            if ret == 0:
                self.emit_msg(f"{SUCCESS_HEAD} modify journal config success")
            else:
                self.emit_msg(f"{WARNING_HEAD} modify journal config failed, error_code: {ret}")
            if self.progress_total < 90:
                self.increase_progress(90-self.progress_total)

            self.emit_msg(END_HEAD+"Install finish ")

            self.increase_progress_to_end()
        except Exception as e:
            self.emit_msg(ERROR_HEAD + str(e))
            self.exit()

    def wait_web_startup(self):
        """waiting WEB startup"""
        max_duration = 30*10
        count = 0
        while count < max_duration:
            yield f"waiting WEB startup ...... {count}s"
            try:
                r = requests.get(WEB_PING_URL, timeout=5)
                if r.status_code == 200:
                    break
            except Exception as e:
                print(e)
                LOGGER.error(f"{e}")
            finally:
                sleep(5)
                count += 5
        yield "WEB startup. Done"

    def increase_progress(self, length):
        """Self-explanatory"""
        if (self.progress_total + length) > 99:
            self.progress_total = 99
        else:
            self.progress_total += length
        self.progress.emit(self.progress_total)

    def increase_progress_to_end(self):
        """Self-explanatory"""
        self.progress_total = 100
        self.progress.emit(100)

    def emit_msg(self, msg) -> bool:
        """Self-explanatory"""
        if ERROR_HEAD in msg:
            print(msg)
            self.logger.info(msg)
            self.install_msg.emit(msg)
            self.exit()
            return False
        print(msg)
        if "[sudo]" in msg:
            return True
        self.logger.info(msg)
        self.install_msg.emit(msg)
        self.increase_progress(1)
        return True


if __name__ == "__main__":
    task = CityInstallTask()
    task.basedir = "/home/demo/code-repo/smart_city_installer/smart_city/package/"
    task.user_passwd = "demo"
    for out in task.change_passwd():
        print(out)
    import sys
    sys.exit(0)

    # for out in task.install_env():
    #     print(out)

    # for out in task.install_od(
    #     "/home/demo/code-repo/smart_city_installer/smart_city/package/OM_Smart_City_OD_03.00.05_20231010_x86_cuda_11.tgz",
    #     "172.16.1.10"
    #     ,remote_web="172.16.1.11"
    #     ):
    #     print(out)

    web_tgz = find_web_tgz(
        "/home/demo/code-repo/smart_city_installer/smart_city/package/")
    for out in task.install_web(web_tgz):
        print(out)
