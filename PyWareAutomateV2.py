# Imports
from customtkinter import *
from tkinter import messagebox
import os
import subprocess
# Keyboard and Mouse
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
# Key Listeners
import threading
from pynput.keyboard import Listener as KeyListener, Key
macro_running = False
macro_thread = None
# Key Inputs
import threading
# Time
import time
import json
# Web browsing
import webbrowser
# Variables
import re
import numpy as np
import mss
# Initialize controllers
keyboard_controller = KeyboardController()
mouse_controller = MouseController()
# AHK scan-code → key mapping (MODULE LEVEL)
SC_TO_KEY = {
    "sc3b": "f1",
    "sc3c": "f2",
    "sc3d": "f3",
    "sc3e": "f4",
    "sc3f": "f5",
    "sc40": "f6",
    "sc41": "f7",
    "sc42": "f8",
    "sc43": "f9",
    "sc44": "f10",
    "sc57": "f11",
    "sc58": "f12",
}
# Get All Required Paths
def get_base_path():
    """Unified base directory for app data."""

    if getattr(sys, 'frozen', False):
        compiled = True
        # Compiled App → Use User Directory
        if sys.platform == "darwin":
            return os.path.join(
                os.path.expanduser("~"),
                "Library", "Application Support",
                "PyWareAutomateV2"
            ), compiled
        elif sys.platform == "win32":
            return os.path.join(
                os.path.expanduser("~"),
                "AppData", "Roaming",
                "PyWareAutomateV2"
            ), compiled
        else:
            return os.path.join(os.path.expanduser("~"), "PyWareAutomateV2"), compiled
    compiled = False
    # Dev Mode → Project Directory
    return os.path.dirname(os.path.abspath(__file__)), compiled

BASE_PATH, IS_COMPILED = get_base_path()

CONFIG_DIR = os.path.join(BASE_PATH, "configs")
IMAGES_PATH = os.path.join(BASE_PATH, "images")
DEBUG_DIR = BASE_PATH

CONFIG_PATH = os.path.join(BASE_PATH, "last_config.json")
APP_VERSION = "2.0"
EXCLUDED_KEYS = {"active_config"}

set_appearance_mode("dark")

def ensure_last_config_exists():
    """Ensure last_config.json exists at BASE_PATH, create default if missing."""
    config_file = os.path.join(BASE_PATH, "last_config.json")
    
    # Check If It Exists As A File (Not A Directory)
    if os.path.exists(config_file):
        if os.path.isdir(config_file):
            # It'S A Directory - Remove It And Recreate As File
            print(f"Removing directory at {config_file} to create file...")
            try:
                os.rmdir(config_file)  # Use Shutil.Rmtree() If Directory Has Contents
                print(f"Removed directory: {config_file}")
            except Exception as e:
                print(f"Could not remove directory: {e}")
                # Try To Rename It As Backup
                backup_path = config_file + "_backup_folder"
                os.rename(config_file, backup_path)
                print(f"Renamed directory to: {backup_path}")
        else:
            # It Exists As A File, No Action Needed
            return config_file
    
    # Create Default Config Structure
    default_config = {
        "version": APP_VERSION,
        "last_config": "default",
        "tos_accepted": False
    }
    
    try:
        # Ensure The Parent Directory Exists
        os.makedirs(BASE_PATH, exist_ok=True)
        
        # Write The File
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=4)
        print(f"Created default config file at: {config_file}")
    except Exception as e:
        print(f"Error creating config file: {e}")
        pass
    
    return config_file

ensure_last_config_exists()
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(IMAGES_PATH, exist_ok=True)

# Terms Of Service Dialogue
class TermsOfServiceDialog(CTkToplevel):
    def __init__(self, parent=None):
        super().__init__()
        
        # Screen Size (Cache Once – Thread Safe)
        self.SCREEN_WIDTH = self.winfo_screenwidth()
        self.SCREEN_HEIGHT = self.winfo_screenheight()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Window
        self.geometry("750x600")
        self.title("PyWare Automate V2.0 - Terms of Use")
        self.minsize(650, 500)
        
        # Center Window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (750 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"+{x}+{y}")

        # Status Bar
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header Stays Fixed
        self.grid_rowconfigure(1, weight=1)  # Content Expands
        self.grid_rowconfigure(2, weight=0)  # Nav Bar Fixed
        
        # Top Bar Frame (Status + Buttons)
        top_bar = CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        top_bar.grid_columnconfigure(0, weight=1)

        # Logo Label
        logo_label = CTkLabel(
            top_bar, 
            text="TERMS OF SERVICE",
            font=CTkFont(size=16, weight="bold")
        )
        logo_label.grid(row=0, column=0, sticky="w")

        # Main Content Container
        self.container = CTkFrame(self)
        self.container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Pages
        self.page_tos = CTkFrame(self.container)
        self.page_setup = CTkFrame(self.container)

        for page in (self.page_tos, self.page_setup):
            page.grid(row=0, column=0, sticky="nsew")

        # Agree Labels
        self.agree_var = BooleanVar(value=False)
        self.accepted = False

        # Build Pages
        self.build_tos_page(self.page_tos)
        self.build_setup_page(self.page_setup)

        # Navigation Bar
        nav_bar = CTkFrame(self)
        nav_bar.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        nav_bar.grid_columnconfigure(0, weight=1)

        self.back_btn = CTkButton(nav_bar, text="Back", command=self.go_back)
        self.next_btn = CTkButton(nav_bar, text="Next", command=self.go_next)
        self.finish_btn = CTkButton(nav_bar, text="Finish", command=self.finish)

        self.back_btn.grid(row=0, column=0, padx=5, sticky="w")
        self.next_btn.grid(row=0, column=1, padx=5)
        self.finish_btn.grid(row=0, column=2, padx=5, sticky="e")

        # Initial State
        self.current_page = 0
        self.show_page(0)
    # Basic Settings Tab
    def build_tos_page(self, parent):
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        textbox = CTkTextbox(parent, wrap="word")
        textbox.grid(row=0, column=0, padx=12, pady=10, sticky="nsew")

        textbox.insert("1.0", """
PyWare Automate V2.0 - Terms of Use

By using this software, you agree to the following:


⚡ 1. USAGE & MODIFICATION

✅ YOU ARE ALLOWED TO:
Use these macros for personal purposes.
Study and reverse engineer the code for educational purposes.
Modify the code for your own personal use.
Share your modifications with proper attribution.
                            
❌ YOU ARE NOT ALLOWED TO:
Repackage or redistribute this software as your own.
Remove or modify credits to the author (Catman2608).
Sell or monetize this software or its derivatives.
Claim ownership of the original codebase.
                            
⚡ IF YOU SHARE MODIFICATIONS:
⚠️ You MUST credit Catman2608 as the original author.
⚠️ You MUST link to the original source (YouTube/Website).
⚠️ You MUST clearly indicate what changes you made.
                            
⚡ 2. INTENDED USE & GAME COMPLIANCE

This software suite is designed for use on multiple platforms.
You are responsible for ensuring your use complies with the platform's Terms of Service and specific game rules.
The developers and the website owner (Catman2608) are NOT responsible for any account actions (bans, suspensions) resulting from your use of this software.
Use at your own risk. (usage in Roblox games are allowed)

⚡ 3. LIABILITY DISCLAIMER

The owner and authors are NOT liable for any damages, data loss, or account issues.
There is no guarantee of functionality, compatibility, or performance.
Software is provided "as-is." Use is entirely at your own risk.
                            
⚡ 4. PRIVACY & DATA

Macros store configuration data (settings) locally on your device.
No personal data is collected or transmitted to external servers.
Your preferences are stored in a local .json file only.
                            
⚡ 5. CREDITS & ATTRIBUTION
                            
Original Author: Catman2608
YouTube: https://www.youtube.com/@HexaTitanGaming
Discord: https://discord.gg/aMZY8yrF8r
If you share, modify, or redistribute this software:
                            
📋 REQUIRED: Credit "Catman2608" as the original creator
📋 REQUIRED: Link to the original source
📋 REQUIRED: Indicate any changes you made
🚫 FORBIDDEN: Claim the entire work as your own
                            
⚡ 6. TERMS UPDATES

These terms may be updated at any time.
Continued use of the software from the PyWare Automate website constitutes acceptance of the updated terms.
                            
✅ 7. ACCEPTANCE

By accepting the terms, you acknowledge that you have read, understood, and agree to these Terms of Use.
If you do not agree, please remove the software from your device.

🚀 Thank you for using PyWare Automate! 🚀
        """)
        textbox.configure(state="disabled")

        checkbox = CTkCheckBox(
            parent,
            text="I agree to the Terms of Service",
            variable=self.agree_var,
            command=self.update_next_button
        )
        checkbox.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")
    # Second Tab
    def build_setup_page(self, parent):
        textbox = CTkTextbox(parent, wrap="word")
        textbox.pack(fill="both", expand=True, padx=12, pady=10)

        textbox.insert("1.0", """
Step 1: Download and extract the config pack and images pack from https://drive.google.com/drive/folders/1e9tZwDtAaiYKTVFeArjWTIuztLgLg88a?usp=drive_link
Step 2: Click Open Base Folder to open the base folder
Step 3: Paste the configs pack in the configs folder
Step 4: Paste the images pack in the images folder
Step 5: Change Bar Areas
        """)
        textbox.configure(state="disabled")
    def show_page(self, index):
        self.current_page = index

        if index == 0:
            self.page_tos.tkraise()
            self.back_btn.configure(state="disabled")
            self.next_btn.configure(state="normal" if self.agree_var.get() else "disabled")
            self.finish_btn.configure(state="disabled")
        elif index == 1:
            self.page_setup.tkraise()
            self.back_btn.configure(state="normal")
            self.next_btn.configure(state="disabled")
            self.finish_btn.configure(state="normal")

    def go_back(self):
        if self.current_page == 1:
            self.show_page(0)

    def update_next_button(self):
        if self.current_page == 0:
            self.next_btn.configure(state="normal" if self.agree_var.get() else "disabled")

    def go_next(self):
        if self.current_page == 0 and self.agree_var.get():
            self.accepted = True
            self.show_page(1)

    def finish(self):
        self.accepted = True
        self.destroy()
    def on_close(self):
        if not self.accepted:
            self.accepted = False
        self.destroy()
