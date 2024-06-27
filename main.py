"""
************************************************************************** 
* READYCADE CONFIDENTIAL
* __________________
* 
*  [2024] Readycade Incorporated 
*  All Rights Reserved.
* 
* NOTICE:  All information contained herein is, and remains* the property of Readycade Incorporated and its suppliers,
* if any.  The intellectual and technical concepts contained* herein are proprietary to Readycade Incorporated
* and its suppliers and may be covered by U.S. and Foreign Patents,
* patents in process, and are protected by trade secret or copyright law.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Readycade Incorporated.
**************************************************************************
* Author Michael Cabral 2024
* Title: EZ_Rom_Packs
* GPL-3.0 License
* Platforms: Windows 10/11, Linux, MacOS
* Description: Downloads and Installs Rom Packs to your Readycade eg: n64.zip, snes.7z ect

## DISCLAIMER: This script is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and noninfringement.

## This script is intended for educational and informational purposes only. The authors and ReadyCade, Inc. do not support or condone the illegal downloading or distribution of video games. Downloading video games
## without proper authorization is illegal and can result in severe penalties. Users are solely responsible for ensuring that their actions comply with applicable laws.

## In no event shall the authors or ReadyCade, Inc. be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the script
## or the use or other dealings in the script. USE AT YOUR OWN RISK. YOU ASSUME ALL LIABILITY FOR ANY ACTIONS TAKEN BASED ON THIS SCRIPT.
#################################################################################################################

"""

import base64
import tkinter as tk
from tkinter.filedialog import askopenfile
from tkinter import ttk, messagebox, simpledialog
from tkinter import Tk, Label, StringVar, Button, Scrollbar, Text
from tkinter.filedialog import askopenfile
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import os
import requests
from PIL import Image, ImageTk
import logging
from pathlib import Path
import platform
import subprocess
import shutil
import sys
import tarfile
import time
from tqdm import tqdm
import playsound  # Cross-platform sound playback

# Get the user's home directory
home_directory = str(Path.home())

# Define the target directory for cleanup
target_directory = os.path.join(home_directory, "readycade", "rompacks")

# Determine the installation directory for 7-Zip
if platform.system() == 'Windows':
    # On Windows, use a common location for program installations
    install_dir = os.path.join("C:", "Program Files", "7-Zip")
else:
    # On Linux and macOS, use a common system-wide location for program installations
    install_dir = "/usr/local/bin"

# global__encrypted_password (already encoded)
encoded_password = "cmVhZHlzZXRnbw=="

# Decoding the password
decoded_password = base64.b64decode(encoded_password.encode()).decode()

# Get the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the relative path to the EULA.txt file
eula_path = os.path.join(script_dir, "EULA.txt")

# Define the relative path to the ready.wav file
sound_file_path = os.path.join(script_dir, "ready.wav")

# Play sound function
def play_ready_sound():
    if platform.system() == 'Windows':
        import winsound
        winsound.PlaySound(sound_file_path, winsound.SND_FILENAME)
    else:
        playsound.playsound(sound_file_path)

# Set up logging configuration (cross-platform)
log_file_path = os.path.join(script_dir, "script_log.txt")
if not os.access(script_dir, os.W_OK):
    log_file_path = "/tmp/script_log.txt"  # Fallback to a writable location
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
 
    return os.path.join(base_path, relative_path)

