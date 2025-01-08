import os
import subprocess
import sys
from pathlib import Path
import importlib

modules = [["filetype","openpyxl"],
           ["filetype","openpyxl"]]


# project_root = Path('.').resolve()
root_file = os.path.abspath(__file__)
root_path = os.path.dirname(root_file)
# print(root_path)
root_path = Path(root_path)

# venv_path = os.path.join(root_path,"p_env","bin") if os.name != "nt" else os.path.join(root_path,"p_env","Scripts")
# venv_py_path = os.path.join(venv_path,"python")#path of venv python executable

#path of bin directory
venv_path = root_path / "p_env" / "bin" if os.name != "nt" else root_path / "p_env" / "Scripts"
venv_py_path = venv_path / "python" #path of venv python executable

if not (venv_path.is_dir() and (venv_path.parent/'pyvenv.cfg').exists()):
    try:
        subprocess.run([sys.executable,"-m","venv",venv_path.parent],stdout = subprocess.DEVNULL)
        print("python v-env created")
    except Exception as e:
        print("Error while creating v-env:",e)
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

