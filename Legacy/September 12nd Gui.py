# Imports
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
# Misc
import webbrowser
import sys
import os
import glob
import re
import traceback
import math
import threading
import time
import subprocess
import mss
from pathlib import Path
# Keyboard and Mouse clicks (platform-specific)
import pyautogui
pyautogui.PAUSE = 0.0
pyautogui.MINIMUM_DURATION = 0.0
pyautogui.MINIMUM_SLEEP = 0.0
pyautogui.FAILSAFE = False
from pynput.keyboard import Listener as KeyListener, Key
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
# File management
import numpy as np
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
elif sys.platform == "darwin":
    import Quartz
    import AppKit
    from AppKit import NSScreen
elif sys.platform == "linux":
    from Xlib import X, XK, display as Xdisplay
    from Xlib.ext import xtest
    from ctypes.util import find_library
# Define platform-specific constants
# All platforms
keyboard_controller = KeyboardController()
mouse_controller = MouseController()
APP_VERSION = 3.0
BETA_VERSION = 0
try:
    playback_path = sys.argv[1]
    open_mode = "Playback"
except:
    open_mode = "Editor"
    folder_path = os.getcwd()
playback_path = "Solar Fishing Lite.ahk"
open_mode = "Playback"
# Other functions and classes
def open_link(url):
    webbrowser.open(url)
# Config Management
def get_base_path():
    # 1. check if the application is bundled/frozen
    if getattr(sys, 'frozen', False):
        # Detect if it's a macos application bundle (.app)
        # In macos bundles, the executable runs inside contents/macos/
        if sys.platform == 'darwin' and '.app/Contents/MacOS' in sys.executable:
            return Path(sys.executable).parent.resolve(), True

        # Detect if it's a linux packaged environment (like appimage)
        # Linux appimages extract to a mount point, keeping assets inside the binary environment
        elif sys.platform.startswith('linux') and 'AppRun' in sys.executable:
            return Path(sys.executable).parent.resolve(), True

        # 2. windows exe (onefile) or standard local folder deployment
        # Returns the directory containing the actual .exe file, not the temporary _meipass folder
        else:
            return Path(sys.executable).parent.resolve(), True

    # 3. running from raw source code (.py file)
    else:
        return Path(__file__).parent.resolve(), False
BASE_PATH, IS_COMPILED = get_base_path()
IMAGES_PATH = os.path.join(BASE_PATH, "images")
RESOURCES_PATH = os.path.join(BASE_PATH, "resources")
# Windows (Transparency and Ctypes WinDLL)
if sys.platform == "win32":
    windll = ctypes.windll.user32
    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_MIDDLEDOWN = 0x0020
    MOUSEEVENTF_MIDDLEUP = 0x0040
    VK_LBUTTON = 0x01
    # Ctypes GUI constants
    SW_MAXIMIZE = 3
    user32 = ctypes.windll.user32
    user32.GetWindowLongW.restype = wintypes.LONG
    user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.SetWindowLongW.restype = wintypes.LONG
    user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]
    user32.SetLayeredWindowAttributes.restype = wintypes.BOOL
    user32.SetLayeredWindowAttributes.argtypes = [wintypes.HWND, wintypes.COLORREF, ctypes.c_byte, wintypes.DWORD]
    user32.ShowWindow.restype = wintypes.BOOL
    user32.ShowWindow.argtypes = [
        wintypes.HWND,
        ctypes.c_int
    ]
    # Set DPI awareness early to ensure consistent coordinate handling
    try:
        windll.shcore.SetProcessDpiAwareness(1)  # PROCESS_PER_MONITOR_DPI_AWARE
        # DPI awareness successfully set
    except:
        try:
            windll.user32.SetProcessDPIAware()  # Fallback for older Windows
            # DPI awareness set (fallback method)
        except:
            pass  # DPI awareness could not be set - coordinates may be inconsistent

    # Windows API related functions
    def get_scale_factor():
        return 1

    def send_key(key, delay=0.05, click_type=0):
        """
        Send a keyboard event using the Windows SendInput API.
        click_type:
            0 = click (press + release)   [default]
            1 = hold (press only)
            2 = release (release only)
        """
        import ctypes
        import time
        user32 = ctypes.windll.user32
        INPUT_KEYBOARD = 1
        KEYEVENTF_KEYUP = 0x0002
        KEY_MAP = { "backspace": 0x08, "tab": 0x09, "enter": 0x0D, "return": 0x0D, "shift": 0x10, "ctrl": 0x11, "control": 0x11, "alt": 0x12, "pause": 0x13, 
                   "capslock": 0x14, "escape": 0x1B, "esc": 0x1B, "space": 0x20, "pageup": 0x21, "pgup": 0x21, "pagedown": 0x22, "pgdn": 0x22, "end": 0x23, 
                   "home": 0x24, "left": 0x25, "up": 0x26, "right": 0x27, "down": 0x28, "insert": 0x2D, "delete": 0x2E, "win": 0x5B, "lwin": 0x5B, "rwin": 0x5C, 
                   "apps": 0x5D, "numlock": 0x90, "scrolllock": 0x91, "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74, "f6": 0x75, "f7": 0x76, 
                   "f8": 0x77, "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B, "f13": 0x7C, "f14": 0x7D, "f15": 0x7E, "f16": 0x7F, "f17": 0x80, "f18": 0x81, 
                   "f19": 0x82, "f20": 0x83, "f21": 0x84, "f22": 0x85, "f23": 0x86, "f24": 0x87,}
        key_string = str(key).lower()
        # Resolve the virtual-key code.
        if key_string in KEY_MAP:
            vk = KEY_MAP[key_string]
        elif len(key_string) == 1:
            vk = user32.VkKeyScanW(ord(key_string))
            if vk == -1:
                return

            vk &= 0xFF
        else:
            return

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
            ]
        class INPUT(ctypes.Structure):
            _fields_ = [
                ("type", ctypes.c_ulong),
                ("ki", KEYBDINPUT),
            ]
        extra = ctypes.c_ulong(0)
        def key_event(is_key_up):
            flags = KEYEVENTF_KEYUP if is_key_up else 0
            inp = INPUT(
                type=INPUT_KEYBOARD,
                ki=KEYBDINPUT(
                    wVk=vk,
                    wScan=0,
                    dwFlags=flags,
                    time=0,
                    dwExtraInfo=ctypes.pointer(extra),
                ),
            )
            user32.SendInput(
                1,
                ctypes.byref(inp),
                ctypes.sizeof(INPUT)
            )
        if click_type == 0:
            key_event(False)
            time.sleep(delay)
            key_event(True)
        elif click_type == 1:
            key_event(False)
        elif click_type == 2:
            key_event(True)
        else:
            key_event(False)
            time.sleep(delay)
            key_event(True)
    def _get_hwnd(window):
        """Return a Windows HWND int from a pywebview window/native object."""
        native = getattr(window, "native", window)
        candidates = (
            native,
            getattr(native, "Handle", None),# WinForms BrowserForm -> System.IntPtr
            getattr(window, "Handle", None),
            getattr(window, "hwnd", None),
        )
        for candidate in candidates:
            if not candidate:
                continue

            if isinstance(candidate, int):
                return candidate

            if hasattr(candidate, "value") and candidate.value:
                return int(candidate.value)

            if hasattr(candidate, "ToInt64"):
                value = int(candidate.ToInt64())
                if value:
                    return value

            if hasattr(candidate, "ToInt32"):
                value = int(candidate.ToInt32())
                if value:
                    return value

            try:
                value = int(candidate)
            except (TypeError, ValueError):
                continue

            if value:
                return value

        return None