# Main App
class App(CTk):
    def __init__(self):

        # Initialize Class
        super().__init__()

        # Initialize Save And Load (We Only Use
        # Entry, Checkboxes And Comboboxes)
        self.vars = {} # Save Entry Variables Here
        self.checkboxes = {}
        self.comboboxes = {} # Save Combobox Widgets Here For Dynamic Updates
        self.switches = {} # Save Ctkswitch Widgets Here For Load/Save
        self.variables = {} # Save variables for AHK playback

        # Store Screen Width And Height To Use Later
        self.SCREEN_WIDTH = self.winfo_screenwidth()
        self.SCREEN_HEIGHT = self.winfo_screenheight()

        # Hotkey Variables
        self.hotkey_start = Key.f5
        self.hotkey_start_recording = Key.f6
        self.hotkey_stop = Key.f7
        self.hotkey_stop_recording = Key.f8
        self.hotkey_labels = {}  # Store Label Widgets For Dynamic Updates

        # Macro state
        self.macro_running = False
        self.macro_thread = None
        self.is_recording = False    # True only while actively recording
        self.is_playing_back = False # True only while playback is running
        
        # Start Capture Thread
        self.capture_running = False
        self.capture_thread = None
        self.latest_frame = None
        self.capture_lock = threading.Lock()

        # Safe Defaults Before Key Listener Starts (Will Be Overwritten By Load_Misc_Settings)
        self.bar_areas = {"shake": None, "fish": None, "friend": None, "totem": None}
        self.current_config_name = "Basic config"

        self.dispatch_map = {
            "sleep": self._cmd_sleep,
            "mousemove": self._cmd_mousemove,
            "click": self._cmd_click,
            "send": self._cmd_send,
            "pixelsearch": self._cmd_pixelsearch,
            "startcapturethread": self._cmd_startcapturethread,
            "stopcapturethread": self._cmd_stopcapturethread,
            # "if" and "else" are handled structurally by execute_script/
            # _parse_if_node — they never reach the dispatch map.
        }

        # Invalidate Scale Cache If The Window Moves To A Different Monitor
        if sys.platform == "darwin":
            self.bind("<Configure>", lambda e: self._invalidate_scale_cache())
        
        # Show Tos Dialogue
        state, first_launch, new_version = self.load_app_state()

        # 🔥 Show Tos If Needed
        if first_launch or not state.get("tos_accepted", False):
            dialog = TermsOfServiceDialog(self)
            self.wait_window(dialog)

            if not dialog.accepted:
                self.destroy()
                return

            # Mark Accepted
            state["tos_accepted"] = True

        # Update Version After Tos
        state["version"] = APP_VERSION

        self.save_app_state(state)

        # Start Hotkey Listener
        self.key_listener = None
        self.after(100, self.start_listeners)

        # Save and load to TXT
        self.recorded_actions = []
        self.recording_file = os.path.join(CONFIG_DIR, "recording.ahk")

        # Handle AHK errors
        self.playback_errors = []
        self.held_keys = set()

        # Create Window
        self.configure(fg_color="#181836")   # <- Main Window Ultra Dark
        self.geometry("800x600")
        self.title("PyWare Automate V2.0")

        # Status Bar
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Top Bar Frame (Status + Buttons)
        top_bar = CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        top_bar.grid_columnconfigure(0, weight=1)

        # Logo Label
        logo_label = CTkLabel(
            top_bar, 
            text="PYWARE AUTOMATE V2.0",
            font=CTkFont(size=16, weight="bold")
        )
        logo_label.grid(row=0, column=0, sticky="w")

        # Status Label (Left Side)
        self.status_label = CTkLabel(top_bar, text="Macro status: Idle")
        self.status_label.grid(row=1, column=0, pady=5, sticky="w")

        # Buttons Frame (Right Side)
        button_frame = CTkFrame(top_bar, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e")

        CTkButton(
            button_frame,
            text="Upcoming",
            width=120,
            corner_radius=8,
            command=self.open_link("https://docs.google.com/document/d/1WwWWMR-eN-R-GO42IioToHpWTgiXkLoiNE_4NeE-GsU/edit?tab=t.0")
        ).pack(side="left", padx=6)

        CTkButton(
            button_frame,
            text="Website",
            width=120,
            corner_radius=8,
            command=self.open_link("https://sites.google.com/view/icf-automation-network/")
        ).pack(side="left", padx=6)

        CTkButton(
            button_frame,
            text="Tutorial",
            width=120,
            corner_radius=8,
            command=self.open_link("https://docs.google.com/document/d/1EgzNRa5nxw90zxP4aij3DXl7cbarKNW_ozISom4McV0/")
        ).pack(side="left", padx=6)

        # Tabs
        self.tabs = CTkTabview(
            self,
            anchor="w",
            border_color = "#414167", fg_color = "#222244"
        )

        self.tabs._segmented_button.configure(
            fg_color="#414167",
            selected_color="#676780",
            selected_hover_color="#525267",
            unselected_color="#414167",
            unselected_hover_color="#565680",
            text_color="#FFFFFF"
        )

        self.tabs.grid(
            row=1, column=0, columnspan=6,
            padx=20, pady=10, sticky="nsew"
        )

        self.tabs.add("Basic")
        self.tabs.add("Automation")
        self.tabs.add("Unused")

        # Build tabs
        self.build_1_tab(self.tabs.tab("Basic"))
        self.build_2_tab(self.tabs.tab("Automation"))
        self.build_3_tab(self.tabs.tab("Unused"))

        # Load Last Config, Reapply Hotkeys And Set Reset Values
        self.load_last_config()
        self._apply_hotkeys_from_vars()
        self.default_settings_data = self._collect_settings_data()

        # Grid Behavior
        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=0)  # Top_Bar
        self.grid_rowconfigure(1, weight=1)  # Tabs Expand

        self.refresh_config_dropdown() # Auto Refresh Config
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    # Build Gui
    def build_1_tab(self, parent):
        # Configure scroll bar
        scroll = CTkScrollableFrame(parent, fg_color = "#222244")
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Configure grid
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Build main GUI
        basic_settings = CTkFrame(scroll, border_width=2, border_color = "#364167", fg_color = "#222244")
        basic_settings.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        CTkLabel(basic_settings, text="Basic Settings", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")

        CTkLabel(basic_settings, text="config Type:").grid(row=1, column=0, padx=12, pady=10, sticky="w")

        self.config_var = StringVar(value="default")

        self.config_dropdown = CTkComboBox(
            basic_settings,
            variable=self.config_var,
            values=self.get_config_list(),
            command=self.on_config_selected
        )
        self.config_dropdown.grid(row=1, column=1, padx=12, pady=10, sticky="w")

        CTkButton(
            basic_settings, 
            text="🔄", 
            width=40,
            corner_radius=8,
            command=self.refresh_config_dropdown
        ).grid(row=0, column=2, padx=12, pady=10, sticky="w")

        CTkButton(basic_settings, text="Open Base Folder", corner_radius=8, 
                  command=self.open_base_folder,
                  width=140
                  ).grid(row=0, column=1, padx=12, pady=12, sticky="w")

        CTkButton(basic_settings, text="Add", width=40, corner_radius=8, command=self.add_config).grid(row=1, column=2, padx=12, pady=12, sticky="w")
        CTkButton(basic_settings, text="Delete", width=40, corner_radius=8, command=self.delete_config).grid(row=1, column=3, padx=12, pady=12, sticky="w")

        CTkButton(basic_settings, text="Reset Settings", width=140, corner_radius=8, command=self.reset_settings).grid(row=3, column=0, padx=12, pady=12, sticky="w")
        # Hotkey and Hotbar Settings
        playback_and_hotkey = CTkFrame(scroll, border_width=2, border_color = "#364167", fg_color = "#222244")
        playback_and_hotkey.grid(row=1, column=0, padx=20, pady=20, sticky="nw")
        CTkLabel(playback_and_hotkey, text="Hotkey Settings", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        # Key binds
        CTkLabel(playback_and_hotkey, text="Start Key").grid(row=1, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(playback_and_hotkey, text="Change Bar Areas Key").grid(row=2, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(playback_and_hotkey, text="Stop Key").grid(row=3, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(playback_and_hotkey, text="Screenshot Key").grid(row=4, column=0, padx=12, pady=6, sticky="w" )
        # Disable hotkeys
        enable_hotkeys_var = StringVar(value="off")
        self.vars["enable_hotkeys"] = enable_hotkeys_var
        sw = CTkSwitch(playback_and_hotkey, text="Toggle", variable=enable_hotkeys_var, onvalue="on", offvalue="off")
        sw.grid(row=0, column=1, padx=12, pady=8, sticky="w")
        self.switches["enable_hotkeys"] = sw
        # Keys text changer
        start_playback_key_var = StringVar(value="F5")
        self.vars["start_playback_key"] = start_playback_key_var
        start_playback_key_entry = CTkEntry(playback_and_hotkey, width=120, textvariable=start_playback_key_var )
        start_playback_key_entry.grid(row=1, column=1, padx=12, pady=10, sticky="w")
        start_recording_key_var = StringVar(value="F6")
        self.vars["start_recording_key"] = start_recording_key_var
        start_recording_key_entry = CTkEntry(playback_and_hotkey, width=120, textvariable=start_recording_key_var )
        start_recording_key_entry.grid(row=2, column=1, padx=12, pady=10, sticky="w")
        stop_playback_key_var = StringVar(value="F7")
        self.vars["stop_playback_key"] = stop_playback_key_var
        stop_playback_key_entry = CTkEntry(playback_and_hotkey, width=120, textvariable=stop_playback_key_var )
        stop_playback_key_entry.grid(row=3, column=1, padx=12, pady=10, sticky="w")
        stop_recording_key_var = StringVar(value="F8")
        self.vars["stop_recording_key"] = stop_recording_key_var
        stop_recording_key_entry = CTkEntry(playback_and_hotkey, width=120, textvariable=stop_recording_key_var)
        stop_recording_key_entry.grid(row=4, column=1, padx=12, pady=10, sticky="w")

        CTkLabel(playback_and_hotkey, text="Record and Playback", font=CTkFont(size=14, weight="bold")).grid(row=0, column=2, padx=12, pady=8, sticky="w")

        CTkLabel(playback_and_hotkey, text="Record Delay").grid(row=1, column=2, padx=12, pady=8, sticky="w") # This is the label syntax
        record_delay_var = StringVar(value="0.0") # This line is the default/placeholder value
        self.vars["record_delay"] = record_delay_var # This line makes the entry save and load
        record_delay_entry = CTkEntry(playback_and_hotkey, width=120, textvariable=record_delay_var) # This line initializes the entry
        record_delay_entry.grid(row=1, column=3, padx=12, pady=8, sticky="w") # This line initializes the position for the entry (most important)

        CTkLabel(playback_and_hotkey, text="Playback Loops").grid(row=2, column=2, padx=12, pady=8, sticky="w") # This is the label syntax
        playback_loops_var = StringVar(value="1") # This line is the default/placeholder value
        self.vars["playback_loops"] = playback_loops_var # This line makes the entry save and load
        playback_loops_entry = CTkEntry(playback_and_hotkey, width=120, textvariable=playback_loops_var) # This line initializes the entry
        playback_loops_entry.grid(row=2, column=3, padx=12, pady=8, sticky="w") # This line initializes the position for the entry (most important)

        CTkLabel(playback_and_hotkey, text="Playback Interval (minutes)").grid(row=3, column=2, padx=12, pady=8, sticky="w") # This is the label syntax
        playback_interval_var = StringVar(value="0") # This line is the default/placeholder value
        self.vars["playback_interval"] = playback_interval_var # This line makes the entry save and load
        playback_interval_entry = CTkEntry(playback_and_hotkey, width=120, textvariable=playback_interval_var) # This line initializes the entry
        playback_interval_entry.grid(row=3, column=3, padx=12, pady=8, sticky="w") # This line initializes the position for the entry (most important)

        CTkLabel(playback_and_hotkey, text="Playback speed (minutes)").grid(row=4, column=2, padx=12, pady=8, sticky="w") # This is the label syntax
        playback_speed_var = StringVar(value="1") # This line is the default/placeholder value
        self.vars["playback_speed"] = playback_speed_var # This line makes the entry save and load
        playback_speed_entry = CTkEntry(playback_and_hotkey, width=120, textvariable=playback_speed_var) # This line initializes the entry
        playback_speed_entry.grid(row=4, column=3, padx=12, pady=8, sticky="w") # This line initializes the position for the entry (most important)
    # Second tab
    def build_2_tab(self, parent):
        # 4 lines below initialize the scroll wheel and the grid section
        # scroll = CTkScrollableFrame(parent)
        # scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        # parent.grid_rowconfigure(0, weight=1)
        # parent.grid_columnconfigure(0, weight=1)

        # Initialize Frame
        # overlay_options = CTkFrame(scroll, border_width=2)
        # overlay_options.grid(row=4, column=0, padx=20, pady=20, sticky="nw")

        # Frame Header Label (important)
        # CTkLabel(overlay_options, text="Overlay Options", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")

        # Initialize Checkbox
        # fish_overlay_var = StringVar(value="off") # This line and the line below makes the checkbox save and load
        # self.vars["fish_overlay"] = fish_overlay_var
        # fish_overlay_cb = CTkCheckBox(overlay_options, text="Fish Overlay", variable=fish_overlay_var, onvalue="on", offvalue="off") # This line initializes checkboxes
        # fish_overlay_cb.grid(row=1, column=0, padx=12, pady=8, sticky="w") # This line initializes the position for the checkboxes (most important)

        # Normal Label and Entry
        # CTkLabel(sequence_options, text="Delay before casting").grid( row=3, column=0, padx=12, pady=8, sticky="w") # This is the label syntax
        # casting_delay2_var = StringVar(value="0.0") # This line is the default/placeholder value
        # self.vars["casting_delay2"] = casting_delay2_var # This line makes the entry save and load
        # casting_delay2_entry = CTkEntry(sequence_options, width=120, textvariable=casting_delay2_var) # This line initializes the entry
        # casting_delay2_entry.grid(row=3, column=1, padx=12, pady=8, sticky="w") # This line initializes the position for the entry (most important)

        pass # Comments doesn't count in functions
    # Third tab
    def build_3_tab(self, parent):
        # This tab contains a combobox
        # CTkLabel(casting_mode, text="Casting Mode:").grid(row=1, column=0, padx=12, pady=10, sticky="w" ) # You already know what this does in the second tab
        # casting_mode_var = StringVar(value="Normal") # This line is the default/placeholder value
        # self.vars["casting_mode"] = casting_mode_var # This line makes the entry save and load
        # casting_cb = CTkComboBox(casting_mode, values=["Perfect", "Normal"], 
        #                        variable=casting_mode_var, command=lambda v: self.set_status(f"Casting Mode: {v}")
        #                        ) # These 3 lines initializes the combobox
        # casting_cb.grid(row=1, column=1, padx=12, pady=10, sticky="w") # This line initializes the position for the comboboxes (most important)
        # self.comboboxes["casting_mode"] = casting_cb # This line makes the entry save and load
        pass
    def open_link(self, url):
        """Open a URL in the default web browser."""
        return lambda: webbrowser.open(url)
    def set_status(self, text, key=None):
        self.status_label.configure(text=text)
    # Get Config List To Save
    def get_config_list(self):
        if not os.path.exists(CONFIG_DIR):
            return ["default"]
        folders = [name for name in os.listdir(CONFIG_DIR) if os.path.isdir(os.path.join(CONFIG_DIR, name))]
        return folders if folders else ["default"]
    def refresh_config_dropdown(self):
        configs = self.get_config_list()
        self.config_dropdown.configure(values=configs)
    def on_config_selected(self, new_name):
        "Save current config BEFORE switching"
        current_name = getattr(self, "_last_config", None)
        if current_name:
            self.save_settings(current_name)
        # Load New Config
        self.load_settings(new_name)
        # Track Current Config
        self._last_config = new_name
    def save_current_config(self):
        name = self.config_var.get()
        self.save_settings(name)
        self.refresh_config_dropdown()
        self.config_dropdown.set(name)
    # Get Items To Load Tos
    def load_app_state(self):
        # Default State
        state = {
            "version": None,
            "tos_accepted": False
        }

        # Use Config_Path (The Actual File) Instead Of Config_Dir
        if os.path.exists(CONFIG_PATH):  # Config_Path Is The File, Config_Dir Is The Folder
            try:
                with open(CONFIG_PATH, "r") as f:
                    state.update(json.load(f))
            except Exception as e:
                print(f"Error loading config: {e}")
                # Corrupted File = Treat As First Launch
                pass

        # 🔥 Detection Logic
        is_first_launch = state["version"] is None
        is_new_version = state["version"] != APP_VERSION

        return state, is_first_launch, is_new_version

    def save_app_state(self, state):
        # Ensure The Directory Exists Before Writing
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(state, f, indent=4)
            # Print(F"Successfully Saved Config To: {Config_Path}")
        except Exception as e:
            print(f"Error saving config: {e}")
            # Optionally Show Error To User
            messagebox.showerror("Save Error", f"Could not save configuration: {e}")
    # Save And Load Settings
    def save_settings(self, name="default", prompt=True):
        """Save all settings to a JSON config file with optional comparison."""
        if not os.path.exists(CONFIG_PATH):
            os.makedirs(CONFIG_PATH)

        data = self._collect_settings_data()
        
        config_folder = os.path.join(CONFIG_DIR, name)
        os.makedirs(config_folder, exist_ok=True)
        path = os.path.join(config_folder, "config.json")
        
        # Check If Settings Have Changed
        settings_changed = False
        if os.path.exists(path) and prompt:
            try:
                with open(path, "r") as f:
                    old_data = json.load(f)
                if old_data != data:
                    settings_changed = True
            except:
                settings_changed = True
        
        # If Settings Changed And Prompt Is True, Ask User
        if settings_changed and prompt:
            result = messagebox.askyesno(
                "Settings Changed",
                f"The settings for '{name}' have changed.\nDo you want to save these changes?",
                icon=messagebox.QUESTION
            )
            if not result:
                self.set_status(f"Cancelled: Settings not saved")
                return
        
        # Save Misc Settings And Set Status
        self.save_misc_settings()
        self._apply_hotkeys_from_vars()
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            self.save_last_config(name)
            self.set_status(f"Config saved: {name}")
        except Exception as e:
            self.set_status(f"Error saving config: {e}")

    def _collect_settings_data(self):
        data = {}

        for key, var in self.vars.items():
            if key in EXCLUDED_KEYS:
                continue

            if hasattr(var, "get") and var is not None:
                try:
                    data[key] = var.get()
                except Exception as e:
                    print(f"Skipping {key}: {e}")

        return data
    def load_settings(self, name="default"):
        """Load settings from a JSON config file."""
        path = os.path.join(CONFIG_DIR, name, "config.json")
        config_folder = os.path.join(CONFIG_DIR, name.replace(".json", ""))
        if not os.path.exists(path):
            self.set_status(f"Config not found: {name}")
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            self.set_status(f"Error loading config: {e}")
            return
        # Load Stringvar And Related Variables
        try:
            for key, var in self.vars.items():
                if hasattr(var, 'set') and key in data:
                    var.set(data[key])
        except Exception as e:
            print(f"Error loading vars: {e}")
        # Load Checkbox States
        try:
            for key, checkbox in self.checkboxes.items():
                checkbox_key = f"checkbox_{key}"
                if checkbox_key in data:
                    value = data[checkbox_key]
                    if value == "on":
                        checkbox.select()
                    else:
                        checkbox.deselect()
        except Exception as e:
            print(f"Error loading checkboxes: {e}")
        # Load Combobox States
        try:
            for key, cb in self.comboboxes.items():
                combobox_key = f"combobox_{key}"
                if combobox_key in data:
                    cb.set(data[combobox_key])
        except Exception as e:
            print(f"Error loading comboboxes: {e}")
        # Load Switch States (Must Call Select/Deselect To Update Visuals)
        try:
            for key, switch in self.switches.items():
                switch_key = f"switch_{key}"
                if switch_key in data:
                    if data[switch_key] == "on":
                        switch.select()
                    else:
                        switch.deselect()
        except Exception as e:
            print(f"Error loading switches: {e}")
        # Save Misc Settings And Show Status
        self.load_misc_settings()
        self.set_status(f"Config loaded: {name}")
    
    def load_last_config(self):
        """Load the last used config."""
        last_config_path = os.path.join(BASE_PATH, "last_config.json")
        last_config = "default"
        if os.path.exists(last_config_path):
            try:
                with open(last_config_path, "r") as f:
                    data = json.load(f)
                    last_config = data.get("last_config", "default")
            except:
                last_config = "default"
        self.load_settings(last_config)
        # Update The Dropdown And Internal Tracker To Reflect The Loaded Config
        self.config_var.set(last_config)
        self.config_dropdown.set(last_config)
        self._last_config = last_config
    
    def save_last_config(self, name):
        """Save the last used config name (merge into last_config.json)."""
        last_config_path = os.path.join(BASE_PATH, "last_config.json")
        data = {}
        if os.path.exists(last_config_path):
            try:
                with open(last_config_path, "r") as f:
                    data = json.load(f)
            except:
                data = {}
        data["last_config"] = name
        try:
            with open(last_config_path, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving last config: {e}")
    def on_close(self):
        """This function will automatically run before the app is closed"""
        if self._last_config:
            self.save_settings(self._last_config)
        self.destroy()
    def load_misc_settings(self):
        """Load miscellaneous settings from last_config.json."""
        try:
            path = os.path.join(BASE_PATH, "last_config.json")
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    self.current_config_name = data.get("last_config", "Basic config")
                    # Important: Load Hotkeys If Present
                    start_playback_key = data.get("start_playback_key", "F5")
                    change_key = data.get("start_recording_key", "F6")
                    stop_recording_key = data.get("stop_recording_key", "F8")
                    stop_playback_key = data.get("stop_playback_key", "F7")

                    self.vars["start_playback_key"].set(start_playback_key)
                    self.vars["start_recording_key"].set(change_key)
                    self.vars["stop_recording_key"].set(stop_recording_key)
                    self.vars["stop_playback_key"].set(stop_playback_key)

                    # Convert To Pynput Keys
                    self.hotkey_start_recording = self._string_to_key_2(start_playback_key)
                    self.hotkey_stop_recording = self._string_to_key_2(change_key)
                    self.hotkey_start = self._string_to_key_2(stop_recording_key)
                    self.hotkey_stop = self._string_to_key_2(stop_playback_key)
            else:
                self.current_config_name = "Basic config"
        except:
            self.current_config_name = "Basic config"
    def save_misc_settings(self):
        """Save misc settings without overwriting last_config."""
        path = os.path.join(BASE_PATH, "last_config.json")
        # Load Existing Content
        data = {}
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
            except:
                data = {}
        # Update Fields (Merge Only)
        data["last_config"] = self.current_config_name
        # Save Hotkeys
        data["start_playback_key"] = self.vars["start_playback_key"].get()
        data["start_recording_key"] = self.vars["start_recording_key"].get()
        data["stop_recording_key"] = self.vars["stop_recording_key"].get()
        data["stop_playback_key"] = self.vars["stop_playback_key"].get()
        # Write Merged Result
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
    # config Utilities
    def add_config(self):
        """Add a new config configuration with user input."""
        # Create A Dialog Window To Ask For config Name
        dialog = CTkToplevel(self)
        dialog.title("Add New config")
        dialog.geometry("300x120")
        dialog.resizable(False, False)
        
        # Make It Modal
        dialog.transient(self)
        dialog.grab_set()
        
        # Center On Parent
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Label
        label = CTkLabel(dialog, text="Enter config Name:")
        label.pack(pady=10)
        
        # Entry
        entry = CTkEntry(dialog, width=250)
        entry.pack(pady=5)
        entry.focus()
        
        result = {"name": None, "confirmed": False}
        
        def on_confirm():
            new_name = entry.get().strip()
            if not new_name:
                messagebox.showwarning("Invalid Input", "config name cannot be empty!")
                return
            
            # Check If Name Already Exists
            if new_name in self.get_config_list():
                messagebox.showwarning("Duplicate Name", f"config '{new_name}' already exists!")
                return
            
            result["name"] = new_name
            result["confirmed"] = True
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=10)
        
        confirm_btn = CTkButton(button_frame, text="Confirm", command=on_confirm, width=100)
        confirm_btn.pack(side="left", padx=5)
        
        cancel_btn = CTkButton(button_frame, text="Cancel", command=on_cancel, width=100)
        cancel_btn.pack(side="left", padx=5)
        
        # Wait For Dialog
        self.wait_window(dialog)
        
        if result["confirmed"]:
            new_name = result["name"]
            # Create New Config Folder
            config_folder = os.path.join(CONFIG_DIR, new_name)
            os.makedirs(config_folder, exist_ok=True)
            
            # Create Config.Json With Default Settings
            config_data = {
                "stopping_distance": 2.0,
                "velocity_smoothing": 0.45,
                "movement_threshold": 3.0
            }
            
            with open(os.path.join(config_folder, "config.json"), "w") as f:
                json.dump(config_data, f, indent=4)
            
            # Update Dropdown And Select New Config
            self.config_dropdown.configure(values=self.get_config_list())
            self.config_var.set(new_name)
            self.on_config_selected(new_name)
            self.set_status(f"config '{new_name}' created and selected")

    def delete_config(self):
        """Delete current config configuration with confirmation."""
        current = self.config_var.get()

        if current == "default":
            messagebox.showwarning("Cannot Delete", "Cannot delete the default config!")
            return
        
        # Show Confirmation Dialog
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{current}'?\nThis action cannot be undone.",
            icon=messagebox.WARNING
        )
        
        if result:
            config_folder = os.path.join(CONFIG_DIR, current)
            try:
                # Remove The Config Folder
                import shutil
                shutil.rmtree(config_folder)
                
                # Update Dropdown And Switch To Default
                new_list = self.get_config_list()
                self.config_dropdown.configure(values=new_list)
                self.config_var.set("default")
                self.on_config_selected("default")
                self.set_status(f"config '{current}' deleted. Switched to default.")
            except Exception as e:
                messagebox.showerror("Delete Error", f"Failed to delete config: {e}")

    def reset_settings(self):
        """Reset settings to default with confirmation."""
        current = self.config_var.get()
        
        result = messagebox.askyesno(
            "Confirm Reset",
            f"Are you sure you want to reset settings for '{current}' to default?\nThis will undo all customizations.",
            icon=messagebox.WARNING
        )
        
        if result:
            config_folder = os.path.join(CONFIG_DIR, current)
            config_path = os.path.join(config_folder, "config.json")
            
            os.makedirs(config_folder, exist_ok=True)
            
            default_settings = self.get_default_settings()
            
            try:
                with open(config_path, "w") as f:
                    json.dump(default_settings, f, indent=4)
                
                self.on_config_selected(current)
                self.set_status(f"Settings for '{current}' reset to default")
            except Exception as e:
                messagebox.showerror("Reset Error", f"Failed to reset settings: {e}")

    def get_default_settings(self):
        return dict(self.default_settings_data)
    def save_recording_to_txt(self):
        """Save recorded actions into a real .ahk file."""

        config_name = self.config_var.get()
        config_folder = os.path.join(CONFIG_DIR, config_name)
        os.makedirs(config_folder, exist_ok=True)

        ahk_path = os.path.join(config_folder, "recording.ahk")
        self.recording_file = ahk_path

        try:
            with open(ahk_path, "w", encoding="utf-8") as f:

                # HEADER
                f.write("; AutoHotKey Script Generated by PyWare Automate\n")
                f.write("F5:: ; Start macro\n")
                f.write("    SetBatchLines, -1\n")
                f.write("    SetKeyDelay, -1, -1\n")
                f.write("    SetMouseDelay, -1\n")
                f.write("    SetDefaultMouseSpeed, 0\n")
                f.write("    SendMode, Input\n")
                f.write("    ; ---- Start of Macro ----\n")

                # BODY
                for action in self.recorded_actions:
                    f.write(f"    {action}\n")

                # END BLOCK
                f.write("    ; ---- End of Macro ----\n")
                f.write("return\n\n")

                # EXIT HOTKEY
                f.write("F7::\n")
                f.write("    ExitApp\n")
                f.write("return\n")

                # PYWARE COMPATIBILITY LAYER
                f.write("; --- PyWare Compatibility Layer ---\n")
                f.write("StartCaptureThread() {\n")
                f.write("    return\n")
                f.write("}\n\n")

                f.write("StopCaptureThread() {\n")
                f.write("    return\n")
                f.write("}\n")
                f.write("; ---------------------------------\n\n")

            self.set_status(f"Saved AHK to: {ahk_path}")

        except Exception as e:
            self.set_status(f"Error saving AHK: {e}")
    def load_recording_file(self):
        """
        Load the recording file from the active config subfolder.
        Structure:
            configs/ConfigName/recording.ahk
        """

        config_var = self.vars.get("active_config", self.config_var)
        config_name = config_var.get()
        config_dir = CONFIG_DIR
        config_folder = os.path.join(config_dir, config_name.replace(".json", ""))

        # Always ensure the config subfolder exists
        os.makedirs(config_folder, exist_ok=True)

        # Define expected paths
        ahk_path = os.path.join(config_folder, "recording.ahk")

        # Always guarantee file exists
        if not os.path.exists(ahk_path):
            with open(ahk_path, "w", encoding="utf-8") as f:
                f.write("")

        path = ahk_path  # ALWAYS DEFINED
        self.recording_file = path

        # Read file
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            self.recorded_actions = []

            for line in lines:
                line = line.strip()

                # Skip non-macro lines in AHK scripts
                if not line:
                    continue
                if line.startswith(";"):
                    continue
                if line.startswith("F5::"):
                    continue
                if line.startswith("F7::"):
                    continue
                if line.lower() == "return":
                    continue

                self.recorded_actions.append(line)

            # print("Loaded", len(self.recorded_actions), "actions from", path)

        except Exception as e:
            print("Error loading recording (load_recording_file):", e)
            self.recorded_actions = []
    # Key Press Functions
    def _apply_hotkeys_from_vars(self):
        """Apply hotkey StringVars to the live hotkey attributes used by on_key_press."""
        self.hotkey_start = self._string_to_key_2(self.vars["start_playback_key"].get())
        self.hotkey_start_recording = self._string_to_key_2(self.vars["start_recording_key"].get())
        self.hotkey_stop_recording = self._string_to_key_2(self.vars["stop_recording_key"].get())
        self.hotkey_stop = self._string_to_key_2(self.vars["stop_playback_key"].get())
        # Show Status Lines
    def _string_to_key_2(self, key_string):
        key_string = key_string.strip().lower()
        # Try Special Keys
        if hasattr(Key, key_string):
            return getattr(Key, key_string)
        # Fallback To Character
        return key_string
    def _normalize_hotkey_value(self, hotkey):
        if isinstance(hotkey, Key):
            return str(hotkey).replace("Key.", "").lower()
        return str(hotkey).strip().lower()
    def normalize_key(self, key):
        try:
            return key.char.lower()  # Letter Keys
        except AttributeError:
            return str(key).replace("Key.", "").lower()
    def _handle_key_press_main_thread(self, pressed_key):
        enable_hotkeys = (self.vars["enable_hotkeys"].get() or "on")
        # Save Settings (No Prompt - Auto Save Before Macro Starts)
        config_name = self.config_var.get()
        # Refresh live hotkey objects from the current StringVars
        self._apply_hotkeys_from_vars()

        auto_zoom = self.vars.get("auto_zoom")
        casting_mode = self.vars.get("casting_mode")

        if enable_hotkeys == "on":
            if pressed_key == self._normalize_hotkey_value(self.hotkey_start_recording) and not self.macro_running:
                self.save_settings(config_name, prompt=True)
                if auto_zoom is not None and casting_mode is not None and auto_zoom.get() == "on" and casting_mode.get() == "Perfect":
                    messagebox.showwarning("Error", "Auto Zoom In and Perfect Cast can't be enabled at once. \nDisable one of them to continue.")
                else:
                    self.macro_running = True
                    self.after(0, self.withdraw)
                    threading.Thread(target=self.start_recording, daemon=True).start() # This Will Start The Macro In A New Thread, Allowing The Gui To Remain Responsive
            elif pressed_key == self._normalize_hotkey_value(self.hotkey_stop_recording):
                self.stop_recording()
            elif pressed_key == self._normalize_hotkey_value(self.hotkey_start) and not self.macro_running:
                    self.macro_running = True
                    self.after(0, self.withdraw)
                    threading.Thread(target=self.start_playback, daemon=True).start() # This Will Start The Macro In A New Thread, Allowing The Gui To Remain Responsive
            elif pressed_key == self._normalize_hotkey_value(self.hotkey_stop):
                self.stop_playback()
        else:
            self.save_settings(config_name, prompt=False)
    def on_key_press(self, key):
        pressed_key = self.normalize_key(key)
        self.after(0, self._handle_key_press_main_thread, pressed_key)
    def set_status(self, text, key=None):
        self.status_label.configure(text=text)
    # Macro Helper Functions
    def open_base_folder(self):
        folder = BASE_PATH
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":  # Macos
            subprocess.run(["open", folder])
        else:  # Linux
            subprocess.run(["xdg-open", folder])
    def _invalidate_scale_cache(self):
        """Force _get_scale_factor to re-query on next call (e.g. window moved to another monitor)."""
        self._scale_cache = None
    # Recording and playback
    def _string_to_key(self, key_string):
        key_string = key_string.strip().lower()

        # --- 1. SC-code normalization ----
        if key_string.startswith("sc"):
            sc = key_string

            # Ensure lowercase
            sc = sc.lower()

            # Direct mapping (SC63 -> f5)
            if sc in SC_TO_KEY:  # SC_TO_KEY is now module-level
                key_string = SC_TO_KEY[sc]  # replace SC-code with usable name

            # After replacement, fall through and let Key[...] handle it
            # or literal character return

        # --- 2. Normal pynput Key lookup ---
        try:
            return Key[key_string]
        except KeyError:
            return key_string  # normal character keys
    def start_listeners(self):
        self.key_listener = KeyListener(
            on_press=self._unified_key_press,
            on_release=self._unified_key_release
        )
        self.key_listener.daemon = True
        self.key_listener.start()

        self.mouse_listener = mouse.Listener(
            on_click=self._unified_mouse_click,
            on_move=self._unified_mouse_move
        )
        self.mouse_listener.daemon = True
        self.mouse_listener.start()
    # ------------------------------------------------------------------
    # Unified listeners – single keyboard + single mouse listener for
    # the whole app lifetime.  Dispatch to hotkey or recording logic
    # based on self.is_recording.
    # ------------------------------------------------------------------
    def _unified_key_press(self, key):
        """Single on_press handler: recording capture + hotkey dispatch."""
        if self.is_recording:
            self.on_key_press_record(key)
        # Always run hotkey logic so F7/F8 can stop an active recording/playback
        self.on_key_press(key)

    def _unified_key_release(self, key):
        """Single on_release handler: only needed during recording."""
        if self.is_recording:
            self.on_key_release_record(key)

    def _unified_mouse_click(self, x, y, button, pressed):
        """Single on_click handler: recording capture only."""
        if self.is_recording:
            self.on_mouse_click(x, y, button, pressed)

    def _unified_mouse_move(self, x, y):
        """Single on_move handler: recording capture only."""
        if self.is_recording:
            self.on_mouse_move(x, y)

    def on_mouse_click(self, x, y, button, pressed):
        button_name = str(button).replace("Button.", "")
        x = round(x)
        y = round(y)
        event = f"Click, {x}, {y}, {'Down' if pressed else 'Up'} {button_name}"
        self.record_action(event)

    def on_mouse_move(self, x, y):
        self.latest_mouse_move = (x, y)
    def _normalize_key_for_ahk(self, key):
        """
        Converts pynput keys into valid AHK-friendly key names.
        Fixes <63>, <65288>, ctrl_l, shift_r, etc.
        """

        # --- If key is a special Key object (Key.enter, Key.shift, etc.) ---
        if isinstance(key, Key):
            special_map = {
                Key.alt: "Alt",
                Key.alt_l: "Alt",
                Key.alt_r: "Alt",
                Key.ctrl: "Ctrl",
                Key.ctrl_l: "Ctrl",
                Key.ctrl_r: "Ctrl",
                Key.shift: "Shift",
                Key.shift_l: "Shift",
                Key.shift_r: "Shift",
                Key.enter: "Enter",
                Key.space: "Space",
                Key.tab: "Tab",
                Key.backspace: "Backspace",
                Key.delete: "Delete",
                Key.esc: "Esc",
                Key.up: "Up",
                Key.down: "Down",
                Key.left: "Left",
                Key.right: "Right",
            }
            return special_map.get(key, str(key).replace("Key.", "").title())

        # --- If it's a character key ---
        if hasattr(key, "char") and key.char:
            c = key.char
            if c.isalnum():
                return c  # safe: letters + numbers

            # return raw character, wrapping will be handled later
            return c

        # --- Fallback: convert <63> => SC063 ---
        s = str(key)

        if s.startswith("<") and s.endswith(">"):
            code = s[1:-1]
            return f"sc{code.lower()}"

        # Default clean-up
        s = s.replace("Key.", "")
        return s
    def on_key_press_record(self, key):
        key_name = self._normalize_key_for_ahk(key)

        # Always wrap in braces for AHK correctness
        event = f"Send, {{{key_name} down}}"
        self.record_action(event)

    def on_key_release_record(self, key):
        key_name = self._normalize_key_for_ahk(key)
        if key_name == "sc63": # Disable this specific unknown key
            event = f"; Disabled"
        else:
            event = f"Send, {{{key_name} up}}"
        self.record_action(event)
    def start_capture_thread(self):
        if self.capture_running:
            return

        self.capture_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
    def stop_capture_thread(self):
        self.capture_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1)
    def record_action(self, action_text):
        """Record delay + the action into recorded_actions list."""

        now = time.time()
        delay = now - self.last_action_time
        self.last_action_time = now

        # Add delay directly (NO recursive call!)
        if delay > 0.001:
            delay2 = int(delay * 1000)
            self.recorded_actions.append(f"Sleep, {delay2}")

        # Add the actual action
        self.recorded_actions.append(action_text)
    # Loops
    def add_loop_start(self, count):
        self.recorded_actions.append(f"Loop, {count}")
        self.recorded_actions.append("{")

    def add_loop_end(self):
        self.recorded_actions.append("}")
    # ------------------------------------------------------------------ #
    #  PLAYBACK ENGINE                                                     #
    # ------------------------------------------------------------------ #

    def execute_script(self, actions, speed=1.0):
        """
        Top-level entry point.  Parses the flat action list into a tree of
        Block objects and then runs them through _exec_block, which handles
        loops, variables, and if/else/endif nesting at every depth.
        """
        block = self._parse_block(actions, 0, len(actions))
        self._exec_block(block, speed)

    # --- Parser -------------------------------------------------------- #

    def _parse_block(self, actions, start, end):
        """
        Converts a slice of the flat actions list (indices [start, end))
        into a list of node dicts that the executor understands.

        Node kinds
        ----------
        {"kind": "line",   "text": str}
        {"kind": "loop",   "count": int|None, "body": [nodes]}   # None = infinite
        {"kind": "while",  "condition": str,  "body": [nodes]}
        {"kind": "if",     "condition": str,
                           "then": [nodes], "else_": [nodes]}
        """
        nodes = []
        i = start

        while i < end:
            raw = actions[i].strip()

            # ---- skip structural noise ----
            if self._should_skip_line(raw):
                i += 1
                continue

            lower = raw.lower()

            # ---- Loop, N  /  Loop (infinite) ----
            if re.match(r"^loop\b", lower):
                count, body_nodes, i = self._parse_loop_node(actions, i, end)
                nodes.append({"kind": "loop", "count": count, "body": body_nodes})
                continue

            # ---- While, <condition> ----
            if re.match(r"^while\b", lower):
                condition, body_nodes, i = self._parse_while_node(actions, i, end)
                nodes.append({"kind": "while", "condition": condition, "body": body_nodes})
                continue

            # ---- If, <condition> ----
            if re.match(r"^if\b", lower):
                then_nodes, else_nodes, condition, i = self._parse_if_node(actions, i, end)
                nodes.append({"kind": "if", "condition": condition,
                               "then": then_nodes, "else_": else_nodes})
                continue

            # ---- Else / EndIf / closing brace → handled by callers ----
            if lower in ("else", "endif") or raw == "}":
                break

            # ---- Plain line ----
            nodes.append({"kind": "line", "text": raw})
            i += 1

        return nodes

    def _collect_block_body(self, actions, i, end):
        """
        Reads lines until the matching closing brace or until a keyword
        that terminates the block (else / endif).
        Returns (body_lines_slice_start, slice_end, new_i).

        Supports both brace-delimited  { … }  and brace-less (one-liners).
        """
        # Advance past optional opening brace on the *same* line as the keyword
        # (already consumed) or on the next line.
        if i < end and actions[i].strip() == "{":
            i += 1  # skip standalone opening brace

        body_start = i
        depth = 1 if (i > 0 and "{" in actions[i - 1]) else 1

        # Walk forward and match braces
        depth = 0
        body_lines = []
        while i < end:
            stripped = actions[i].strip()
            if stripped == "{":
                depth += 1
                i += 1
                continue
            if stripped == "}":
                if depth == 0:
                    i += 1  # consume the closing brace
                    break
                depth -= 1
                i += 1
                continue
            lower = stripped.lower()
            if depth == 0 and lower in ("else", "endif"):
                break
            body_lines.append(stripped)
            i += 1

        return body_lines, i

    def _parse_loop_node(self, actions, i, end):
        """Parse  Loop[, N]  { … }  and return (count, body_nodes, new_i)."""
        header = actions[i].strip()
        i += 1

        # Extract count from  "Loop, 10"  or  "Loop, 10 {"  or just  "Loop"
        m = re.match(r"loop\s*(?:,\s*(\d+))?", header, re.IGNORECASE)
        count = int(m.group(1)) if (m and m.group(1)) else None  # None = infinite

        # Consume optional opening brace on same line or next line
        if i < end and actions[i].strip() == "{":
            i += 1

        body_lines, i = self._collect_block_body(actions, i, end)
        body_nodes = self._parse_block(body_lines, 0, len(body_lines))
        return count, body_nodes, i

    def _parse_while_node(self, actions, i, end):
        """Parse  While, <condition>  { … }  and return (condition, body_nodes, new_i)."""
        header = actions[i].strip()
        i += 1

        m = re.match(r"while\s*,?\s*(.+)", header, re.IGNORECASE)
        condition = m.group(1).strip() if m else "False"

        if i < end and actions[i].strip() == "{":
            i += 1

        body_lines, i = self._collect_block_body(actions, i, end)
        body_nodes = self._parse_block(body_lines, 0, len(body_lines))
        return condition, body_nodes, i

    def _parse_if_node(self, actions, i, end):
        """
        Parse  If, <condition>  { … }  [Else  { … }]  [EndIf]
        Returns (then_nodes, else_nodes, condition, new_i).
        """
        header = actions[i].strip()
        i += 1

        m = re.match(r"if\s*,?\s*(.+)", header, re.IGNORECASE)
        condition = m.group(1).strip() if m else "False"

        if i < end and actions[i].strip() == "{":
            i += 1

        then_lines, i = self._collect_block_body(actions, i, end)
        then_nodes = self._parse_block(then_lines, 0, len(then_lines))

        # Check for Else
        else_nodes = []
        if i < end and actions[i].strip().lower() == "else":
            i += 1  # consume "else"
            if i < end and actions[i].strip() == "{":
                i += 1
            else_lines, i = self._collect_block_body(actions, i, end)
            else_nodes = self._parse_block(else_lines, 0, len(else_lines))

        # Consume optional EndIf
        if i < end and actions[i].strip().lower() == "endif":
            i += 1

        return then_nodes, else_nodes, condition, i

    # --- Executor ------------------------------------------------------ #

    def _exec_block(self, nodes, speed):
        """
        Recursively execute a list of parsed nodes.
        Respects self.macro_running so F7 stops everything immediately.
        """
        for node in nodes:
            if not self.macro_running:
                return

            kind = node["kind"]

            if kind == "line":
                self._exec_line(node["text"], speed)

            elif kind == "loop":
                count = node["count"]
                body  = node["body"]
                if count is None:
                    # Infinite loop — only self.macro_running breaks it
                    while self.macro_running:
                        self._exec_block(body, speed)
                else:
                    for _ in range(count):
                        if not self.macro_running:
                            return
                        self._exec_block(body, speed)

            elif kind == "while":
                while self.macro_running and self._evaluate_condition(
                        self._resolve_variables(node["condition"])):
                    self._exec_block(node["body"], speed)

            elif kind == "if":
                resolved_cond = self._resolve_variables(node["condition"])
                if self._evaluate_condition(resolved_cond):
                    self._exec_block(node["then"], speed)
                else:
                    self._exec_block(node["else_"], speed)

    def _exec_line(self, line, speed):
        """Execute a single resolved action line."""
        # Variable assignment  (x := expr)
        if self._handle_assignment(line):
            return
        # Math shorthand  (x += 5 / x -= 2 / x *= 3 / x /= 2)
        if self._handle_math(line):
            return
        # Substitute %Var% tokens before dispatching
        line = self._handle_variable(line)
        self.playback_action(line, speed)
    # Playback functions
    def _handle_assignment(self, action):
        """
        Handles:
        x := 612
        """
        if ":=" in action:
            var, value = action.split(":=", 1)
            var = var.strip()
            value = value.strip()

            try:
                self.variables[var] = eval(value)
            except:
                self.variables[var] = value

            return True  # handled

        return False
    def _handle_math(self, action):
        """
        Handles compound assignment operators:
            x += 5   x -= 2   x *= 3   x /= 2
        Values on the right-hand side may themselves be expressions or
        %variable% references, so we resolve them before evaluating.
        """
        for op in ("+=", "-=", "*=", "/="):
            if op in action:
                var, rhs = action.split(op, 1)
                var = var.strip()
                rhs = self._handle_variable(rhs.strip())
                try:
                    rhs_val = float(eval(rhs))
                except Exception:
                    return False

                cur = self.variables.get(var, 0)
                try:
                    cur = float(cur)
                except Exception:
                    cur = 0.0

                if op == "+=":
                    self.variables[var] = cur + rhs_val
                elif op == "-=":
                    self.variables[var] = cur - rhs_val
                elif op == "*=":
                    self.variables[var] = cur * rhs_val
                elif op == "/=":
                    self.variables[var] = cur / rhs_val if rhs_val != 0 else 0
                return True

        return False

    def _handle_variable(self, action):
        """
        Replace AHK-style variables:
        %Var% → actual value
        """

        def replace_var(match):
            var_name = match.group(1)
            return str(self.variables.get(var_name, 0))

        # Replace %Var% patterns
        action = re.sub(r"%(\w+)%", replace_var, action)

        return action
    def _should_skip_line(self, line):
        line = line.strip()

        if not line:
            return True

        # Hotkeys / labels
        if line.endswith("::"):
            return True

        # Block markers
        if line in ("{", "}"):
            return True

        # AHK boilerplate
        if line.startswith((
            "SetBatchLines",
            "SetKeyDelay",
            "SetMouseDelay",
            "SetTitleMatchMode",
            "SendMode"
        )):
            return True

        # Flow control noise
        if line.lower() == "return":
            return True

        # Function definitions (important)
        if line.endswith("{") and "(" in line:
            return True

        return False
    # _handle_loop removed — loop parsing is now done by _parse_loop_node
    # inside the block-aware execute_script engine.
    def _clean_ahk_braces(self, key_raw):
        # Remove braces like {Enter}, {Down}, {Space}
        key_raw = key_raw.strip()

        if key_raw.startswith("{") and key_raw.endswith("}"):
            key_raw = key_raw[1:-1]  # strip {}

        return key_raw.lower()
    def add_error(self, action, description="Syntax error"):
        self.playback_errors.append(
            f"Error: The script contains syntax errors.\n"
            f"Specifically:\n"
            f"    {action}\n"
            f"    {description}\n"
        )
        print(f"Error: The script contains syntax errors.",
            f"Specifically:",
            f"    {action}",
            f"    {description}")
    def release_all_keys(self):
        for key in list(self.held_keys):
            try:
                keyboard_controller.release(key)
            except:
                pass
        self.held_keys.clear()
    def force_release_modifiers(self):
        for key in [Key.ctrl, Key.shift, Key.alt]:
            try:
                keyboard_controller.release(key)
            except:
                pass
    def _resolve_variables(self, text):
        def replacer(match):
            var_name = match.group(1)
            return str(self.variables.get(var_name, f"%{var_name}%"))

        return re.sub(r"%(.+?)%", replacer, text)
    # Functions to support pipelines
    def _grab_screen_full(self, thread_local):
        scale = self._get_scale_factor()

        if not hasattr(thread_local, "sct"):
            thread_local.sct = mss.mss()

        if not hasattr(thread_local, "monitor"):
            thread_local.monitor = {
                "left": 0,
                "top": 0,
                "width": int(self.SCREEN_WIDTH * scale),
                "height": int(self.SCREEN_HEIGHT * scale)
            }

        m = thread_local.monitor
        img = thread_local.sct.grab(m)

        return np.frombuffer(img.raw, dtype=np.uint8).reshape(
            m["height"], m["width"], 4
        )[:, :, :3]


    def _capture_loop_full(self, stop_event, scan_delay):
        thread_local = threading.local()

        # On Macos, Mss Uses Core Graphics Which Is Slow To Call In A Tight Loop.
        # Enforce A Minimum Sleep So We Don'T Saturate The Cpu And Starve The Game
        # And The Pid Thread.  At 20 Fps A Frame Is ~0.05 S; Floor At 0.033 S
        # (~30 Fps) So We Never Spin Faster Than The Game Can Pconfiguce New Pixels.
        import sys as _sys
        _mac_floor = 0.033 if _sys.platform == "darwin" else 0.0

        try:
            while self.macro_running and not stop_event.is_set():
                t0 = time.perf_counter()
                frame = self._grab_screen_full(thread_local)

                with self._cap_lock:
                    self._cap_frame = frame
                    self._cap_event.set()

                elapsed = time.perf_counter() - t0
                sleep_for = max(_mac_floor, scan_delay) - elapsed
                if sleep_for > 0:
                    time.sleep(sleep_for)
        finally:
            sct = getattr(thread_local, "sct", None)
            if sct is not None:
                try:
                    sct.close()
                except Exception:
                    pass
            self._cap_event.set()
    def get_latest_frame(self):
        with self.capture_lock:
            return None if self.latest_frame is None else self.latest_frame.copy()
    def _stop_active_capture(self, join_timeout=0.2):
        stop_event = getattr(self, "_active_capture_stop", None)
        thread = getattr(self, "_active_capture_thread", None)

        if stop_event is not None:
            stop_event.set()

        if (
            thread is not None
            and thread.is_alive()
            and thread is not threading.current_thread()
        ):
            thread.join(join_timeout)

        self._active_capture_stop = None
        self._active_capture_thread = None

    def _start_capture(self, scan_delay):
        """
        Starts a background thread that continuously grabs full frames.
        Stops any previously running capture thread first to prevent races.
        Returns a stop_event to terminate the new thread.
        """
        # Overlapping Capture Threads Share _Cap_Frame/_Cap_Event/_Cap_Lock And
        # Will Race Each Other, Which Causes Segfaults In The Mss/Coregraphics
        # Capture Path On Macos.
        self._stop_active_capture()

        self._cap_frame = None

        # Ensure These Exist
        if not hasattr(self, "_cap_lock"):
            self._cap_lock = threading.Lock()
        if not hasattr(self, "_cap_event"):
            self._cap_event = threading.Event()

        self._cap_event.clear()
        stop_event = threading.Event()
        self._active_capture_stop = stop_event  # Track The Active Stop Event

        import sys as _sys
        _mac_floor = 0.033 if _sys.platform == "darwin" else 0.0

        def _loop():
            try:
                thread_local = threading.local()

                while self.macro_running and not stop_event.is_set():
                    t0 = time.perf_counter()
                    frame = self._grab_screen_full(thread_local)

                    with self._cap_lock:
                        self._cap_frame = frame
                        self._cap_event.set()

                    elapsed = time.perf_counter() - t0
                    sleep_for = max(_mac_floor, scan_delay) - elapsed
                    if sleep_for > 0:
                        time.sleep(sleep_for)
            finally:
                sct = getattr(thread_local, "sct", None)
                if sct is not None:
                    try:
                        sct.close()
                    except Exception:
                        pass
                self._cap_event.set()
                if self._active_capture_stop is stop_event:
                    self._active_capture_stop = None
                if self._active_capture_thread is threading.current_thread():
                    self._active_capture_thread = None

        thread = threading.Thread(target=_loop, daemon=True, name="PyWareCapture")
        self._active_capture_thread = thread
        thread.start()
        return stop_event
    def _find_first_pixel(self, frame, target_rgb, tolerance=8):
        tolerance = int(np.clip(tolerance, 0, 255))

        frame_i = frame.astype(np.int16)
        target = np.array(target_rgb, dtype=np.int16)

        mask = np.max(
            np.abs(frame_i - target),
            axis=-1
        ) <= tolerance
        
        coords = np.argwhere(mask)

        if coords.size > 0:
            y, x = coords[0]
            return int(x), int(y)

        return None
    def _parse_ahk_color(self, color):
        """
        Convert AHK color (0xBBGGRR) or standard hex (#RRGGBB) to RGB tuple.
        """

        if not color:
            return None

        color = color.strip().lower()

        try:
            # --- AHK format: 0xBBGGRR ---
            if color.startswith("0x"):
                value = int(color, 16)

                b = (value >> 16) & 0xFF
                g = (value >> 8) & 0xFF
                r = value & 0xFF

                return (r, g, b)  # ✅ RGB

            # --- Standard hex: #RRGGBB ---
            if color.startswith("#"):
                color = color[1:]

                r = int(color[0:2], 16)
                g = int(color[2:4], 16)
                b = int(color[4:6], 16)

                return (r, g, b)

        except Exception:
            return None

        return None
    # Pipelines
    def _cmd_sleep(self, action, speed):
        _, value = action.split(",", 1)
        ms = int(value.strip())
        time.sleep((ms / 1000) / speed)
    def _cmd_mousemove(self, action, speed):
        _, args = action.split(",", 1)
        x, y = [int(v.strip()) for v in args.split(",")]
        mouse_controller.position = (x, y)
    def _cmd_click(self, action, speed):
        try:
            _, args = action.split(",", 1)
            parts = [p.strip() for p in args.split(",")]

            # --- REQUIRED ---
            if len(parts) < 2:
                raise ValueError("Click requires at least x and y")

            x = int(float(parts[0]))
            y = int(float(parts[1]))

            # --- DEFAULT BEHAVIOR (AHK style) ---
            down_up = "click"
            btn = "left"

            # --- OPTIONAL EVENT ---
            if len(parts) >= 3:
                event = parts[2].split()

                if len(event) >= 1:
                    down_up = event[0].lower()

                if len(event) >= 2:
                    btn = event[1].lower()

            # --- MAP BUTTON ---
            if btn in ("left", "l"):
                button = mouse.Button.left
            elif btn in ("right", "r"):
                button = mouse.Button.right
            elif btn in ("middle", "m"):
                button = mouse.Button.middle
            else:
                return

            mouse_controller.position = (x, y)

            # --- EXECUTE ---
            if down_up == "down":
                mouse_controller.press(button)
            elif down_up == "up":
                mouse_controller.release(button)
            else:
                # Default = full click
                mouse_controller.click(button)

        except Exception as e:
            self.add_error(action, str(e))
    def _cmd_send(self, action, speed):
        _, raw = action.split(",", 1)
        raw = raw.strip()

        if raw.startswith("{") and raw.endswith("}"):
            inner = raw[1:-1].strip()
            tokens = inner.split()

            key_name = tokens[0].lower()
            key = self._string_to_key(key_name)

            if len(tokens) == 1:
                keyboard_controller.press(key)
                keyboard_controller.release(key)

            elif tokens[1] == "down":
                keyboard_controller.press(key)
                self.held_keys.add(key)

            elif tokens[1] == "up":
                keyboard_controller.release(key)
                self.held_keys.discard(key)

            return

        if raw.startswith(("^", "!", "+")):
            mod = raw[0]
            key_raw = self._clean_ahk_braces(raw[1:])
            key = self._string_to_key(key_raw)

            if mod == "^":
                keyboard_controller.press(Key.ctrl)
                keyboard_controller.press(key)
                keyboard_controller.release(key)
                keyboard_controller.release(Key.ctrl)

            elif mod == "!":
                keyboard_controller.press(Key.alt)
                keyboard_controller.press(key)
                keyboard_controller.release(key)
                keyboard_controller.release(Key.alt)

            elif mod == "+":
                keyboard_controller.press(Key.shift)
                keyboard_controller.press(key)
                keyboard_controller.release(key)
                keyboard_controller.release(Key.shift)

            return

        key_raw = self._clean_ahk_braces(raw)
        key = self._string_to_key(key_raw)
        keyboard_controller.press(key)
        keyboard_controller.release(key)
    def _cmd_pixelsearch(self, action, speed):
        try:
            _, args = action.split(",", 1)
            parts = [p.strip() for p in args.split(",")]

            out_x = parts[0]
            out_y = parts[1]

            x1 = int(parts[2])
            y1 = int(parts[3])
            x2 = int(parts[4])
            y2 = int(parts[5])

            color = parts[6]
            tolerance = int(parts[7]) if len(parts) > 7 else 8

            frame = self.get_latest_frame()
            if frame is None:
                self.variables[out_x] = -1
                self.variables[out_y] = -1
                return

            # Crop AFTER capture (your optimization)
            region = frame[y1:y2, x1:x2]

            rgb = self._parse_ahk_color(color)

            if rgb is None:
                self.variables[out_x] = -1
                self.variables[out_y] = -1
                return
            
            pos = self._find_first_pixel(region, rgb, tolerance)

            if pos:
                px, py = pos
                self.variables[out_x] = px + x1
                self.variables[out_y] = py + y1
            else:
                self.variables[out_x] = -1
                self.variables[out_y] = -1

            if pos:
                px, py = pos
                px += x1
                py += y1

                self.variables[out_x] = px
                self.variables[out_y] = py
                self.variables["ErrorLevel"] = 0
            else:
                self.variables[out_x] = -1
                self.variables[out_y] = -1
                self.variables["ErrorLevel"] = 1

        except Exception as e:
            self.playback_errors.append((action, str(e)))
    def _cmd_startcapturethread(self, action, speed):
        self.start_capture_thread()

    def _cmd_stopcapturethread(self, action, speed):
        self.stop_capture_thread()
    # _cmd_if and _cmd_else have been removed.
    # Conditional logic is now handled structurally by _parse_if_node /
    # _exec_block, so "If" lines never reach the dispatch map.
    def _evaluate_condition(self, condition):
        """
        Evaluate a condition string, supporting AHK-style operators.

        Examples
        --------
        ErrorLevel = 0       →  ErrorLevel == 0
        Px != -1
        Px > 100
        x >= 5 and y < 10
        """
        # Substitute variable values
        for var, value in self.variables.items():
            condition = re.sub(rf"\b{re.escape(var)}\b", str(value), condition)

        # AHK bare `=` → Python `==` (but leave !=, >=, <=, == untouched)
        condition = re.sub(r'(?<![!<>=])=(?!=)', '==', condition)

        # AHK `&&` / `||`  →  Python `and` / `or`
        condition = condition.replace("&&", " and ").replace("||", " or ")

        try:
            return bool(eval(condition))
        except Exception:
            return False
    # Playback
    def playback_action(self, action, speed=1.0):
        action = action.strip()
        action = self._resolve_variables(action)

        # Ignore
        if action.startswith(("SetBatchLines", "SetKeyDelay", "SetMouseDelay", "SetTitleMatchMode", "SendMode")):
            return

        if action.startswith((";", "F5::", "F7::", "ExitApp")) or action.lower() == "return":
            return

        if action.startswith(("{", "}")):
            return

        # Variable assignment
        if ":=" in action:
            action = self._handle_variable(action)
            return

        # Dispatcher
        cmd = action.split(",", 1)[0].strip().lower()
        handler = self.dispatch_map.get(cmd)

        if handler:
            try:
                handler(action, speed)
            except Exception as e:
                self.add_error(action, str(e))
            return

        self.add_error(action, "Unknown or unsupported command")
    def start_recording(self):
        print("Macro Status: Recording...")
        self.macro_running = True
        self.recorded_actions = []

        config_name = self.config_var.get()  # use existing system
        config_folder = os.path.join(CONFIG_DIR, config_name)

        # Ensure folder exists
        os.makedirs(config_folder, exist_ok=True)

        # Set recording path inside config folder
        self.recording_file = os.path.join(config_folder, "recording.ahk")

        self.pending_events = []
        self.latest_mouse_move = None
        self.last_record_time = time.time()
        self.last_action_time = time.time()

        scan_delay = float(self.vars["record_delay"].get() or 0.05)

        # Signal the unified listeners to start capturing events
        self.is_recording = True

        while self.macro_running:
            now = time.time()

            if now - self.last_record_time >= scan_delay:
                # Log buffered keyboard events
                if self.pending_events:
                    self.recorded_actions.extend(self.pending_events)
                    self.pending_events.clear()

                # Log last mouse position if moved
                if self.latest_mouse_move:
                    x, y = self.latest_mouse_move
                    x = round(x)
                    y = round(y)
                    self.record_action(f"MouseMove, {x}, {y}")
                    self.latest_mouse_move = None

                self.last_record_time = now

            time.sleep(0.001)  # prevent CPU burn
    def stop_recording(self):
        if not self.macro_running:
            return

        self.macro_running = False
        self.is_recording = False
        self.after(0, self.deiconify)
        print("Macro Status: Stopped Recording")

        # convert path: recording.txt → recording.ahk
        ahk_path = self.recording_file.replace(".txt", ".ahk")
        self.recording_file = ahk_path

        try:
            with open(ahk_path, "w", encoding="utf-8") as f:

                # HEADER
                f.write("; AutoHotKey Script Generated by PyWare Automate\n")
                f.write("F5:: ; Start macro\n")
                f.write("    SetBatchLines, -1\n")
                f.write("    SetKeyDelay, -1\n")
                f.write("    SetMouseDelay, -1\n")
                f.write("    SetTitleMatchMode, \n")
                f.write("    SendMode, Input\n")
                f.write("    ; ---- Start of Macro ----\n")

                # BODY: recorded actions
                for action in self.recorded_actions:
                    f.write(f"    {action}\n")

                # END BLOCK
                f.write("    ; ---- End of Macro ----\n")
                f.write("return\n\n")

                # EXIT HOTKEY
                f.write("F7::\n")
                f.write("    ExitApp\n")
                f.write("return\n")

                # PYWARE COMPATIBILITY LAYER
                f.write("; --- PyWare Compatibility Layer ---\n")
                f.write("StartCaptureThread() {\n")
                f.write("    return\n")
                f.write("}\n\n")

                f.write("StopCaptureThread() {\n")
                f.write("    return\n")
                f.write("}\n")
                f.write("; ---------------------------------\n\n")

            # print("Saved", len(self.recorded_actions), "actions to", ahk_path)

        except Exception as e:
            print("Error saving AHK:", e)
    def start_playback(self):
        # print("Macro Status: Started Playback")
        self.macro_running = True
        time.sleep(1) # to prevent macro never runs

        # Load actions from file (handles both .ahk and .txt, skips headers/comments)
        self.after(0, self.load_recording_file)
        time.sleep(0.1)  # brief wait for the main-thread call to complete

        # ---- READ SETTINGS ----
        loops_raw = self.vars["playback_loops"].get().strip()
        interval_raw = self.vars["playback_interval"].get().strip()

        # default values
        try:
            loops = int(float(loops_raw))
        except:
            loops = 1

        try:
            interval_minutes = float(interval_raw)
        except:
            interval_minutes = 0.0

        interval_seconds = interval_minutes * 60

        # Read playback speed multiplier (1.0 = normal, 2.0 = 2× faster)
        try:
            speed = float(self.vars["playback_speed"].get().strip())
            if speed <= 0:
                speed = 1.0
        except:
            speed = 1.0

        # If loops is 0 → infinite loop
        infinite_loop = (loops == 0)

        loop_count = 0
        self.is_playing_back = True  # suppress hotkey processing during playback

        # ---- PLAYBACK LOOP ----
        while self.macro_running and (infinite_loop or loop_count < loops):

            loop_count += 1
            # print(f"Starting loop {loop_count}")

            # Play all actions
            self.execute_script(self.recorded_actions, speed)

            if not self.macro_running:
                break

            # If there is an interval → wait before next loop
            if interval_seconds > 0 and (infinite_loop or loop_count < loops):
                # print(f"Waiting {interval_seconds} seconds before next loop...")
                time.sleep(interval_seconds)

        # finished looping
        self.is_playing_back = False
        self.set_status("Macro Status: Stopped Playback (Done)")
        self.macro_running = False
        # Check for errors
        if self.playback_errors:
            errors_text = "\n".join(self.playback_errors)
            self.playback_errors.clear()
            messagebox.showerror("Script Error", errors_text)
        self.after(0, self.deiconify)
        self.release_all_keys()
        self.force_release_modifiers()
    def stop_playback(self):
        if not self.macro_running:
            return

        self.macro_running = False
        self.is_playing_back = False
        self.release_all_keys()   # 🔥 IMPORTANT
        self.after(0, self.deiconify)
        self.set_status("Macro Status: Stopped Playback")
if __name__ == "__main__":
    app = App()
    app.mainloop()
