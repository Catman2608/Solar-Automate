# Imports
import tkinter as tk
from tkinter import ttk, messagebox
# Misc
import webbrowser
import sys
import os
import re
# Keyboard and Mouse clicks (platform-specific)
from pynput.keyboard import Listener as KeyListener, Key
from pynput import keyboard, mouse
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
elif sys.platform == "darwin":
    import Quartz
    from AppKit import NSScreen
elif sys.platform == "linux":
    from Xlib import X, XK, display as Xdisplay
    from Xlib.ext import xtest
# Define platform-specific constants
# All platforms
keyboard_controller = KeyboardController()
mouse_controller = MouseController()
macro_running = False
macro_thread = None
APP_VERSION = "3.0"
BETA_VERSION = 0
try:
    playback_path = sys.argv[1]
    open_mode = "Playback"
except:
    open_mode = "Editor"
    folder_path = os.getcwd()
open_mode = "Playback"
file_path = "test.ahk"
playback_path = os.path.join(folder_path, file_path)
def open_link(url):
    webbrowser.open(url)
class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("700x350")
        self.title("AutoHotKey Dash")
        # Sidebar
        self.sidebar = tk.Frame(self, width=300)
        self.sidebar.pack(side="left", fill="y")
        # FIX 1: Prevent sidebar from shrinking below 300px
        self.sidebar.pack_propagate(False)
        self.sidebar.config(width=250)  # Ensure width is explicitly set
        # Main content
        self.content = tk.Frame(self)
        self.content.pack(side="right", fill="both", expand=True)
        # Build UI
        self.build_sidebar()
        self.build_main_content()
        self.mainloop()
    def build_sidebar(self):
        # Configure button style to prevent dark mode auto-coloring
        tk.Button(
            self.sidebar,
            text="New Script"
        ).pack(fill="x", padx=5, pady=5)
        tk.Button(
            self.sidebar,
            text="Compile"
        ).pack(fill="x", padx=5, pady=5)
        tk.Button(
            self.sidebar,
            text="Help Files"
        ).pack(fill="x", padx=5, pady=5)
        tk.Button(
            self.sidebar,
            text="Window Spy"
        ).pack(fill="x", padx=5, pady=5)
        tk.Button(
            self.sidebar,
            text="Launch Settings"
        ).pack(fill="x", padx=5, pady=5)
        tk.Button(
            self.sidebar,
            text="Editor Settings"
        ).pack(fill="x", padx=5, pady=5)
        tk.Button(
            self.sidebar,
            text="Record Script"
        ).pack(fill="x", padx=5, pady=5)
        tk.Button(
            self.sidebar,
            text="AHK Visual Editor"
        ).pack(fill="x", padx=5, pady=5)
    def build_main_content(self):
        body = tk.Frame(self.content)
        body.pack(anchor="nw", fill="both", expand=True, padx=5, pady=10)
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
        ).pack(anchor="w", fill="x", padx=5, pady=0)
        tk.Button(
            body,
            text="How to Write Hotkeys"
        ).pack(anchor="w", fill="x", padx=5, pady=0)
        tk.Button(
            body,
            text="How to Send Keystrokes"
        ).pack(anchor="w", fill="x", padx=5, pady=0)
        tk.Button(
            body,
            text="How to Run Programs"
        ).pack(anchor="w", fill="x", padx=5, pady=0)
        tk.Button(
            body,
            text="How to Manage Windows"
        ).pack(anchor="w", fill="x", padx=5, pady=0)
        tk.Button(
            body,
            text="Quick Reference"
        ).pack(anchor="w", fill="x", padx=5, pady=0)
        tk.Checkbutton(
            body,
            text="Show this info next time",
            anchor="w"
        ).pack(fill="x", padx=5)
