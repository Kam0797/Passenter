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
try:
    import requests
except ImportError:
    print("Module 'requests' not found. Installing...")
    subprocess.run(["pip","install","requests"])
    print("Module 'requests' is Installed.")
    import requests
import zipfile

import shutil

def download_poppler(url, destination):
    print("Downloading Poppler...")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(destination, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def extract_zip(zip_path, extract_to):
    print("Extracting Poppler...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)

def add_to_path(directory):
    print("Adding Poppler to PATH...")
    path = os.environ.get("PATH", "")
    if directory not in path:
        os.system(f'setx PATH "%PATH%;{directory}"')
        print(f"Added {directory} to PATH.")
    else:
        print(f"{directory} is already in PATH.")

def clean_up(file_path):
    print("Cleaning up...")
    if os.path.exists(file_path):
        os.remove(file_path)

def main():
    # Define variables
    poppler_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"
    zip_path = os.path.join(os.getenv("TEMP"), "poppler.zip")
    poppler_dir = "C:\\poppler"
    bin_dir = os.path.join(poppler_dir, "poppler-24.08.0", "Library", "bin")

    # Step 1: Download Poppler
    download_poppler(poppler_url, zip_path)

    # Step 2: Extract the ZIP file
    extract_zip(zip_path, poppler_dir)

    # Step 3: Add Poppler to the PATH
    add_to_path(bin_dir)

    # Step 4: Clean up
    clean_up(zip_path)

    # Verify Installation
    try:
        print("Verifying Poppler installation...")
        result = subprocess.run(["cmd","/c","cmd.exe","/k", "pdftotext", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Poppler installed successfully!")
            print(result.stdout)
        else:
            print("Poppler installation verification failed.")
            print(result.stderr)
    except FileNotFoundError:
        print("Poppler is not accessible. Please check the installation.")

if __name__ == "__main__":
    try:
        subprocess.run(["pdftotext", "-v"],stderr = subprocess.DEVNULL)
    except:
        main()