# macOS (Keyboard, scale factor, mouse button)
elif sys.platform == "darwin":
    _scale_cache = None
    LEFT_BUTTON = 0
    MAC_KEY_MAP = {
        "a": 0, "s": 1, "d": 2, "f": 3, "h": 4, "g": 5, "z": 6, "x": 7, "c": 8, "v": 9,
        "b": 11, "q": 12, "w": 13, "e": 14, "r": 15, "y": 16, "t": 17, "1": 18, "2": 19, "3": 20,
        "4": 21, "6": 22, "5": 23, "equal": 24, "9": 25, "7": 26, "minus": 27, "8": 28, "0": 29, "o": 31,
        "u": 32, "i": 34, "p": 35, "l": 37, "j": 38, "k": 40, "semicolon": 41, "comma": 43, "slash": 44, "n": 45,
        "m": 46, "period": 47, "space": 49, "return": 36, "enter": 76, "tab": 48, "escape": 53,
    }
    def get_scale_factor():
        global _scale_cache
        if _scale_cache is not None:
            return _scale_cache

        try:
            _scale_cache = float(AppKit.NSScreen.mainScreen().backingScaleFactor())
        except Exception:
            _scale_cache = 1.0
        return _scale_cache

    def get_mouse_position():
        event = Quartz.CGEventCreate(None)
        loc = Quartz.CGEventGetLocation(event)
        return loc.x, loc.y

    def _move_mouse(x, y):
        """Expects logical points."""
        point = Quartz.CGPointMake(x, y)
        Quartz.CGWarpMouseCursorPosition(point)
        Quartz.CGAssociateMouseAndMouseCursorPosition(True)
    def _mouse_event(button="left", press=True, x=None, y=None):
        """Unified cross-platform mouse event.
        button: 'left'/'right'/'middle' or 1/2/3
        press=True → down, False → up
        """
        if x is None or y is None:
            x, y = get_mouse_position()
        # Map button → (Quartz button constant, down event, up event)
        button_map = {
            "left":   (Quartz.kCGMouseButtonLeft, Quartz.kCGEventLeftMouseDown, Quartz.kCGEventLeftMouseUp),
            1:        (Quartz.kCGMouseButtonLeft, Quartz.kCGEventLeftMouseDown, Quartz.kCGEventLeftMouseUp),
            "right":  (Quartz.kCGMouseButtonRight,Quartz.kCGEventRightMouseDown,Quartz.kCGEventRightMouseUp),
            3:        (Quartz.kCGMouseButtonRight,Quartz.kCGEventRightMouseDown,Quartz.kCGEventRightMouseUp),
            "middle": (Quartz.kCGMouseButtonCenter, Quartz.kCGEventOtherMouseDown,Quartz.kCGEventOtherMouseUp),
            2:        (Quartz.kCGMouseButtonCenter, Quartz.kCGEventOtherMouseDown,Quartz.kCGEventOtherMouseUp),
        }
        key = button.lower() if isinstance(button, str) else button
        if key not in button_map:
            key = "left"
        btn, down_evt, up_evt = button_map[key]
        event_type = down_evt if press else up_evt
        event = Quartz.CGEventCreateMouseEvent(
            None,
            event_type,
            Quartz.CGPointMake(float(x), float(y)),
            btn
        )
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)
    def send_key(key, delay=0.05, click_type=0):
        """
        Send a keyboard event.
        click_type:
            0 = click (press + release)   [default]
            1 = hold (press only)
            2 = release (release only)
        """
        keycode = MAC_KEY_MAP.get(str(key).lower())
        if keycode is None:
            return

        if click_type == 0:           # Click (press + release)
            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                Quartz.CGEventCreateKeyboardEvent(None, keycode, True)   # key down
            )
            time.sleep(delay)
            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                Quartz.CGEventCreateKeyboardEvent(None, keycode, False)  # key up
            )
        elif click_type == 1:         # Hold (press only)
            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                Quartz.CGEventCreateKeyboardEvent(None, keycode, True)   # key down
            )
        elif click_type == 2:         # Release only
            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                Quartz.CGEventCreateKeyboardEvent(None, keycode, False)  # key up
            )
        else:
            # Fallback to normal click if invalid value is passed
            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                Quartz.CGEventCreateKeyboardEvent(None, keycode, True)
            )
            time.sleep(delay)
            Quartz.CGEventPost(
                Quartz.kCGHIDEventTap,
                Quartz.CGEventCreateKeyboardEvent(None, keycode, False)
            )
