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
    import pygetwindow as gw
    import ctypes
    from ctypes import wintypes
elif sys.platform == "darwin":
    import Quartz
    import AppKit
    from AppKit import NSScreen
elif sys.platform == "linux":
    from Xlib import X, XK, display as Xdisplay
    from Xlib.ext import xtest
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
# All Platforms
CONTROL_KEYWORDS = {
    "if", "else", "while", "loop",
    "for", "switch", "catch", "try"
}
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
        self.loop_end = 0
        self.gui_variables = {}
        self.gui_controls = {}
        self.active_windows = {}
        script_full = os.path.abspath(playback_path)
        self.builtin_variables = {
            "A_ScriptFullPath": script_full,
            "A_ScriptDir": os.path.dirname(script_full),
            "A_ScriptName": os.path.basename(script_full),
            "A_WorkingDir": os.getcwd(),
            "A_Space": " ",
            "A_Tab": "\t",
        }
        self.builtin_functions = {}
        self.functions_start = {}
        self.functions_end = {}
        self.labels_start = {}
        self.labels_end = {}
        self.local_variables = {}
        self.pending_actions = {}
        self.font_bold = False
        try:
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TNotebook.Tab", padding=(2, 1, 2, 1))
        except:
            pass

        # Find Functions and Labels
        self.build_builtin_functions()
        self.find_functions()
        self.find_labels()
        # Main Loop
        self.execute_script(-1, len(self.script))
        self.withdraw
        self.mainloop()
    def execute_script(self, start_line, end_line, _script=None, debug=False):
        # Initialize Defaults
        if _script == None:
            _script = self.script
        # After a Loop runs, skip its body so this pass does not execute it again
        skip_until = -1
        # Convert start and end to integer
        start = int(start_line)
        end = int(end_line)
        # Start Macro
        for line, processed_line in enumerate(_script):
            if line <= start or line <= skip_until:
                continue

            if line >= end:
                break

            processed_line2 = processed_line.lower().replace("    ", "")
            if processed_line.startswith(";") or processed_line == "":
                continue

            if processed_line == "return":
                break

            if debug == True:
                print("Processing: ", _script[line])
            # if (Condition)
            # Keep function-call parentheses. Stripping every "(" / ")"
            # turned InStr(a, b) into InStr a, b and skipped handle_variable.
            if_pattern = r'(?mi)^\s*if\s+(.+?)\s*$'
            is_if = re.match(if_pattern, processed_line)
            if is_if:
                condition = is_if.group(1).strip()
                if condition.endswith("{"):
                    condition = condition[:-1].strip()
                condition = self._unwrap_parens(condition)
                split = self._split_if_condition(condition)
                if split is None:
                    # Bare variable / function / literal: AHK truthy check.
                    value = self.handle_variable(condition, line)
                    result = self._if_truthy(value)
                else:
                    left, operator, right = split
                    left = self._eval_if_operand(left, line)
                    right = self._eval_if_operand(right, line)
                    try:
                        left = int(left)
                        right = int(right)
                    except Exception:
                        left = str(left).replace('"', "")
                        right = str(right).replace('"', "")
                    if operator == "=":
                        if isinstance(left, str):
                            left = left.lower()
                            right = str(right).lower()
                        operator = "=="
                    processed_condition = f"{left!r} {operator} {right!r}"
                    result = eval(processed_condition)
                skip_until = self.cmd_if(line, result, _script)
                continue

            # Loop, Files, Directory
            loop_files_pattern = r'(?mi)^\s*Loop\s*,\s*Files\s*,\s*(.*?)(?:\s*,\s*(.*?))?\s*\{'
            is_loop_files = re.match(loop_files_pattern, processed_line)
            if is_loop_files:
                file_pattern = is_loop_files.group(1).strip()
                mode = is_loop_files.group(2)
                skip_until = self.cmd_loop_files(line, file_pattern, mode, _script)
                continue

            # Loop, Amount
            loop_pattern = r'(?mi)^\s*Loop(?:\s*,\s*(\d+))?\s*\{'
            is_loop = re.match(loop_pattern, processed_line)
            if is_loop:
                try:
                    loop_count = int(is_loop.group(1))
                except:
                    try:
                        # Plain "Loop" = infinite loop is not currently supported,
                        # so default to one iteration.
                        loop_count = 1
                    except:
                        continue

                # cmd_loop already runs the body loop_count times.
                # Jump past the matching } so the body is not run an extra time.
                skip_until = self.cmd_loop(line, loop_count, _script)
                continue

            # GoSub, LabelName
            if processed_line2.startswith("gosub"):
                gosub = self.cmd_gosub(processed_line)
                if gosub != 0:
                    messagebox.showerror(f"Error at line {line + 1}", f"Error at line {line + 1}\nMissing Label: {gosub}")
            # FunctionName(Parameters)
            function_pattern = r'(?mi)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*'
            is_function_call = re.match(function_pattern, processed_line)
            if is_function_call:
                function_name = is_function_call.group(1)
                parameters = is_function_call.group(2)
                # print("Function:", function_name)
                # print("Parameters:", parameters)
                try:
                    start_line2 = self.functions_start[function_name]
                    end_line2 = self.functions_end[function_name]
                    self.execute_script(start_line2, end_line2)
                except Exception as e:
                    if function_name in self.builtin_functions:
                        args = self.split_args(parameters)
                        result = self.builtin_functions[function_name](*args)
                    else:
                        print(traceback.format_exc())
                        messagebox.showerror(f"Error at line {line + 1}", f"Error at line {line + 1}\nMissing Function: {e}")
            # VariableName := Value
            variable_assignment_pattern = r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*(.*?)\s*$'
            match = re.match(variable_assignment_pattern, processed_line)
            if match:
                variable_name = match.group(1)
                variable_value = self.handle_variable(match.group(2), line)
                try:
                    int(variable_value)
                except:
                    variable_value = self.handle_math(variable_value)
                self.local_variables[variable_name] = variable_value
            # VariableName .= Value
            # AHK v1: same as Var := Var . Value (expression).
            # FileName "|"  ->  FileName . "|"
            variable_append_pattern = r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\.\=\s*(.*?)\s*$'
            match = re.match(variable_append_pattern, processed_line)
            if match:
                variable_name = match.group(1)
                variable_value = self.handle_concat(match.group(2))
                current_value = self.local_variables.get(variable_name, "")
                self.local_variables[variable_name] = (
                    str(current_value) + str(variable_value)
                )
            # SplitPath, InputVar, OutFileName, OutDir, OutExtension, OutNameNoExt, OutDrive
            if processed_line2.startswith("splitpath"):
                self.cmd_splitpath(processed_line)
            # MsgBox, Text
            if processed_line2.startswith("msgbox"):
                arguments = [p.strip() for p in processed_line.split(",")]
                msgbox_text = self.handle_variable(arguments[1], line)
                try:
                    int(float(arguments[1]))
                except:
                    msgbox_text = self.handle_math(msgbox_text)
                try:
                    msgbox_text = msgbox_text.replace("`n", "\n")
                except:
                    pass

                messagebox.showerror(f"MsgBox", f"{msgbox_text}")
            # IniRead, OutputVar, Filename, Section, Key, Default=ERROR
            # IniWrite, Value, Filename, Section, Key
            if processed_line2.startswith("ini"):
                self.cmd_ini(processed_line)
            # GuiControl, Subcommand, Control, Value
            if processed_line2.startswith("guicontrol"):
                self.cmd_guicontrol(processed_line)
            # WinActivate, Window
            if processed_line2.startswith("winactivate"):
                self.cmd_winactivate(processed_line)
            # WinGetPos, OutX, OutY, OutWidth, OutHeight [, WinTitle]
            if processed_line2.startswith("wingetpos"):
                self.cmd_wingetpos(processed_line)
            # Gui, Action
            if processed_line2.startswith("gui") and not processed_line2.startswith("guicontrol"):
                self.cmd_gui(processed_line)
            self._flush_pending_actions()
    def cmd_gui(self, line):
        # Define defaults
        arguments = [p.strip() for p in line.split(",")]
        x = 0
        y = 0
        w = 100
        h = 30
        v = ""
        g = ""
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
                for item in placement:
                    if item.startswith("x"):
                        x = int(item[1:])
                    elif item.startswith("y"):
                        y = int(item[1:])
                    elif item.startswith("w"):
                        w = int(item[1:])
                    elif item.startswith("h"):
                        h = int(item[1:])
                    elif item.startswith("v"):
                        v = str(item[1:])
                    elif item.startswith("g"):
                        g = str(item[1:])
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
                entry_var = tk.StringVar(value="")
                self.gui_variables[v] = entry_var
                entry = tk.Entry(self.current_tab2, bg="white", fg="black", textvariable=entry_var,
                                 insertbackground="black", disabledbackground="white", 
                                 disabledforeground="black", highlightbackground=self.gui_color)
                entry.place(x=(x - current_offset_x), y=(y - current_offset_y - 5), width=w, height=h)
                self.gui_controls[v] = entry
            # Gui, Add, GroupBox
            if arguments[2] == "GroupBox":
                group = tk.LabelFrame(self.current_tab2, text=arguments[4], borderwidth=3, bg=self.gui_color, fg=self.color, font=("Segoe UI", self.font_size, font_style))
                group.place(x=(x - current_offset_x), y=(y - current_offset_y), width=w, height=h)
                self.gui_controls[v] = group
            # Gui, Add, Checkbox
            if arguments[2] == "Checkbox":
                checkbox = ttk.Checkbutton(self.current_tab2, text=arguments[4], style="Dark.TCheckbutton")
                checkbox.place(x=(x - current_offset_x), y=(y - current_offset_y))
                self.gui_controls[v] = checkbox
            # Gui, Add, Button
            if arguments[2] == "Button":
                button = tk.Button(
                    self.current_tab2,
                    text=arguments[4],
                    command=lambda label=g: self.cmd_gosub(f"GoSub, {label}") if label else None
                )
                button.place(x=(x - current_offset_x), y=(y - current_offset_y), width=w, height=h)
            # Gui, Add, DropDownList
            if arguments[2] == "DropDownList":
                values2 = self.handle_variable(arguments[4])
                values = values2.split("|")
                combo_var = tk.StringVar()
                if values and values[0] != "":
                    combo_var.set(values[0])
                combobox = ttk.Combobox(
                    self.current_tab2,
                    state="readonly",
                    values=values,
                    textvariable=combo_var
                )
                combobox.place(x=(x - current_offset_x), y=(y - current_offset_y), width=w) # Do not use height
                self.gui_controls[v] = combobox
                if v:
                    self.gui_variables[v] = combo_var
                    self.local_variables[v] = combo_var.get()
                if g:
                    def _on_dropdown_selected(event, label=g, var_name=v, tvar=combo_var):
                        if var_name:
                            self.local_variables[var_name] = tvar.get()
                        self.cmd_gosub(f"GoSub, {label}")
                    combobox.bind("<<ComboboxSelected>>", _on_dropdown_selected)
        # Gui, Show
        if arguments[1] == "Show":
            self.deiconify
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
            foreground=self.color
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
    def _collect_settings_data(self):
        data = {}
        for key, var in self.gui_variables.items():
            if hasattr(var, "get") and var is not None:
                try:
                    data[key] = var.get()
                except Exception as e:
                    print(f"Skipping {key}: {e}")
        # Save editor script directly into config
        if hasattr(self, "editor_textbox"):
            data["ahk_script"] = self.editor_textbox.get("1.0", "end").strip()
        return data

    def split_args(self, s):
        args, buf, depth, quote = [], [], 0, None
        for ch in s:
            if quote:
                buf.append(ch)
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
                buf.append(ch)
            elif ch == ',' and depth == 0:
                args.append(''.join(buf))
                buf = []
            else:
                if ch in '([': depth += 1
                elif ch in ')]': depth -= 1
                buf.append(ch)
        if buf:
            args.append(''.join(buf))
        return args

    def build_builtin_functions(self):
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
            info = self._find_window(self.handle_variable(str(window)))
            if info is None:
                return 0
            return info.get("hwnd", 0) or 0

        self.builtin_functions = {
            "A_TickCount": int(time.monotonic() * 1000),
            # Basic Functions
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
            # Window Management
            "WinExist": WinExist
        }
    def find_labels(self, script=None):
        # Initialize Defaults
        if script == None:
            _script = self.script
        else:
            _script = script
        label_pattern = r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(?:;.*)?$'
        function_pattern = r'(?mi)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*\{'
        def is_function_declaration(text):
            match = re.match(function_pattern, text)
            if not match:
                return False

            # Don't treat control-flow as a function (if, while, loop, for, ...)
            return match.group(1).lower() not in CONTROL_KEYWORDS

        for start_line, line in enumerate(_script):
            match = re.match(label_pattern, line)
            if not match:
                continue

            label_name = match.group(1)
            # A label continues through later labels and control-flow
            # blocks. It ends at the next real function, or EOF.
            end_line = len(_script)
            for i in range(start_line + 1, len(_script)):
                if is_function_declaration(_script[i]) or re.match(label_pattern, _script[i]):
                    end_line = i
                    break

            self.labels_start[label_name] = start_line
            self.labels_end[label_name] = end_line
    def find_functions(self, script=None):
        # Initialize Defaults
        if script == None:
            _script = self.script
        else:
            _script = script
        function_name = ""
        parameters = ""
        function_line = -1
        command = "none"
        braces = 0
        pattern = r'(?mi)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*\{'
        for line in range(len(_script)):
            match = re.search(pattern, _script[line], re.DOTALL)
            if not match:
                continue

            function_name = match.group(1)
            parameters = match.group(2).strip()
            # Don't treat control-flow statements as functions
            if function_name.lower() in CONTROL_KEYWORDS:
                continue

            function_line = line
            self.functions_start[function_name] = f"{function_line}"
            # Start counting braces from the function declaration
            braces = 0
            # Scan from the function declaration until all braces are closed
            for function_scan_line in range(function_line, len(_script)):
                braces += _script[function_scan_line].count("{")
                braces -= _script[function_scan_line].count("}")
                if braces == 0:
                    self.functions_end[function_name] = f"{function_scan_line}"
                    break
    def _unwrap_parens(self, value):
        """
        Strip wrapping ( ... ) pairs that enclose the whole string.
        Inner parentheses belonging to function calls are left alone.
        """
        s = "" if value is None else str(value).strip()
        while len(s) >= 2 and s.startswith("(") and s.endswith(")"):
            depth = 0
            quote = None
            wraps = True
            for i, ch in enumerate(s):
                if quote:
                    if ch == quote:
                        quote = None
                    continue
                if ch in "\"'":
                    quote = ch
                    continue
                if ch == "(":
                    depth += 1
                elif ch == ")":
                    depth -= 1
                    if depth == 0 and i != len(s) - 1:
                        wraps = False
                        break
                    if depth < 0:
                        wraps = False
                        break
            if not wraps or depth != 0:
                break
            s = s[1:-1].strip()
        return s

    def _split_if_condition(self, condition):
        """
        Split an IF condition on the comparison operator that sits
        outside quotes and function-call parentheses.
        """
        s = "" if condition is None else str(condition)
        ops = ("==", "!=", ">=", "<=", ">", "<", "=")
        depth = 0
        quote = None
        i = 0
        while i < len(s):
            ch = s[i]
            if quote:
                if ch == quote:
                    quote = None
                i += 1
                continue
            if ch in "\"'":
                quote = ch
                i += 1
                continue
            if ch == "(":
                depth += 1
                i += 1
                continue
            if ch == ")":
                depth -= 1
                i += 1
                continue
            if depth == 0:
                for op in ops:
                    if s.startswith(op, i):
                        left = s[:i].strip()
                        right = s[i + len(op):].strip()
                        if left != "" and right != "":
                            return left, op, right
                        break
            i += 1
        return None

    def _eval_if_operand(self, token, line=0):
        """
        Resolve one side of an IF comparison the same way := does:
        quoted literals stay literal (except %Var% inside), function
        calls and identifiers go through handle_variable.
        """
        raw = "" if token is None else str(token).strip()
        if raw == "":
            return ""
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
            inner = raw[1:-1]
            if "%" in inner:
                return re.sub(
                    r"%([A-Za-z_][A-Za-z0-9_]*)%",
                    lambda m: (
                        "" if self._lookup_variable(m.group(1), None) is None
                        else str(self._lookup_variable(m.group(1), ""))
                    ),
                    inner,
                )
            return inner
        return self.handle_variable(raw, line)

    def _if_truthy(self, value):
        """AHK v1: blank and 0 are false; anything else is true."""
        if value is None or value is False:
            return False
        if value is True:
            return True
        if isinstance(value, (int, float)):
            return value != 0
        text = str(value).strip()
        if text == "" or text == "0":
            return False
        try:
            return float(text) != 0
        except (TypeError, ValueError):
            return True

    def cmd_if(self, start_line, condition, script=None):
        # Initialize Defaults
        if script == None:
            _script = self.script
        else:
            _script = script

        # Find the end of the IF block.
        braces = 0
        if_end = start_line
        same_line_else = False

        for scan_line in range(start_line, len(_script)):
            line = _script[scan_line]

            # Check for "} else {" on the same line.
            if scan_line > start_line and re.search(r'}\s*else\s*{', line):
                if_end = scan_line
                same_line_else = True
                break

            braces += line.count("{")
            braces -= line.count("}")

            if braces <= 0 and scan_line > start_line:
                if_end = scan_line
                break

        # Find the ELSE block.
        else_start = None
        else_end = None

        if same_line_else:
            # The ELSE starts on the same line as the IF's closing brace.
            else_start = if_end

            # The "{" belonging to ELSE is on this same line.
            braces = 1

            for else_scan_line in range(if_end + 1, len(_script)):
                line = _script[else_scan_line]

                braces += line.count("{")
                braces -= line.count("}")

                if braces <= 0:
                    else_end = else_scan_line
                    break

        else:
            # Check for an ELSE on the following line.
            for scan_line in range(if_end + 1, len(_script)):
                line = _script[scan_line].strip()

                # Ignore blank lines between IF and ELSE.
                if not line:
                    continue

                if re.match(r'(?mi)^else\b', line):
                    else_start = scan_line

                    # Find the end of the ELSE block.
                    braces = 0

                    for else_scan_line in range(else_start, len(_script)):
                        line = _script[else_scan_line]

                        braces += line.count("{")
                        braces -= line.count("}")

                        if braces <= 0 and else_scan_line > else_start:
                            else_end = else_scan_line
                            break

                break

        # Execute the correct block.
        if condition:
            self.execute_script(start_line, if_end, _script)

            # Skip the ELSE block.
            if else_end is not None:
                return else_end

            return if_end

        else:
            # Execute ELSE block if it exists.
            if else_start is not None and else_end is not None:
                self.execute_script(else_start, else_end, _script)
                return else_end

            return if_end

    def cmd_loop(self, start_line, loop_count, script=None):
        # Initialize Defaults
        if script == None:
            _script = self.script
        else:
            _script = script
        # Find the matching closing brace for this Loop block.
        # Use a local end index so nested loops cannot overwrite it mid-run.
        braces = 0
        loop_end = start_line
        for scan_line in range(start_line, len(_script)):
            braces += _script[scan_line].count("{")
            braces -= _script[scan_line].count("}")
            if braces <= 0:
                loop_end = scan_line
                break

        self.loop_end = loop_end
        # execute_script skips start_line and stops at end_line, so the body
        # is start_line+1 .. loop_end-1 (the lines inside the braces).
        for i in range(int(loop_count)):
            self.execute_script(start_line, loop_end, _script)
        return loop_end

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
    def cmd_splitpath(self, line):
        parts = [p.strip() for p in line.split(",")]
        parts = parts[1:]
        # Pad Missing Parameters
        while len(parts) < 6:
            parts.append("")
        input_path, out_file, out_dir, out_ext, out_name, out_drive = parts[:6]
        # Remove Surrounding Quotes If Present
        input_path2 = input_path.strip('"').strip("'")
        if input_path2 == input_path:
            input_path = f"%{input_path}%"
        # Resolve Variables Like %A_LoopFileName%
        input_path = self.handle_variable(input_path)
        directory = os.path.dirname(input_path)
        filename = os.path.basename(input_path)
        name_no_ext, extension = os.path.splitext(filename)
        extension = extension.lstrip(".")
        drive, _ = os.path.splitdrive(input_path)
        # Assign Only Requested Outputs
        if out_file:
            self.local_variables[out_file] = filename
        if out_dir:
            self.local_variables[out_dir] = directory
        if out_ext:
            self.local_variables[out_ext] = extension
        if out_name:
            self.local_variables[out_name] = name_no_ext
        if out_drive:
            self.local_variables[out_drive] = drive
    def cmd_loop_files(self, start_line, file_pattern, mode=None, script=None):
        # Initialize Defaults
        if script == None:
            _script = self.script
        else:
            _script = script
        # Find the matching closing brace for this Loop block.
        braces = 0
        loop_end = start_line
        for scan_line in range(start_line, len(_script)):
            braces += _script[scan_line].count("{")
            braces -= _script[scan_line].count("}")
            if braces <= 0:
                loop_end = scan_line
                break

        self.loop_end = loop_end
        # Resolve variables in the file pattern
        file_pattern = self.handle_variable(file_pattern)
        # Normalize Windows-style paths for cross-platform support
        file_pattern = file_pattern.replace("\\", "/")
        # R = Recursive
        recursive = bool(mode and "r" in mode.lower())
        # Find matching files
        try:
            if recursive:
                matches = glob.glob(file_pattern, recursive=True)
            else:
                matches = glob.glob(file_pattern)
        except Exception as glob_err:
            matches = []
            try:
                messagebox.showerror(
                    "Error",
                    f"Error expanding Loop, Files pattern:\n"
                    f"{file_pattern}\n\n{glob_err}"
                )
            except:
                pass

        # Keep file order deterministic
        matches = sorted(matches)
        # Preserve A_Index for nested loops
        old_a_index = self.local_variables.get("A_Index")
        for idx, filepath in enumerate(matches, 1):
            self.local_variables["A_Index"] = idx
            # Set AHK Loop, Files variables
            self._set_file_loop_variables(filepath)
            # Execute the body
            self.execute_script(start_line, loop_end, _script)
        # Restore A_Index
        if old_a_index is not None:
            self.local_variables["A_Index"] = old_a_index
        else:
            self.local_variables.pop("A_Index", None)
        return loop_end

    def cmd_gosub(self, line):
        try:
            arguments = [p.strip() for p in line.split(",")]
            function_name = arguments[1]
            start = self.labels_start[function_name]
            end = self.labels_end[function_name]
            self.execute_script(start, end)
            return 0

        except KeyError as e:
            return e

    def _ahk_float(self, token):
        """
        Coerce one math operand to float.
        Unset / blank / non-numeric values become 0 (AHK v1 expression behaviour).
        """
        token = "" if token is None else str(token).strip()
        try:
            return float(token)

        except (TypeError, ValueError):
            pass

        resolved = self.handle_variable(token)
        if resolved is None or resolved == "":
            return 0.0

        try:
            return float(resolved)

        except (TypeError, ValueError):
            return 0.0

    def _eval_math(self, value):
        """
        Evaluate a more complex math expression.
        Known script variables are substituted first so a + b + c works.
        """
        expr = str(value)
        def replace_percent(match):
            name = match.group(1)
            return str(self._ahk_float(self._lookup_variable(name, "")))

        expr = re.sub(r"%([A-Za-z_][A-Za-z0-9_]*)%", replace_percent, expr)
        def replace_ident(match):
            name = match.group(0)
            found = self._lookup_variable(name, None)
            if found is not None:
                return str(self._ahk_float(found))

            return name

        expr = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\b", replace_ident, expr)
        try:
            return eval(expr, {"__builtins__": {}}, {})

        except Exception:
            return value

    def handle_math(self, value):
        raw = "" if value is None else str(value).strip()
        if raw == "":
            return 0.0

        # One operator only: left +|-|*|/ right
        # Operands may be numbers, identifiers, or %Var% (including a leading minus).
        math_pattern = (
            r"^\s*"
            r"(%?[A-Za-z_][A-Za-z0-9_]*%?|-?\d+(?:\.\d+)?)"
            r"\s*([+\-*/])\s*"
            r"(%?[A-Za-z_][A-Za-z0-9_]*%?|-?\d+(?:\.\d+)?)"
            r"\s*$"
        )
        match = re.match(math_pattern, raw)
        if match:
            try:
                left = self._ahk_float(match.group(1))
                operator = match.group(2)
                right = self._ahk_float(match.group(3))
                if operator == "+":
                    return left + right

                if operator == "-":
                    return left - right

                if operator == "*":
                    return left * right

                if operator == "/":
                    return left / right

            except Exception:
                pass

        # No single operator, conversion/op failed, or a chained equation (a + b + c).
        return self._eval_math(raw)

    def _lookup_variable(self, name, default=None):
        if name in self.local_variables:
            return self.local_variables[name]

        if name in self.builtin_variables:
            return self.builtin_variables[name]

        return default

    def handle_concat(self, value):
        """
        Evaluate an AHK v1 string expression (used by .=).
        Quoted literals stay literal. Bare identifiers and %Var% resolve
        (missing -> ""). Space and '.' concatenate terms.
        Example: FileName "|"  ->  <FileName> + "|"
        """
        s = "" if value is None else str(value)
        n = len(s)
        i = 0
        parts = []
        escapes = {"n": "\n", "t": "\t", "r": "\r", "s": " ", "`": "`"}
        while i < n:
            ch = s[i]
            if ch.isspace() or ch == ".":
                i += 1
                continue

            if ch in "\"'":
                quote = ch
                i += 1
                buf = []
                while i < n and s[i] != quote:
                    if s[i] == "`" and i + 1 < n:
                        nxt = s[i + 1]
                        buf.append(escapes.get(nxt, nxt))
                        i += 2
                        continue

                    buf.append(s[i])
                    i += 1
                if i < n:
                    i += 1
                parts.append("".join(buf))
                continue

            pct = re.match(r"%([A-Za-z_][A-Za-z0-9_]*)%", s[i:])
            if pct:
                found = self._lookup_variable(pct.group(1), None)
                parts.append("" if found is None else str(found))
                i += pct.end()
                continue

            ident = re.match(r"[A-Za-z_][A-Za-z0-9_]*", s[i:])
            if ident:
                found = self._lookup_variable(ident.group(0), None)
                parts.append("" if found is None else str(found))
                i += ident.end()
                continue

            num = re.match(r"\d+(?:\.\d+)?", s[i:])
            if num:
                parts.append(num.group(0))
                i += num.end()
                continue

            parts.append(ch)
            i += 1
        return "".join(parts)

    def _lookup_builtin_function(self, name):
        if name in self.builtin_functions:
            found = self.builtin_functions[name]
            return found if callable(found) else None
        lower = str(name).lower()
        for key, fn in self.builtin_functions.items():
            if key.lower() == lower and callable(fn):
                return fn
        return None

    def _lookup_user_function(self, name):
        if name in self.functions_start and name in self.functions_end:
            return name
        lower = str(name).lower()
        for key in self.functions_start:
            if key.lower() == lower and key in self.functions_end:
                return key
        return None

    def handle_variable(self, value, line=0, scan_functions=True):
        # %Name% inside a larger string is expanded. A bare identifier
        # that is a known variable is resolved. Missing vars -> "".
        # Literals and expressions (1, 1 + 1, paths, quotes) pass through.
        # When the whole value is Func(args), evaluate the call (nested
        # calls and %Var% inside arguments included).
        if value is None:
            return ""

        raw = str(value)
        stripped = raw.strip()

        if scan_functions:
            function_pattern = r'(?mi)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)\s*$'
            is_function_call = re.match(function_pattern, stripped)
            if is_function_call:
                function_name = is_function_call.group(1)
                parameters = is_function_call.group(2)
                user_name = self._lookup_user_function(function_name)
                if user_name is not None:
                    start_line2 = self.functions_start[user_name]
                    end_line2 = self.functions_end[user_name]
                    self.execute_script(start_line2, end_line2)
                    return raw
                builtin = self._lookup_builtin_function(function_name)
                if builtin is not None:
                    args = self.split_args(parameters)
                    for i in range(len(args)):
                        arg = args[i].strip()
                        if len(arg) >= 2 and arg[0] == arg[-1] and arg[0] in "\"'":
                            # Quoted args stay literal except %Var%.
                            inner = arg[1:-1]
                            args[i] = re.sub(
                                r"%([A-Za-z_][A-Za-z0-9_]*)%",
                                lambda m: (
                                    "" if self._lookup_variable(m.group(1), None) is None
                                    else str(self._lookup_variable(m.group(1), ""))
                                ),
                                inner,
                            )
                        else:
                            resolved = self.handle_variable(arg, line, True)
                            if isinstance(resolved, str) and re.fullmatch(r"-?\d+", resolved):
                                resolved = int(resolved)
                            elif isinstance(resolved, str) and re.fullmatch(r"-?\d+\.\d+", resolved):
                                resolved = float(resolved)
                            args[i] = resolved
                    return builtin(*args)

        def repl_percent(match):
            found = self._lookup_variable(match.group(1), None)
            return "" if found is None else str(found)

        expanded = re.sub(r"%([A-Za-z_][A-Za-z0-9_]*)%", repl_percent, raw)
        if expanded != raw:
            return expanded

        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", stripped):
            found = self._lookup_variable(stripped, None)
            return "" if found is None else str(found)

        return raw

    def read_ini(self, filename):
        for encoding in ("utf-8-sig", "utf-8", "utf-16", "cp1252"):
            try:
                with open(filename, "r", encoding=encoding) as f:
                    return f.readlines()

            except UnicodeError:
                pass

        raise UnicodeError(f"Unable to read {filename}")

    def _get_pending_ini(self, filename):
        """
        Get the in-memory version of an INI file.

        The file is only read from disk once until the pending actions
        are flushed.
        """
        if filename not in self.pending_actions:
            if os.path.exists(filename):
                try:
                    lines = self.read_ini(filename)
                except Exception:
                    lines = []
            else:
                lines = []

            self.pending_actions[filename] = lines

        return self.pending_actions[filename]

    def _flush_pending_actions(self):
        """
        Write all pending INI changes to disk.

        Multiple IniWrite commands targeting the same file therefore
        result in only one actual file write.
        """
        if not self.pending_actions:
            return

        for filename, lines in self.pending_actions.items():
            try:
                with open(filename, "w", encoding="utf-16") as f:
                    f.writelines(lines)
            except Exception as e:
                print(f"Failed to write INI file '{filename}': {e}")

        self.pending_actions.clear()

    def cmd_ini(self, action):
        parts = [x.strip() for x in action.split(",")]
        command = parts[0].lower()
        # IniRead, OutputVar, Filename, Section, Key, Default=ERROR
        if command == "iniread":
            if len(parts) < 5:
                raise SyntaxError(f"{action}, IniRead requires OutputVar, Filename, Section, Key")

            output_var, filename, section, key = parts[1:5]
            default = parts[5] if len(parts) > 5 else "ERROR"
            # Handle Variable
            filename = self.handle_variable(filename)
            if section.startswith("%"):
                section = self.handle_variable(section)
            if key.startswith("%"):
                key = self.handle_variable(key)
            if default.startswith("%"):
                default = self.handle_variable(default)
            # Handle Concatenation
            # Same guard as handle_variable: a bare name like Settings is a
            # literal section/key, not a variable. handle_concat would look it
            # up and turn a missing name into "".
            filename = self.handle_concat(filename)
            if section.startswith("%"):
                section = self.handle_concat(section)
            if key.startswith("%"):
                key = self.handle_concat(key)
            if default.startswith("%"):
                default = self.handle_concat(default)
            # Strip Surrounding Quotes If Present
            filename = filename.strip('"').strip("'")
            section = section.strip('"').strip("'")
            key = key.strip('"').strip("'")
            default = default.strip('"').strip("'")
            # Fix macOS bugs with \
            if sys.platform != "win32":
                filename = filename.replace("\\", "/")
            # Start With The Default; Only Overwrite If The Key Is Actually Found
            value = default
            if filename in self.pending_actions:
                lines = self.pending_actions[filename]
            elif os.path.exists(filename):
                try:
                    lines = self.read_ini(filename)
                except Exception:
                    lines = []
            else:
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

            self.local_variables[output_var] = value
            return

        # IniWrite, Value, Filename, Section, Key
        elif command == "iniwrite":
            if len(parts) < 5:
                raise SyntaxError(
                    f"{action}: IniWrite requires Value, Filename, Section, Key"
                )

            value, filename, section, key = parts[1:5]

            # Resolve %Var% References
            value = self._handle_variable(value)
            filename = self._handle_variable(filename)
            section = self._handle_variable(section)
            key = self._handle_variable(key)

            filename = filename.strip('"').strip("'")
            section = section.strip('"').strip("'")
            key = key.strip('"').strip("'")

            # Fix macOS paths
            if sys.platform != "win32":
                filename = filename.replace("\\", "/")

            # Get the cached/in-memory version of this INI file.
            # This only reads the file from disk the first time.
            lines = self._get_pending_ini(filename)

            found_section = False
            written = False
            output = []

            for line in lines:
                stripped = line.strip()

                # Section header
                if stripped.startswith("[") and stripped.endswith("]"):
                    # We reached the next section without finding the key.
                    if found_section and not written:
                        output.append(f"{key}={value}\n")
                        written = True

                    current_section = stripped[1:-1]
                    found_section = (current_section == section)

                    output.append(line)
                    continue

                # Existing key
                if found_section and "=" in stripped:
                    k, _ = stripped.split("=", 1)

                    if k.strip() == key:
                        output.append(f"{key}={value}\n")
                        written = True
                        continue

                output.append(line)

            # Section does not exist
            if not found_section:
                if output and not output[-1].endswith("\n"):
                    output.append("\n")

                output.append(f"[{section}]\n")
                output.append(f"{key}={value}\n")

            # Section exists but key does not
            elif not written:
                output.append(f"{key}={value}\n")

            # Store the modified file in memory.
            # DO NOT write to disk here.
            self.pending_actions[filename] = output

            return

    def cmd_guicontrol(self, action):
        parts = [x.strip() for x in action.split(",", 3)]
        # GuiControl, Subcommand, Control, Value
        while len(parts) < 4:
            parts.append("")
        _, subcommand, control, value = parts
        widget = self.gui_controls.get(control)
        if widget is None:
            return

        value = self.handle_variable(value)
        subcommand = subcommand.lower()
        if subcommand == "":
            # Set Text/Value (Or Image File For Picture/Image Controls)
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
                widget.insert(0, value)
            elif isinstance(widget, ttk.Combobox):
                widget.set(value)
            elif isinstance(widget, ttk.Checkbutton):
                widget.invoke() if bool(value) != bool(widget.instate(["selected"])) else None
            elif getattr(widget, "_is_gui_image", False):
                pass

            elif isinstance(widget, tk.Label):
                pass

            elif isinstance(widget, tk.Button):
                pass

        elif subcommand == "enable":
            pass

        elif subcommand == "disable":
            pass

        elif subcommand == "hide":
            pass

        elif subcommand == "show":
            pass

    def refresh_windows(self):
        """
        Rebuild the window cache. active_windows stays owner -> title.
        window_list holds the richer records _find_window / WinActivate need
        (hwnd, title, exe, class_name, geometry) without a second enumeration.
        """
        self.active_windows = {}
        self.window_list = []
        if sys.platform == "win32":
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            kernel32 = ctypes.windll.kernel32
            user32 = ctypes.windll.user32

            def win_owner(hwnd):
                pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                handle = kernel32.OpenProcess(
                    PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value
                )
                if not handle:
                    return "Unknown", ""
                try:
                    size = wintypes.DWORD(260)
                    buf = ctypes.create_unicode_buffer(size.value)
                    if kernel32.QueryFullProcessImageNameW(
                        handle, 0, buf, ctypes.byref(size)
                    ):
                        exe = os.path.basename(buf.value) or ""
                        owner = os.path.splitext(exe)[0] or "Unknown"
                        return owner, exe
                    return "Unknown", ""
                finally:
                    kernel32.CloseHandle(handle)

            for window in gw.getAllWindows():
                title = window.title or "<no title>"
                hwnd = getattr(window, "_hWnd", None) or getattr(window, "_hwnd", None)
                owner, exe = win_owner(hwnd) if hwnd else ("Unknown", "")
                class_name = ""
                if hwnd:
                    try:
                        class_buf = ctypes.create_unicode_buffer(256)
                        user32.GetClassNameW(hwnd, class_buf, 256)
                        class_name = class_buf.value or ""
                    except Exception:
                        class_name = ""
                self.active_windows[owner] = title
                self.window_list.append({
                    "hwnd": int(hwnd) if hwnd else 0,
                    "title": title,
                    "exe": exe,
                    "class_name": class_name,
                    "left": int(getattr(window, "left", 0) or 0),
                    "top": int(getattr(window, "top", 0) or 0),
                    "width": int(getattr(window, "width", 0) or 0),
                    "height": int(getattr(window, "height", 0) or 0),
                })
        elif sys.platform == "darwin":
            # Get a list of on-screen windows (excluding desktop elements)
            window_list = Quartz.CGWindowListCopyWindowInfo(
                Quartz.kCGWindowListExcludeDesktopElements | Quartz.kCGWindowListOptionOnScreenOnly,
                Quartz.kCGNullWindowID
            )

            for window in window_list:
                owner = window.get(Quartz.kCGWindowOwnerName, "Unknown") or "Unknown"
                title = window.get(Quartz.kCGWindowName, "<no title>") or "<no title>"
                bounds = window.get(Quartz.kCGWindowBounds, {}) or {}
                hwnd = window.get(Quartz.kCGWindowNumber, 0) or 0
                self.active_windows[owner] = title
                self.window_list.append({
                    "hwnd": int(hwnd) if hwnd else 0,
                    "title": title,
                    "exe": owner if owner != "Unknown" else "",
                    "class_name": "",
                    "left": int(bounds.get("X", 0) or 0),
                    "top": int(bounds.get("Y", 0) or 0),
                    "width": int(bounds.get("Width", 0) or 0),
                    "height": int(bounds.get("Height", 0) or 0),
                })
        elif sys.platform.startswith("linux"):
            # Import is `display as Xdisplay`; reuse the shared connection.
            disp = _get_xdisplay()
            root = disp.screen().root
            NET_CLIENT_LIST = disp.intern_atom("_NET_CLIENT_LIST")
            NET_WM_NAME = disp.intern_atom("_NET_WM_NAME")
            NET_WM_PID = disp.intern_atom("_NET_WM_PID")
            UTF8_STRING = disp.intern_atom("UTF8_STRING")
            prop = root.get_full_property(NET_CLIENT_LIST, X.AnyPropertyType)
            if not prop:
                return
            for win_id in prop.value:
                try:
                    window = disp.create_resource_object("window", win_id)
                except Exception:
                    continue
                title = None
                try:
                    net_name = window.get_full_property(NET_WM_NAME, UTF8_STRING)
                    if net_name and net_name.value:
                        raw = net_name.value
                        title = raw.decode("utf-8", errors="replace") if isinstance(raw, bytes) else str(raw)
                except Exception:
                    pass
                if not title:
                    try:
                        wm_name = window.get_wm_name()
                        if wm_name:
                            title = wm_name if isinstance(wm_name, str) else str(wm_name)
                    except Exception:
                        pass
                if not title:
                    title = "<no title>"
                owner = "Unknown"
                try:
                    pid_prop = window.get_full_property(NET_WM_PID, X.AnyPropertyType)
                    if pid_prop and pid_prop.value:
                        comm_path = f"/proc/{int(pid_prop.value[0])}/comm"
                        with open(comm_path, "r", encoding="utf-8") as comm:
                            owner = comm.read().strip() or owner
                except Exception:
                    pass
                class_name = ""
                class_instance = ""
                try:
                    wm_class = window.get_wm_class()
                    if wm_class:
                        class_instance = wm_class[0] if wm_class else ""
                        class_name = wm_class[1] if len(wm_class) > 1 else wm_class[0]
                        if owner == "Unknown":
                            owner = class_name or class_instance or owner
                except Exception:
                    pass
                left, top, width, height = 0, 0, 0, 0
                try:
                    geom = window.get_geometry()
                    width, height = geom.width, geom.height
                    try:
                        abs_coords = root.translate_coords(window, 0, 0)
                        left, top = abs_coords.x, abs_coords.y
                    except Exception:
                        left, top = geom.x, geom.y
                except Exception:
                    pass
                self.active_windows[owner] = title
                self.window_list.append({
                    "hwnd": int(win_id),
                    "title": title,
                    "exe": owner if owner != "Unknown" else (class_instance or ""),
                    "class_name": class_name,
                    "left": left,
                    "top": top,
                    "width": width,
                    "height": height,
                })

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

        remaining = criteria
        m = re.search(r"\bahk_exe\s+([^\s]+)", remaining, re.IGNORECASE)
        if m:
            result["exe"] = m.group(1)
            remaining = remaining[:m.start()] + remaining[m.end():]
        m = re.search(r"\bahk_class\s+([^\s]+)", remaining, re.IGNORECASE)
        if m:
            result["class_name"] = m.group(1)
            remaining = remaining[:m.start()] + remaining[m.end():]
        m = re.search(r"\bahk_id\s+([^\s]+)", remaining, re.IGNORECASE)
        if m:
            try:
                result["hwnd"] = int(m.group(1), 0)
            except ValueError:
                pass
            remaining = remaining[:m.start()] + remaining[m.end():]
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
            want_base = want[:-4] if want.endswith(".exe") else want
            have = (info.get("exe") or "").lower()
            have_base = have[:-4] if have.endswith(".exe") else have
            if want not in have and want_base not in have_base and have_base not in want_base:
                return False

        if criteria.get("class_name"):
            if (info.get("class_name") or "").lower() != criteria["class_name"].lower():
                return False

        if criteria.get("title"):
            title = (info.get("title") or "")
            if criteria["title"].lower() not in title.lower():
                return False

        if not any([criteria.get("title"), criteria.get("exe"),
                    criteria.get("class_name"), criteria.get("hwnd") is not None]):
            return False

        return True

    def _find_window(self, criteria_str):
        """Find the first matching window. Returns info dict or None."""
        self.refresh_windows()
        criteria = self._parse_window_criteria(criteria_str)
        for info in self.window_list:
            if self._window_matches(info, criteria):
                return info
        return None

    def win_exist(self, criteria=""):
        """AHK-compatible WinExist. Returns True if a matching window is found."""
        return self._find_window(criteria) is not None

    def cmd_winactivate(self, action):
        """
        WinActivate [, WinTitle]
        Brings the matching window to the foreground.
        """
        # Parse: Winactivate, Title   Or   Winactivate Title
        if "," in action:
            _, rest = action.split(",", 1)
            criteria = rest.strip()
        else:
            parts = action.split(None, 1)
            criteria = parts[1] if len(parts) > 1 else ""
        criteria = self.handle_variable(criteria)
        info = self._find_window(criteria)
        if info is None:
            return

        if sys.platform == "win32":
            try:
                user32 = ctypes.windll.user32
                hwnd = info["hwnd"]
                # Restore If Minimized
                if user32.IsIconic(hwnd):
                    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                user32.SetForegroundWindow(hwnd)
            except Exception:
                pass

        elif sys.platform == "darwin":
            try:
                # Prefer Process Name (Exe) For Activation
                process_name = info.get("exe") or ""
                title = info.get("title") or ""
                if process_name:
                    script = f'''
                    tell application "System Events"
                        set frontmost of process "{process_name}" to true
                    end tell
                    '''
                else:
                    # Fallback By Title (Less Reliable)
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
        if "," not in action:
            return

        _, rest = action.split(",", 1)
        parts = [p.strip() for p in rest.split(",")]
        while len(parts) < 5:
            parts.append("")
        out_x, out_y, out_w, out_h, criteria = parts[:5]
        criteria = self.handle_variable(criteria)
        info = self._find_window(criteria)
        if info is None:
            # AHK leaves the variables unchanged if not found; set to 0 for safety.
            if out_x:
                self.local_variables[out_x] = 0
            if out_y:
                self.local_variables[out_y] = 0
            if out_w:
                self.local_variables[out_w] = 0
            if out_h:
                self.local_variables[out_h] = 0
            return

        if out_x:
            self.local_variables[out_x] = info["left"]
        if out_y:
            self.local_variables[out_y] = info["top"]
        if out_w:
            self.local_variables[out_w] = info["width"]
        if out_h:
            self.local_variables[out_h] = info["height"]

if __name__ == "__main__":
    if open_mode == "Editor":
        app = MainGUI()
        app.mainloop()
    elif open_mode == "Playback":
        playback = Playback(playback_path)