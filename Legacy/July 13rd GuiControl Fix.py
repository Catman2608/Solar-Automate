# Imports
import tkinter as tk
from tkinter import ttk, messagebox
# Misc
import webbrowser
import sys
import os
import re
import traceback
import math
# File management
import configparser
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
file_path = "Solar Fishing V4 Lite.ahk"
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
        self.gui_variables = {}
        self.gui_controls = {}
        self.functions = {}
        self.labels = {}
        self._init_builtin_variables()
        self.font_bold = False
        self.current_line_count = 0
        self.font_size = 9
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
        with open(playback_path, "r", encoding="utf-8-sig") as f:
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
            "A_ScriptDir": script_directory
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
        condition = self._extract_if_condition(line)
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
                if isinstance(val, str):
                    return repr(val)

                return str(int(val)) if isinstance(val, float) and val == int(val) else str(val)

            if name in self.builtin_variables:
                val = self.builtin_variables[name]
                if isinstance(val, str):
                    return repr(val)

                return str(int(val)) if isinstance(val, float) and val == int(val) else str(val)

            return name  # leave unknown words untouched (e.g. "and", "or", "not")

        condition = re.sub(r'\b[A-Za-z_]\w*\b', replace_bare, condition)
        # Convert AHK backslash paths to Python-safe strings
        condition = re.sub(
            r'"([^"]*?)\\([^"]*?)"',
            lambda m: '"' + m.group(1) + r'\\' + m.group(2) + '"',
            condition
        )
        try:
            return bool(eval(condition,{},self._get_eval_namespace()))

        except Exception as e:
            full_error = traceback.format_exc()
            error = full_error.splitlines()
            try:
                messagebox.showerror("title", f"Error at line {self.current_line_count + 1}\n\nLine text: {error[5]}\n{error[7]}\n\nThe program will exit")
            except:
                messagebox.showerror("title", f"Error at line {self.current_line_count + 1}\n\nLine text: {error[2]}\n{error[5]}\n\nThe program will exit")
            raise SyntaxError(e)
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
        # Replace <> with !=
        condition = condition.replace("<>", "!=")
        condition = condition.replace("||", " or ")
        condition = condition.replace("&&", " and ")
        # Replace = with == ONLY when it's a comparison
        condition = re.sub(r'(?<![<>=!])=(?!=)', '==', condition)
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
            value = eval(expr, {}, self._get_eval_namespace())
            return int(value)
        
        except Exception as e:
            full_error = traceback.format_exc()
            error = full_error.splitlines()
            try:
                messagebox.showerror("title", f"Invalid Loop Count: {e}\n\nLine text: {error[5]}\n{error[7]}\n\nThe program will exit")
            except:
                messagebox.showerror("title", f"Invalid Loop Count: {e}\n\nLine text: {error[2]}\n{error[4]}\n\nThe program will exit")
            return 1

    def _is_function_definition(self, line):
        if not re.match(r"^[A-Za-z_]\w*\s*\([^)]*\)\s*\{?\s*$", line):
            return False

        if re.match(r"^(if|while|loop|for)\b", line, re.IGNORECASE):
            return False

        return line.rstrip().endswith("{")

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

    def _get_eval_namespace(self):
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

        return {
            **self.builtin_variables,
            **self.variables,

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

            "IsInteger": lambda v: isinstance(v, int) or (isinstance(v, str) and v.isdigit()),
            "IsNumber": lambda v: str(v).replace(".", "", 1).isdigit(),
        }

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
            try:
                self.variables[var] = eval(value, {}, self._get_eval_namespace())
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
                    rhs_val = float(eval(rhs, {}, self._get_eval_namespace()))
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

    def cmd_ini(self, action):
        parts = [x.strip() for x in action.split(",")]
        command = parts[0].lower()
        if command == "iniwrite":
            if len(parts) < 5:
                self.raise_error(action, "IniWrite requires Value, Filename, Section, Key")
                return

            value = parts[1]
            filename = parts[2]
            section = parts[3]
            key = parts[4]
            config = configparser.ConfigParser()
            if os.path.exists(filename):
                config.read(filename)
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, key, value)
            with open(filename, "w") as f:
                config.write(f)
            return

        elif command == "iniread":
            if len(parts) < 5:
                self.raise_error(action, "IniRead requires OutputVar, Filename, Section, Key")
                return

            output_var = parts[1]
            filename = parts[2]
            section = parts[3]
            key = parts[4]
            config = configparser.ConfigParser()
            config.read(filename)
            try:
                value = config.get(section, key)
            except Exception:
                value = ""
            # Store result like AHK OutputVar
            self.variables[output_var] = value
            return

    def raise_error(self, action, msg=""):
        try:
            messagebox.showerror(
                "Solar Error",
                f"Error processing:\n{action}\n\n{msg}\n\nThe program will exit"
            )
        except Exception:
            pass
        # Exit to match AHK behavior on error
        import sys
        sys.exit(1)

    def cmd_guicontrol(self, action):
        """
        GuiControl [, Sub-command, ControlID, Value]
        Supports setting text, enable/disable, hide/show (partial)
        ControlID is the vVar name from options vXXX
        """
        try:
            parts = [x.strip() for x in action.split(",", 3)]
            while len(parts) < 4:
                parts.append("")
            # parts[0] = "GuiControl", [1]=subcmd or "", [2]=controlID (v name), [3]=value
            _, subcommand, control, value = parts
            widget = self.gui_controls.get(control)
            if widget is None:
                # Try by name if not found? or ignore
                return
            subcommand = subcommand.lower().strip()
            if subcommand == "" or subcommand == "text":
                # Set text/value
                if isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, value)
                elif isinstance(widget, ttk.Combobox):
                    widget.set(value)
                elif isinstance(widget, tk.Label) or isinstance(widget, tk.LabelFrame):
                    widget.config(text=value)
                elif isinstance(widget, tk.Button):
                    widget.config(text=value)
                elif hasattr(widget, "delete") and hasattr(widget, "insert"):  # fallback
                    try:
                        widget.delete(0, tk.END)
                        widget.insert(0, value)
                    except:
                        pass
            elif subcommand in ("enable", "enabled"):
                try:
                    widget.configure(state="normal")
                except:
                    pass
            elif subcommand in ("disable", "disabled"):
                try:
                    widget.configure(state="disabled")
                except:
                    pass
            elif subcommand == "hide":
                try:
                    widget.place_forget()
                except:
                    pass
            elif subcommand == "show":
                # Partial: would need stored original position; for now do nothing or re-place if possible
                pass
        except Exception as e:
            self.raise_error(action, str(e))

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
                if "v" in options:
                    self.gui_variables[options["v"]] = text  # for Submit if needed, though Label has no .get()
                    self.gui_controls[options["v"]] = text
                text.place(x=safe_int(options["x"]), y=safe_int(options["y"]))
                right = safe_int(options["x"]) + safe_int(options.get("w", 0))
                bottom = safe_int(options["y"]) + safe_int(options.get("h", 0))
                self.max_x = max(self.max_x, right)
                self.max_y = max(self.max_y, bottom)
            elif command2 == "Edit":
                var = tk.StringVar()
                if command4:
                    var.set(command4)
                entry = tk.Entry(parent, textvariable=var, bg="white", fg="black", insertbackground="black", disabledbackground="white", disabledforeground="black",)
                # Initialize values
                if not "h" in options:
                    options["h"] = 28 if sys.platform == "darwin" else 30
                entry.place(x=safe_int(options["x"]),y=safe_int(options["y"]),width=safe_int(options["w"]),height=safe_int(options["h"]))
                if "v" in options:
                    self.gui_variables[options["v"]] = var
                    self.gui_controls[options["v"]] = entry
                right = safe_int(options["x"]) + safe_int(options.get("w", 0))
                bottom = safe_int(options["y"]) + safe_int(options.get("h", 0))
                self.max_x = max(self.max_x, right)
                self.max_y = max(self.max_y, bottom)
            elif command2 == "GroupBox":
                group = tk.LabelFrame(parent, text=command4, borderwidth=3, bg=self.background_color, fg=self.foreground_color, font=("Segoe UI", self.font_size, font_style))
                if "v" in options:
                    self.gui_controls[options["v"]] = group
                group.place(x=safe_int(options["x"]), y=safe_int(options["y"]), width=safe_int(options["w"]), height=safe_int(options["h"]))
                right = safe_int(options["x"]) + safe_int(options.get("w", 0))
                bottom = safe_int(options["y"]) + safe_int(options.get("h", 0))
                self.max_x = max(self.max_x, right)
                self.max_y = max(self.max_y, bottom)
            elif command2 == "Button":
                def _btn_cmd():
                    if "g" in options:
                        self.execute_gosub(options["g"])
                button = tk.Button(parent, text=command4, command=_btn_cmd)
                if "v" in options:
                    self.gui_controls[options["v"]] = button
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
                    x=safe_int(options.get("x", 0)),
                    y=safe_int(options.get("y", 0))
                )
            elif command2 == "ComboBox":
                values = command4.split("|")
                var = tk.StringVar()
                if values:
                    var.set(values[0])
                combobox = ttk.Combobox(parent, values=values, textvariable=var)
                if "v" in options:
                    self.gui_variables[options["v"]] = var
                    self.gui_controls[options["v"]] = combobox
                combobox.place(
                    x=safe_int(options["x"]),
                    y=safe_int(options["y"]),
                    width=safe_int(options["w"])
                )
                if "g" in options:
                    try:
                        combobox.bind("<<ComboboxSelected>>", lambda event: self.execute_gosub(options["g"]))
                    except:
                        pass
            elif command2 == "Checkbox":
                try:
                    var = tk.BooleanVar()
                    checkbox = ttk.Checkbutton(
                        parent,
                        text=command4,
                        variable=var,
                        style="Dark.TCheckbutton"
                    )
                    if "v" in options:
                        self.gui_variables[options["v"]] = var
                        self.gui_controls[options["v"]] = checkbox
                    checkbox.place(
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
    def _execute_script(self, actions):
        """
        Process a list of script lines (supports nested loops via recursion on blocks).
        Uses self.current_line_count to get the line
        """
        actions = self._normalize_inline_else_lines(actions)
        self.current_line_count = 0
        while self.current_line_count < len(actions):
            raw_line = actions[self.current_line_count]
            line = raw_line.strip()
            line = self._strip_inline_comment(line)
            if not line or line.startswith(";"):
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

            # Function definition
            if self._is_function_definition(line):
                name = line.split("(")[0].strip()
                # Extract the function body
                body_lines, end_index = self._extract_block(actions, self.current_line_count)
                self.functions[name] = body_lines
                self.current_line_count = end_index + 1
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
                    self.current_line_count += 1
                continue

            # Label definition
            if self._is_label_definition(line):
                name = line[:-1].strip()  # Remove :
                # Extract until return or next label
                body_lines, end_index = self._extract_label_block(
                    actions,
                    self.current_line_count + 1
                )
                self.labels[name] = body_lines
                self.current_line_count = end_index + 1
                continue

            # Label call (Gosub, LabelName)
            match = re.fullmatch(r"Gosub,\s*([A-Za-z_]\w*)", line, re.IGNORECASE)
            if match:
                name = match.group(1)
                self.execute_gosub(name)
                continue

            # Loop command (uses the pre-existing helper functions)
            if line.lower().startswith("loop"):
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
            # All commands go here
            if processed_line.startswith("GuiControl"):
                self.cmd_guicontrol(processed_line)
            elif processed_line.startswith("Gui"):
                self.cmd_gui(processed_line)
            if processed_line.startswith("MsgBox"):
                self._cmd_msgbox(processed_line)
            if processed_line.startswith("Ini"):
                self.cmd_ini(processed_line)
            self.current_line_count += 1
    # Final playback
    def build_main_content(self):
        self._execute_script(self.script)
if __name__ == "__main__":
    if open_mode == "Editor":
        app = MainGUI()
        app.mainloop()
    elif open_mode == "Playback":
        playback = Playback(playback_path)