# Linux (Mouse positions and Xdisplay)
elif sys.platform.startswith("linux"):
    _xdisplay = None
    def _get_xdisplay():
        global _xdisplay
        if _xdisplay is None:
            _xdisplay = Xdisplay.Display()
        return _xdisplay

    def get_scale_factor():
        """
        X11 normally works in physical pixels.
        Return 1.0 unless you implement desktop-specific scaling detection.
        """
        return 1.0

    def get_mouse_position():
        d = _get_xdisplay()
        root = d.screen().root
        pointer = root.query_pointer()
        return pointer.root_x, pointer.root_y

    def _move_mouse(x, y):
        d = _get_xdisplay()
        root = d.screen().root
        root.warp_pointer(int(x), int(y))
        d.sync()
    def _mouse_event(button="left", press=True, x=None, y=None):
        """Unified cross-platform mouse event.
        button: 'left'/'right'/'middle' or 1/2/3
        press=True → down, False → up
        """
        d = _get_xdisplay()
        if x is not None and y is not None:
            _move_mouse(x, y)   # move first so the click happens at the desired location
        button_map = {
            "left": 1, 1: 1,
            "middle": 2, 2: 2,
            "right": 3, 3: 3,
        }
        key = button.lower() if isinstance(button, str) else button
        btn = button_map.get(key, 1)
        xtest.fake_input(
            d,
            X.ButtonPress if press else X.ButtonRelease,
            btn
        )
        d.sync()
    def send_key(key, delay=0.05, click_type=0):
        d = _get_xdisplay()
        keysym = XK.string_to_keysym(str(key))
        if keysym == 0:
            keysym = XK.string_to_keysym(str(key).lower())
        if keysym == 0:
            return

        keycode = d.keysym_to_keycode(keysym)
        if keycode == 0:
            return

        if click_type == 0:
            xtest.fake_input(d, X.KeyPress, keycode)
            d.sync()
            time.sleep(delay)
            xtest.fake_input(d, X.KeyRelease, keycode)
            d.sync()
        elif click_type == 1:
            xtest.fake_input(d, X.KeyPress, keycode)
            d.sync()
        elif click_type == 2:
            xtest.fake_input(d, X.KeyRelease, keycode)
            d.sync()
        else:
            xtest.fake_input(d, X.KeyPress, keycode)
            d.sync()
            time.sleep(delay)
            xtest.fake_input(d, X.KeyRelease, keycode)
            d.sync()
    try:
        X11 = ctypes.cdll.LoadLibrary(find_library("X11"))
    except Exception:
        X11 = None
# Screen dimensions via mss — use monitor[1] (primary) not monitor[0] (virtual combined).
# On Windows with DPI scaling, pywebview's x/y/width/height use physical pixels,
# so we must query the raw physical resolution, not the scaled logical resolution.
try:
    MSS = mss.MSS
except AttributeError:
    MSS = mss.mss
with MSS() as _sct:
    if len(_sct.monitors) > 1:
        _m = _sct.monitors[1]   # Primary monitor
    else:
        _m = _sct.monitors[0]   # Fallback: only one entry exists
    SCREEN_WIDTH  = _m["width"]
    SCREEN_HEIGHT = _m["height"]
    SCREEN_LEFT   = _m["left"]
    SCREEN_TOP    = _m["top"]
HALF_WIDTH = int(SCREEN_WIDTH / 2)
HALF_HEIGHT = int(SCREEN_HEIGHT / 2)
def cgimage_to_srgb_numpy(image):
    if sys.platform == "darwin":
        width = Quartz.CGImageGetWidth(image)
        height = Quartz.CGImageGetHeight(image)
        bytes_per_row = width * 4
        # Create sRGB color space
        color_space = Quartz.CGColorSpaceCreateWithName(
            Quartz.kCGColorSpaceSRGB
        )
        # Allocate buffer
        raw = np.empty((height, width, 4), dtype=np.uint8)
        # Create bitmap context targeting numpy buffer
        context = Quartz.CGBitmapContextCreate(
            raw,
            width,
            height,
            8,
            bytes_per_row,
            color_space,
            Quartz.kCGImageAlphaPremultipliedLast |
            Quartz.kCGBitmapByteOrder32Big
        )
        # Draw image into sRGB context
        Quartz.CGContextDrawImage(
            context,
            Quartz.CGRectMake(0, 0, width, height),
            image
        )
        # RGBA -> BGR
        bgr = raw[:, :, :3][:, :, ::-1]
        return bgr.copy()

    else:
        return image

