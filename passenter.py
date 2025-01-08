import os
import subprocess
import sys
from pathlib import Path

root_file = os.path.abspath(__file__)
root_path = os.path.dirname(root_file)
root_path = Path(root_path)

#path of bin directory
venv_path = root_path / "p_env" / "bin" if os.name != "nt" else root_path / "p_env" / "Scripts"
venv_py_path = venv_path / "python" #path of venv python executable

if not (venv_path.is_dir() and (venv_path.parent/'pyvenv.cfg').exists()):
    try:
        subprocess.run([sys.executable,"-m","venv",venv_path.parent],stdout = subprocess.DEVNULL)
        print("python v-env created")
        
    except Exception as e:
        print("Error while creating v-env:",e)

if (venv_path.is_dir() and (venv_path.parent/'pyvenv.cfg').exists()):       
    try:
        subprocess.run([venv_py_path,"main.py"],check = True)
    except subprocess.CalledProcessError as e:
        print(f"error:",e)
        sys.exit(e.returncode)







