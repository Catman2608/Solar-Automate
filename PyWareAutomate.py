# Initialization
from customtkinter import *
from tkinter import messagebox
import os
import sys
import subprocess
# Keyboard and Mouse
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
# Key Listeners
import threading
from pynput.keyboard import Listener as KeyboardListener, Key
from pynput.mouse import Listener as MouseListener
macro_running = False
macro_thread = None
# Key Inputs
import threading
# Time
import time
import json
# Web browsing
import webbrowser
# Initialize controllers
keyboard_controller = KeyboardController()
mouse_controller = MouseController()
# Test
# Set appearance
set_default_color_theme("blue")

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
def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()

# ---- SINGLE SOURCE OF TRUTH ----
if getattr(sys, 'frozen', False):
    # Running as compiled app
    if sys.platform == "darwin":
        USER_CONFIG_DIR = os.path.join(
            os.path.expanduser("~"),
            "Library", "Application Support",
            "PyWareAutomateV1", "configs"
        )
    elif sys.platform == "win32":
        USER_CONFIG_DIR = os.path.join(
            os.path.expanduser("~"),
            "AppData", "Roaming",
            "PyWareAutomateV1", "configs"
        )
    else:
        USER_CONFIG_DIR = os.path.join(BASE_PATH, "configs")
else:
    # Development mode
    USER_CONFIG_DIR = os.path.join(BASE_PATH, "configs")

