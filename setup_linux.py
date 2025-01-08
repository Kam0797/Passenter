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