def show_eula():
    # Load EULA from EULA.txt
    with open(eula_path, "r") as file:
        eula_text = file.read()

    # Create a new window for displaying the EULA
    eula_window = tk.Toplevel()
    eula_window.title("End User License Agreement")

    # Configure the grid layout
    eula_window.rowconfigure(0, weight=1)
    eula_window.columnconfigure(0, weight=1)

    # Add a Text widget for displaying the EULA text with a scroll bar
    text_box = ScrolledText(eula_window, wrap=tk.WORD, height=24, width=70, padx=15, pady=15)
    text_box.insert(tk.END, eula_text)
    text_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Add a scrollbar
    scrollbar = tk.Scrollbar(eula_window, command=text_box.yview)
    scrollbar.grid(row=0, column=1, sticky="nsew")
    text_box['yscrollcommand'] = scrollbar.set

    # Add "Agree" and "Disagree" buttons
    def agree():
        eula_window.destroy()
        root.deiconify()

    agree_button = tk.Button(eula_window, text="Agree", command=agree)
    agree_button.grid(row=1, column=0, padx=5, pady=5)

    # Adjust the size of the EULA window
    eula_window.geometry("640x480")

    # Force the focus on the EULA window
    eula_window.focus_force()

    # Handle window closure
    eula_window.protocol("WM_DELETE_WINDOW", agree)

# Instead of exiting, inform the user and proceed if necessary (CROSS PLATFORM)
def check_platform():
    current_platform = platform.system()
    if current_platform not in ['Windows', 'Darwin', 'Linux']:
        messagebox.showerror("Error", "This script is intended to run on Windows, Mac, or Linux only. Exiting.")
        sys.exit(1)

# Call the function to check the platform
check_platform()

# If the platform check passed, continue with the rest of your code
print(f"Script is running on {platform.system()}. Continue execution.")

# CHECK NETWORK SHARE
def check_network_share():
    if platform.system() == 'Windows':
        command = ["ping", "-n", "1", "RECALBOX"]
    else:
        command = ["ping", "-c", "1", "RECALBOX"]

    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Network share found.")
    except subprocess.CalledProcessError:
        print("Error: Could not connect to the network share \\RECALBOX.")
        print("Please make sure you are connected to the network and try again.")
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showerror("Error", "Network Share not found. Please make sure you are connected to the network and try again.")
        sys.exit()

check_network_share()

def run_with_sudo(command):
    """
    Run a shell command with sudo using osascript on macOS or pkexec for graphical sudo prompt on Linux.
    """
    try:
        if platform.system() == 'Darwin':
            # Use AppleScript to run the command with administrator privileges on macOS
            script = f'do shell script "{command}" with administrator privileges'
            subprocess.run(['osascript', '-e', script], check=True)
        elif platform.system() == 'Linux':
            # Use pkexec to run the command with a graphical sudo prompt on Linux
            subprocess.run(['pkexec', 'sh', '-c', command], check=True)
        else:
            print("Unsupported operating system.")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running command with sudo: {e}")
        sys.exit(1)

# Define the 7-Zip version and download URLs
version = "2406"
download_urls = {
    "Windows": f"https://www.7-zip.org/a/7z{version}-x64.msi",
    "Linux_x86_64": f"https://www.7-zip.org/a/7z{version}-linux-x64.tar.xz",
    "Linux_arm64": f"https://www.7-zip.org/a/7z{version}-linux-arm64.tar.xz",
    "macOS": f"https://www.7-zip.org/a/7z{version}-mac.tar.xz"
}

# Determine the current platform
current_platform = platform.system()
if current_platform == 'Linux':
    arch = platform.machine()
    if arch == 'x86_64':
        downloadURL = download_urls["Linux_x86_64"]
    elif arch == 'aarch64':
        downloadURL = download_urls["Linux_arm64"]
    else:
        print(f"Unsupported Linux architecture: {arch}")
        exit(1)
elif current_platform == 'Darwin':
    downloadURL = download_urls["macOS"]
elif current_platform == 'Windows':
    downloadURL = download_urls["Windows"]
else:
    print(f"Unsupported platform: {current_platform}")
    exit(1)

# Define the installation directory for 7-Zip
if current_platform == 'Windows':
    installDir = "C:\\Program Files\\7-Zip"
    executable_name = "7z.exe"
elif current_platform in ['Linux', 'Darwin']:
    installDir = "/usr/local/bin"  # Correct installation directory
    executable_name = "7zz"
else:
    print(f"Unsupported platform: {current_platform}")
    exit(1)

