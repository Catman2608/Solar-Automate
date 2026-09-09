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
open_mode = "Playback"
file_path = "Solar Fishing Lite.ahk"
playback_path = os.path.join(folder_path, file_path)
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
        super().__init__()
        self.background_color = "white"
        self.foreground_color = "black"
        self.max_x = 0
        self.max_y = 0
        self.variables = {}
        self.gui_variables = {}
        self.gui_control_placements = {}
        self.gui_images = {}
        self.functions = {}
        # Unified hotkey registry: normalized_key -> label_name (str) or body lines (list)
        # Presence in the dict means the hotkey is enabled. Hotkey, ..., Off deletes the entry.
        self.hotkeys = {}
        self._active_hotkey_modifiers = set()
        self.hotkey_listener = None  # retained for compatibility (unused; unified key_listener is used)
        self._hotkey_listener_started = False
        self.labels = {}
        self.gui_controls = {}
        self._init_builtin_variables()
        self.font_bold = False
        self.current_line_count = 0
        self.font_size = 9
        self.scan_delay = 1
        self.send_backend = "Event"
        self.key_delay = 100
        self.last_scan_request = time.monotonic()
        # Start unified key listener (handles both recording capture and hotkey dispatch)
        self.key_listener = KeyListener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.key_listener.daemon = True
        self.key_listener.start()
        try:
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TNotebook.Tab", padding=(2, 1, 2, 1))
        except:
            pass

        self.geometry("300x300")
        title = os.path.basename(playback_path)
        self.current_tab = None
        self.tabs = {}
        self.title(title)
        # Cleanly stop the unified hotkey listener when the window is closed
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        with open(playback_path, "r", encoding="utf-8-sig") as f:
            self.script_text = f.read()
        self.script = self.script_text.splitlines()
        self.after(0, self.withdraw)
        self.build_main_content()
        if sys.platform == "darwin":
            self.capture_thread = threading.Thread(target=self.capture_loop_quartz, daemon=True)
        else:
            self.capture_thread = threading.Thread(target=self.capture_loop_mss, daemon=True)
        self.capture_thread.start()
        self.mainloop()
    def _on_close(self):
        if hasattr(self, "key_listener") and self.key_listener is not None:
            try:
                self.key_listener.stop()
            except Exception:
                pass

        if hasattr(self, "hotkey_listener") and self.hotkey_listener is not None:
            try:
                self.hotkey_listener.stop()
            except Exception:
                pass

        self.destroy()
    # Supporter functions
    def update_style(self):
        style = ttk.Style()
        style.configure(
            "Dark.TNotebook",
            background=self.background_color
        )
        style.configure(
            "Dark.TFrame",
            background=self.background_color
        )
        style.configure(
            "Dark.TNotebook.Tab",
            background=self.background_color,
            foreground=self.foreground_color,
            padding=(0, 0)
        )
        style.map(
            "Dark.TNotebook.Tab",
            background=[
                ("selected", self.background_color),
                ("active", self.background_color)
            ],
            foreground=[
                ("selected", self.foreground_color),
                ("active", self.foreground_color)
            ]
        )
        style.configure(
            "Dark.TCheckbutton",
            background=self.background_color,
            foreground=self.foreground_color
        )
        style.map(
            "Dark.TCheckbutton",
            background=[
                ("active", self.background_color)
            ],
            foreground=[
                ("active", self.foreground_color)
            ]
        )
    def _init_builtin_variables(self):
        # Screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        script_directory = os.getcwd()
        # Platform mapping
        if sys.platform.startswith("darwin"):
            platform_val = 0
        elif sys.platform.startswith("linux"):
            platform_val = 1
        else:
            # Windows OR standard AHK behavior
            platform_val = -1
        self.builtin_variables = {
            "A_ScreenWidth": screen_width,
            "A_ScreenHeight": screen_height,
            "A_Platform": platform_val,
            "A_ScriptDir": script_directory,
            "A_ScreenDPI": self.get_screen_dpi()
        }
    def _strip_inline_comment(self, line):
        """
        Remove AHK comments while preserving ; inside quotes.
        Example:
            MsgBox, Hello ; comment
        becomes:
            MsgBox, Hello
        """
        in_single = False
        in_double = False
        for i, char in enumerate(line):
            if char == '"' and not in_single:
                in_double = not in_double
            elif char == "'" and not in_double:
                in_single = not in_single
            elif char == ";" and not in_single and not in_double:
                # ; starts a comment if it is not inside text
                return line[:i].rstrip()

        return line

    def _extract_block(self, actions, start_index):
        """
        Extracts a { ... } block starting after a Loop/If/Function statement.
        Returns:
            (block_lines, ending_index_of_closing_brace)
        """
        block = []
        i = start_index
        # Skip to the opening brace
        brace_depth = 0
        found_opening_brace = False
        while i < len(actions):
            line = actions[i].strip()
            # Skip empty lines and comments
            if not line or line.startswith(";"):
                i += 1
                continue

            # Check if this line contains an opening brace
            if "{" in line:
                # Calculate brace depth from this line
                open_count = line.count("{")
                close_count = line.count("}")
                brace_depth += open_count - close_count
                # If brace_depth is 0, the block is on one line
                if brace_depth == 0:
                    # Extract content between braces
                    start = line.find("{") + 1
                    end = line.rfind("}")
                    content = line[start:end].strip()
                    if content:
                        block.append(content)
                    return block, i

                found_opening_brace = True
                # If there's content after the opening brace on the same line
                after_brace = line[line.find("{")+1:].strip()
                if after_brace and "}" not in line:
                    block.append(after_brace)
                i += 1
                break

            else:
                # Check if next line has the opening brace
                next_i = i + 1
                while next_i < len(actions) and not actions[next_i].strip():
                    next_i += 1
                if next_i < len(actions) and actions[next_i].strip() == "{":
                    # Next line is the opening brace
                    i = next_i + 1
                    brace_depth = 1
                    found_opening_brace = True
                    break

                else:
                    # No block, treat as single-line statement
                    return [line], i

        if not found_opening_brace:
            return [], i

        # Collect block contents until braces balance out
        while i < len(actions) and brace_depth > 0:
            current = actions[i]
            stripped = current.strip()
            # Skip empty lines and comments inside the block
            if not stripped or stripped.startswith(";"):
                i += 1
                continue

            # Count braces in this line
            open_count = stripped.count("{")
            close_count = stripped.count("}")
            brace_depth += open_count
            brace_depth -= close_count
            # Add the line if it's not the final closing brace and not a standalone opening brace
            if stripped:
                if not (brace_depth == 0 and stripped == "}" and open_count == 0 and close_count == 1):
                    if not (stripped == "{" and open_count == 1 and close_count == 0 and i > start_index):
                        block.append(stripped)
            i += 1
        # i is now at the index after the closing brace
        return block, i - 1

    def _extract_if_condition(self, line):
        match = re.match(r"^if\s*\((.*?)\)\s*\{?\s*$", line, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        match = re.match(r"^if\s*,?\s*(.*?)\s*\{?\s*$", line, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        return line[2:].strip().rstrip("{").strip()

    def _extract_if_blocks(self, actions, start_index):
        """
        Extracts if / else if / else structure.
        Returns: (condition, if_block, else_block, ending_index)
        Nested ifs (without else) are handled by brace-depth matching in
        _extract_block; the nested statements remain as lines inside if_block
        and are re-parsed when the block is executed.
        else-if chains are handled by a single recursive call on a sliced
        remainder (converted to a plain "If"), guaranteeing termination
        because each recursion receives a strictly shorter list.
        """
        line = actions[start_index].strip()
        condition = self._extract_if_condition(line)
        # Extract IF body (brace matching correctly includes any nested ifs)
        if_block, end_index = self._extract_block(actions, start_index)
        else_block = []
        i = end_index + 1
        # Skip blank lines and comments after the if-block
        while i < len(actions):
            current = actions[i].strip()
            if not current or current.startswith(";"):
                i += 1
                continue

            break

        else:
            # Reached end of actions with no else / else-if
            return condition, if_block, else_block, end_index

        lower = current.lower()
        # Else If  → recurse once on the remaining chain
        if lower.startswith("else if"):
            # Convert "else if ..." into a plain "If ..." for the recursive call
            nested_if = "If" + current[7:]
            # fake_actions[0] corresponds to the original line at index i
            fake_actions = [nested_if] + actions[i + 1:]
            nested_condition, nested_true, nested_false, nested_end = (
                self._extract_if_blocks(fake_actions, 0)
            )
            # Rebuild an executable if/else structure so later execution of
            # else_block behaves exactly like the else-if chain
            else_block = [f"If {nested_condition}"]
            else_block.append("{")
            else_block.extend(nested_true)
            else_block.append("}")
            if nested_false:
                else_block.append("Else")
                else_block.append("{")
                else_block.extend(nested_false)
                else_block.append("}")
            # Map the recursive end index back onto the original actions list
            end_index = i + nested_end
        # Normal Else
        elif lower.startswith("else"):
            else_block, else_end = self._extract_block(actions, i)
            end_index = else_end
        # else: plain if with no else clause – keep the end_index we already have
        return condition, if_block, else_block, end_index

    def _try_number(self, val):
        """
        AHK-style numeric coercion: if value looks like a number, return int/float;
        otherwise return the original value unchanged.
        Empty / whitespace-only strings become 0 (AHK numeric context).
        """
        if isinstance(val, bool):
            return int(val)
        if isinstance(val, (int, float)):
            return val
        if val is None:
            return 0
        if isinstance(val, str):
            s = val.strip()
            if not s:
                return 0
            try:
                # Prefer int when possible (no decimal / exponent)
                if re.fullmatch(r"[+-]?\d+", s):
                    return int(s)
                return float(s)
            except ValueError:
                return val
        return val

    def _coerce_numeric_literals(self, expr, force_non_numeric_to_zero=False):
        """
        Turn string literals that look like numbers into bare numeric literals
        so that Python eval behaves like AHK expression evaluation.
        e.g.  '"1" + 1'  →  '1 + 1'
              "'2.5' > 1" → '2.5 > 1'
        Non-numeric strings are left quoted unless force_non_numeric_to_zero=True,
        in which case any remaining quoted string becomes 0 (AHK "invalid → 0").
        """
        def repl_numeric(m):
            s = m.group(1) if m.group(1) is not None else m.group(2)
            try:
                if re.fullmatch(r"[+-]?\d+", s):
                    return str(int(s))
                return str(float(s))
            except ValueError:
                return m.group(0)  # keep original quotes

        expr = re.sub(
            r'"([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)"|\'([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\'',
            repl_numeric,
            expr,
        )
        if force_non_numeric_to_zero:
            # Turn any remaining quoted string into 0
            expr = re.sub(r'"[^"]*"|\'[^\']*\'', "0", expr)
        return expr

    def _safe_eval(self, expr):
        """
        Evaluate an expression with AHK-compatible type coercion.
        - Numeric-looking string literals are always turned into numbers first
          (so "2.5"*2 becomes 5.0, not the Python string-repeat "2.52.5").
        - Variables whose values look numeric are exposed as numbers; pure
          non-numeric strings stay as strings (so "foo"=="foo" still works).
        - Unset / unknown names evaluate to 0 (AHK treats unset vars as empty,
          which becomes 0 in numeric context) instead of raising NameError.
        - On TypeError we fall back to a fully numeric context where every
          non-numeric string (variable or literal) becomes 0, matching AHK's
          "invalid number → 0" rule. Thus "abc"+1 → 1 and "1"+1 → 2.
        """
        # Dict that returns 0 for any missing name (AHK unset-variable behaviour)
        class _AHKNS(dict):
            def __missing__(self, key):
                return 0

        # Always coerce numeric-looking string literals first
        coerced_expr = self._coerce_numeric_literals(expr)

        # Primary namespace: numeric-looking values → numbers, non-numeric
        # strings stay as strings (preserves pure string comparisons).
        raw_ns = self._get_eval_namespace()
        ns = _AHKNS()
        for k, v in raw_ns.items():
            if callable(v):
                ns[k] = v
            else:
                ns[k] = self._try_number(v)

        try:
            return eval(coerced_expr, {"__builtins__": {}}, ns)
        except Exception:
            pass

        # Secondary: force remaining non-numeric strings (vars + literals) to 0
        forced_expr = self._coerce_numeric_literals(expr, force_non_numeric_to_zero=True)
        coerced_ns = _AHKNS()
        for k, v in ns.items():
            if callable(v):
                coerced_ns[k] = v
            elif isinstance(v, str):
                coerced_ns[k] = 0
            else:
                coerced_ns[k] = v
        try:
            return eval(forced_expr, {"__builtins__": {}}, coerced_ns)
        except Exception as e:
            # Last resort: original expression with original namespace + missing→0
            try:
                fallback = _AHKNS(raw_ns)
                return eval(expr, {"__builtins__": {}}, fallback)
            except Exception:
                raise e

    def _evaluate_condition(self, condition):
        """
        Evaluate a condition string, supporting AHK-style operators.
        Examples
        --------
        ErrorLevel = 0       →  ErrorLevel == 0
        Px != -1
        Px > 100
        x >= 5 and y < 10
        "1" > 2              →  False   (AHK numeric coercion)
        """
        condition = condition.strip()
        if condition.startswith("(") and condition.endswith(")"):
            condition = condition[1:-1]
        # Normalize operators
        condition = self._normalize_condition(condition)
        # Replace %VarName% tokens
        condition = self._handle_variable(condition)
        # Replace bare variable names (no % signs) that match known variables/builtins.
        # Prefer numeric form when the value looks like a number (AHK expression rules).
        def replace_bare(match):
            name = match.group(0)

            # Function names must NEVER be replaced by variable values.
            # AHK function names are case-insensitive.
            eval_namespace = self._get_eval_namespace()

            for func_name, func in eval_namespace.items():
                if func_name.lower() == name.lower() and callable(func):
                    return func_name

            # Built-in constants / variables
            if name in self.variables:
                val = self.variables[name]
                coerced = self._try_number(val)

                if isinstance(coerced, str):
                    return repr(coerced)

                if isinstance(coerced, float) and coerced == int(coerced):
                    return str(int(coerced))

                return str(coerced)

            if name in self.builtin_variables:
                val = self.builtin_variables[name]
                coerced = self._try_number(val)

                if isinstance(coerced, str):
                    return repr(coerced)

                if isinstance(coerced, float) and coerced == int(coerced):
                    return str(int(coerced))

                return str(coerced)

            # Python/boolean/logical keywords remain untouched.
            return name
        # Convert AHK backslash paths to Python-safe strings
        condition = re.sub(
            r'"([^"]*?)\\([^"]*?)"',
            lambda m: '"' + m.group(1) + r'\\' + m.group(2) + '"',
            condition
        )
        # Coerce numeric-looking string literals so "1" > 2 works
        condition = self._coerce_numeric_literals(condition)
        try:
            return bool(self._safe_eval(condition))
        except Exception as e:
            full_error = traceback.format_exc()
            print(full_error)
            # On unrecoverable error treat condition as False rather than crashing
            # (keeps macros running; previous stub simply returned None)
            return False

    def _normalize_inline_else_lines(self, actions):
        normalized = []
        for action in actions:
            stripped = action.strip()
            lower = stripped.lower()
            if lower.startswith("} else") or lower.startswith("}else"):
                normalized.append("}")
                normalized.append(stripped[1:].strip())
            else:
                normalized.append(action)
        return normalized

    def _normalize_condition(self, condition):
        # AHK operators
        condition = condition.replace("<>", "!=")
        condition = condition.replace("||", " or ")
        condition = condition.replace("&&", " and ")
        # !expression -> not expression
        condition = re.sub(r'!(?!=)', 'not ', condition)
        # = -> ==
        condition = re.sub(r'(?<![<>=!:])=(?!=)', '==', condition)
        return condition

    def _evaluate_loop_count(self, line):
        """
        Evaluates:
            Loop
            Loop, 5
            Loop, %Amount%
            Loop, Amount
            Loop, InStr(...)
            Loop, Round(...)
            Loop, 2+3
        """
        parts = line.split(",", 1)
        # Infinite/default loop
        if len(parts) < 2:
            return 1

        expr = parts[1].replace("{", "").strip()
        # Resolve %Var%
        expr = self._handle_variable(expr)
        try:
            # AHK-compatible coercion so Loop, "5" or Loop, Amount works when Amount is str
            value = self._safe_eval(expr)
            return int(value)

        except Exception as e:
            full_error = traceback.format_exc()
            error = full_error.splitlines()
            try:
                messagebox.showerror("title", f"Invalid Loop Count: {e}\n\nLine text: {error[5]}\n{error[7]}\n\nThe program will exit")
            except:
                messagebox.showerror("title", f"Invalid Loop Count: {e}\n\nLine text: {error[2]}\n{error[4]}\n\nThe program will exit")
            return 1

    def _parse_loop_type(self, line):
        """
        Determines the type of Loop command.
        Returns: (loop_type, file_pattern_or_expr, mode)
        loop_type: "files" or "count"
        """
        line_stripped = line.strip()
        if not line_stripped.lower().startswith("loop"):
            return "count", "", ""

        # Split into at most 4 parts: Loop, Type, Pattern, Mode
        parts = [p.strip() for p in line_stripped.split(",", 3)]
        if len(parts) < 2:
            return "count", "", ""

        second_part = parts[1].lower()
        if second_part == "files":
            file_pattern = parts[2] if len(parts) > 2 else ""
            mode = parts[3] if len(parts) > 3 else ""
            return "files", file_pattern, mode

        # Future: could detect "read", "parse", "reg" here
        return "count", "", ""

    def _set_file_loop_variables(self, filepath):
        """
        Sets AHK v1 style A_LoopFile* variables for the current iteration.
        Cross-platform compatible.
        """
        if not filepath:
            return

        try:
            if not os.path.exists(filepath):
                return

            abspath = os.path.abspath(filepath)
            basename = os.path.basename(abspath)
            dirname = os.path.dirname(abspath)
            name_part, ext_part = os.path.splitext(basename)
            self.builtin_variables["A_LoopFileName"] = basename
            self.builtin_variables["A_LoopFileFullPath"] = abspath
            self.builtin_variables["A_LoopFileLongPath"] = abspath
            self.builtin_variables["A_LoopFileDir"] = dirname
            self.builtin_variables["A_LoopFileExt"] = ext_part[1:] if ext_part.startswith(".") else ext_part
            stat = os.stat(filepath)
            self.builtin_variables["A_LoopFileSize"] = stat.st_size
            self.builtin_variables["A_LoopFileSizeKB"] = int(stat.st_size / 1024) if stat.st_size > 0 else 0
            self.builtin_variables["A_LoopFileSizeMB"] = int(stat.st_size / (1024 * 1024)) if stat.st_size > 0 else 0
            # AHK datetime format: YYYYMMDDHH24MISS
            def _format_ahk_time(ts):
                try:
                    return time.strftime("%Y%m%d%H%M%S", time.localtime(ts))

                except Exception:
                    return ""

            self.builtin_variables["A_LoopFileTimeModified"] = _format_ahk_time(stat.st_mtime)
            # st_birthtime may not exist on all platforms (Linux), fallback to ctime
            birth_ts = getattr(stat, "st_birthtime", stat.st_ctime)
            self.builtin_variables["A_LoopFileTimeCreated"] = _format_ahk_time(birth_ts)
            self.builtin_variables["A_LoopFileTimeAccessed"] = _format_ahk_time(stat.st_atime)
            # Basic attrib
            if os.path.isdir(filepath):
                self.builtin_variables["A_LoopFileAttrib"] = "D"
            else:
                self.builtin_variables["A_LoopFileAttrib"] = "A"
        except Exception as e:
            # Non-fatal: continue execution even if stat fails for one file
            messagebox.showwarning("Warning", f"Warning setting A_LoopFile* for {filepath}:\n{e}")
    def scan_functions(self, actions):
        self.functions.clear()
        self.labels.clear()
        # Clear static hotkeys; dynamic ones registered later via Hotkey command will re-populate self.hotkeys
        self.hotkeys.clear()
        self.current_line_count = 0
        while self.current_line_count < len(actions):
            line = self._strip_inline_comment(actions[self.current_line_count].strip())
            # Function definition
            if self._is_function_definition(line):
                name = line.split("(", 1)[0].strip()
                body, end_index = self._extract_block(actions, self.current_line_count)
                self.functions[name] = body
                # Skip the function body so sequential execution does not run it
                self.current_line_count = end_index
            # Label definition
            elif self._is_label_definition(line):
                name = line.rstrip(":").strip()  # Remove one or more trailing colons
                body_lines, end_index = self._extract_label_block(
                    actions,
                    self.current_line_count + 1
                )
                self.labels[name] = body_lines
                # Skip the label body
                self.current_line_count = end_index
            # Hotkey Labels  (e.g. F1::  or  ^!s:: )
            else:
                m = re.match(r"^([^\s:]+)::$", line)
                if m:
                    key = m.group(1).upper()
                    body_lines, end_index = self._extract_label_block(
                        actions,
                        self.current_line_count + 1
                    )
                    normalized_key = self._normalize_hotkey_name(key)
                    # Static hotkey: store body lines; on press we execute them directly
                    self.hotkeys[normalized_key] = body_lines
                    # Skip the hotkey body during sequential execution
                    self.current_line_count = end_index
            self.current_line_count = self.current_line_count + 1

    def _is_function_definition(self, line):
        "Detects AHK functions"
        function2 = False
        if line.endswith(") {"):
            if not "if" in line:
                function2 = True
        return function2

    def _is_label_definition(self, line):
        """
        Detects AHK labels:
            MyLabel:
        """
        return bool(re.match(r"^[A-Za-z_]\w*:$", line.strip()))

    def execute_gosub(self, label_name):
        """
        Execute a label (Gosub, LabelName)
        """
        if label_name in self.labels:
            saved_line = self.current_line_count
            self._execute_script(self.labels[label_name])
            self.current_line_count = saved_line + 1
        else:
            messagebox.showerror("title", f"Error: Call to nonexistent function\nSpecifically: {label_name}\n\n--->    {self.current_line_count}: {self.script[self.current_line_count - 1]}\n\nThe program will exit")
            raise NameError(label_name)

    def _extract_label_block(self, actions, start):
        body = []
        i = start
        while i < len(actions):
            line = actions[i].strip()
            # End of label
            if line.lower() == "return":
                return body, i

            # Another label starts
            if self._is_label_definition(line):
                return body, i - 1

            body.append(actions[i])
            i += 1
        return body, i

    def read_ini(self, filename):
        for encoding in ("utf-8-sig", "utf-8", "utf-16", "cp1252"):
            try:
                with open(filename, "r", encoding=encoding) as f:
                    return f.readlines()

            except UnicodeError:
                pass

        raise UnicodeError(f"Unable to read {filename}")

    def capture_single_frame(self):
        """
        Capture a single full-screen frame.
        Used by debug screenshots, eyedropper freeze, and Discord screenshot logging.
        """
        if sys.platform == "darwin":
            image = Quartz.CGWindowListCreateImage(
                Quartz.CGRectInfinite,
                Quartz.kCGWindowListOptionOnScreenOnly,
                Quartz.kCGNullWindowID,
                Quartz.kCGWindowImageDefault
            )
            if image is None:
                return None

            return cgimage_to_srgb_numpy(image)

        else:
            scale = self._get_scale_factor()
            with MSS() as sct:
                monitor = {
                    "top": 0,
                    "left": 0,
                    "width": int(SCREEN_WIDTH * scale),
                    "height": int(SCREEN_HEIGHT * scale),
                }
                return np.asarray(sct.grab(monitor))[:, :, :3]

    def capture_loop_mss(self):
        """Continuous capture loop for the macro."""
        self.capture_id = 0
        scale = self._get_scale_factor()
        with MSS() as sct:
            monitor = {
                "top": 0,
                "left": 0,
                "width": int(SCREEN_WIDTH * scale),
                "height": int(SCREEN_HEIGHT * scale),
            }
            while True:
                self.capture_frame = np.asarray(sct.grab(monitor))[:, :, :3]
                self.capture_id += 1
                if time.monotonic() - self.last_scan_request > 1:
                    self.scan_delay = 1
                time.sleep(self.scan_delay)
    def capture_loop_quartz(self):
        """Continuous capture loop for the macro (macOS)."""
        self.capture_id = 0
        while True:
            if sys.platform == "darwin":
                image = Quartz.CGWindowListCreateImage(
                    Quartz.CGRectInfinite,
                    Quartz.kCGWindowListOptionOnScreenOnly,
                    Quartz.kCGNullWindowID,
                    Quartz.kCGWindowImageDefault
                )
            else:
                image = None
            if image is None:
                time.sleep(0.1)
                continue

            self.capture_frame = cgimage_to_srgb_numpy(image)
            self.capture_id += 1
            if time.monotonic() - self.last_scan_request > 1:
                self.scan_delay = 1
            time.sleep(self.scan_delay)
    def get_screen_dpi(self):
        if sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32
                if hasattr(user32, "GetDpiForSystem"):
                    screen_dpi = user32.GetDpiForSystem()
                else:
                    LOGPIXELSX = 88
                    hdc = user32.GetDC(0)
                    gdi32 = ctypes.windll.gdi32
                    screen_dpi = gdi32.GetDeviceCaps(hdc, LOGPIXELSX)
                    user32.ReleaseDC(0, hdc)
            except Exception:
                screen_dpi = 96
        else:
            screen_dpi = 96
        return screen_dpi

    def _get_eval_namespace(self):
        def RTrim(string, trim=" "):
            return string.rstrip(trim)

        def StrLen(string):
            return len(str(string))

        def InStr(haystack, needle, case_sensitive=False, starting_pos=1, occurrence=1):
            haystack = str(haystack)
            needle = str(needle)
            if not case_sensitive:
                haystack = haystack.lower()
                needle = needle.lower()
            start_idx = max(0, starting_pos - 1) if starting_pos > 0 else 0
            idx = haystack.find(needle, start_idx)
            return idx + 1 if idx != -1 else 0

        def SubStr(string, starting_pos, length=None):
            string = str(string)
            string_len = len(string)
            if starting_pos > 0:
                start = starting_pos - 1
            elif starting_pos < 0:
                start = string_len + starting_pos
            else:
                start = 0
            if length is None:
                return string[start:]

            elif length > 0:
                return string[start:start + length]

            else:
                return string[start:string_len + length]

        def WinExist(window=""):
            """
            AHK-compatible WinExist() expression function.

            Returns the matching window's HWND when a window is found,
            or 0 when no matching window exists.
            """
            window = self._handle_variable(str(window))
            info = self._find_window(window)

            if info is None:
                return 0

            return info.get("hwnd", 0) or 0

        def GetKeyState(key, mode=""):
            """
            Basic AHK-compatible GetKeyState().

            Returns True when the requested key/button is currently pressed.
            For physical-state mode ("P"), use the current physical state.
            """
            key = str(key).strip().lower()

            try:
                if key in ("lbutton", "left"):
                    if sys.platform == "win32":
                        return bool(
                            ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON) & 0x8000
                        )

                    elif sys.platform == "darwin":
                        return bool(
                            Quartz.CGEventSourceButtonState(
                                Quartz.kCGEventSourceStateCombinedSessionState,
                                LEFT_BUTTON
                            )
                        )

                    elif sys.platform.startswith("linux"):
                        if X11 is None:
                            return False

                        # XQueryPointer returns the current mouse-button mask.
                        class Display(ctypes.Structure):
                            pass

                        X11.XOpenDisplay.restype = ctypes.POINTER(Display)
                        X11.XOpenDisplay.argtypes = [ctypes.c_char_p]

                        display = X11.XOpenDisplay(None)

                        if not display:
                            return False

                        root = ctypes.c_ulong()
                        child = ctypes.c_ulong()
                        root_x = ctypes.c_int()
                        root_y = ctypes.c_int()
                        win_x = ctypes.c_int()
                        win_y = ctypes.c_int()
                        mask = ctypes.c_uint()

                        X11.XQueryPointer(
                            display,
                            ctypes.c_ulong(0),
                            ctypes.byref(root),
                            ctypes.byref(child),
                            ctypes.byref(root_x),
                            ctypes.byref(root_y),
                            ctypes.byref(win_x),
                            ctypes.byref(win_y),
                            ctypes.byref(mask),
                        )

                        # Button1Mask = 0x100
                        return bool(mask.value & 0x100)

            except Exception:
                pass

            return False

        # Build the namespace so user variables cannot overwrite
        # built-in AHK functions such as Round(), InStr(), WinExist(), etc.
        namespace = {
            **self.builtin_variables,
            **self.variables,
            "A_TickCount": int(time.monotonic() * 1000),

            # AHK functions
            "RTrim": RTrim,
            "InStr": InStr,
            "SubStr": SubStr,
            "StrLen": StrLen,
            "Round": round,
            "Abs": abs,
            "Min": min,
            "Max": max,
            "Ceil": lambda x: math.ceil(float(x)),
            "Floor": lambda x: math.floor(float(x)),
            "Sqrt": lambda x: math.sqrt(float(x)),
            "Mod": lambda x, y: float(x) % float(y),
            "StrReplace": lambda s, t, r="": str(s).replace(str(t), str(r)),
            "Trim": lambda s: str(s).strip(),
            "Chr": lambda n: chr(int(n)),
            "Ord": lambda c: ord(str(c)[0]) if c else 0,
            "IsInteger": lambda v: (
                isinstance(v, int)
                or (isinstance(v, str) and v.isdigit())
            ),
            "IsNumber": lambda v: (
                str(v).replace(".", "", 1).isdigit()
            ),
            "WinExist": WinExist,
            "GetKeyState": GetKeyState,
        }

        return namespace
    def _handle_assignment(self, action):
        """
        Split the value and the target variables, then update the value based on the target variable.
        Handles: x := 612, y := ABC
        Returns: True if variable found in action or False if not.
        """
        if ":=" in action:
            var, value = action.split(":=", 1)
            var = var.strip()
            value = value.strip()
            # Prevent overwriting built-ins
            if var in self.builtin_variables:
                messagebox.showerror("title", f"Error at line {self.current_line_count + 1}\n\nLine text: {action}\nError: Cannot overwrite built-in variable: {var}\n\nThe program will exit")
                raise NameError(f"Cannot overwrite built-in variable: '{var}'")

            # Convert common AHK syntax into Python syntax first
            expr = value
            # AHK string concatenation -> Python
            # (Note: pure string concat via "." becomes "+" ; numeric coercion
            #  will turn non-numeric strings into 0, matching AHK math rules.
            #  Use .= for true string append.)
            expr = re.sub(r"\s+\.\s+", " + ", expr)
            # Escape backslashes inside quoted strings
            def escape_string(match):
                text = match.group(0)
                return text.replace("\\", "\\\\")

            expr = re.sub(r'"[^"]*"', escape_string, expr)
            try:
                # Use AHK-compatible eval so "1" + 1 → 2, mixed types coerce
                self.variables[var] = self._safe_eval(expr)
            except Exception as e:
                full_error = traceback.format_exc()
                print(full_error)
                # Fallback: store the raw right-hand side as a string
                self.variables[var] = value
            return True

        if ".=" in action:
            var, rhs = action.split(".=", 1)
            var = var.strip()
            rhs = rhs.strip()
            # Resolve %Var% references first
            rhs = self._handle_variable(rhs)
            try:
                # Valid Python expression?
                rhs = eval(rhs, {}, self._get_eval_namespace())
            except Exception:
                # AHK-style concatenation (e.g. FileName "|" Var2)
                result = ""
                tokens = re.findall(
                    r'"[^"]*"|\'[^\']*\'|[A-Za-z_]\w*|\S',
                    rhs
                )
                for token in tokens:
                    if token.startswith('"') or token.startswith("'"):
                        # String literal
                        result += token[1:-1]
                    elif token in self.variables:
                        result += str(self.variables[token])
                    elif token in self.builtin_variables:
                        result += str(self.builtin_variables[token])
                    else:
                        # Operators/punctuation/literal text
                        result += token
                rhs = result
            self.variables[var] = str(self.variables.get(var, "")) + str(rhs)
            return True

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
                    # AHK-compatible: "1" * 2 → 2.0, non-numeric → 0
                    rhs_val = float(self._safe_eval(rhs))
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

    def _handle_variable(self, text):
        "Handles %Var%"
        if not isinstance(text, str):
            return text

        def replacer(match):
            var_name = match.group(1)
            # Priority: user variables
            if var_name in self.variables:
                return str(self.variables[var_name])

            # Then builtin variables
            if var_name in self.builtin_variables:
                return str(self.builtin_variables[var_name])

            return ""  # or keep original if you prefer strict mode

        return re.sub(r"%(\w+)%", replacer, text)

    def _resolve_value(self, value):
        "Handles Var"
        if not isinstance(value, str):
            return value

        value = value.strip()
        # Direct variable lookup (PixelSearch, MouseMove, etc.)
        if value in self.variables:
            return self.variables[value]

        if value in self.builtin_variables:
            return self.builtin_variables[value]

        # Then resolve any %var% references inside strings
        return self._handle_variable(value)

    def _parse_ahk_color(self, color):
        """
        Convert AHK color (0xBBGGRR) or standard hex (#RRGGBB) to RGB tuple.
        """
        if not color:
            return None, None, None

        color = color.strip().lower()
        try:
            # --- AHK format: 0xBBGGRR ---
            if color.startswith("0x"):
                value = int(color, 16)
                b = (value >> 16) & 0xFF
                g = (value >> 8) & 0xFF
                r = value & 0xFF
                return r, g, b  # ✅ RGB

            # --- Standard hex: #RRGGBB ---
            if color.startswith("#"):
                color = color[1:]
                r = int(color[0:2], 16)
                g = int(color[2:4], 16)
                b = int(color[4:6], 16)
                return r, g, b

        except Exception:
            return None, None, None

        return None, None, None

    def _find_first_pixel(self, frame, hex, tolerance=8):
        if frame is None or frame.size == 0:
            return None, None

        try:
            tolerance = int(np.clip(tolerance, 0, 255))
            b, g, r = self._parse_ahk_color(hex)
            target = np.array([b, g, r], dtype=np.int32)
            frame_i = frame.astype(np.int32)
            diff = frame_i - target
            mask = np.sqrt(np.sum(diff ** 2, axis=-1)) <= tolerance
            coords = np.argwhere(mask)
            if coords.size > 0:
                y, x = coords[0]
                return int(x), int(y)
            return None, None
        except:
            return None, None

    # ── Window commands (WinExist / WinActivate / WinGetPos) ──────────────────
    def _parse_window_criteria(self, criteria):
        """
        Parse AHK-style window matching criteria.
        Returns dict with keys: title, exe, class_name, hwnd
        Examples:
            "Roblox"
            "ahk_exe RobloxPlayerBeta.exe"
            "My Title ahk_exe notepad.exe"
            "ahk_class Notepad"
        """
        criteria = str(criteria or "").strip().strip('"').strip("'")
        result = {
            "title": None,
            "exe": None,
            "class_name": None,
            "hwnd": None,
        }
        if not criteria:
            return result

        # Extract ahk_ tokens (order independent)
        remaining = criteria
        # ahk_exe
        m = re.search(r"\bahk_exe\s+([^\s]+)", remaining, re.IGNORECASE)
        if m:
            result["exe"] = m.group(1)
            remaining = remaining[:m.start()] + remaining[m.end():]
        # ahk_class
        m = re.search(r"\bahk_class\s+([^\s]+)", remaining, re.IGNORECASE)
        if m:
            result["class_name"] = m.group(1)
            remaining = remaining[:m.start()] + remaining[m.end():]
        # ahk_id (hwnd)
        m = re.search(r"\bahk_id\s+([^\s]+)", remaining, re.IGNORECASE)
        if m:
            try:
                result["hwnd"] = int(m.group(1), 0)  # accept hex or decimal
            except ValueError:
                pass

            remaining = remaining[:m.start()] + remaining[m.end():]
        # Whatever is left is treated as title (partial match)
        title = remaining.strip()
        if title:
            result["title"] = title
        return result

    def _window_matches(self, info, criteria):
        """
        info: dict with at least title, exe, class_name, hwnd (platform normalised)
        criteria: from _parse_window_criteria
        """
        if criteria.get("hwnd") is not None:
            if info.get("hwnd") != criteria["hwnd"]:
                return False

        if criteria.get("exe"):
            want = criteria["exe"].lower()
            # Allow matching with or without .exe
            if want.endswith(".exe"):
                want_base = want[:-4]
            else:
                want_base = want
            have = (info.get("exe") or "").lower()
            have_base = have[:-4] if have.endswith(".exe") else have
            if want not in have and want_base not in have_base and have_base not in want_base:
                return False

        if criteria.get("class_name"):
            if (info.get("class_name") or "").lower() != criteria["class_name"].lower():
                return False

        if criteria.get("title"):
            title = (info.get("title") or "")
            # AHK default: partial, case-insensitive
            if criteria["title"].lower() not in title.lower():
                return False

        # If no criteria at all were given, match nothing (or everything? AHK matches last found)
        # Require at least one criterion to have been specified
        if not any([criteria.get("title"), criteria.get("exe"),
                    criteria.get("class_name"), criteria.get("hwnd") is not None]):
            return False

        return True

    def _list_windows(self):
        """
        Return a list of window info dicts for the current platform.
        Each dict: {hwnd, title, exe, class_name, left, top, width, height}
        """
        windows = []
        if sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32
                kernel32 = ctypes.windll.kernel32
                EnumWindows = user32.EnumWindows
                EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
                GetWindowText = user32.GetWindowTextW
                GetWindowTextLength = user32.GetWindowTextLengthW
                IsWindowVisible = user32.IsWindowVisible
                GetClassName = user32.GetClassNameW
                GetWindowRect = user32.GetWindowRect
                GetWindowThreadProcessId = user32.GetWindowThreadProcessId
                # Try to resolve process image name
                try:
                    QueryFullProcessImageNameW = kernel32.QueryFullProcessImageNameW
                    OpenProcess = kernel32.OpenProcess
                    CloseHandle = kernel32.CloseHandle
                    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                    has_query = True
                except AttributeError:
                    has_query = False
                def get_exe(pid):
                    if not has_query or not pid:
                        return ""

                    h = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
                    if not h:
                        return ""

                    try:
                        buf = ctypes.create_unicode_buffer(1024)
                        size = wintypes.DWORD(1024)
                        if QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
                            path = buf.value
                            return os.path.basename(path)

                    finally:
                        CloseHandle(h)
                    return ""

                def callback(hwnd, lParam):
                    if not IsWindowVisible(hwnd):
                        return True

                    length = GetWindowTextLength(hwnd)
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buff, length + 1)
                    title = buff.value
                    class_buf = ctypes.create_unicode_buffer(256)
                    GetClassName(hwnd, class_buf, 256)
                    class_name = class_buf.value
                    rect = wintypes.RECT()
                    GetWindowRect(hwnd, ctypes.byref(rect))
                    left, top = rect.left, rect.top
                    width = rect.right - rect.left
                    height = rect.bottom - rect.top
                    pid = wintypes.DWORD()
                    GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                    exe = get_exe(pid.value)
                    windows.append({
                        "hwnd": int(hwnd),
                        "title": title,
                        "exe": exe,
                        "class_name": class_name,
                        "left": left,
                        "top": top,
                        "width": width,
                        "height": height,
                    })
                    return True

                EnumWindows(EnumWindowsProc(callback), 0)
            except Exception:
                pass

        elif sys.platform == "darwin":
            try:
                options = (Quartz.kCGWindowListOptionOnScreenOnly |
                           Quartz.kCGWindowListExcludeDesktopElements)
                window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)
                if window_list:
                    for win in window_list:
                        owner = win.get(Quartz.kCGWindowOwnerName, "") or ""
                        title = win.get(Quartz.kCGWindowName, "") or ""
                        bounds = win.get(Quartz.kCGWindowBounds, {})
                        hwnd = win.get(Quartz.kCGWindowNumber, 0)
                        windows.append({
                            "hwnd": int(hwnd) if hwnd else 0,
                            "title": title,
                            "exe": owner,          # process name acts as "exe"
                            "class_name": "",
                            "left": int(bounds.get("X", 0)),
                            "top": int(bounds.get("Y", 0)),
                            "width": int(bounds.get("Width", 0)),
                            "height": int(bounds.get("Height", 0)),
                        })
            except Exception:
                pass

        elif sys.platform.startswith("linux"):
            try:
                d = Xdisplay.Display()
                root = d.screen().root
                window_ids = root.get_full_property(
                    d.intern_atom("_NET_CLIENT_LIST"), X.AnyPropertyType
                )
                if window_ids:
                    for wid in window_ids.value:
                        try:
                            win = d.create_resource_object("window", wid)
                            # Title
                            title = ""
                            try:
                                wm_name = win.get_wm_name()
                                if wm_name:
                                    title = wm_name if isinstance(wm_name, str) else str(wm_name)
                            except Exception:
                                pass

                            # Class / instance
                            class_name = ""
                            exe = ""
                            try:
                                wm_class = win.get_wm_class()
                                if wm_class:
                                    class_name = wm_class[1] if len(wm_class) > 1 else wm_class[0]
                                    exe = wm_class[0] if wm_class else ""
                            except Exception:
                                pass

                            # Geometry
                            geom = win.get_geometry()
                            # Translate to root coordinates
                            try:
                                abs_coords = root.translate_coords(win, 0, 0)
                                left, top = abs_coords.x, abs_coords.y
                            except Exception:
                                left, top = geom.x, geom.y
                            windows.append({
                                "hwnd": int(wid),
                                "title": title or "",
                                "exe": exe or "",
                                "class_name": class_name or "",
                                "left": left,
                                "top": top,
                                "width": geom.width,
                                "height": geom.height,
                            })
                        except Exception:
                            continue

                d.close()
            except Exception:
                pass

        return windows

    def _find_window(self, criteria_str):
        """Find the first matching window. Returns info dict or None."""
        criteria = self._parse_window_criteria(criteria_str)
        for info in self._list_windows():
            if self._window_matches(info, criteria):
                return info

        return None

    def win_exist(self, criteria=""):
        """AHK-compatible WinExist. Returns True if a matching window is found."""
        return self._find_window(criteria) is not None

    def _normalize_pynput_key(self, key):
        """Convert a pynput key event to an AHK-style uppercase key name (F1, A, SPACE, etc.)."""
        try:
            if key is None:
                return None

            if hasattr(key, "char") and key.char is not None:
                char = key.char
                if char in {"\r", "\n"}:
                    return "ENTER"

                if char == " ":
                    return "SPACE"

                return char.upper()

            name = str(key).replace("Key.", "").upper()
            aliases = {
                "SPACE": "SPACE",
                "ENTER": "ENTER",
                "RETURN": "ENTER",
                "ESC": "ESCAPE",
                "ESCAPE": "ESCAPE",
                "BACKSPACE": "BACKSPACE",
                "TAB": "TAB",
                "SHIFT": "SHIFT",
                "CTRL": "CTRL",
                "CONTROL": "CTRL",
                "CTRL_L": "CTRL",
                "CTRL_R": "CTRL",
                "ALT": "ALT",
                "ALT_L": "ALT",
                "ALT_R": "ALT",
                "CMD": "LWIN",
                "CMD_L": "LWIN",
                "CMD_R": "RWIN",
                "SUPER": "LWIN",
                "SUPER_L": "LWIN",
                "SUPER_R": "RWIN",
                "LEFT": "LEFT",
                "RIGHT": "RIGHT",
                "UP": "UP",
                "DOWN": "DOWN",
                "PAGEUP": "PGUP",
                "PAGEDOWN": "PGDN",
                "HOME": "HOME",
                "END": "END",
                "INSERT": "INSERT",
                "DELETE": "DELETE",
                "CAPSLOCK": "CAPSLOCK",
            }
            return aliases.get(name, name)

        except Exception:
            return None

    def _normalize_hotkey_name(self, key_name):
        """Normalize AHK-style hotkey names so they can be compared with pynput events."""
        if key_name is None:
            return ""

        raw = str(key_name).strip().replace(" ", "")
        if not raw:
            return ""

        modifiers = []
        main_parts = []
        i = 0
        while i < len(raw):
            ch = raw[i]
            if ch == "^":
                modifiers.append("CTRL")
                i += 1
            elif ch == "!":
                modifiers.append("ALT")
                i += 1
            elif ch == "+":
                modifiers.append("SHIFT")
                i += 1
            elif ch == "#":
                modifiers.append("LWIN")
                i += 1
            else:
                j = i
                while j < len(raw) and raw[j] not in "^!+#":
                    j += 1
                token = raw[i:j].upper()
                if token in {"CTRL", "CONTROL", "CTL"}:
                    modifiers.append("CTRL")
                elif token in {"ALT"}:
                    modifiers.append("ALT")
                elif token in {"SHIFT"}:
                    modifiers.append("SHIFT")
                elif token in {"WIN", "LWIN", "RWIN", "SUPER", "LSUPER", "RSUPER"}:
                    modifiers.append("LWIN")
                else:
                    main_parts.append(token)
                i = j
        if not main_parts:
            return "+".join(modifiers)

        main = "".join(main_parts)
        if not modifiers:
            return main

        return "+".join(modifiers + [main])

    def on_key_press(self, key):
        """Dispatch a registered hotkey when a pynput key press matches a known binding."""
        normalized = self._normalize_pynput_key(key)
        if normalized is None:
            return

        for hotkey, label in self.hotkeys.items():
            if label in self.labels:
                self.execute_gosub(label)
    def on_key_release(self, key):
        """Clear active modifiers when a modifier key is released."""
        pass

    def cmd_splitpath(self, line):
        """
        SplitPath, InputVar, OutFileName, OutDir, OutExtension, OutNameNoExt, OutDrive
        Examples:
            SplitPath, A_LoopFileName,,, Extension, FileName
        """
        parts = [p.strip() for p in line.split(",")]
        parts = parts[1:]
        # Pad missing parameters
        while len(parts) < 6:
            parts.append("")
        input_path, out_file, out_dir, out_ext, out_name, out_drive = parts[:6]
        # Remove surrounding quotes if present
        input_path2 = input_path.strip('"').strip("'")
        if input_path2 == input_path:
            input_path = f"%{input_path}%"
        # Resolve variables like %A_LoopFileName%
        input_path = self._handle_variable(input_path)
        directory = os.path.dirname(input_path)
        filename = os.path.basename(input_path)
        name_no_ext, extension = os.path.splitext(filename)
        extension = extension.lstrip(".")
        drive, _ = os.path.splitdrive(input_path)
        # Assign only requested outputs
        if out_file:
            self.variables[out_file] = filename
        if out_dir:
            self.variables[out_dir] = directory
        if out_ext:
            self.variables[out_ext] = extension
        if out_name:
            self.variables[out_name] = name_no_ext
        if out_drive:
            self.variables[out_drive] = drive
    def cmd_guicontrol(self, action):
        parts = [x.strip() for x in action.split(",", 3)]

        # GuiControl, SubCommand, Control, Value
        while len(parts) < 4:
            parts.append("")

        _, subcommand, control, value = parts

        widget = self.gui_controls.get(control)

        if widget is None:
            return

        subcommand = subcommand.lower()

        if subcommand == "":
            # Set text/value (or image file for Picture/Image controls)
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, value)

            elif isinstance(widget, ttk.Combobox):
                widget.set(value)

            elif getattr(widget, "_is_gui_image", False):
                placement = self.gui_control_placements.get(control, {})
                photo = self._load_gui_image(
                    value,
                    placement.get("width", 0),
                    placement.get("height", 0),
                )
                if photo is not None:
                    widget.config(image=photo, text="")
                    widget.image = photo
                    self.gui_images[control] = photo

            elif isinstance(widget, tk.Label):
                widget.config(text=value)

            elif isinstance(widget, tk.Button):
                widget.config(text=value)

        elif subcommand == "enable":
            widget.configure(state="normal")

        elif subcommand == "disable":
            widget.configure(state="disabled")

        elif subcommand == "hide":
            widget.place_forget()

        elif subcommand == "show":
            placement = self.gui_control_placements.get(control)

            if placement is None:
                return

            place_kwargs = {
                "x": placement["x"],
                "y": placement["y"],
            }
            # Only apply size when the control was created with explicit w/h.
            # Text/Link/Checkbox often omit them; forcing 0 would collapse the widget.
            if placement.get("width"):
                place_kwargs["width"] = placement["width"]
            if placement.get("height"):
                place_kwargs["height"] = placement["height"]
            widget.place(**place_kwargs)

    def cmd_hotkey(self, action):
        """
        Emulate AHK Hotkey command (basic On/Off support):
            Hotkey, %StartKey%, StartMacro, On
            Hotkey, %StopKey%, StopMacro, Off
        Syntax supported:
            Hotkey, KeyName, LabelName, On|Off
            Hotkey, KeyName, LabelName  (defaults to On)
        """
        if "," not in action:
            return

        _, rest = action.split(",", 1)
        parts = [p.strip() for p in rest.split(",")]
        while len(parts) < 3:
            parts.append("")
        key_name = parts[0].upper()
        label_name = parts[1]
        state = parts[2].lower() if parts[2] else "on"
        if not key_name:
            return

        normalized_key = self._normalize_hotkey_name(key_name)
        if state in ("on", "1", "true", "toggle"):
            self.hotkeys[normalized_key] = label_name
        elif state in ("off", "0", "false"):
            try:
                del self.hotkeys[normalized_key]
            except:
                pass
    def cmd_pixelsearch(self, line):
        self.last_scan_request = time.monotonic()
        self.scan_delay = 0.01
        _, args = line.split(",", 1)
        parts = [p.strip() for p in args.split(",")]
        out_x = parts[0]
        out_y = parts[1]
        left = int(float(self._resolve_value(parts[2])))
        top = int(float(self._resolve_value(parts[3])))
        right = int(float(self._resolve_value(parts[4])))
        bottom = int(float(self._resolve_value(parts[5])))
        color = parts[6]
        # Strip trailing AHK options like "Fast", "RGB"
        tolerance = 8
        if len(parts) > 7:
            try:
                tolerance = int(float(parts[7]))
            except:
                tolerance = 8
        color = self._resolve_value(color)
        tolerance = self._resolve_value(tolerance)
        mode_flags = [p.lower() for p in parts[8:]]
        fast_mode = "fast" in mode_flags
        rgb_mode = "rgb" in mode_flags
        scale = get_scale_factor()
        if color.startswith("0x"):
            if rgb_mode == True: # Use 0xRRGGBB directly
                parsed_color = "#" + color[1:]
            elif rgb_mode == False: # Convert 0xBBGGRR to #RRGGBB
                parsed_color = self._parse_ahk_color(color)
        else:
            parsed_color = None
        img = self.capture_frame[top:bottom, left:right]
        if parsed_color is None:
            self.variables[out_x] = -1
            self.variables[out_y] = -1
            self.variables["ErrorLevel"] = 1
            return

        x, y = self._find_first_pixel(img, parsed_color, tolerance)
        if x is not None and y is not None:
            self.variables[out_x] = int((x + left) / scale)
            self.variables[out_y] = int((y + top) / scale)
            self.variables["ErrorLevel"] = 0
        else:
            self.variables[out_x] = -1
            self.variables[out_y] = -1
            self.variables["ErrorLevel"] = 1
        return

    def _cmd_pixelgetcolor(self, action):
        # AHK: PixelGetColor, OutputVar, X, Y [, RGB]
        try:
            _, args = action.split(",", 1)
            parts = [p.strip() for p in args.split(",")]
            out_var = parts[0]
            x = int(float(parts[1]))
            y = int(float(parts[2]))
            # --- Grab frame: use capture thread if running, else one-shot ---
            if self.capture_running and hasattr(self, "_cap_lock"):
                if hasattr(self, "_cap_event"):
                    self._cap_event.wait(timeout=0.2)
                with self._cap_lock:
                    frame = self._cap_frame.copy() if self._cap_frame is not None else None
            else:
                thread_local = threading.local()
                frame = self._grab_screen_full(thread_local)
            if frame is None:
                self.variables[out_var] = 0
                self.variables["ErrorLevel"] = 1
                return
            h, w = frame.shape[:2]
            x = max(0, min(x, w - 1))
            y = max(0, min(y, h - 1))
            # frame is BGR (from mss): index [y, x] -> (B, G, R)
            b, g, r = int(frame[y, x, 0]), int(frame[y, x, 1]), int(frame[y, x, 2])
            # AHK PixelGetColor returns 0xBBGGRR
            color_val = (b << 16) | (g << 8) | r
            self.variables[out_var] = f"0x{color_val:06X}"
            self.variables["ErrorLevel"] = 0
        except Exception as e:
            self.raise_error(action, str(e))

    def _send_key(self, key2, backend2, delay2=0.05, click_type=0):
        """
        Send a keyboard event.
        delay: Delay between send and release
        click_type:
            0 = click (press + release)   [default]
            1 = hold (press only)
            2 = release (release only)
        """
        if self.macro_running == False:
            return

        key = str(key2)
        backend = backend2.lower()
        try:
            delay = abs(float(delay2))
        except:
            delay = 0.1
        if backend == "Input":
            send_key(key, delay=delay, click_type=click_type)
        elif backend == "Event":
            # Convert special key names
            special_keys = {
                "enter": Key.enter,
                "return": Key.enter,
                "tab": Key.tab,
                "space": Key.space,
                "esc": Key.esc,
                "escape": Key.esc,
                "backspace": Key.backspace,
                "delete": Key.delete,
                "up": Key.up,
                "down": Key.down,
                "left": Key.left,
                "right": Key.right,
            }
            key = special_keys.get(key.lower(), key)
            try:
                if click_type == 0:
                    keyboard_controller.press(key)
                    time.sleep(delay)
                    keyboard_controller.release(key)
                elif click_type == 1:
                    keyboard_controller.press(key)
                elif click_type == 2:
                    keyboard_controller.release(key)
            except Exception as e:
                print("Error sending keys:", e)
        elif backend == "Play":
            try:
                if click_type == 0:
                    pyautogui.keyDown(key)
                    time.sleep(delay)
                    pyautogui.keyUp(key)
                elif click_type == 1:
                    pyautogui.keyDown(key)
                elif click_type == 2:
                    pyautogui.keyUp(key)
            except Exception as e:
                print("Error sending keys with PyAutoGUI:", e)
    def _click_at(self, x, y, backend, button="left", action="click", click_count=1):
        if self.macro_running == False:
            return

        # Convert coordinates if needed (Retina scaling)
        if x is not None and y is not None:
            if sys.platform == "darwin":
                scale = get_scale_factor()
                x = int(x / scale)
                y = int(y / scale)
        # Resolve backend-specific button names.
        if backend == "Input":
            # Separate branches for Windows and macOS/Linux mouse events.
            if sys.platform == "win32":
                if x is not None and y is not None:
                    windll.SetCursorPos(x, y)
                    windll.mouse_event(MOUSEEVENTF_MOVE, 0, 1, 0, 0)
                button_flags = {
                    "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
                    "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
                    "middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
                }
                down_flag, up_flag = button_flags.get(
                    button,
                    button_flags["left"]
                )
                if action == "down":
                    windll.mouse_event(down_flag, 0, 0, 0, 0)
                elif action == "up":
                    windll.mouse_event(up_flag, 0, 0, 0, 0)
                else:
                    for i in range(click_count):
                        windll.mouse_event(down_flag, 0, 0, 0, 0)
                        windll.mouse_event(up_flag, 0, 0, 0, 0)
                        if i < click_count - 1:
                            time.sleep(0.03)
            else:
                if x is not None and y is not None:
                    _move_mouse(x, y)
                    _move_mouse(x + 2, y + 2)
                    _move_mouse(x, y)
                if action == "down":
                    _mouse_event(button=button, press=True)
                elif action == "up":
                    _mouse_event(button=button, press=False)
                else:
                    for i in range(click_count):
                        _mouse_event(button=button, press=True)
                        _mouse_event(button=button, press=False)
                        if i < click_count - 1:
                            time.sleep(0.03)
        elif backend == "Event":
            if x is not None and y is not None:
                mouse_controller.position = (x, y)
            button_map = {
                "left": mouse.Button.left,
                "right": mouse.Button.right,
                "middle": mouse.Button.middle,
            }
            mouse_button = button_map.get(
                button,
                mouse.Button.left
            )
            if action == "down":
                mouse_controller.press(mouse_button)
            elif action == "up":
                mouse_controller.release(mouse_button)
            else:
                for i in range(click_count):
                    mouse_controller.click(mouse_button)
                    if i < click_count - 1:
                        time.sleep(0.03)
        elif backend == "Play":
            if x is not None and y is not None:
                pyautogui.moveTo(x, y)
            if action == "down":
                pyautogui.mouseDown(button=button)
            elif action == "up":
                pyautogui.mouseUp(button=button)
            else:
                for i in range(click_count):
                    pyautogui.click(button=button)
                    if i < click_count - 1:
                        time.sleep(0.03)
    def _cmd_send(self, action):
        """
        Parse AHK "Send" format into key, delay, and click type
        Supports:
        Send, 67
        Send, D
        Send, {Down}
        Send, {W down}
        """
        try:
            # Split off the command name; args may be empty
            if "," in action:
                _, args = action.split(",", 1)
                parts = [p.strip() for p in args.split(",")]
            else:
                parts = []
            if parts[0] == "SendMode":
                backend = parts[1]
                self.send_backend = backend
                return

            if parts[0] == "Send":
                backend = self.send_backend # "Event" by default
            elif parts[0] == "SendInput":
                backend = "Input"
            elif parts[0] == "SendEvent":
                backend = "Event"
            elif parts[0] == "SendPlay":
                backend = "Play"
            click_type = 0 # Temporary
            self._send_key(parts[1], backend, self.key_delay, click_type)
        except:
            pass

        return

    def _cmd_click(self, action):
        """
        Parse AHK Click syntax and pass the resolved values to _click_at().
        Supported forms:
          Click
          Click, X, Y
          Click, X, Y, Down
          Click, X, Y, Up
          Click, X, Y, Right
          Click, X, Y, Down Right
          Click, Down Right
          Click, X, Y, Middle
        """
        try:
            # Split off the command name; args may be empty
            if "," in action:
                _, args = action.split(",", 1)
                parts = [p.strip() for p in args.split(",")]
            else:
                parts = []
            coords = []
            modifiers = []
            # Extract coordinates and modifier words.
            for p in parts:
                if not p:
                    continue

                try:
                    coords.append(int(float(p)))
                except ValueError:
                    for word in p.split():
                        modifiers.append(word.lower())
            # Resolve X/Y.
            if len(coords) >= 2:
                x, y = coords[0], coords[1]
            else:
                x, y = None, None
            # Resolve button.
            button = "left"
            for word in modifiers:
                if word in {"right", "r"}:
                    button = "right"
                elif word in {"middle", "m"}:
                    button = "middle"
                elif word in {"left", "l"}:
                    button = "left"
            # Resolve action.
            click_action = "click"
            for word in modifiers:
                if word == "down":
                    click_action = "down"
                elif word == "up":
                    click_action = "up"
            # SendMode determines the backend used by Click.
            backend = self.send_backend
            self._click_at(
                x,
                y,
                backend,
                button=button,
                action=click_action
            )
        except Exception as e:
            return e
    def _cmd_sleep(self, action):
        _, value = action.split(",", 1)
        ms = float(value.strip())   # float() accepts "400.0" and "400"
        time.sleep((ms / 1000))
    def _cmd_mousemove(self, action):
        _, args = action.split(",", 1)
        x, y = [int(v.strip()) for v in args.split(",")]
        mouse_controller.position = (x, y)
    def _cmd_mousegetpos(self, action):
        # AHK: MouseGetPos [, OutX, OutY]
        try:
            parts = []
            if "," in action:
                _, args = action.split(",", 1)
                parts = [p.strip() for p in args.split(",")]
            out_x = parts[0] if len(parts) > 0 else "MouseX"
            out_y = parts[1] if len(parts) > 1 else "MouseY"
            pos = mouse_controller.position
            self.variables[out_x] = int(pos[0])
            self.variables[out_y] = int(pos[1])
        except Exception as e:
            self.raise_error(action, str(e))
    def cmd_ini(self, action):
        parts = [x.strip() for x in action.split(",")]
        command = parts[0].lower()
        if command == "iniread":
            if len(parts) < 5:
                raise SyntaxError(f"{action}, IniRead requires OutputVar, Filename, Section, Key")

            output_var, filename, section, key = parts[1:5]
            default = parts[5] if len(parts) > 5 else "ERROR"
            # Resolve %Var% references in parameters (AHK style)
            filename = self._handle_variable(filename)
            section = self._handle_variable(section)
            key = self._handle_variable(key)
            default = self._handle_variable(default)
            # Strip surrounding quotes if present
            filename = filename.strip('"').strip("'")
            section = section.strip('"').strip("'")
            key = key.strip('"').strip("'")
            default = default.strip('"').strip("'")
            # Start with the default; only overwrite if the key is actually found
            value = default
            if os.path.exists(filename):
                try:
                    lines = self.read_ini(filename)
                except Exception:
                    lines = []
                current_section = None
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("[") and stripped.endswith("]"):
                        current_section = stripped[1:-1]
                        continue

                    if current_section != section:
                        continue

                    if "=" in stripped:
                        k, v = stripped.split("=", 1)
                        if k.strip() == key:
                            value = v.rstrip("\r\n")
                            break

            self.variables[output_var] = value
            return

        elif command == "iniwrite":
            if len(parts) < 5:
                raise SyntaxError("{action}: IniWrite requires Value, Filename, Section, Key")

            value, filename, section, key = parts[1:5]
            # Resolve %Var% references
            value = self._handle_variable(value)
            filename = self._handle_variable(filename)
            section = self._handle_variable(section)
            key = self._handle_variable(key)
            filename = filename.strip('"').strip("'")
            section = section.strip('"').strip("'")
            key = key.strip('"').strip("'")
            if os.path.exists(filename):
                lines = self.read_ini(filename)
            else:
                lines = []
            found_section = False
            written = False
            output = []
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                if stripped.startswith("[") and stripped.endswith("]"):
                    if found_section and not written:
                        output.append(f"{key}={value}\n")
                        written = True
                    current_section = stripped[1:-1]
                    found_section = (current_section == section)
                    output.append(line)
                    i += 1
                    continue

                if found_section and "=" in stripped:
                    k, _ = stripped.split("=", 1)
                    if k.strip() == key:
                        output.append(f"{key}={value}\n")
                        written = True
                        i += 1
                        continue

                output.append(line)
                i += 1
            if not found_section:
                if output and not output[-1].endswith("\n"):
                    output.append("\n")
                output.append(f"[{section}]\n")
                output.append(f"{key}={value}\n")
            elif found_section and not written:
                output.append(f"{key}={value}\n")
            with open(filename, "w", encoding="utf-16") as f:
                f.writelines(output)
            return

    def cmd_winactivate(self, action):
        """
        WinActivate [, WinTitle]
        Brings the matching window to the foreground.
        """
        # Parse: WinActivate, Title   or   WinActivate Title
        if "," in action:
            _, rest = action.split(",", 1)
            criteria = rest.strip()
        else:
            parts = action.split(None, 1)
            criteria = parts[1] if len(parts) > 1 else ""
        criteria = self._handle_variable(criteria)
        info = self._find_window(criteria)
        if info is None:
            return

        if sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32
                hwnd = info["hwnd"]
                # Restore if minimized
                if user32.IsIconic(hwnd):
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                user32.SetForegroundWindow(hwnd)
            except Exception:
                pass

        elif sys.platform == "darwin":
            try:
                # Prefer process name (exe) for activation
                process_name = info.get("exe") or ""
                title = info.get("title") or ""
                if process_name:
                    script = f'''
                    tell application "System Events"
                        set frontmost of process "{process_name}" to true
                    end tell
                    '''
                else:
                    # Fallback by title (less reliable)
                    script = f'''
                    tell application "System Events"
                        set procs to every process whose name contains "{title}"
                        if (count of procs) > 0 then
                            set frontmost of item 1 of procs to true
                        end if
                    end tell
                    '''
                subprocess.run(["osascript", "-e", script],
                               capture_output=True, text=True, timeout=3)
            except Exception:
                pass

        elif sys.platform.startswith("linux"):
            try:
                d = Xdisplay.Display()
                win = d.create_resource_object("window", info["hwnd"])
                win.set_input_focus(X.RevertToParent, X.CurrentTime)
                win.configure(stack_mode=X.Above)
                d.sync()
                d.close()
            except Exception:
                pass

    def cmd_wingetpos(self, action):
        """
        WinGetPos, OutX, OutY, OutWidth, OutHeight [, WinTitle]
        Retrieves the position and size of the matching window.
        """
        # Split after command name
        if "," not in action:
            return

        _, rest = action.split(",", 1)
        parts = [p.strip() for p in rest.split(",")]
        # Pad to at least 5 slots: OutX, OutY, OutW, OutH, WinTitle
        while len(parts) < 5:
            parts.append("")
        out_x, out_y, out_w, out_h, criteria = parts[:5]
        criteria = self._handle_variable(criteria)
        info = self._find_window(criteria)
        if info is None:
            # AHK leaves the variables unchanged if not found; we set to 0 for safety
            if out_x:
                self.variables[out_x] = 0
            if out_y:
                self.variables[out_y] = 0
            if out_w:
                self.variables[out_w] = 0
            if out_h:
                self.variables[out_h] = 0
            return

        if out_x:
            self.variables[out_x] = info["left"]
        if out_y:
            self.variables[out_y] = info["top"]
        if out_w:
            self.variables[out_w] = info["width"]
        if out_h:
            self.variables[out_h] = info["height"]
    def _register_gui_widget(self, widget, options, width=None, height=None):
        """Store widget + place() geometry so GuiControl Hide/Show can restore it."""
        def _si(value, default=0):
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default

        x = _si(options.get("x", 0))
        y = _si(options.get("y", 0))
        w = width if width is not None else _si(options.get("w", 0))
        h = height if height is not None else _si(options.get("h", 0))
        if "v" in options:
            name = options["v"]
            self.gui_controls[name] = widget
            self.gui_control_placements[name] = {
                "x": x,
                "y": y,
                "width": w,
                "height": h,
            }
        return x, y, w, h

    def _load_gui_image(self, filename, width=0, height=0):
        """Load an image for Gui, Add, Image / Picture. Returns a PhotoImage or None."""
        if not filename:
            return None
        path = self._resolve_value(str(filename)).strip().strip('"').strip("'")
        if not path:
            return None
        candidates = [path]
        if not os.path.isabs(path):
            script_dir = self.builtin_variables.get("A_ScriptDir", os.getcwd())
            candidates.append(os.path.join(script_dir, path))
            candidates.append(os.path.join(IMAGES_PATH, path))
        resolved = None
        for candidate in candidates:
            if candidate and os.path.isfile(candidate):
                resolved = candidate
                break
        if resolved is None:
            return None
        try:
            width = int(float(width or 0))
            height = int(float(height or 0))
        except (ValueError, TypeError):
            width, height = 0, 0
        try:
            from PIL import Image, ImageTk
            img = Image.open(resolved)
            if width > 0 and height > 0:
                img = img.resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception:
            try:
                return tk.PhotoImage(file=resolved)
            except Exception:
                return None

    def cmd_gui(self, line):
        """Supports Gui commands like Gui, Tab"""
        # Helper function to safely convert to int, handling floats
        def safe_int(value):
            try:
                return int(float(value))

            except (ValueError, TypeError):
                return 0

        # Split the input into multiple lines (if it contains newlines)
        lines = line.splitlines()
        # Loop
        for single_line in lines:
            # Process each line individually
            parts = [p.strip() for p in single_line.split(",")]
            command = parts[1]
            if len(parts) > 2:
                command2 = parts[2]
            else:
                command2 = ""
            if len(parts) > 3:
                command3 = parts[3]
            else:
                command3 = ""
            if len(parts) > 4:
                command4 = parts[4]
            else:
                command4 = ""
            # For widgets, parent should be a widget, not a string
            parent = self.current_tab if isinstance(self.current_tab, (tk.Widget, ttk.Widget)) else self
            # Splitting elements - always define options, parse any options string (supports vVar x10 etc)
            options = {}
            if command3.strip():
                for token in command3.split():
                    if token:
                        key = token[0]
                        value = token[1:]
                        options[key] = value
                try:
                    if parent is not self:
                        if "x" in options:
                            options["x"] = str(int(float(options["x"])) - 10 - safe_int(self.offset_x))
                        if "y" in options:
                            options["y"] = str(int(float(options["y"])) - 30 - safe_int(self.offset_y))
                except:
                    pass

            # Tabs
            if "|" in command4:
                tabs = command4.split("|")
            # Handle Colors
            if command == "Font":
                color = None
                bold = False
                self.font_size = 9
                for token in command2.split():
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
                self.foreground_color = color
                self.font_bold = bold
                self.update_style()
            if command == "Color":
                color = command2
                if color.startswith("0x"):
                    color = "#" + color[2:]
                elif len(color) == 6:
                    color = "#" + color
                self.configure(bg=color)
                self.background_color = color
                self.update_style()
            # Handle Tab2 (Notebook creation)
            if command2 == "Tab2":
                try:
                    self.offset_x = options["x"]
                    self.offset_y = options["y"]
                except:
                    options["x"] = 0
                    options["y"] = 0
                notebook = ttk.Notebook(self, padding=10, style="Dark.TNotebook")
                notebook.place(x=safe_int(options["x"]), y=safe_int(options["y"]), width=safe_int(options["w"]) + 10, height=safe_int(options["h"]) + 20)
                self.notebook = notebook  # Store notebook reference
                self.tabs = {}  # Store tab frames
                for i, tab_name in enumerate(tabs):
                    tab_frame = ttk.Frame(notebook, style="Dark.TFrame")
                    notebook.add(tab_frame, text=tab_name)
                    self.tabs[tab_name] = tab_frame
                self.max_x = max(self.max_x, safe_int(options["w"]) + safe_int(options["x"]))
                self.max_y = max(self.max_y, safe_int(options["h"]) + safe_int(options["y"]))
            # Handle Tab switching
            elif command == "Tab":
                if command2 and command2 in self.tabs:
                    self.current_tab = self.tabs[command2]
                else:
                    self.current_tab = self
            # Text, edit, show, hide
            font_style = "bold" if self.font_bold else "normal"
            if command2 == "Text":
                text = tk.Label(parent, text=command4, bg=self.background_color, fg=self.foreground_color, font=("Segoe UI", self.font_size, font_style))
                x, y, width, height = self._register_gui_widget(text, options)
                if "v" in options:
                    self.gui_variables[options["v"]] = text  # for Submit if needed, though Label has no .get()
                place_kwargs = {"x": x, "y": y}
                if width:
                    place_kwargs["width"] = width
                if height:
                    place_kwargs["height"] = height
                text.place(**place_kwargs)
                self.max_x = max(self.max_x, x + width)
                self.max_y = max(self.max_y, y + height)
            elif command2 == "Edit":
                var = tk.StringVar()

                if command4:
                    var.set(command4)

                entry = tk.Entry(
                    parent,
                    textvariable=var,
                    bg="white",
                    fg="black",
                    insertbackground="black",
                    disabledbackground="white",
                    disabledforeground="black",
                )

                # Initialize default height
                if "h" not in options:
                    options["h"] = 28 if sys.platform == "darwin" else 30

                x, y, width, height = self._register_gui_widget(entry, options)
                entry.place(x=x, y=y, width=width, height=height)

                if "v" in options:
                    self.gui_variables[options["v"]] = var

                self.max_x = max(self.max_x, x + width)
                self.max_y = max(self.max_y, y + height)
            elif command2 == "GroupBox":
                group = tk.LabelFrame(parent, text=command4, borderwidth=3, bg=self.background_color, fg=self.foreground_color, font=("Segoe UI", self.font_size, font_style))
                x, y, width, height = self._register_gui_widget(group, options)
                group.place(x=x, y=y, width=width, height=height)
                self.max_x = max(self.max_x, x + width)
                self.max_y = max(self.max_y, y + height)
            elif command2 == "Button":
                def _btn_cmd():
                    if "g" in options:
                        self.execute_gosub(options["g"])

                button = tk.Button(
                    parent,
                    text=command4,
                    command=_btn_cmd
                )

                x, y, width, height = self._register_gui_widget(button, options)
                place_kwargs = {"x": x, "y": y}
                if width:
                    place_kwargs["width"] = width
                if height:
                    place_kwargs["height"] = height
                button.place(**place_kwargs)

                self.max_x = max(self.max_x, x + width)
                self.max_y = max(self.max_y, y + height)
            elif command2 == "Link":
                link = command4.replace('<a href="', "")
                link = link.replace("</a>", "")
                url, text = link.split('">')
                label = tk.Label(
                    parent,
                    text=text,
                    fg="#0093ff",
                    cursor="hand2",
                    bg=self.background_color,
                    font=("Segoe UI", 9, "underline")
                )
                label.bind(
                    "<Button-1>",
                    lambda e, u=url: open_link(u)()
                )
                x, y, width, height = self._register_gui_widget(label, options)
                place_kwargs = {"x": x, "y": y}
                if width:
                    place_kwargs["width"] = width
                if height:
                    place_kwargs["height"] = height
                label.place(**place_kwargs)
                self.max_x = max(self.max_x, x + width)
                self.max_y = max(self.max_y, y + height)
            elif command2 == "ComboBox":
                values = command4.split("|")
                var = tk.StringVar()
                if values:
                    var.set(values[0])
                combobox = ttk.Combobox(parent, values=values, textvariable=var)
                x, y, width, height = self._register_gui_widget(combobox, options)
                place_kwargs = {"x": x, "y": y}
                if width:
                    place_kwargs["width"] = width
                if height:
                    place_kwargs["height"] = height
                combobox.place(**place_kwargs)
                if "v" in options:
                    self.gui_variables[options["v"]] = var
                if "g" in options:
                    try:
                        combobox.bind("<<ComboboxSelected>>", lambda event: self.execute_gosub(options["g"]))
                    except:
                        pass
                self.max_x = max(self.max_x, x + width)
                self.max_y = max(self.max_y, y + height)

            elif command2 == "DropDownList":
                values = command4.split("|")
                var = tk.StringVar()
                if values:
                    var.set(values[0])
                combobox = ttk.Combobox(parent, state="readonly", values=values, textvariable=var)
                x, y, width, height = self._register_gui_widget(combobox, options)
                place_kwargs = {"x": x, "y": y}
                if width:
                    place_kwargs["width"] = width
                if height:
                    place_kwargs["height"] = height
                combobox.place(**place_kwargs)
                if "v" in options:
                    self.gui_variables[options["v"]] = var
                if "g" in options:
                    try:
                        combobox.bind("<<ComboboxSelected>>", lambda event: self.execute_gosub(options["g"]))
                    except:
                        pass
                self.max_x = max(self.max_x, x + width)
                self.max_y = max(self.max_y, y + height)

            elif command2 == "Checkbox":
                try:
                    var = tk.BooleanVar()
                    def _checkbox_cmd():
                        if "g" in options:
                            self.execute_gosub(options["g"])
                    checkbox = ttk.Checkbutton(
                        parent,
                        text=command4,
                        variable=var,
                        command=_checkbox_cmd,
                        style="Dark.TCheckbutton"
                    )
                    x, y, width, height = self._register_gui_widget(checkbox, options)
                    place_kwargs = {"x": x, "y": y}
                    if width:
                        place_kwargs["width"] = width
                    if height:
                        place_kwargs["height"] = height
                    checkbox.place(**place_kwargs)
                    if "v" in options:
                        self.gui_variables[options["v"]] = var
                    self.max_x = max(self.max_x, x + width)
                    self.max_y = max(self.max_y, y + height)
                except:
                    pass

            elif command2 in ("Image", "Picture", "Pic"):
                x = safe_int(options.get("x", 0))
                y = safe_int(options.get("y", 0))
                width = safe_int(options.get("w", 0))
                height = safe_int(options.get("h", 0))
                photo = self._load_gui_image(command4, width, height)
                image_label = tk.Label(
                    parent,
                    image=photo if photo is not None else "",
                    text="" if photo is not None else command4,
                    bg=self.background_color,
                    fg=self.foreground_color,
                    borderwidth=0,
                    highlightthickness=0,
                )
                image_label._is_gui_image = True
                if photo is not None:
                    image_label.image = photo
                if "g" in options:
                    image_label.config(cursor="hand2")
                    image_label.bind("<Button-1>", lambda e: self.execute_gosub(options["g"]))
                x, y, width, height = self._register_gui_widget(image_label, options, width, height)
                if "v" in options and photo is not None:
                    self.gui_images[options["v"]] = photo
                place_kwargs = {"x": x, "y": y}
                if width:
                    place_kwargs["width"] = width
                if height:
                    place_kwargs["height"] = height
                image_label.place(**place_kwargs)
                self.max_x = max(self.max_x, x + width)
                self.max_y = max(self.max_y, y + height)

            elif command == "Submit":
                for name, widget in self.gui_variables.items():
                    self.variables[name] = widget.get()
            elif command == "Show":
                padding = 20
                width = max(300, self.max_x + padding)
                height = max(100, self.max_y + padding)
                self.geometry(f"{width}x{height}")
                self.after(0, self.deiconify)
            elif command == "Hide":
                self.after(0, self.withdraw)
    def _cmd_msgbox(self, action):
        try:
            # Split once after command
            _, args = action.split(",", 1)
            # Split parameters
            parts = [p.strip() for p in args.split(",")]
            # Apply variable substitution BEFORE using values
            parts = [self._handle_variable(p) for p in parts]
            # Default values
            options = None
            title = ""
            text = ""
            # AHK supports multiple forms:
            if len(parts) == 1:
                # MsgBox, Text
                text = parts[0]
            elif len(parts) == 2:
                # MsgBox, Options, Text
                options = parts[0]
                text = parts[1]
            elif len(parts) >= 3:
                # MsgBox, Options, Title, Text
                options = parts[0]
                title = parts[1]
                text = parts[2]
            # Show messagebox
            messagebox.showinfo(title if title else "recording.ahk", text)
        except Exception as e:
            raise SyntaxError(f"{action}: {str(e)}")

    def _execute_script(self, actions, scan_functions=False):
        """
        Process a list of script lines (supports nested loops via recursion on blocks).
        Uses self.current_line_count to get the line.
        """
        saved_line_count = self.current_line_count
        actions = self._normalize_inline_else_lines(actions)
        # Pre-scan function and label definitions
        if scan_functions:
            self.scan_functions(actions)
        self.current_line_count = 0
        while self.current_line_count < len(actions):
            raw_line = actions[self.current_line_count]
            line = raw_line.strip()
            line = self._strip_inline_comment(line)
            if not line or line.startswith(";"):
                self.current_line_count += 1
                continue

            # DllCall is not implemented
            if "DllCall" in line.lower():
                self.current_line_count += 1
                continue

            # Return breaks the (current) execution scope
            if line.lower() == "return":
                break

            # Variable assignment  (x := expr)
            if self._handle_assignment(line):
                self.current_line_count += 1
                continue

            # Math shorthand  (x += 5 / x -= 2 / x *= 3 / x /= 2)
            if self._handle_math(line):
                self.current_line_count += 1
                continue

            # Function call
            match = re.fullmatch(r"([A-Za-z_]\w*)\((.*?)\)", line)
            if match:
                name = match.group(1)
                # Only execute if we actually have a definition for it
                if name in self.functions:
                    # Save current parse_line to restore after function execution
                    saved_line = self.current_line_count
                    self._execute_script(self.functions[name])
                    self.current_line_count = saved_line + 1
                else:
                    messagebox.showerror("title", f"Error: Call to nonexistent function\nSpecifically: {name}\n\nThe program will exit")
                    self.current_line_count += 1
                continue

            # Label call (Gosub, LabelName)
            match = re.fullmatch(r"Gosub,\s*([A-Za-z_]\w*)", line, re.IGNORECASE)
            if match:
                name = match.group(1)
                self.execute_gosub(name)
                continue

            # Hotkey labels
            if re.match(r"^[^\s:]+::$", line):
                self.current_line_count += 1
                continue

            # Loop command (supports count-based and Loop, Files, ...)
            if line.lower().startswith("loop"):
                loop_type, file_pattern, mode = self._parse_loop_type(line)
                if loop_type == "files":
                    # File loop: Loop, Files, Pattern [, Mode]
                    file_pattern = self._handle_variable(file_pattern)
                    # Normalize separators so \ patterns from AHK scripts work cross-platform
                    file_pattern = file_pattern.replace("\\", "/")
                    recursive = bool(mode and "r" in mode.lower())
                    block, end_index = self._extract_block(actions, self.current_line_count)
                    # Collect matches
                    try:
                        if recursive:
                            matches = glob.glob(file_pattern, recursive=True)
                        else:
                            matches = glob.glob(file_pattern)
                    except Exception as glob_err:
                        matches = []
                        try:
                            messagebox.showerror(
                                "title",
                                f"Error expanding Loop, Files pattern:\n{file_pattern}\n\n{glob_err}"
                            )
                        except:
                            pass

                    matches = sorted(matches)  # deterministic alphabetical order
                    # Save/restore A_Index for nesting support
                    old_a_index = self.variables.get("A_Index")
                    for idx, filepath in enumerate(matches, 1):
                        self.variables["A_Index"] = idx
                        self._set_file_loop_variables(filepath)
                        self._execute_script(block)
                    if old_a_index is not None:
                        self.variables["A_Index"] = old_a_index
                    else:
                        self.variables.pop("A_Index", None)
                    self.current_line_count = end_index + 1
                    continue

                else:
                    # Original numeric / expression count-based loop
                    count = self._evaluate_loop_count(line)
                    block, end_index = self._extract_block(actions, self.current_line_count)
                    # Temporarily set A_Index (1-based) for AHK compatibility; restore for nesting
                    old_a_index = self.variables.get("A_Index")
                    for idx in range(1, count + 1):
                        self.variables["A_Index"] = idx
                        self._execute_script(block)
                    if old_a_index is not None:
                        self.variables["A_Index"] = old_a_index
                    else:
                        self.variables.pop("A_Index", None)
                    self.current_line_count = end_index + 1
                    continue

            if line.lower().startswith("if"):
                condition, if_block, else_block, end_index = self._extract_if_blocks(actions, self.current_line_count)
                if self._evaluate_condition(condition):
                    self._execute_script(if_block)
                else:
                    if len(else_block) != 0:
                        self._execute_script(else_block)
                self.current_line_count = end_index + 1
                continue

            if line.lower().startswith("while"):
                condition = line[5:].strip()
                # Extract the while block
                block, end_index = self._extract_block(actions, self.current_line_count)
                while self._evaluate_condition(
                    self._handle_variable(condition)
                ):
                    self._execute_script(block)
                self.current_line_count = end_index + 1
                continue

            # Substitute %Var% tokens before dispatching other commands
            processed_line = self._handle_variable(line)
            print("Processing: ", processed_line)
            # All commands go here
            if processed_line.startswith("GuiControl"):
                self.cmd_guicontrol(processed_line)
            if processed_line.startswith("Gui") and not processed_line.startswith("GuiControl"):
                self.cmd_gui(processed_line)
            if processed_line.startswith("MsgBox"):
                self._cmd_msgbox(processed_line)
            if processed_line.startswith("Ini"):
                self.cmd_ini(processed_line)
            if processed_line.startswith("SplitPath"):
                self.cmd_splitpath(processed_line)
            if processed_line.lower().startswith("hotkey"):
                self.cmd_hotkey(processed_line)
            if processed_line.startswith("PixelSearch"):
                self.cmd_pixelsearch(processed_line)
            if processed_line.startswith("PixelGetColor"):
                self._cmd_pixelgetcolor(processed_line)
            if processed_line.startswith("Send"):
                self._cmd_send(processed_line)
            if processed_line.startswith("Click"):
                self._cmd_click(processed_line)
            if processed_line.startswith("Sleep"):
                self._cmd_sleep(processed_line)
            if processed_line.startswith("MouseMove"):
                self._cmd_mousemove(processed_line)
            if processed_line.startswith("MouseGetPos"):
                self._cmd_mousegetpos(processed_line)
            if processed_line.lower().startswith("winactivate"):
                self.cmd_winactivate(processed_line)
            if processed_line.lower().startswith("wingetpos"):
                self.cmd_wingetpos(processed_line)
            if processed_line.lower().startswith("winexist"):
                # Command form is rarely used; mainly the function form is needed.
                # Still support basic WinExist, Title  (sets ErrorLevel-like behaviour via return)
                pass

            if processed_line.lower().startswith("setkeydelay"):
                parts = [x.strip() for x in processed_line.split(",")]
                self.key_delay = int(parts[1])
            if processed_line.startswith("Reload"):
                os.execv(sys.executable, [sys.executable] + sys.argv)
            if processed_line.startswith("ExitApp"):
                self.destroy()
            self.current_line_count += 1
        self.current_line_count = saved_line_count
        return

    # Final playback
    def build_main_content(self):
        self._execute_script(self.script, True)
        return

if __name__ == "__main__":
    if open_mode == "Editor":
        app = MainGUI()
        app.mainloop()
    elif open_mode == "Playback":
        playback = Playback(playback_path)
print("Program exited with exit code 0")