class Playback(tk.Tk):
    def __init__(self, playback_path):
        super().__init__()
        self.background_color = "white"
        self.foreground_color = "black"
        self.max_x = 0
        self.max_y = 0
        self.variables = {}
        self._init_builtin_variables()
        self.font_bold = False
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
        with open(playback_path, "r", encoding="utf-8") as f:
            self.script_text = f.read()
        self.script = self.script_text.splitlines()
        self.after(0, self.withdraw)
        self.build_main_content()
        self.mainloop()
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
        import sys
        # Screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
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
        }
    def _normalize_condition(self, condition):
        # Replace <> with !=
        condition = condition.replace("<>", "!=")
        # Replace = with == ONLY when it's a comparison
        condition = re.sub(r'(?<![<>=!])=(?!=)', '==', condition)
        return condition
    def _evaluate_loop_count(self, line):
        """
        Evaluates:
            Loop, 5
            Loop, %Amount%
            Loop
        """
        try:
            parts = line.split(",", 1)
            # Infinite/default loop style
            if len(parts) < 2:
                return 1
            count_part = parts[1].replace("{", "").strip()
            # Variable dereference
            if count_part.startswith("%") and count_part.endswith("%"):
                var_name = count_part[1:-1]
                value = self.variables.get(var_name, 1)
                return int(value)
            return int(count_part.split()[0])
        except Exception as e:
            print(f"[LOOP ERROR] {line} → {e}")
            return 1
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
        condition = condition.strip()
        if condition.startswith("(") and condition.endswith(")"):
            condition = condition[1:-1]
        # Normalize operators
        condition = self._normalize_condition(condition)
        # Replace %VarName% tokens
        condition = self._handle_variable(condition)
        # Replace bare variable names (no % signs) that match known variables/builtins
        def replace_bare(match):
            name = match.group(0)
            if name in self.variables:
                val = self.variables[name]
                return str(int(val)) if isinstance(val, float) and val == int(val) else str(val)
            if name in self.builtin_variables:
                val = self.builtin_variables[name]
                return str(int(val)) if isinstance(val, float) and val == int(val) else str(val)
            return name  # leave unknown words untouched (e.g. "and", "or", "not")
        condition = re.sub(r'\b[A-Za-z_]\w*\b', replace_bare, condition)
        try:
            return bool(eval(condition))
        except Exception as e:
            self.raise_error(condition, f"IF condition error: {e}")
    def _extract_if_blocks(self, actions, start_index):
        """
        Extracts:
        if (condition = 0) {
            ; content
        } else if (condition = 1) {
            ; content 2
        } else {
            ; content 3
        }

        Returns:
            (condition, if_block, else_block, ending_index)
        """
        line = actions[start_index].strip()
        # Remove "If"
        condition = line[2:].strip()
        # Extract IF body
        if_block, end_index = self._extract_block(actions, start_index)
        else_block = []
        i = end_index + 1
        while i < len(actions):
            current = actions[i].strip()
            if not current or current.startswith(";"):
                i += 1
                continue
            lower = current.lower()
            # Else If
            if lower.startswith("else if"):
                # Convert:
                # Else If (x > 5)
                # into:
                # If (x > 5)
                nested_if = "If" + current[7:]
                fake_actions = [
                    nested_if
                ] + actions[i+1:]
                _, _, else_block, nested_end = self._extract_if_blocks(
                    fake_actions,
                    0
                )
                # Need the true branch from nested IF
                nested_condition, nested_true, nested_false, _ = self._extract_if_blocks(
                    fake_actions,
                    0
                )
                else_block = [
                    f"If {nested_condition}"
                ]
                else_block.extend(["{"])
                else_block.extend(nested_true)
                else_block.append("}")
                if nested_false:
                    else_block.append("Else")
                    else_block.append("{")
                    else_block.extend(nested_false)
                    else_block.append("}")
                end_index = i + nested_end
                break
            # Normal Else
            elif lower.startswith("else"):
                else_block, else_end = self._extract_block(actions, i)
                end_index = else_end
                break
            break
        return condition, if_block, else_block, end_index
    def _extract_block(self, actions, start_index):
        """
        Extracts a { ... } block starting after a Loop/If/etc statement.
        Returns:
            (block_lines, ending_index)
        """
        block = []
        i = start_index
        line = actions[i].strip()
        # Detect opening brace
        if "{" in line:
            brace_depth = line.count("{") - line.count("}")
            i += 1
        else:
            i += 1
            if i >= len(actions):
                return [], i
            next_line = actions[i].strip()
            if next_line == "{":
                brace_depth = 1
                i += 1
            else:
                # Single-line loop
                return [actions[i]], i
        # Collect block
        while i < len(actions) and brace_depth > 0:
            current = actions[i]
            stripped = current.strip()
            open_count = stripped.count("{")
            close_count = stripped.count("}")
            brace_depth += open_count
            brace_depth -= close_count
            # Don't include pure closing braces
            if stripped != "}":
                block.append(current)
            i += 1
        return block, i - 1
    def _execute_script(self, actions):
        """Process a list of script lines (supports nested loops via recursion on blocks)."""
        i = 0
        while i < len(actions):
            raw_line = actions[i]
            line = raw_line.strip()
            if not line or line.startswith(";"):
                i += 1
                continue
            # Return breaks the (current) execution scope
            if line.lower() == "return":
                break
            # Variable assignment  (x := expr)
            if self._handle_assignment(line):
                i += 1
                continue
            # Math shorthand  (x += 5 / x -= 2 / x *= 3 / x /= 2)
            if self._handle_math(line):
                i += 1
                continue
            # Loop command (uses the pre-existing helper functions)
            if line.lower().startswith("loop"):
                count = self._evaluate_loop_count(line)
                block, end_index = self._extract_block(actions, i)
                # Temporarily set A_Index (1-based) for AHK compatibility; restore for nesting
                old_a_index = self.variables.get("A_Index")
                for idx in range(1, count + 1):
                    self.variables["A_Index"] = idx
                    self._execute_script(block)
                if old_a_index is not None:
                    self.variables["A_Index"] = old_a_index
                else:
                    self.variables.pop("A_Index", None)
                i = end_index + 1
                continue
            if line.lower().startswith("if"):
                condition, if_block, else_block, end_index = self._extract_if_blocks(actions, i)
                if self._evaluate_condition(condition):
                    self._execute_script(if_block)
                else:
                    self._execute_script(else_block)
                i = end_index + 1
                continue
            if line.lower().startswith("while"):
                condition = line[5:].strip()
                # Extract the while block
                block, end_index = self._extract_block(actions, i)
                while self._evaluate_condition(
                    self._handle_variable(condition)
                ):
                    self._execute_script(block)
                i = end_index + 1
                continue
            # Substitute %Var% tokens before dispatching other commands
            processed_line = self._handle_variable(line)
            print(processed_line)
            # All commands go here
            if processed_line.startswith("Gui"):
                self.cmd_gui(processed_line)
            if processed_line.startswith("MsgBox"):
                self._cmd_msgbox(processed_line)
            # TODO: integrate other commands e.g.
            # elif processed_line.lower().startswith(("click", "send")):
            #     ...
            i += 1
    # Final playback
    def build_main_content(self):
        self._execute_script(self.script)
    # Commands
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
                self.raise_error(
                    action,
                    f"Cannot overwrite built-in variable: {var}"
                )
            # Numeric values
            # Build a merged namespace: builtins first, then user vars (user vars win on conflict)
            eval_namespace = {**self.builtin_variables, **self.variables}
            try:
                self.variables[var] = eval(value, {}, eval_namespace)
            # Raw expression/string
            except:
                self.variables[var] = value
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
    def _handle_variable(self, text):
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
            # Splitting elements
            if command3.startswith("x") or command3.startswith("w"):
                options = {}
                for token in command3.split():
                    key = token[0]
                    value = token[1:]
                    options[key] = value
                try:
                    if parent is not self:
                        options["x"] = str(int(float(options["x"])) - 10)
                        options["y"] = str(int(float(options["y"])) - 30)
                except:
                    pass
            # Tabs
            if "|" in command4:
                tabs = command4.split("|")
            # Handle Colors
            if command == "Font":
                color = None
                bold = False
                for token in command2.split():
                    # Color option
                    if token.lower().startswith("c"):
                        color = token[1:]
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
                notebook = ttk.Notebook(self, padding=10, style="Dark.TNotebook")
                notebook.place(x=0, y=0, width=safe_int(options["w"]) + 10, height=safe_int(options["h"]) + 20)
                self.notebook = notebook  # Store notebook reference
                self.tabs = {}  # Store tab frames
                for i, tab_name in enumerate(tabs):
                    tab_frame = ttk.Frame(notebook, style="Dark.TFrame")
                    notebook.add(tab_frame, text=tab_name)
                    self.tabs[tab_name] = tab_frame
                self.max_x = max(self.max_x, safe_int(options["w"]))
                self.max_y = max(self.max_y, safe_int(options["h"]))
            # Handle Tab switching
            elif command == "Tab":
                if command2 and command2 in self.tabs:
                    self.current_tab = self.tabs[command2]
                else:
                    self.current_tab = self
            # Text, edit, show, hide
            font_style = "bold" if self.font_bold else "normal"
            if command2 == "Text":
                tk.Label(parent, text=command4, bg=self.background_color, fg=self.foreground_color, font=("Segoe UI", 9, font_style)).place(x=safe_int(options["x"]), y=safe_int(options["y"]))
                right = safe_int(options["x"]) + safe_int(options.get("w", 0))
                bottom = safe_int(options["y"]) + safe_int(options.get("h", 0))
                self.max_x = max(self.max_x, right)
                self.max_y = max(self.max_y, bottom)
            elif command2 == "Edit":
                tk.Entry(parent, width=30).place(x=safe_int(options["x"]), y=safe_int(options["y"]), width=safe_int(options["w"]))
                right = safe_int(options["x"]) + safe_int(options.get("w", 0))
                bottom = safe_int(options["y"]) + safe_int(options.get("h", 0))
                self.max_x = max(self.max_x, right)
                self.max_y = max(self.max_y, bottom)
            elif command2 == "GroupBox":
                group = tk.LabelFrame(parent, text=command4, borderwidth=3, bg=self.background_color, fg=self.foreground_color, font=("Segoe UI", 9, font_style))
                group.place(x=safe_int(options["x"]), y=safe_int(options["y"]), width=safe_int(options["w"]), height=safe_int(options["h"]))
                right = safe_int(options["x"]) + safe_int(options.get("w", 0))
                bottom = safe_int(options["y"]) + safe_int(options.get("h", 0))
                self.max_x = max(self.max_x, right)
                self.max_y = max(self.max_y, bottom)
            elif command2 == "Button":
                button = tk.Button(parent, text=command4)
                button.place(x=safe_int(options["x"]), y=safe_int(options["y"]), width=safe_int(options["w"]), height=safe_int(options["h"]))
                right = safe_int(options["x"]) + safe_int(options.get("w", 0))
                bottom = safe_int(options["y"]) + safe_int(options.get("h", 0))
                self.max_x = max(self.max_x, right)
                self.max_y = max(self.max_y, bottom)
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
                label.place(
                    x=safe_int(options["x"]),
                    y=safe_int(options["y"])
                )
            elif command2 == "ComboBox":
                values = command4.split("|")
                ttk.Combobox(
                    parent,
                    values=values
                ).place(
                    x=safe_int(options["x"]),
                    y=safe_int(options["y"]),
                    width=safe_int(options["w"])
                )
            elif command2 == "Checkbox":
                try:
                    ttk.Checkbutton(
                        parent,
                        text=command4,
                        style="Dark.TCheckbutton"
                    ).place(
                        x=safe_int(options["x"]),
                        y=safe_int(options["y"])
                    )
                except:
                    pass
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
            self.raise_error(action, str(e))
    def _cmd_click(self, action):
        """
        Supports AHK Click syntax variants (Normal click only for now):
          Click                          → left click at current pos
          Click, X, Y                    → left click at X, Y
          Click, X, Y, Down Right        → press right button at X, Y
          Click, Down                    → press left button at current pos
          Click, Right                   → right click at current pos
          Click, Down Right              → press right button at current pos
          (any combination of optional X, Y, Down/Up, Left/Right/Middle)
        """
        try:
            # Split off the command name; args may be empty
            if "," in action:
                _, args = action.split(",", 1)
                parts = [p.strip() for p in args.split(",")]
            else:
                parts = []
            # Classify each token: numeric → coordinate, else → modifier word
            # AHK order: [X, Y,] [Down|Up] [Left|Right|Middle]
            coords = []
            modifiers = []
            for p in parts:
                if p == "":
                    continue
                try:
                    coords.append(int(float(p)))
                except ValueError:
                    # Could be "Down Right" in one comma-field, split on spaces
                    for word in p.split():
                        modifiers.append(word.lower())
            # Resolve X, Y
            if len(coords) >= 2:
                x, y = coords[0], coords[1]
                move = True
            else:
                move = False   # stay at current cursor position
            # Resolve button and down/up from modifier words
            btn_map = {
                "left": mouse.Button.left,
                "l":    mouse.Button.left,
                "right": mouse.Button.right,
                "r":    mouse.Button.right,
                "middle": mouse.Button.middle,
                "m":    mouse.Button.middle,
            }
            direction_words = {"down", "up"}
            button_words    = set(btn_map.keys())
            down_up = "click"   # default: full click
            button  = mouse.Button.left  # default button
            for word in modifiers:
                if word in direction_words:
                    down_up = word
                elif word in button_words:
                    button = btn_map[word]
            # Move if coordinates were supplied
            if move:
                mouse_controller.position = (x, y)
            # Execute
            if down_up == "down":
                mouse_controller.press(button)
            elif down_up == "up":
                mouse_controller.release(button)
            else:
                mouse_controller.click(button)
            return
        except Exception as e:
            return e
if __name__ == "__main__":
    if open_mode == "Editor":
        app = MainGUI()
        app.mainloop()
    elif open_mode == "Playback":
        playback = Playback(playback_path)