# Check if 7-Zip is already installed
if not os.path.exists(os.path.join(installDir, executable_name)):
    # Define the temporary directory for downloading the installer
    home_directory = str(Path.home())
    tempDir = os.path.join(home_directory, "readycade", "7zip_temp")
    os.makedirs(tempDir, exist_ok=True)
    downloadPath = os.path.join(tempDir, os.path.basename(downloadURL))

    # Download the installer
    with requests.get(downloadURL, stream=True) as response, open(downloadPath, 'wb') as outFile:
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading 7-Zip') as pbar:
            for data in response.iter_content(block_size):
                pbar.update(len(data))
                outFile.write(data)

    # Run the installer based on the platform
    if current_platform == 'Windows':
        try:
            subprocess.run(["msiexec", "/i", downloadPath], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Installation failed with error: {e}")
            exit(1)
    elif current_platform == 'Linux' or current_platform == 'Darwin':
        try:
            with tarfile.open(downloadPath, 'r:xz') as tar:
                tar.extractall(path=tempDir)
        except Exception as e:
            print(f"Installation failed with error: {e}")
            exit(1)

        # Locate the 7zz binary and move it to the install directory
        source_path = os.path.join(tempDir, '7zz')
        if not os.path.exists(source_path):
            print(f"7zz binary not found in the extracted folder: {tempDir}")
            exit(1)

        target_path = os.path.join(installDir, executable_name)
        try:
            os.rename(source_path, target_path)
            os.chmod(target_path, 0o755)  # Make executable
            print(f"Moved {source_path} to {target_path}")
        except PermissionError:
            try:
                # Combine mv and chmod into a single command
                command = f'mv {source_path} {target_path} && chmod 755 {target_path}'
                run_with_sudo(command)
                print(f"Moved {source_path} to {target_path} with sudo")
            except subprocess.CalledProcessError as e:
                print(f"Error moving binary {source_path} to {target_path}: {e}")
                exit(1)
        except Exception as e:
            print(f"Error moving binary {source_path} to {target_path}: {e}")
            exit(1)

        print("7-Zip is now installed.")
else:
    print("7-Zip is already installed.")

# Function to update the status label
def update_status(message):
    status_var.set(message)
    root.update_idletasks()

# Function to perform cleanup
def cleanup():
    # Update the GUI more frequently during the cleanup process
    def update_gui_cleanup():
        root.update_idletasks()
        root.after(100, update_gui_cleanup)

    update_gui_cleanup()  # Start updating the GUI

    # Clean up downloaded and extracted files
    shutil.rmtree(target_directory, ignore_errors=True)

    # Update status label
    update_status("Deleting Temporary Files... Please Wait...")
    print("Deleting Temporary Files... Please Wait...")

    # Sleep for 2 seconds
    time.sleep(2)

    # Clear status label
    status_var.set("")

# Function to print the contents of a directory
def print_directory_contents(directory):
    print(f"Contents of directory {directory}:")
    for item in os.listdir(directory):
        print(item)

# Dictionary of valid console names
valid_consoles = {
    "64dd": "Nintendo 64DD",
    "amiga600": "Amiga 600",
    "amiga1200": "Amiga 1200",
    "amstradcpc": "Amstrad CPC",
    "apple2": "Apple II",
    "apple2gs": "Apple IIGS",
    "arduboy": "Arduboy",
    "atari800": "Atari 800",
    "atari2600": "Atari 2600",
    "atari5200": "Atari 5200",
    "atari7800": "Atari 7800",
    "atarist": "Atari ST",
    "atomiswave": "Atomiswave",
    "bbcmicro": "BBC Micro",
    "bk": "BK",
    "c64": "Commodore 64",
    "channelf": "Channel F",
    "colecovision": "ColecoVision",
    "daphne": "Daphne",
    "dos": "DOS",
    "fds": "Famicom Disk System",
    "gamegear": "Game Gear",
    "gba": "Game Boy Advance",
    "gbc": "Game Boy Color",
    "gb": "Game Boy",
    "gw": "GW",
    "gx4000": "GX4000",
    "intellivision": "Intellivision",
    "jaguar": "Atari Jaguar",
    "lowresnx": "LowRes NX",
    "lutro": "Lutro",
    "mastersystem": "Sega Master System",
    "megadrive": "Sega Genesis",
    "model3": "Model 3",
    "msx1": "MSX1",
    "msx2": "MSX2",
    "msxturbor": "MSX Turbo R",
    "multivision": "Multivision",
    "n64": "Nintendo 64",
    "naomigd": "Naomi GD",
    "naomi": "Naomi",
    "neogeocd": "Neo Geo CD",
    "neogeo": "Neo Geo",
    "nes": "Nintendo Entertainment System",
    "ngpc": "Neo Geo Pocket Color",
    "ngp": "Neo Geo Pocket",
    "o2em": "O2EM",
    "oricatmos": "Oric Atmos",
    "pcenginecd": "PC Engine CD",
    "pcengine": "PC Engine",
    "pcfx": "PC-FX",
    "pcv2": "PCV2",
    "pokemini": "Pokemini",
    "ports": "Ports",
    "samcoupe": "Sam Coupe",
    "satellaview": "Satellaview",
    "scv": "Super Cassette Vision",
    "sega32x": "Sega 32X",
    "sg1000": "SG-1000",
    "snes": "Super Nintendo Entertainment System",
    "solarus": "Solarus",
    "spectravideo": "Spectravideo",
    "sufami": "Sufami Turbo",
    "supergrafx": "SuperGrafx",
    "supervision": "Supervision",
    "thomson": "Thomson",
    "tic80": "TIC-80",
    "trs80coco": "TRS-80 CoCo",
    "uzebox": "Uzebox",
    "vectrex": "Vectrex",
    "vic20": "Commodore VIC-20",
    "videopacplus": "Videopac Plus",
    "virtualboy": "Virtual Boy",
    "wasm4": "Wasm4",
    "wswanc": "Wonderswan Color",
    "wswan": "Wonderswan",
    "x1": "X1",
    "x68000": "X68000",
    "zx81": "ZX81",
    "zxspectrum images": "ZX Spectrum Images",
    "zxspectrum videos": "ZX Spectrum Videos"
}

def process_rom(file):
    try:
        # Get the base filename (without extension)
        base_filename = os.path.splitext(os.path.basename(file.name))[0]

        # Get the user's home directory
        home_directory = str(Path.home())

        # Define paths
        appdata_path = os.path.join(home_directory, 'readycade', 'rompacks')

        # Check if the base filename matches a valid console name
        if base_filename in valid_consoles:
            # Ensure the directories exist
            os.makedirs(appdata_path, exist_ok=True)

            # Update status label
            update_status("Extracting Files...")

            # Determine the platform
            current_platform = platform.system()

            # Define the extraction path to a subfolder named after the base filename
            extraction_path = os.path.join(appdata_path, base_filename)

            # Adjust the extraction path for the platform
            extraction_path = os.path.normpath(extraction_path)

            print(f"Destination directory: {extraction_path}")  # Debugging statement

            # Define the extraction command using 7-Zip
            if current_platform == "Windows":
                extraction_command = ["7z", 'x', '-aoa', '-o{}'.format(extraction_path), '-p{}'.format(decoded_password), os.path.join(appdata_path, file.name)]
                roms_directory = r"\\RECALBOX\share\roms"
            else:
                # For Linux and Mac
                extraction_command = ["/usr/local/bin/7zz", 'x', '-aoa', '-o{}'.format(extraction_path), '-p{}'.format(decoded_password), os.path.join(appdata_path, file.name)]
                
                if current_platform == "Darwin":
                    roms_directory = "/Volumes/share/roms"
                elif current_platform == "Linux":
                    possible_paths = [
                        "/run/user/1000/gvfs/smb-share:server=recalbox.local,share=roms",
                        "/media/$(whoami)/recalbox/share/roms",
                        "/mnt/RECALBOX/share/roms"
                    ]
                    # Check which path exists
                    roms_directory = next((path for path in possible_paths if os.path.exists(path)), None)
                    if not roms_directory:
                        raise FileNotFoundError("RECALBOX share directory not found on Linux.")
                else:
                    raise NotImplementedError("Unsupported platform: {}".format(current_platform))

            # Execute the extraction command
            extraction_process = subprocess.run(extraction_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Check if the extraction is successful
            if extraction_process.returncode == 0:
                # Extraction was successful
                update_status("Extraction successful!")

                # Copy the extracted files to the destination directory on the network share
                try:
                    update_status("Copying files to Readycade")
                    # Copy contents of extraction_path directly to roms_directory
                    for item in os.listdir(extraction_path):
                        source = os.path.join(extraction_path, item)
                        destination = os.path.join(roms_directory, base_filename, item)
                        if os.path.isdir(source):
                            shutil.copytree(source, destination, dirs_exist_ok=True)
                        else:
                            shutil.copy2(source, destination)
                    
                    update_status("Copying files successful!")
                    update_status("Deleting temporary extracted files")
                    # Clean up downloaded and extracted files
                    shutil.rmtree(os.path.join(home_directory, 'readycade', 'rompacks'), ignore_errors=True)
                    update_status("Deleting temporary extracted files")
                    # Clean up temporary files
                    shutil.rmtree(os.path.join(home_directory, 'readycade', 'temp'), ignore_errors=True)
                    update_status("Deleting temporary extracted files")
                    update_status("Ready!")
                    play_ready_sound()
                    
                    cleanup()  # Ensure cleanup is called after successful copy
                except Exception as e:
                    # Handle exceptions
                    update_status("Copying files failed!")
                    messagebox.showerror("Error", f"Copying files failed: {str(e)}")
                    cleanup()  # Ensure cleanup is called after failed copy

            else:
                # Extraction failed
                update_status("Extraction failed!")
                # Display an error message
                messagebox.showerror("Error", f"Extraction failed for {valid_consoles[base_filename]}.")

        else:
            # Display an error message for an invalid console name
            messagebox.showerror("Error", "Invalid console name. Please use a valid console name e.g., n64, amiga600, etc.")

    except Exception as e:
        # Display an error message for any exception
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        # Log the error
        print(f"An error occurred: {str(e)}")
        # Cleanup on error
        cleanup()

# Function to handle opening a ROM file
def open_rom_file():
    browse_text.set("loading...")

    # Update the GUI more frequently during the process
    def update_gui():
        root.update_idletasks()
        root.after(100, update_gui)

    update_gui()  # Start updating the GUI

    file = askopenfile(parent=root, mode='rb', title="Choose a ROM Pack (.zip or .7z only)", filetypes=[("ZIP files", "*.zip;*.7z")])
    if file:
        process_rom(file)

    # Set button text back to "Browse" regardless of whether a file was selected or not
    browse_text.set("Browse")

# Set up the main window
root = tk.Tk()

# Hide the main window initially
root.withdraw()

# Show EULA before creating the main window
show_eula()

# set the window title
root.title("Readycade™")

# Set the window icon
icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')  # Replace 'icon.ico' with your actual icon file
root.iconbitmap(icon_path)

# Instructions
Instructions = tk.Label(root, text="Select a ROM Pack on your computer to install to your Readycade", font="open-sans")
Instructions.grid(columnspan=3, column=0, row=1)

# Logo
logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
logo = Image.open(logo_path)
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.grid(column=1, row=0)

# Status label
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font="open-sans")
status_label.grid(columnspan=3, column=0, row=4)

# Browse Button
browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text, command=open_rom_file, font="open-sans", bg="#ff6600", fg="white", height=2, width=15)
browse_text.set("Browse")
browse_btn.grid(column=1, row=2)

cleanup()

root.mainloop()
