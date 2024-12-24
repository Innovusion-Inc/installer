# SETUP ENV
## 1. install miniconda

## 2. setup virtual environment

  x86:

```bash
conda create -n qt
conda activate qt
conda env update -f env/env_x86.yml
```

arm:

```bash
conda create -n qt
conda activate qt
conda env update -f env/env_arm.yml
```
# BUILD
## 1.convert app.ui to ui.py

    pyuic5 -o ui/installer_ui.py ui/installer_ui.ui

## 2.build installer and uninstaller

    pyinstaller --add-data "ui/imgs:ui/imgs" -F ./installer.py
    
    pyinstaller --add-data "ui/imgs:ui/imgs" -F ./uninstaller.py
