#!/bin/bash
function tag_version() {
    if [ ! -z "$1" ]; then
        VERSION_FILE="./common/version.py"
        echo "tagging version $1"
        sed -i 's/VERSION = "test"/VERSION = "'"$1"'"/g' $VERSION_FILE
    fi
}

tag_version test

pyinstaller --add-data "ui/imgs:ui/imgs" --add-data "ui/font:ui/font" -F ./installer.py

pyinstaller --add-data "ui/imgs:ui/imgs" --add-data "ui/font:ui/font" -F ./uninstaller.py

#pyinstaller --onefile -y --name my_executable --distpath /path/to/output my_script.py

mv dist/installer ./smart_city/
mv dist/uninstaller ./smart_city/