os.makedirs(USER_CONFIG_DIR, exist_ok=True)
class App(CTk):
    def __init__(self):
        super().__init__()
        self.vars = {}     # Entry / Slider / Combobox vars
        self.vars = {}        # IntVar / StringVar / BooleanVar
        self.checkboxes = {}   # CTkCheckBox vars
        self.comboboxes = {}   # CTkComboBox vars
        
        # Screen size (cache once – thread safe)
        self.SCREEN_WIDTH = self.winfo_screenwidth()
        self.SCREEN_HEIGHT = self.winfo_screenheight()

        # Window 
        self.geometry("800x600")
        self.title("PyWare Automate V1.0")

        # Macro state
        self.macro_running = False
        self.macro_thread = None
        self.is_recording = False    # True only while actively recording
        self.is_playing_back = False # True only while playback is running

        # Hotkey variables
        self.hotkey_start = Key.f5
        self.hotkey_stop = Key.f7
        self.hotkey_start_recording = Key.f6
        self.hotkey_stop_recording = Key.f8
        self.hotkey_labels = {}  # Store label widgets for dynamic updates

        # Single persistent keyboard listener (handles both hotkeys and recording)
        self.key_listener = KeyboardListener(
            on_press=self._unified_key_press,
            on_release=self._unified_key_release,
        )
        self.key_listener.daemon = True

        # Single persistent mouse listener (handles both hotkeys and recording)
        self.mouse_listener = MouseListener(
            on_click=self._unified_mouse_click,
            on_move=self._unified_mouse_move,
        )
        self.mouse_listener.daemon = True

        # Start key listeners safely
        try:
            self.key_listener.start()
            self.mouse_listener.start()
        except:
            self.set_status("Error starting key listeners, please restart the macro.")

        # Save and load to TXT
        self.recorded_actions = []
        self.recording_file = os.path.join(USER_CONFIG_DIR, "recording.ahk")

        # Handle AHK errors
        self.playback_errors = []
        self.held_keys = set()

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
            text="PYWARE AUTOMATE V1.0",
            font=CTkFont(size=16, weight="bold")
        )
        logo_label.grid(row=0, column=0, sticky="w")

        # Status label (left side)
        self.status_label = CTkLabel(top_bar, text="Macro status: Idle")
        self.status_label.grid(row=1, column=0, pady=5, sticky="w")

        # Buttons frame (right side)
        button_frame = CTkFrame(top_bar, fg_color="transparent")
        button_frame.grid(row=0, column=1, sticky="e")

        CTkButton(
            button_frame,
            text="Website",
            corner_radius=32,
            command=self.open_link("https://sites.google.com/view/icf-automation-network/")
       ).pack(side="left", padx=6)

        CTkButton(
            button_frame,
            text="Discord",
            corner_radius=32,
            command=self.open_link("https://discord.gg/aMZY8yrF8r")
       ).pack(side="left", padx=6)

        CTkButton(
            button_frame,
            text="Upcoming Features",
            corner_radius=32,
            command=self.open_link("https://docs.google.com/document/d/1WwWWMR-eN-R-GO42IioToHpWTgiXkLoiNE_4NeE-GsU/edit?tab=t.0")
       ).pack(side="left", padx=6)

        # Tabs 
        self.tabs = CTkTabview(
            self,
            anchor="w",
        )

        self.tabs.grid(
            row=2, column=0,
            padx=20, pady=10,
            sticky="nsew"
        )

        self.tabs.add("Basic")
        # Other tabs go here

        # Build tabs
        self.build_general_tab(self.tabs.tab("Basic"))
        # Other tabs go here

        # Grid behavior
        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=0)  # Logo
        self.grid_rowconfigure(1, weight=0)  # Status
        self.grid_rowconfigure(2, weight=1)  # Tabs take remaining space

        last = self.load_last_config_name()
        self.bar_areas = {"fish": None, "recording": None}
        self.load_settings(last or "default.json")
        self._apply_hotkeys_from_vars()

        # Arrow variables
        self.initial_bar_size = None
        # Utility variables
        self.area_selector = None
        self.last_fish_x = None
    # BASIC SETTINGS TAB
    def build_general_tab(self, parent):
        scroll = CTkScrollableFrame(parent)
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        # VERY important
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        # Configs 
        configs = CTkFrame(scroll, border_width=2)
        configs.grid(row=1, column=0, padx=20, pady=20, sticky="nw")
        CTkLabel(configs, text="Config Settings", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        CTkLabel(configs, text="Active Configuration:").grid( row=1, column=0, padx=12, pady=6, sticky="w" )
        config_list = self.load_configs()
        config_var = StringVar(value=config_list[0] if config_list else "default.json")
        self.vars["active_config"] = config_var
        config_cb = CTkComboBox( configs, values=config_list, 
                                variable=config_var, command=lambda v: self.load_settings(v) )
        config_cb.grid(row=1, column=1, padx=12, pady=6, sticky="w")
        self.comboboxes["active_config"] = config_cb
        CTkButton(configs, text="Open Configs Folder", corner_radius=10, 
                  command=self.open_configs_folder
                  ).grid(row=2, column=0, padx=12, pady=12, sticky="w")
        CTkButton(configs, text="Save Misc Settings", 
                  corner_radius=10, command=self.save_misc_settings
        ).grid(row=2, column=1, padx=12, pady=12, sticky="w")
        # Grant Permissions (macOS only)
        if sys.platform == "darwin":
            CTkLabel(configs, text="Required Functions", font=CTkFont(size=14, weight="bold")).grid(row=0, column=2, padx=12, pady=8, sticky="w")
            CTkLabel(configs, text="Accessibility:").grid(row=1, column=2, padx=12, pady=6, sticky="w")
            CTkLabel(configs, text="Input Monitoring:").grid(row=2, column=2, padx=12, pady=6, sticky="w")
            CTkButton(configs, text="Enable", corner_radius=10, 
                    command=self.accessibility_perms # Accessibility
                    ).grid(row=1, column=3, padx=12, pady=12, sticky="w")
            CTkButton(configs, text="Enable", corner_radius=10, 
                    command=self.hotkey_perms # Input Monitoring
                    ).grid(row=2, column=3, padx=12, pady=12, sticky="w")
        # Hotkey Settings
        playback_and_hotkey = CTkFrame(scroll, border_width=2)
        playback_and_hotkey.grid(row=2, column=0, padx=20, pady=20, sticky="nw")
        CTkLabel(playback_and_hotkey, text="Hotkey Settings", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        # Start key
        CTkLabel(playback_and_hotkey, text="Start Playback Key").grid( row=1, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(playback_and_hotkey, text="Start Recording Key").grid( row=2, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(playback_and_hotkey, text="Stop Playback Key").grid( row=3, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(playback_and_hotkey, text="Stop Recording Key").grid( row=4, column=0, padx=12, pady=6, sticky="w" )
        # Start, screenshot and stop key changer
        start_playback_key_var = StringVar(value="F5")
        self.vars["start_playback_key"] = start_playback_key_var
        start_playback_key_entry = CTkEntry( playback_and_hotkey, width=120, textvariable=start_playback_key_var )
        start_playback_key_entry.grid(row=1, column=1, padx=12, pady=10, sticky="w")
        start_recording_key_var = StringVar(value="F6")
        self.vars["start_recording_key"] = start_recording_key_var
        start_recording_key_entry = CTkEntry( playback_and_hotkey, width=120, textvariable=start_recording_key_var )
        start_recording_key_entry.grid(row=2, column=1, padx=12, pady=10, sticky="w")
        stop_playback_key_var = StringVar(value="F7")
        self.vars["stop_playback_key"] = stop_playback_key_var
        stop_playback_key_entry = CTkEntry( playback_and_hotkey, width=120, textvariable=stop_playback_key_var )
        stop_playback_key_entry.grid(row=3, column=1, padx=12, pady=10, sticky="w")
        stop_recording_key_var = StringVar(value="F8")
        self.vars["stop_recording_key"] = stop_recording_key_var
        stop_recording_key_entry = CTkEntry( playback_and_hotkey, width=120, textvariable=stop_recording_key_var )
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
    # Save and load settings
    def load_configs(self):
        """Load list of available config files."""
        config_dir = USER_CONFIG_DIR
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        # Get config names from subdirectories
        config_names = [
            name for name in os.listdir(config_dir)
            if os.path.isdir(os.path.join(config_dir, name))
        ]

        if not config_names:
            # Create default config if none exists
            self.save_settings("default.json")
            config_names = ["default.json"]
        
        return sorted(config_names)
    
    def load_last_config_name(self):
        """Load the name of the last used config."""
        try:
            if os.path.exists("last_config.json"):
                with open("last_config.json", "r") as f:
                    data = json.load(f)
                    return data.get("last_config", "default.json")
        except:
            pass
        return "default.json"
    
    def save_last_config_name(self, name):
        """Save the name of the last used config."""
        try:
            with open("last_config.json", "w") as f:
                json.dump({"last_config": name}, f)
        except:
            pass
    
    def save_misc_settings(self):
        """Save miscellaneous settings to last_config.json."""
        try:
            data = {
                # IMPORTANT: Save hotkeys
                "start_playback_key": self.vars["start_playback_key"].get(),
                "start_recording_key": self.vars["start_recording_key"].get(),
                "stop_recording_key": self.vars["stop_recording_key"].get(),
                "stop_playback_key": self.vars["stop_playback_key"].get()
            }
            with open("last_config.json", "w") as f:
                json.dump(data, f, indent=4)
            # IMPORTANT: Immediately update active hotkeys
            self.hotkey_start = self._string_to_key(self.vars["start_playback_key"].get())
            self.hotkey_start_recording = self._string_to_key(self.vars["start_recording_key"].get())
            self.hotkey_stop_recording = self._string_to_key(self.vars["stop_recording_key"].get())
            self.hotkey_stop = self._string_to_key(self.vars["stop_playback_key"].get())
        except Exception as e:
            import traceback
            traceback.print_exc()

    def save_settings(self, name):
        """Save all settings to a JSON config file."""
        config_dir = USER_CONFIG_DIR
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        data = {}
        
        # Save all StringVar and related variables
        try:
            for key, var in self.vars.items():
                if hasattr(var, 'get'):
                    data[key] = var.get()
                else:
                    data[key] = var
        except Exception as e:
            print(f"Error saving vars: {e}")
        
        # Save checkbox states
        try:
            for key, checkbox in self.checkboxes.items():
                data[f"checkbox_{key}"] = checkbox.get()
        except Exception as e:
            print(f"Error saving checkboxes: {e}")
        
        # Save combobox states
        try:
            for key, combobox in self.comboboxes.items():
                data[f"combobox_{key}"] = combobox.get()
        except Exception as e:
            print(f"Error saving comboboxes: {e}")

        # Get rod folder based on config name
        rod_folder = os.path.join(config_dir, name.replace(".json", ""))
        self.recording_file = os.path.join(rod_folder, "recording.txt")
        os.makedirs(rod_folder, exist_ok=True)

        path = os.path.join(rod_folder, "config.json")
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            self.save_last_config_name(name)
            self.save_misc_settings()  # Also save misc settings
            self._apply_hotkeys_from_vars()  # Apply new hotkeys immediately
        except Exception as e:
            self.set_status(f"Error saving config: {e}")
    
    def load_settings(self, name):
        """Load settings from a JSON config file."""
        config_dir = USER_CONFIG_DIR
        rod_folder = os.path.join(config_dir, name.replace(".json", ""))
        path = os.path.join(rod_folder, "config.json")

        if not os.path.exists(path):
            self.set_status(f"Config not found: {name}")
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except Exception as e:
            self.set_status(f"Error loading config: {e}")
            return
        
        # Load StringVar and related variables
        try:
            for key, var in self.vars.items():
                if hasattr(var, 'set') and key in data:
                    var.set(data[key])
        except Exception as e:
            print(f"Error loading vars: {e}")
        
        # Load checkbox states
        try:
            for key, checkbox in self.checkboxes.items():
                checkbox_key = f"checkbox_{key}"
                if checkbox_key in data:
                    checkbox.set(data[checkbox_key])
        except Exception as e:
            print(f"Error loading checkboxes: {e}")
        
        # Load combobox states
        try:
            for key, cb in self.comboboxes.items():
                if key in data:
                    cb.set(data[key])
        except Exception as e:
            print(f"Error loading comboboxes: {e}")

        # Load text file
        self.load_recording_file()

        self.save_last_config_name(name)
    def load_misc_settings(self):
        """Load miscellaneous settings from last_config.json."""
        try:
            if os.path.exists("last_config.json"):
                with open("last_config.json", "r") as f:
                    data = json.load(f)
                    # IMPORTANT: Load hotkeys if present
                    start_playback_key = data.get("start_playback_key", "F5")
                    start_playback_key = data.get("start_recording_key", "F6")
                    stop_recording_key = data.get("stop_recording_key", "F8")
                    stop_playback_key = data.get("stop_playback_key", "F7")

                    self.vars["start_playback_key"].set(start_playback_key)
                    self.vars["start_recording_key"].set(start_playback_key)
                    self.vars["stop_recording_key"].set(stop_recording_key)
                    self.vars["stop_playback_key"].set(stop_playback_key)

                    # Convert to pynput keys
                    self.hotkey_start = self._string_to_key(start_playback_key)
                    self.hotkey_start_recording = self._string_to_key(start_playback_key)
                    self.hotkey_stop_recording = self._string_to_key(stop_recording_key)
                    self.hotkey_stop = self._string_to_key(stop_playback_key)
        except:
            pass # don't do anything here
    def save_recording_to_txt(self):
        """Save recorded actions into a real .ahk file."""

        ahk_path = self.recording_file.replace(".txt", ".ahk")

        try:
            with open(ahk_path, "w", encoding="utf-8") as f:

                # HEADER
                f.write("; AutoHotKey Script Generated by I Can't Automate\n")
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

            self.set_status(f"Saved AHK to: {ahk_path}")

        except Exception as e:
            self.set_status(f"Error saving AHK: {e}")
    def load_recording_file(self):
        """
        Load the recording file from the active config subfolder.
        Structure:
            configs/ConfigName/recording.ahk
        """

        config_name = self.vars["active_config"].get()
        config_dir = USER_CONFIG_DIR
        rod_folder = os.path.join(config_dir, config_name.replace(".json", ""))

        # Always ensure the config subfolder exists
        os.makedirs(rod_folder, exist_ok=True)

        # Define expected paths
        ahk_path = os.path.join(rod_folder, "recording.ahk")

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
    # Macro functions
    def open_configs_folder(self):
        folder = USER_CONFIG_DIR
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", folder])
        else:  # Linux
            subprocess.run(["xdg-open", folder])
    def open_link(self, url):
        """Open a URL in the default web browser."""
        return lambda: webbrowser.open(url)
    def accessibility_perms(self):
        """Askes macOS to grant the permission to do a single click"""
    def hotkey_perms(self):
        self.on_key_press(",")
        mouse_controller.position = (300, 300)
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
        self.pending_events.append(event)

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
        self.pending_events.append(event)

    def on_key_release_record(self, key):
        key_name = self._normalize_key_for_ahk(key)
        if key_name == "sc63": # Disable this specific unknown key
            event = f"; Disabled"
        else:
            event = f"Send, {{{key_name} up}}"
        self.pending_events.append(event)
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
    def execute_script(self, actions, speed=1.0):
        i = 0

        while i < len(actions) and self.macro_running:
            line = actions[i].strip()

            # ---- LOOP ----
            if line.startswith("Loop"):
                try:
                    # Extract loop count safely
                    count_part = line.split(",")[1].strip()
                    count = int(count_part.split()[0])  # handles "2 {" case
                except:
                    count = 1

                block = []

                # --- Detect inline { ---
                if "{" in line:
                    brace_depth = 1
                    i += 1
                else:
                    i += 1
                    if i < len(actions) and actions[i].strip() == "{":
                        brace_depth = 1
                        i += 1
                    else:
                        brace_depth = 0

                # --- Collect block ---
                while i < len(actions) and brace_depth > 0:
                    current = actions[i].strip()

                    if "{" in current:
                        brace_depth += current.count("{")
                    if "}" in current:
                        brace_depth -= current.count("}")
                        if brace_depth <= 0:
                            break

                    block.append(actions[i])
                    i += 1

                # --- Execute loop ---
                for _ in range(count):
                    self.execute_script(block, speed)

            else:
                self.playback_action(line, speed)

            i += 1
    # Playback functions
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
    def playback_action(self, action, speed=1.0):
        action = action.strip()
        # Others: MouseMove, Click, Send
        if action.startswith("SetBatchLines") or action.startswith("SetKeyDelay") or action.startswith("SetMouseDelay") or action.startswith("SetDefaultMouseSpeed") or action.startswith("SendMode"):
            return  # I Can't Automate can skip these lines
        if action.startswith(";") or action.startswith("F5::") or action.startswith("F7::") or action.startswith("ExitApp") or action.lower() == "return":
            return  # Comments and hotkeys are controlled by I Can't Automate
        if action.startswith("{") or action.startswith("}"):
            return  # Loops are controlled by I Can't Automate
        # Sleep / Delay (AHK format: Sleep, 150)
        if action.startswith("Sleep"):
            try:
                ms = int(action.split(",")[1].strip())
                time.sleep((ms / 1000) / speed)  # divide by speed: 2.0 = 2× faster
            except Exception as e:
                self.add_error(action, str(e))
            return

        # Split line but preserve original formatting style
        parts = [p.strip() for p in action.split(",")]

        # MouseMove (MouseMove, x, y)
        if parts[0] == "MouseMove":
            try:
                x = int(parts[1])
                y = int(parts[2])
                mouse_controller.position = (x, y)
            except Exception as e:
                self.add_error(action, str(e))
            return

        # Click (Click, x, y, Down L / Up R)
        if parts[0] == "Click":
            try:
                x = int(parts[1])
                y = int(parts[2])

                # "Down L" or "Up R"
                event = parts[3].split(" ")
                down_up = event[0]     # Down / Up
                btn = event[1].lower() # L / R / M

                btn = event[1].lower()  # left / right / middle / l / r / m

                # normalize
                if btn in ("left", "l"):
                    button = mouse.Button.left
                elif btn in ("right", "r"):
                    button = mouse.Button.right
                elif btn in ("middle", "m"):
                    button = mouse.Button.middle
                else:
                    print("Unknown mouse button:", btn)
                    return

                # Move mouse first (AHK behavior)
                mouse_controller.position = (x, y)

                # Press / release
                if down_up.lower() == "down":
                    mouse_controller.press(button)
                else:
                    mouse_controller.release(button)

            except Exception as e:
                self.add_error(action, str(e))
            return
        # Send
        if parts[0] == "Send":
            try:
                raw = parts[1].strip()

                # --- CASE: {key}, {key down}, {key up} ---
                if raw.startswith("{") and raw.endswith("}"):
                    inner = raw[1:-1].strip()   # remove {}

                    tokens = inner.split()
                    key_name = tokens[0].lower()

                    key = self._string_to_key(key_name)

                    # --- {key} ---
                    if len(tokens) == 1:
                        keyboard_controller.press(key)
                        keyboard_controller.release(key)

                    # --- {key down} ---
                    elif tokens[1].lower() == "down":
                        keyboard_controller.press(key)
                        self.held_keys.add(key)
                    # --- {key up} ---
                    elif tokens[1].lower() == "up":
                        keyboard_controller.release(key)
                        self.held_keys.discard(key)
                    return

                # --- EXISTING MODIFIER HANDLING ---
                if raw.startswith("^") or raw.startswith("!") or raw.startswith("+"):
                    mod = raw[0]
                    key_raw = raw[1:]

                    key_raw = self._clean_ahk_braces(key_raw)
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

                # --- FALLBACK ---
                key_raw = self._clean_ahk_braces(raw)
                key = self._string_to_key(key_raw)
                keyboard_controller.press(key)
                keyboard_controller.release(key)

            except Exception as e:
                self.add_error(action, str(e))
            return
        self.add_error(action, "Unknown or unsupported command")
    # Key press functions
    def _apply_hotkeys_from_vars(self):
            """Apply hotkey StringVars to the live hotkey attributes used by on_key_press."""
            self.hotkey_start = self._string_to_key(self.vars["start_playback_key"].get())
            self.hotkey_start_recording = self._string_to_key(self.vars["start_recording_key"].get())
            self.hotkey_stop_recording = self._string_to_key(self.vars["stop_recording_key"].get())
            self.hotkey_stop = self._string_to_key(self.vars["stop_playback_key"].get())
    def normalize_key(self, key):
        try:
            return key.char.lower()  # letter keys
        except:
            return str(key).replace("Key.", "").lower()
    def on_key_press(self, key):
            # During playback, only allow the stop hotkey through.
            # All other hotkeys (including start) are suppressed so that
            # replayed keystrokes don't accidentally re-trigger them.
            if self.is_playing_back:
                if key == self.hotkey_stop:
                    self.stop_playback()
                return

            if key == self.hotkey_start_recording and not self.macro_running:
                config_name = self.vars["active_config"].get()
                self.save_settings(config_name)

                self.macro_running = True
                self.after(0, self.withdraw)
                threading.Thread(target=self.start_recording, daemon=True).start()

            elif key == self.hotkey_stop_recording:
                self.stop_recording()

            elif key == self.hotkey_start and not self.macro_running:
                config_name = self.vars["active_config"].get()
                self.save_settings(config_name)

                self.macro_running = True
                self.after(0, self.withdraw)
                threading.Thread(target=self.start_playback, daemon=True).start()

            elif key == self.hotkey_stop:
                self.stop_playback()
    def set_status(self, text, key=None):
        self.status_label.configure(text=text)
    def start_recording(self):
        print("Macro Status: Recording...")
        self.macro_running = True
        self.recorded_actions = []

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
                f.write("; AutoHotKey Script Generated by I Can't Automate\n")
                f.write("F5:: ; Start macro\n")
                f.write("    SetBatchLines, -1\n")
                f.write("    SetKeyDelay, -1, -1\n")
                f.write("    SetMouseDelay, -1\n")
                f.write("    SetDefaultMouseSpeed, 0\n")
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