# Main GUI
class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("650x300")
        self.title("AutoHotKey Dash")
        # Sidebar
        self.sidebar = tk.Frame(self, width=350)
        self.sidebar.pack(side="left", fill="y")
        # Prevent sidebar from shrinking below 300px
        self.sidebar.pack_propagate(False)
        self.sidebar.config(width=250)  # Ensure width is explicitly set
        # Main content
        self.content = tk.Frame(self)
        self.content.pack(side="right", fill="both", expand=True)
        # Ahk2Py
        self.ahk_converter = Ahk2Py(self)
        self.ahk_editor = AhkEditor(self)
        # Build UI
        self.build_sidebar()
        self.build_main_content()
        self.mainloop()
    def build_sidebar(self):
        # Load Icons
        self.editor_icon = tk.PhotoImage(file=os.path.join(IMAGES_PATH, "editor_icon.png"))
        self.compile_icon = tk.PhotoImage(file=os.path.join(IMAGES_PATH, "compile_icon.png"))
        self.help_icon = tk.PhotoImage(file=os.path.join(IMAGES_PATH, "help_icon.png"))
        self.window_spy_icon = tk.PhotoImage(file=os.path.join(IMAGES_PATH, "window_spy_icon.png"))
        self.launch_icon = tk.PhotoImage(file=os.path.join(IMAGES_PATH, "launch_icon.png"))
        self.record_icon = tk.PhotoImage(file=os.path.join(IMAGES_PATH, "record_icon.png"))
        # Configure button style to prevent dark mode auto-coloring
        tk.Button(
            self.sidebar,
            text="AHK Visual Editor\nEdit AHK scripts directly",
            image=self.editor_icon,
            compound="left",
            anchor="w",
            justify="left",
            padx=0,
            command=self.ahk_editor.show
        ).pack(fill="x", padx=0, pady=0)
        tk.Button(
            self.sidebar,
            text="Compile\nOpen Ahk2Py - convert .ahk to .py",
            image=self.compile_icon,
            compound="left",
            anchor="w",
            justify="left",
            padx=0,
            command=self.ahk_converter.show
        ).pack(fill="x", padx=0, pady=0)
        tk.Button(
            self.sidebar,
            text="Help Files",
            image=self.help_icon,
            compound="left",
            anchor="w",
            justify="left",
            padx=0
        ).pack(fill="x", padx=0, pady=0)
        tk.Button(
            self.sidebar,
            text="Window Spy",
            image=self.window_spy_icon,
            compound="left",
            anchor="w",
            justify="left",
            padx=0
        ).pack(fill="x", padx=0, pady=0)
    def build_main_content(self):
        body = tk.Frame(self.content)
        body.pack(anchor="nw", fill="both", expand=True, padx=0, pady=10)
        tk.Label(
            body,
            text="Welcome!",
            font=("Segoe UI", 16)
        ).pack(anchor="w")
        tk.Label(
            body,
            text="This is the Dash. It provides access to tools, settings and help files."
        ).pack(anchor="w", pady=(5, 0))
        tk.Label(
            body,
            text="To learn how to use AutoHotKey, refer to:"
        ).pack(anchor="w", pady=(5, 0))
        tk.Button(
            body,
            text="Using the program"
        ).pack(anchor="w", fill="x", padx=0, pady=0)
        tk.Button(
            body,
            text="How to Write Hotkeys"
        ).pack(anchor="w", fill="x", padx=0, pady=0)
        tk.Button(
            body,
            text="How to Send Keystrokes"
        ).pack(anchor="w", fill="x", padx=0, pady=0)
        tk.Button(
            body,
            text="How to Run Programs"
        ).pack(anchor="w", fill="x", padx=0, pady=0)
        tk.Button(
            body,
            text="How to Manage Windows"
        ).pack(anchor="w", fill="x", padx=0, pady=0)
        tk.Button(
            body,
            text="Quick Reference"
        ).pack(anchor="w", fill="x", padx=0, pady=0)
        tk.Checkbutton(
            body,
            text="Show this info next time",
            anchor="w"
        ).pack(fill="x", padx=0)
