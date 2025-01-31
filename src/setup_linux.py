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
#to be optimised
fail = True
platform_supported = False
if "ANDROID_ROOT" in os.environ or "ANDROID_DATA" in os.environ:
    platform_supported = True
    try:
        subprocess.run(["pdftotext","-v"],stderr = subprocess.DEVNULL)
    except:
        print("Poppler not found. Installing...")
        try:
            subprocess.run(["apt-get","install","poppler"],stdout = subprocess.DEVNULL)
            fail = False
            # print("Poppler installed.")
        except Exception as e:
            print("Unable to install poppler.\n",e)
     
else:
    vars = [["apt-get","install"],["pacman","-Sy"],["dnf","install"]]
    
    for var in vars:
        try:
            subprocess.run([var[0],"--version"],stdout = subprocess.DEVNULL)
            platform_supported = True
            try:
                subprocess.run(["pdftotext","-v"],stderr= subprocess.DEVNULL)
            except FileNotFoundError:
                print("Poppler not found. Installing...")
                try:
                    subprocess.run(["sudo", var[0], var[1], "poppler"],stdout = subprocess.DEVNULL)
                    # print("Poppler installed.")
                    fail = False
                except Exception as e:
                    print(f"ERROR: Unable to install poppler via {var[0]}\n",e)
        except:
            pass
if(platform_supported == False):
        print("Not Debian/Arch/Fedora/Termux :(\nInstall Poppler with you distro's package manager and come back!")
elif fail == False:
    try:
        subprocess.run(["pdftotext","-v"],stderr = subprocess.DEVNULL)
        print("Poppler installed.")
    except Exception as e:
        print("Unable to install Poppler. Try installing manually.",e)
