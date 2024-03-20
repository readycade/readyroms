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
* Description: Downloads and Installs Rom Packs to your Readycade eg: n64.zip, snes.7z ect
"""

import base64
import tkinter as tk
from tkinter.filedialog import askopenfile
from tkinter import ttk, messagebox, simpledialog
from tkinter import Tk, Label, StringVar, Button, Scrollbar, Text
from tkinter.filedialog import askopenfile
from tkinter import messagebox
import os
import requests
from PIL import Image, ImageTk
import platform
import subprocess
import shutil
import sys
import time
from tqdm import tqdm

encoded_password = "cmVhZHlzZXRnbw=="

decoded_password = base64.b64decode(encoded_password.encode()).decode()

script_dir = os.path.dirname(os.path.abspath(__file__))

eula_path = os.path.join(script_dir, "EULA.txt")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
 
    return os.path.join(base_path, relative_path)

def show_eula():
    with open(eula_path, "r") as file:
        eula_text = file.read()

    eula_window = tk.Toplevel()
    eula_window.title("End User License Agreement")

    text_box = Text(eula_window, wrap=tk.WORD, height=24, width=70, padx=15, pady=15)
    text_box.insert(tk.END, eula_text)
    text_box.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    scrollbar = Scrollbar(eula_window, command=text_box.yview)
    scrollbar.grid(row=0, column=1, sticky="nsew")
    text_box['yscrollcommand'] = scrollbar.set

    def agree():
        eula_window.destroy()
        root.deiconify()

    agree_button = tk.Button(eula_window, text="Agree", command=agree)
    agree_button.grid(row=1, column=0, padx=5, pady=5)

    eula_window.geometry("640x480")

    eula_window.focus_force()

    eula_window.protocol("WM_DELETE_WINDOW", agree)

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

def check_windows():
    if platform.system() != 'Windows':
        messagebox.showerror("Error", "This script is intended to run on Windows only. Exiting.")
        sys.exit(1)

print("Checking if the network share is available...")

try:
    subprocess.run(["ping", "-n", "1", "RECALBOX"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("Network share found.")
except subprocess.CalledProcessError:
    print("Error: Could not connect to the network share \\RECALBOX.")
    print("Please make sure you are connected to the network and try again.")
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", "Network Share not found. Please make sure you are connected to the network and try again.")
    sys.exit()

print()

installDir = "C:\\Program Files\\7-Zip"

version = "2301"

downloadURL = f"https://www.7-zip.org/a/7z{version}-x64.exe"

seven_zip_installed = os.path.exists(os.path.join(installDir, "7z.exe"))

if seven_zip_installed:
    print("7-Zip is already installed.")
else:
    print("Authentication successful. Proceeding with installation...")

    localTempDir = os.path.join(os.environ["APPDATA"], "readycade", "temp")

    os.makedirs(localTempDir, exist_ok=True)
    downloadPath = os.path.join(localTempDir, "7z_installer.exe")
    with requests.get(downloadURL, stream=True) as response, open(downloadPath, 'wb') as outFile:
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024
        with tqdm(total=total_size, unit='B', unit_scale=True, desc='Downloading 7-Zip') as pbar:
            for data in response.iter_content(block_size):
                pbar.update(len(data))
                outFile.write(data)

    subprocess.run(["start", "/wait", "", downloadPath], shell=True)

    if not os.path.exists(os.path.join(installDir, "7z.exe")):
        print("Installation failed.")
        sys.exit()

    print("7-Zip is now installed.")

def update_status(message):
    status_var.set(message)
    root.update_idletasks()

def cleanup():
    def update_gui_cleanup():
        root.update_idletasks()
        root.after(100, update_gui_cleanup)

    update_gui_cleanup()

    shutil.rmtree(os.path.join(os.environ['APPDATA'], 'readycade', 'rompacks'), ignore_errors=True)

    update_status("Deleting Temporary Files... Please Wait...")
    print("Deleting Temporary Files... Please Wait...")

    time.sleep(2)

    status_var.set("")

def process_rom(file):
    base_filename = os.path.splitext(os.path.basename(file.name))[0]

    if base_filename in valid_consoles:
        appdata_path = os.path.join(os.environ['APPDATA'], 'readycade', 'rompacks')
        temp_path = r'\\RECALBOX\share\roms'
        os.makedirs(appdata_path, exist_ok=True)
        os.makedirs(temp_path, exist_ok=True)

        print("Extracting Files...")

        update_status("Extracting Files...")

        extraction_command = [r'C:\Program Files\7-Zip\7z.exe', 'x', '-aoa', '-p{}'.format(decoded_password), os.path.join(temp_path, file.name), '-o{}'.format(appdata_path)]

        subprocess.run(extraction_command)

        status_var.set("")

        update_status(f"Copying {valid_consoles[base_filename]} to your Readycade...")

        print(f"Copying {valid_consoles[base_filename]} to your Readycade...")

        destination_path = os.path.join(temp_path, base_filename)
        shutil.copytree(appdata_path, destination_path, dirs_exist_ok=True)

        update_status("Success. Please Update your Gameslist Now.")

        messagebox.showinfo("Success", f"Extraction and Copying completed for {valid_consoles[base_filename]}. Remember to Update your Gamelists.")

        cleanup()
    else:
        messagebox.showerror("Error", "Invalid console name. Please use a valid console name eg: n64, amiga600 etc.")

def open_rom_file():
    browse_text.set("loading...")

    def update_gui():
        root.update_idletasks()
        root.after(100, update_gui)

    update_gui()

    file = askopenfile(parent=root, mode='rb', title="Choose a ROM Pack (.zip or .7z only)", filetype=[("ZIP files", "*.zip;*.7z")])
    if file:
        process_rom(file)

    browse_text.set("Browse")

root = tk.Tk()

root.withdraw()

show_eula()

root.title("Readycade™")

icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
root.iconbitmap(icon_path)

Instructions = tk.Label(root, text="Select a ROM Pack on your computer to install to your Readycade", font="open-sans")
Instructions.grid(columnspan=3, column=0, row=1)

logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
logo = Image.open(logo_path)
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.grid(column=1, row=0)

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font="open-sans")
status_label.grid(columnspan=3, column=0, row=4)

browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text, command=open_rom_file, font="open-sans", bg="#ff6600", fg="white", height=2, width=15)
browse_text.set("Browse")
browse_btn.grid(column=1, row=2)

cleanup()

root.mainloop()
