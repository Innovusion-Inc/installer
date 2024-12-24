#!/bin/bash

function tag_version() {
    if [ ! -z "$1" ]; then
        VERSION_FILE="./common/version.py"
        echo "tagging version $1"
        sed -i 's/VERSION = "test"/VERSION = "'"$1"'"/g' $VERSION_FILE
    fi
}

function build_x86() {
    mkdir -p /root/miniconda3
    bash ./env/miniconda.sh -b -u -p /root/miniconda3
    /root/miniconda3/bin/conda init bash
    source /root/.bashrc

    # >>> conda initialize >>>
    # !! Contents within this block are managed by 'conda init' !!
    __conda_setup="$('/root/miniconda3/bin/conda' 'shell.bash' 'hook' 2>/dev/null)"
    if [ $? -eq 0 ]; then
        eval "$__conda_setup"
    else
        if [ -f "/root/miniconda3/etc/profile.d/conda.sh" ]; then
            . "/root/miniconda3/etc/profile.d/conda.sh"
        else
            export PATH="/root/miniconda3/bin:$PATH"
        fi
    fi
    unset __conda_setup
    # <<< conda initialize <<<

    conda env remove -n qt
    conda env create -f ./env/env_x86.yml
    apt update
    DEBIAN_FRONTEND=noninteractive apt-get install -y libglib2.0-0 binutils libgl1-mesa-glx binutils
    apt-get install -y qt5-default
    apt install -y curl
    conda activate qt

    # tag version
    tag_version $1

    pyinstaller --add-data "ui/imgs:ui/imgs" --add-data "ui/font:ui/font" -F ./installer.py

    pyinstaller --add-data "ui/imgs:ui/imgs" --add-data "ui/font:ui/font" -F ./uninstaller.py

}

function build_arm() {
    mkdir -p /root/miniconda3
    bash ./env/Miniconda3-latest-Linux-aarch64.sh -b -u -p /root/miniconda3
    /root/miniconda3/bin/conda init bash
    source /root/.bashrc

    # >>> conda initialize >>>
    # !! Contents within this block are managed by 'conda init' !!
    __conda_setup="$('/root/miniconda3/bin/conda' 'shell.bash' 'hook' 2>/dev/null)"
    if [ $? -eq 0 ]; then
        eval "$__conda_setup"
    else
        if [ -f "/root/miniconda3/etc/profile.d/conda.sh" ]; then
            . "/root/miniconda3/etc/profile.d/conda.sh"
        else
            export PATH="/root/miniconda3/bin:$PATH"
        fi
    fi
    unset __conda_setup
    # <<< conda initialize <<<

    conda env remove -n qt
    conda env create -f ./env/env_arm.yml
    apt update
    DEBIAN_FRONTEND=noninteractive apt-get install -y libglib2.0-0 binutils libgl1-mesa-glx binutils
    apt-get install -y qt5-default
    apt install -y curl
    conda activate qt

    # tag version
    tag_version $1

    pyinstaller --add-data "ui/imgs:ui/imgs" --add-data "ui/font:ui/font" -F ./installer.py

    pyinstaller --add-data "ui/imgs:ui/imgs" --add-data "ui/font:ui/font" -F ./uninstaller.py

}

# judge if $1 is x86
if [[ $1 == "x86" ]]; then
    build_x86 $2
else
    build_arm $2
fi
