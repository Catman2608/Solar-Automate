# Initialization
from customtkinter import *
import os
import subprocess
# Keyboard and Mouse
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
# Key Listeners
import threading
from pynput.keyboard import Listener as KeyListener, Key
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
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

# Set appearance
set_default_color_theme("blue")
set_appearance_mode("dark")
def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))
if sys.platform == "darwin":
    user_config_dir = os.path.join(os.path.expanduser("~"), 
                                   "Library", "Application Support", 
                                   "IcantAutomate", "configs")
else:
    user_config_dir = os.path.join(os.path.expanduser("~"),
                                   "AppData","Roaming",
                                   "IcantAutomate","configs")

os.makedirs(user_config_dir, exist_ok=True)
BASE_PATH = get_base_path()

if sys.platform == "darwin" and getattr(sys, "frozen", False):
    # Only use Application Support when bundled
    USER_CONFIG_DIR = os.path.join(os.path.expanduser("~"), "Library", 
                                   "Application Support", "IcantAutomate", 
                                   "configs")
elif sys.platform == "win32" and getattr(sys, "frozen", False):
    # Only use AppData/Roaming when bundled
    USER_CONFIG_DIR = os.path.join(os.path.expanduser("~"), "AppData",
                                   "Roaming", "IcantAutomate",
                                   "configs")
else:
    # During development, use local project folder
    USER_CONFIG_DIR = os.path.join(BASE_PATH, "configs")

