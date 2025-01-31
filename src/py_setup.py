# Copyright (C) 2025 Kam <gv.kamal2003@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.


import os
import subprocess
import sys
from pathlib import Path
import importlib
from .settings import root_path

modules = [["filetype","openpyxl","termcolor"],
           ["filetype","openpyxl","termcolor"]]


## root_path imported from src/settings

# venv_path = os.path.join(root_path,"p_env","bin") if os.name != "nt" else os.path.join(root_path,"p_env","Scripts")
# venv_py_path = os.path.join(venv_path,"python")#path of venv python executable

#path of bin directory
venv_path = root_path / "p_env" / "bin" if os.name != "nt" else root_path / "p_env" / "Scripts"
venv_py_path = venv_path / "python" #path of venv python executable

if not (venv_path.is_dir() and (venv_path.parent/'pyvenv.cfg').exists()):
    
    try:
        print("Creating v-env...")
        subprocess.run([sys.executable,"-m","venv",venv_path.parent],stdout = subprocess.DEVNULL)
        print("python v-env created")
    except Exception as e:
        print("Error while creating v-env:",e)
        exit('maybe, re-run or create venv manually')
imported_modules = {}
for mod,mod_name in zip(modules[0],modules[1]):
    # print(subprocess.run(['pip','show',f"{mod}"]))
    try:
        imported_modules[mod] = importlib.import_module(mod)
    except ImportError:
        try:
            print(f"Module '{mod}' not found. Installing...")
            subprocess.run([f"{venv_py_path}","-m","pip","install",mod_name],stdout = subprocess.DEVNULL)
            print(f"{mod} installed.")
        except Exception as e:
            print("Unable to install Module '{mod}'",e)