# AHK Editor
class AhkEditor:
    # Recorder tuning
    MOVE_PIXEL_THRESHOLD = 8      # ignore jitter smaller than this
    MOVE_MIN_INTERVAL = 0.05      # seconds between MouseMove samples
    MIN_SLEEP_MS = 20             # do not emit Sleep for tiny gaps
    MAX_SLEEP_MS = 60000
    CLICK_TAP_MS = 220            # collapse Down+Up into a single Click
    RECORD_ARM_DELAY = 0.25       # skip the Start Recording click
    def __init__(self, master):
        self.master = master

        self.window = tk.Toplevel(self.master)
        self.window.title("AutoHotKey Script Editor")
        self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self.hide)

        # Current editor file
        self.file_path = None

        # Recorder state
        self.is_recording = False
        self.recorded_actions = []
        self.recording_lock = threading.Lock()

        self.recording_start_time = 0.0
        self.last_action_time = 0.0

        # Mouse recording state
        self.last_mouse_position = None
        self.last_mouse_move_time = 0.0

        # Keyboard recording state
        self.pressed_keys = set()

        # Ignore the mouse click used to press Start Recording.
        self.record_arm_time = 0.0

        self.build_main_content()

        # Start global keyboard listener
        self.keyboard_listener = None
        try:
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.keyboard_listener.daemon = True
            self.keyboard_listener.start()
        except Exception as e:
            print(f"Keyboard listener error: {e}")

        # Start global mouse listener
        self.mouse_listener = None
        try:
            self.mouse_listener = mouse.Listener(
                on_move=self.on_move,
                on_click=self.on_click,
                on_scroll=self.on_scroll
            )
            self.mouse_listener.daemon = True
            self.mouse_listener.start()
        except Exception as e:
            print(f"Mouse listener error: {e}")

        self.build_menu()
        self.hide()

    def show(self):
        self.window.deiconify()

    def hide(self):
        if getattr(self, "is_recording", False):
            self.stop_recording()
        self.window.withdraw()

    def build_main_content(self):
        # Configure grid weights
        self.window.grid_rowconfigure(0, weight=0)  # Top bar - fixed height
        self.window.grid_rowconfigure(1, weight=1)  # Editor - takes remaining space
        self.window.grid_columnconfigure(0, weight=1)

        # Top Bar with content
        self.top_bar = tk.LabelFrame(self.window, text="Top Bar", height=80)
        self.top_bar.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.top_bar.grid_propagate(False)
        
        # Configure grid for self.top_bar
        self.top_bar.grid_columnconfigure(0, weight=1)
        self.top_bar.grid_columnconfigure(1, weight=0)

        commands = ["Send", "Click", "Sleep", "MouseMove", "PixelSearch", "PixelGetColor", "MouseGetPos"]
        self.current_command = ttk.Combobox(self.top_bar, values=commands)  # Specify master as self.top_bar
        self.current_command.grid(row=0, column=0, sticky="ew")  # Only east-west

        button = tk.Button(self.top_bar, text="Add", command=self.add_content)  # Specify master as self.top_bar
        button.grid(row=0, column=1, sticky="ew")  # Only east-west

        self.recording_button = tk.Button(self.top_bar, text="Start Recording", command=self.start_recording)  # Specify master as self.top_bar
        self.recording_button.grid(row=0, column=2, sticky="ew")  # Only east-west

        # Editor
        editor = tk.LabelFrame(self.window, text="Editor")
        editor.grid(row=1, column=0, sticky="nsew")
        
        # Add a Text widget as the editor
        self.text_editor = tk.Text(editor, wrap=tk.WORD)
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def build_menu(self):
        menubar = tk.Menu(self.window)

        # File
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit
        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo", command=self.text_editor.edit_undo)
        edit_menu.add_command(label="Redo", command=self.text_editor.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=lambda: self.text_editor.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copy", command=lambda: self.text_editor.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Paste", command=lambda: self.text_editor.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Find", command=self.find_text)
        edit_menu.add_command(label="Find and Replace", command=self.find_and_replace)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # View
        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Reset Zoom", command=self.reset_zoom)
        menubar.add_cascade(label="View", menu=view_menu)

        self.window.config(menu=menubar)

    def record_action(self, action_text, timestamp=None):
        """
        Add an action to the recording with the delay since the previous action.

        This method is called by pynput listener threads, so it must not touch
        Tkinter widgets directly.
        """
        if not self.is_recording or not action_text:
            return

        if timestamp is None:
            timestamp = time.monotonic()

        with self.recording_lock:
            if not self.is_recording:
                return

            # First action starts from the recording start time.
            if self.last_action_time <= 0:
                self.last_action_time = self.recording_start_time

            delay_ms = int(
                max(0.0, timestamp - self.last_action_time) * 1000
            )

            self.last_action_time = timestamp

            if delay_ms >= self.MIN_SLEEP_MS:
                delay_ms = min(delay_ms, self.MAX_SLEEP_MS)
                self.recorded_actions.append(f"Sleep, {delay_ms}")

            self.recorded_actions.append(action_text)

    def start_recording(self):
        """
        Start recording keyboard and mouse events.

        The listeners run independently from Tkinter, so this method does not
        contain a blocking loop.
        """
        if self.is_recording:
            return

        print("Macro Status: Recording...")

        with self.recording_lock:
            self.recorded_actions.clear()
            self.pressed_keys.clear()

            self.recording_start_time = time.monotonic()
            self.last_action_time = self.recording_start_time

            self.last_mouse_position = None
            self.last_mouse_move_time = 0.0

            # Ignore the click that pressed the recording button.
            self.record_arm_time = (
                self.recording_start_time + self.RECORD_ARM_DELAY
            )

            self.is_recording = True

        self.recording_button.config(
            text="Stop Recording",
            command=self.stop_recording
        )


    def stop_recording(self):
        """
        Stop recording and insert the recorded actions into the editor.
        """
        if not self.is_recording:
            return

        print("Macro Status: Recording stopped.")

        with self.recording_lock:
            self.is_recording = False

            # Release any keys that were still held when recording stopped.
            for key_name in list(self.pressed_keys):
                self.recorded_actions.append(
                    f"Send, {{{key_name} up}}"
                )

            self.pressed_keys.clear()

            # Copy the result so the listener threads cannot modify the list
            # while we are inserting it into the editor.
            actions = list(self.recorded_actions)
            self.recorded_actions.clear()

        self.recording_button.config(
            text="Start Recording",
            command=self.start_recording
        )

        if actions:
            # Tkinter operations must happen on the Tkinter thread.
            self.window.after(
                0,
                lambda: self._insert_recorded_actions(actions)
            )

    def _insert_recorded_actions(self, actions):
        """Insert a completed recording into the Text widget."""
        if not actions:
            return

        current_text = self.text_editor.get("1.0", "end-1c")

        if current_text.strip():
            self.text_editor.insert("end-1c", "\n")

        self.text_editor.insert("end-1c", "\n".join(actions))
        self.text_editor.see("end")
        self.text_editor.focus_set()

    def _key_to_ahk(self, key):
        """Convert a pynput key into an AHK Send key name."""
        try:
            if hasattr(key, "char") and key.char is not None:
                char = key.char

                if char == " ":
                    return "Space"

                if char in {"\r", "\n"}:
                    return "Enter"

                return char

            name = str(key).replace("Key.", "")

            aliases = {
                "space": "Space",
                "enter": "Enter",
                "return": "Enter",
                "tab": "Tab",
                "esc": "Escape",
                "escape": "Escape",
                "backspace": "Backspace",
                "delete": "Delete",

                "shift": "Shift",
                "shift_l": "LShift",
                "shift_r": "RShift",

                "ctrl": "Ctrl",
                "ctrl_l": "LCtrl",
                "ctrl_r": "RCtrl",
                "control": "Ctrl",

                "alt": "Alt",
                "alt_l": "LAlt",
                "alt_r": "RAlt",

                "cmd": "LWin",
                "cmd_l": "LWin",
                "cmd_r": "RWin",

                "up": "Up",
                "down": "Down",
                "left": "Left",
                "right": "Right",

                "home": "Home",
                "end": "End",
                "insert": "Insert",
                "page_up": "PgUp",
                "page_down": "PgDn",

                "caps_lock": "CapsLock",
                "num_lock": "NumLock",
                "scroll_lock": "ScrollLock",
            }

            if name.lower() in aliases:
                return aliases[name.lower()]

            # F1-F24
            if name.lower().startswith("f") and name[1:].isdigit():
                return name.upper()

            return name

        except Exception:
            return None

    def on_press(self, key):
        """Record keyboard press events."""
        if not self.is_recording:
            return

        now = time.monotonic()

        # Don't record anything during the arming period.
        if now < self.record_arm_time:
            return

        key_name = self._key_to_ahk(key)

        if not key_name:
            return

        with self.recording_lock:
            # Prevent repeated key-down events from key auto-repeat.
            if key_name in self.pressed_keys:
                return

            self.pressed_keys.add(key_name)

        # Modifier keys and other held keys need a down event.
        self.record_action(
            f"Send, {{{key_name} down}}",
            timestamp=now
        )


    def on_release(self, key):
        """Record keyboard release events."""
        if not self.is_recording:
            return

        now = time.monotonic()

        if now < self.record_arm_time:
            return

        key_name = self._key_to_ahk(key)

        if not key_name:
            return

        with self.recording_lock:
            if key_name not in self.pressed_keys:
                return

            self.pressed_keys.remove(key_name)

        self.record_action(
            f"Send, {{{key_name} up}}",
            timestamp=now
        )


    def on_move(self, x, y):
        """Record significant mouse movement."""
        if not self.is_recording:
            return

        now = time.monotonic()

        if now < self.record_arm_time:
            return

        with self.recording_lock:
            if self.last_mouse_position is not None:
                last_x, last_y = self.last_mouse_position

                distance = math.hypot(
                    x - last_x,
                    y - last_y
                )

                # Ignore tiny mouse jitter.
                if distance < self.MOVE_PIXEL_THRESHOLD:
                    return

            # Limit mouse-move recording frequency.
            if (
                self.last_mouse_move_time > 0
                and now - self.last_mouse_move_time < self.MOVE_MIN_INTERVAL
            ):
                self.last_mouse_position = (x, y)
                return

            self.last_mouse_position = (x, y)
            self.last_mouse_move_time = now

        self.record_action(
            f"MouseMove, {round(x)}, {round(y)}",
            timestamp=now
        )


    def on_click(self, x, y, button, pressed):
        """Record mouse button presses and releases."""
        if not self.is_recording:
            return

        now = time.monotonic()

        if now < self.record_arm_time:
            return

        button_name = str(button).replace("Button.", "").lower()

        button_map = {
            "left": "Left",
            "right": "Right",
            "middle": "Middle",
        }

        ahk_button = button_map.get(button_name)

        if ahk_button is None:
            return

        action = "Down" if pressed else "Up"

        self.record_action(
            f"Click, {round(x)}, {round(y)}, {action} {ahk_button}",
            timestamp=now
        )


    def on_scroll(self, x, y, dx, dy):
        """Record mouse-wheel events."""
        if not self.is_recording:
            return

        now = time.monotonic()

        if now < self.record_arm_time:
            return

        # AHK-compatible wheel commands.
        if dy > 0:
            action = "Send, {WheelUp}"
        elif dy < 0:
            action = "Send, {WheelDown}"
        else:
            return

        self.record_action(
            action,
            timestamp=now
        )

    def new_file(self):
        """Clear the editor and start a new unsaved AHK script."""
        if self.is_recording:
            self.stop_recording()

        self.text_editor.delete("1.0", tk.END)

        self.file_path = None
        self.window.title("AutoHotKey Script Editor")


    def open_file(self):
        """Open an AHK script into the editor."""
        if self.is_recording:
            self.stop_recording()

        file_path = filedialog.askopenfilename(
            parent=self.window,
            title="Open AutoHotKey Script",
            filetypes=[
                ("AutoHotKey Scripts", "*.ahk"),
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8-sig") as file:
                content = file.read()

        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="cp1252") as file:
                    content = file.read()
            except Exception as e:
                messagebox.showerror(
                    "Open File",
                    f"Could not open the file:\n\n{e}",
                    parent=self.window
                )
                return

        except Exception as e:
            messagebox.showerror(
                "Open File",
                f"Could not open the file:\n\n{e}",
                parent=self.window
            )
            return

        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", content)

        self.file_path = file_path
        self.window.title(
            f"AutoHotKey Script Editor - {os.path.basename(file_path)}"
        )

        self.text_editor.focus_set()


    def save_file(self):
        """Save the current editor contents to an AHK file."""
        if self.is_recording:
            self.stop_recording()

        file_path = self.file_path

        # If this is a new/unsaved document, ask where to save it.
        if not file_path:
            file_path = filedialog.asksaveasfilename(
                parent=self.window,
                title="Save AutoHotKey Script",
                defaultextension=".ahk",
                filetypes=[
                    ("AutoHotKey Scripts", "*.ahk"),
                    ("Text Files", "*.txt"),
                    ("All Files", "*.*")
                ]
            )

            if not file_path:
                return

        try:
            content = self.text_editor.get("1.0", "end-1c")

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)

            self.file_path = file_path

            self.window.title(
                f"AutoHotKey Script Editor - {os.path.basename(file_path)}"
            )

        except Exception as e:
            messagebox.showerror(
                "Save File",
                f"Could not save the file:\n\n{e}",
                parent=self.window
            )


    def find_text(self):
        pass


    def find_and_replace(self):
        pass


    def zoom_in(self):
        pass


    def zoom_out(self):
        pass


    def reset_zoom(self):
        pass
        
    def add_content(self, selected2=0):
        if selected2 == 0:
            selected = self.current_command.get()
        else:
            selected = selected2

        if not selected:
            return

        last_line = self.text_editor.get("end-1c linestart", "end-1c")

        if last_line.strip():
            self.text_editor.insert(tk.END, "\n" + selected)
        else:
            self.text_editor.insert("end-1c", selected)

        self.text_editor.focus_set()

# AHK to Python converter
class Ahk2Py:
    def __init__(self, master):
        self.master = master

        self.window = tk.Toplevel(self.master)
        self.window.title("Ahk2Py")
        self.window.geometry("500x400")
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        self.build_main_content()
        self.hide()

    def show(self):
        self.window.deiconify()

    def hide(self):
        self.window.withdraw()

    def build_main_content(self):
        main_parameters = tk.LabelFrame(self.window, text="Main Parameters")
        main_parameters.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # FIX: Use pack() or grid() to display the Labels
        tk.Label(main_parameters, text="Script Location").grid(row=0, column=0, sticky="w")
        self.script_location = tk.StringVar()
        tk.Entry(main_parameters, textvariable=self.script_location).grid(row=0, column=1, sticky="w")
        tk.Label(main_parameters, text="Output Directory").grid(row=1, column=0, sticky="w")
        self.output_directory = tk.StringVar()
        tk.Entry(main_parameters, textvariable=self.output_directory).grid(row=1, column=1, sticky="w")

        tk.Button(main_parameters, text="Convert AHK to Python", command=self.ahk_to_py).grid(row=2, column=0, sticky="w")

        self.window.grid_rowconfigure(0, weight=0)
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

    def ahk_to_py(self):
        """Bundle playback.py with the selected AHK script."""

        playback_path = os.path.join(RESOURCES_PATH, "playback.py")

        # Load the AHK script.
        with open(self.script_location.get(), "r", encoding="utf-8") as file:
            ahk_script = file.read()

        # Load the Solar Automate playback runtime.
        with open(playback_path, "r", encoding="utf-8") as file:
            playback_lines = file.readlines()

        # Split playback.py around the selected insertion point.
        runtime_start = playback_lines[:502]
        runtime_end = playback_lines[502:]

        # Build the generated Python file.
        with open(self.output_directory.get(), "w", encoding="utf-8") as outfile:
            outfile.writelines(runtime_start)

            outfile.write("\n\n")
            outfile.write(f"script = {ahk_script!r}\n")

            outfile.write("\n\n")
            outfile.writelines(runtime_end)

        return
# AHK playback
class Playback(tk.Tk):
    def __init__(self, playback_path):
        # Initialization
        super().__init__()
        self.geometry("300x300")
        self.title("title")
        # Read File
        with open(playback_path, "r", encoding="utf-8-sig") as f:
            self.script_text = f.read()
        self.script = self.script_text.splitlines()
        # Other GUI constants
        self.tabs = []
        self.tab_frames = []
        self.color = "Black"
        self.gui_color = "White"
        self.size = 9
        self.current_tab2 = self
        self.tab_offset_x = 0
        self.tab_offset_y = 0
        self.font_bold = False
        try:
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TNotebook.Tab", padding=(2, 1, 2, 1))
        except:
            pass
        # Main Loop
        self.execute_script()
        self.mainloop()

    def execute_script(self, _script=None):
        if _script == None:
            _script = self.script
        for line in range(len(_script)):
            # Process Script
            processed_line = _script[line]
            if processed_line.startswith(";") or processed_line == "":
                continue
            if processed_line == "return":
                break
            # Execute Script
            if processed_line.startswith("Gui"):
                self.cmd_gui(processed_line)

    def cmd_gui(self, line):
        # Define defaults
        arguments = [p.strip() for p in line.split(",")]
        x = 0
        y = 0
        w = 100
        h = 30
        # Gui, Color
        if arguments[1] == "Color":
            self.gui_color = arguments[2].replace("c0x", "#")
            self.gui_color = self.gui_color.replace("0x", "#")
            self.configure(bg=self.gui_color)
        # Gui, Font
        if arguments[1] == "Font":
            color = None
            bold = False
            self.font_size = 9
            for token in arguments[2].split():
                # Color option
                if token.lower().startswith("c"):
                    color = token[1:]
                # Color option
                if token.lower().startswith("s"):
                    self.font_size = token[1:]
                # Style flags
                elif token.lower() == "bold":
                    bold = True
            # Default
            if not color:
                color = "white"
            # Hex color
            if color.startswith("0x"):
                color = "#" + color[2:]
            elif len(color) == 6:
                color = "#" + color
            self.color = color
            self.font_bold = bold
            self.update_style()
        # Gui, Tab
        if arguments[1] == "Tab":
            try:
                if arguments[2] == "":
                    fallback = True
                else:
                    fallback = False
            except:
                fallback = True
            if fallback == True:
                self.current_tab2 = self
            else:
                for tab_index in range(len(self.tabs)):
                    if arguments[2] == self.tabs[tab_index]:
                        self.current_tab2 = self.tab_frames[tab_index]
                        break
        font_style = "bold" if self.font_bold else "normal"
        # Gui, Add
        if arguments[1] == "Add":
            placement = arguments[3].split(" ")
            for item in range(len(placement)):
                if placement[item].startswith("x"):
                    x = int(placement[item].replace("x", ""))
                if placement[item].startswith("y"):
                    y = int(placement[item].replace("y", ""))
                if placement[item].startswith("w"):
                    w = int(placement[item].replace("w", ""))
                if placement[item].startswith("h"):
                    h = int(placement[item].replace("h", ""))
            # Gui, Add, Tab2
            if arguments[2] == "Tab2":
                tab = ttk.Notebook(self, style="Dark.TNotebook")
                tab.place(x=x, y=y, width=w, height=h)
                self.tab_offset_x = x
                self.tab_offset_y = y + 30

                tabs = arguments[4].split("|")

                for tab_name in tabs:
                    frame = ttk.Frame(tab, style="Dark.TFrame")
                    self.tabs.append(tab_name)
                    self.tab_frames.append(frame)
                    tab.add(frame, text=tab_name)
            if self.current_tab2 == self:
                current_offset_x = 0
                current_offset_y = 0
            else:
                current_offset_x = self.tab_offset_x
                current_offset_y = self.tab_offset_y
            # Gui, Add, Text
            if arguments[2] == "Text":
                label = tk.Label(self.current_tab2, text=arguments[4], fg=self.color, bg=self.gui_color, font=("Segoe UI", self.font_size, font_style))
                label.place(x=(x - current_offset_x), y=(y - current_offset_y))
            # Gui, Add, Edit
            if arguments[2] == "Edit":
                entry = tk.Entry(self.current_tab2, highlightbackground=self.gui_color)
                entry.place(x=(x - current_offset_x), y=(y - current_offset_y), width=w, height=h)
            # Gui, Add, GroupBox
            if arguments[2] == "GroupBox":
                group = tk.LabelFrame(self.current_tab2, text=arguments[4], borderwidth=3, bg=self.gui_color, fg=self.color, font=("Segoe UI", self.font_size, font_style))
                group.place(x=(x - current_offset_x), y=(y - current_offset_y), width=w, height=h)
            # Gui, Add, Checkbox
            if arguments[2] == "Checkbox":
                checkbox = ttk.Checkbutton(self.current_tab2, text=arguments[4], style="Dark.TCheckbutton")
                checkbox.place(x=(x - current_offset_x), y=(y - current_offset_y), width=w, height=h)
            # Gui, Add, Button
            if arguments[2] == "Button":
                button = tk.Button(self.current_tab2, text=arguments[4])
                button.place(x=(x - current_offset_x), y=(y - current_offset_y), width=w, height=h)
            # Gui, Add, DropDownList
            if arguments[2] == "DropDownList":
                values = arguments[4].split("|")
                combobox = ttk.Combobox(self.current_tab2, state="readonly", values=values)
                combobox.place(x=(x - current_offset_x), y=(y - current_offset_y), width=w, height=h)

    # Update Style
    def update_style(self):
        style = ttk.Style()
        style.configure(
            "Dark.TNotebook",
            background=self.gui_color
        )
        style.configure(
            "Dark.TFrame",
            background=self.gui_color
        )
        style.configure(
            "Dark.TNotebook.Tab",
            background=self.gui_color,
            foreground=self.color,
            padding=(0, 0)
        )
        style.map(
            "Dark.TNotebook.Tab",
            background=[
                ("selected", self.gui_color),
                ("active", self.gui_color)
            ],
            foreground=[
                ("selected", self.color),
                ("active", self.color)
            ]
        )
        style.configure(
            "Dark.TCheckbutton",
            background=self.gui_color,
            foreground=self.color
        )
        style.map(
            "Dark.TCheckbutton",
            background=[
                ("active", self.gui_color)
            ],
            foreground=[
                ("active", self.color)
            ]
        )

if __name__ == "__main__":
    if open_mode == "Editor":
        app = MainGUI()
        app.mainloop()
    elif open_mode == "Playback":
        playback = Playback(playback_path)