os.makedirs(USER_CONFIG_DIR, exist_ok=True)
if sys.platform == "darwin":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
else:
    pass # You're on Windows, no need to change the working directory
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
        self.title("I Can't Automate V1.0")

        # Macro state
        self.macro_running = False
        self.macro_thread = None

        # Hotkey variables
        self.hotkey_start = Key.f5
        self.hotkey_stop = Key.f7
        self.hotkey_start_recording = Key.f6            # added for the bar area selector
        self.hotkey_stop_recording = Key.f8
        self.hotkey_labels = {}  # Store label widgets for dynamic updates

        # Start hotkey listener
        self.key_listener = KeyListener(on_press=self.on_key_press)
        self.key_listener.daemon = True
        self.key_listener.start()

        # Save and load to ahk
        self.recorded_actions = []
        self.recording_file = os.path.join(USER_CONFIG_DIR, "recording.ahk")

        # Create ONE listener
        self.recording_enabled = False

        self.mouse_listener = mouse.Listener(
            on_click=self._mouse_click,
            on_move=self._mouse_move
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._key_press,
            on_release=self._key_release
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()

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
            text="I CAN'T AUTOMATE V1.0",
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
            text="Upcoming Features",
            corner_radius=32,
            command=self.open_link("https://docs.google.com/document/d/1WwWWMR-eN-R-GO42IioToHpWTgiXkLoiNE_4NeE-GsU/edit?tab=t.0")
       ).pack(side="left", padx=6)

        CTkButton(
            button_frame,
            text="Tutorial",
            corner_radius=32,
            command=self.open_link("https://docs.google.com/document/d/1qjhgcONxpZZbSAEYiSCXoUXGjQwd7Jghf4EysWC4Cps/edit?usp=drive_link")
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
        self.tabs.add("Recording")
        self.tabs.add("Playback")

        # Build tabs
        self.build_general_tab(self.tabs.tab("Basic"))
        self.build_recording_tab(self.tabs.tab("Recording"))
        self.build_playback_tab(self.tabs.tab("Playback"))

        # Grid behavior
        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=0)  # Logo
        self.grid_rowconfigure(1, weight=0)  # Status
        self.grid_rowconfigure(2, weight=1)  # Tabs take remaining space

        last = self.load_last_config_name()
        self.bar_areas = {"fish": None, "recording": None}
        self.load_settings(last or "default.json")
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
        # Hotkey Settings
        hotkey_settings = CTkFrame(scroll, border_width=2)
        hotkey_settings.grid(row=2, column=0, padx=20, pady=20, sticky="nw")
        CTkLabel(hotkey_settings, text="Hotkey Settings", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")
        # Start key
        CTkLabel(hotkey_settings, text="Start Playback Key").grid( row=1, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(hotkey_settings, text="Start Recording Key").grid( row=2, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(hotkey_settings, text="Stop Playback Key").grid( row=3, column=0, padx=12, pady=6, sticky="w" )
        CTkLabel(hotkey_settings, text="Stop Recording Key").grid( row=4, column=0, padx=12, pady=6, sticky="w" )
        # Start, screenshot and stop key changer
        start_key_var = StringVar(value="F5")
        self.vars["start_key"] = start_key_var
        start_key_entry = CTkEntry( hotkey_settings, width=120, textvariable=start_key_var )
        start_key_entry.grid(row=1, column=1, padx=12, pady=10, sticky="w")
        start_recording_key_var = StringVar(value="F6")
        self.vars["start_recording_key"] = start_recording_key_var
        start_recording_key_entry = CTkEntry( hotkey_settings, width=120, textvariable=start_recording_key_var )
        start_recording_key_entry.grid(row=2, column=1, padx=12, pady=10, sticky="w")
        stop_key_var = StringVar(value="F7")
        self.vars["stop_key"] = stop_key_var
        stop_key_entry = CTkEntry( hotkey_settings, width=120, textvariable=stop_key_var )
        stop_key_entry.grid(row=3, column=1, padx=12, pady=10, sticky="w")
        stop_recording_key_var = StringVar(value="F8")
        self.vars["stop_recording_key"] = stop_recording_key_var
        stop_recording_key_entry = CTkEntry( hotkey_settings, width=120, textvariable=stop_recording_key_var )
        stop_recording_key_entry.grid(row=4, column=1, padx=12, pady=10, sticky="w")
    # Recording TAB
    def build_recording_tab(self, parent):
        scroll = CTkScrollableFrame(parent)
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        recording_options = CTkFrame(scroll, border_width=2)
        recording_options.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        CTkLabel(recording_options, text="Recording Configuration", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")

        CTkLabel(recording_options, text="Scan Delay").grid(row=1, column=0, padx=12, pady=8, sticky="w") # This is the label syntax
        record_delay_var = StringVar(value="0.0") # This line is the default/placeholder value
        self.vars["record_delay"] = record_delay_var # This line makes the entry save and load
        record_delay_entry = CTkEntry(recording_options, width=120, textvariable=record_delay_var) # This line initializes the entry
        record_delay_entry.grid(row=1, column=1, padx=12, pady=8, sticky="w") # This line initializes the position for the entry (most important)
    # Playback TAB
    def build_playback_tab(self, parent):
        scroll = CTkScrollableFrame(parent)
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        playback_options = CTkFrame(scroll, border_width=2)
        playback_options.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        CTkLabel(playback_options, text="Playback Options", font=CTkFont(size=14, weight="bold")).grid(row=0, column=0, padx=12, pady=8, sticky="w")

        CTkLabel(playback_options, text="Playback Loops").grid(row=1, column=0, padx=12, pady=8, sticky="w") # This is the label syntax
        playback_loops_var = StringVar(value="1") # This line is the default/placeholder value
        self.vars["playback_loops"] = playback_loops_var # This line makes the entry save and load
        playback_loops_entry = CTkEntry(playback_options, width=120, textvariable=playback_loops_var) # This line initializes the entry
        playback_loops_entry.grid(row=1, column=1, padx=12, pady=8, sticky="w") # This line initializes the position for the entry (most important)

        CTkLabel(playback_options, text="Playback Interval (minutes)").grid(row=2, column=0, padx=12, pady=8, sticky="w") # This is the label syntax
        playback_interval_var = StringVar(value="0") # This line is the default/placeholder value
        self.vars["playback_interval"] = playback_interval_var # This line makes the entry save and load
        playback_interval_entry = CTkEntry(playback_options, width=120, textvariable=playback_interval_var) # This line initializes the entry
        playback_interval_entry.grid(row=2, column=1, padx=12, pady=8, sticky="w") # This line initializes the position for the entry (most important)

        CTkLabel(playback_options, text="Playback speed (minutes)").grid(row=3, column=0, padx=12, pady=8, sticky="w") # This is the label syntax
        playback_speed_var = StringVar(value="1") # This line is the default/placeholder value
        self.vars["playback_speed"] = playback_speed_var # This line makes the entry save and load
        playback_speed_entry = CTkEntry(playback_options, width=120, textvariable=playback_speed_var) # This line initializes the entry
        playback_speed_entry.grid(row=3, column=1, padx=12, pady=8, sticky="w") # This line initializes the position for the entry (most important)

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
                "start_key": self.vars["start_key"].get(),
                "start_recording_key": self.vars["start_recording_key"].get(),
                "stop_recording_key": self.vars["stop_recording_key"].get(),
                "stop_key": self.vars["stop_key"].get()
            }
            with open("last_config.json", "w") as f:
                json.dump(data, f, indent=4)
            # IMPORTANT: Immediately update active hotkeys
            self.hotkey_start = self._string_to_key(self.vars["start_key"].get())
            self.hotkey_start_recording = self._string_to_key(self.vars["start_recording_key"].get())
            self.hotkey_stop_recording = self._string_to_key(self.vars["stop_recording_key"].get())
            self.hotkey_stop = self._string_to_key(self.vars["stop_key"].get())
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
        self.recording_file = os.path.join(rod_folder, "recording.ahk")
        os.makedirs(rod_folder, exist_ok=True)

        path = os.path.join(rod_folder, "config.json")
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            self.save_last_config_name(name)
            self.save_misc_settings()  # Also save misc settings
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
                    start_key = data.get("start_key", "F5")
                    change_key = data.get("start_recording_key", "F6")
                    stop_recording_key = data.get("stop_recording_key", "F8")
                    stop_key = data.get("stop_key", "F7")

                    self.vars["start_key"].set(start_key)
                    self.vars["start_recording_key"].set(change_key)
                    self.vars["stop_recording_key"].set(stop_recording_key)
                    self.vars["stop_key"].set(stop_key)

                    # Convert to pynput keys
                    self.hotkey_start = self._string_to_key(start_key)
                    self.hotkey_start_recording = self._string_to_key(change_key)
                    self.hotkey_stop_recording = self._string_to_key(stop_recording_key)
                    self.hotkey_stop = self._string_to_key(stop_key)
        except:
            pass # don't do anything here
    def save_recording_to_ahk(self):
        """Save recorded actions to an AHK file."""
        try:
            with open(self.recording_file, "w", encoding="utf-8") as f:
                f.write("; Auto-generated macro\n")
                f.write("; AHK script\n\n")
                for action in self.recorded_actions:
                    f.write(action + "\n")
            self.set_status(f"Recording saved to {self.recording_file}")
        except Exception as e:
            self.set_status(f"Error saving recording: {e}")
    def load_recording_file(self):
        """Load or create recording.ahk inside current config folder."""
        config_name = self.vars["active_config"].get()
        config_dir = USER_CONFIG_DIR
        rod_folder = os.path.join(config_dir, config_name.replace(".json", ""))
        os.makedirs(rod_folder, exist_ok=True)

        self.recording_file = os.path.join(rod_folder, "recording.ahk")

        # Auto-create if missing
        if not os.path.exists(self.recording_file):
            with open(self.recording_file, "w") as f:
                f.write("")
            self.recorded_actions = []
            print(f"Created empty recording.ahk for {config_name}")
            return

        # Load existing file
        try:
            with open(self.recording_file, "r") as f:
                self.recorded_actions = [line.strip() for line in f.readlines()]
            print("Loaded", len(self.recorded_actions), "actions")
        except:
            self.recorded_actions = []
    def load_recording_from_ahk(self):
        """Load or create recording.ahk inside the current config."""
        config_name = self.vars["active_config"].get()
        config_dir = USER_CONFIG_DIR
        rod_folder = os.path.join(config_dir, config_name.replace(".json", ""))

        os.makedirs(rod_folder, exist_ok=True)

        self.recording_file = os.path.join(rod_folder, "recording.ahk")

        if not os.path.exists(self.recording_file):
            with open(self.recording_file, "w", encoding="utf-8") as f:
                f.write("; Empty AHK macro\n")
            self.recorded_actions = []
            print(f"Created empty recording.ahk for {config_name}")
            return

        try:
            with open(self.recording_file, "r", encoding="utf-8") as f:
                self.recorded_actions = [
                    line.strip()
                    for line in f.readlines()
                    if not line.strip().startswith(";") and line.strip()
                ]
            print("Loaded", len(self.recorded_actions), "actions")
        except:
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
    def _string_to_key(self, key_string):
        key_string = key_string.strip().lower()

        try:
            return Key[key_string]
        except KeyError:
            return key_string  # normal character keys
    def _mouse_move(self, x, y):
        if self.recording_enabled:
            self.latest_mouse_move = (x, y)

    def _mouse_click(self, x, y, button, pressed):
        if not self.recording_enabled:
            return

        button2 = str(button).replace("Button.", "")
        event = f"Click, {x}, {y}, {'Down' if pressed else 'Up'} {button2}"
        self.pending_events.append(event)

    def _key_press(self, key):
        if not self.recording_enabled:
            return

        try:
            if hasattr(key, "char") and key.char and ord(key.char) >= 32:
                key_name = key.char
            else:
                key_name = str(key)
        except:
            key_name = str(key)

        key_name = key_name.replace("Key.", "")
        self.pending_events.append(f"Send, {key_name} down")

    def _key_release(self, key):
        if not self.recording_enabled:
            return

        try:
            if hasattr(key, "char") and key.char and ord(key.char) >= 32:
                key_name = key.char
            else:
                key_name = str(key)
        except:
            key_name = str(key)

        key_name = key_name.replace("Key.", "")
        self.pending_events.append(f"Send, {key_name} up")
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
    # Playback functions
    def _clean_ahk_braces(self, key_raw):
        # Remove braces like {Enter}, {Down}, {Space}
        key_raw = key_raw.strip()

        if key_raw.startswith("{") and key_raw.endswith("}"):
            key_raw = key_raw[1:-1]  # strip {}

        return key_raw.lower()
    def playback_action(self, action):
        action = action.strip()

        # -------------------------------------------------------
        # Sleep / Delay  (AHK format: Sleep, 150)
        # -------------------------------------------------------
        if action.startswith("Sleep"):
            try:
                ms = int(action.split(",")[1].strip())
                time.sleep(ms / 1000)
            except:
                print("Bad Sleep format:", action)
            return

        # Split line but preserve original formatting style
        parts = [p.strip() for p in action.split(",")]

        # -------------------------------------------------------
        # MouseMove (MouseMove, x, y)
        # -------------------------------------------------------
        if parts[0] == "MouseMove":
            try:
                x = int(parts[1])
                y = int(parts[2])
                mouse_controller.position = (x, y)
            except:
                print("Bad MouseMove:", action)
            return

        # -------------------------------------------------------
        # Click (Click, x, y, Down L / Up R)
        # -------------------------------------------------------
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
                print("Bad Click format:", action, e)
            return

        # -------------------------------------------------------
        # Send (Send, a down / Send, enter up)
        # -------------------------------------------------------
        if parts[0] == "Send":
            try:
                raw = parts[1].strip()

                # --- Case 1: {Down}, {Enter}, {Left} ----
                if raw.startswith("{") and raw.endswith("}"):
                    key_raw = self._clean_ahk_braces(raw)
                    key = self._string_to_key(key_raw)

                    keyboard_controller.press(key)
                    keyboard_controller.release(key)
                    return

                # --- Case 2: ^x, ^v, !a, +b (Ctrl, Alt, Shift modifiers) ---
                if raw.startswith("^") or raw.startswith("!") or raw.startswith("+"):
                    mod = raw[0]
                    key_raw = raw[1:]

                    key_raw = self._clean_ahk_braces(key_raw)
                    key = self._string_to_key(key_raw)

                    # ctrl / alt / shift
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

                # --- Case 3: two-part "Send, a down" or "Send, enter up" ---
                if " " in raw:
                    key_raw, direction = raw.split(" ")
                    key_raw = self._clean_ahk_braces(key_raw)
                    direction = direction.lower()

                    key = self._string_to_key(key_raw)

                    if direction == "down":
                        keyboard_controller.press(key)
                    else:
                        keyboard_controller.release(key)
                    return

                # --- Case 4: simple single key "Send, a" ---
                key_raw = self._clean_ahk_braces(raw)
                key = self._string_to_key(key_raw)
                keyboard_controller.press(key)
                keyboard_controller.release(key)

            except Exception as e:
                print("Bad Send format:", action, e)
            return
        # -------------------------------------------------------
        print("Unknown action →", action)
    # Record and playback
    def on_key_press(self, key):
        try:
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

        except Exception as e:
            self.set_status(f"Hotkey error: {e}")
    def set_status(self, text, key=None):
        self.status_label.configure(text=text)
    def start_recording(self):
        print("Macro Status: Recording...")

        self.recording_enabled = True
        self.recorded_actions = []
        self.pending_events = []
        self.latest_mouse_move = None

        # FIX: must initialize BOTH timestamps
        now = time.time()
        self.last_record_time = now
        self.last_action_time = now

        # Start listeners
        self.mouse_listener = mouse.Listener(
            on_click=self._mouse_click,
            on_move=self._mouse_move
        )
        self.keyboard_listener = keyboard.Listener(
            on_press=self._key_press,
            on_release=self._key_release
        )

        self.mouse_listener.start()
        self.keyboard_listener.start()
    def stop_recording(self):
        print("Macro Status: Stopped Recording")
        self.recording_enabled = False

        try:
            with open(self.recording_file, "w") as f:
                for action in self.recorded_actions:
                    f.write(action + "\n")
            print("Saved", len(self.recorded_actions), "actions")
        except Exception as e:
            print("Error saving:", e)
    def start_playback(self):
        print("Macro Status: Started Playback")
        self.macro_running = True
        time.sleep(1) # to prevent macro never runs

        # Load actions from file
        self.load_recording_from_ahk()

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

        # If loops is 0 → infinite loop
        infinite_loop = (loops == 0)

        loop_count = 0

        # ---- PLAYBACK LOOP ----
        while self.macro_running and (infinite_loop or loop_count < loops):

            loop_count += 1
            print(f"Starting loop {loop_count}")

            # Play all actions
            for action in self.recorded_actions:
                if not self.macro_running:
                    break

                try:
                    self.playback_action(action)
                except Exception as e:
                    print("Error executing:", action, e)

            if not self.macro_running:
                break

            # If there is an interval → wait before next loop
            if interval_seconds > 0 and (infinite_loop or loop_count < loops):
                print(f"Waiting {interval_seconds} seconds before next loop...")
                time.sleep(interval_seconds)

        # finished looping
        print("Macro Status: Stopped Playback (Done)")
        self.macro_running = False
        self.after(0, self.deiconify)
    def stop_playback(self):
        if not self.macro_running:
            return
        self.macro_running = False
        self.after(0, self.deiconify)  # show window safely
        print("Macro Status: Stopped Playback")
if __name__ == "__main__":
    app = App()
    app.mainloop()