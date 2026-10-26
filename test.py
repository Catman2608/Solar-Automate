import tkinter as tk
from tkinter import ttk
import os
import sys
import re
from tkinter import messagebox
import traceback
def open_link():
    pass
class Ahk2Py():
    def __init__(self, a):
        pass
    def show(self):
        pass
class AhkEditor():
    def __init__(self, a):
        pass
    def show(self):
        pass
class WindowSpy():
    def __init__(self, a):
        pass
    def show(self):
        pass
class MainGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("670x670")
        self.title("Solar Automate Main Menu")
        # Ahk2Py
        self.ahk_converter = Ahk2Py(self)
        self.ahk_editor = AhkEditor(self)
        self.window_spy = WindowSpy(self)
        # TTK Notebook/TabView
        notebook = ttk.Notebook(self)
        notebook.place(x=10, y=5, width=650, height=650)
        self.overview_tab = ttk.Frame(notebook)
        notebook.add(self.overview_tab, text="Overview")
        # Build Tabs
        self.build_overview_tab()
        self.mainloop()
    def build_overview_tab(self):
        tk.Label(
            self.overview_tab,
            text="Overview",
            font=("Segoe UI", 9, "bold")
        ).place(x=10, y=10)

        # Compatibility Options
        compatibility_options = ttk.LabelFrame(
            self.overview_tab,
            text="Compatibility Options"
        )
        compatibility_options.place(x=10, y=30, width=300, height=150)

        ttk.Checkbutton(
            compatibility_options,
            text="Option 1"
        ).place(x=20, y=10)

        ttk.Checkbutton(
            compatibility_options,
            text="Option 2"
        ).place(x=20, y=40)

        ttk.Checkbutton(
            compatibility_options,
            text="Option 3"
        ).place(x=20, y=70)

        ttk.Checkbutton(
            compatibility_options,
            text="Option 4"
        ).place(x=20, y=100)

        # AHK Tools
        ahk_tools = ttk.LabelFrame(
            self.overview_tab,
            text="AHK Tools"
        )
        ahk_tools.place(x=320, y=30, width=300, height=150)

        tk.Button(
            ahk_tools,
            text="AHK Visual Editor",
            command=self.ahk_editor.show
        ).place(x=20, y=25, width=200)

        tk.Button(
            ahk_tools,
            text="AHK To Python",
            command=self.ahk_converter.show
        ).place(x=20, y=60, width=200)

        tk.Button(
            ahk_tools,
            text="Window Spy",
            command=self.window_spy.show
        ).place(x=20, y=95, width=200)

        # Solar Automate Links
        solar_links = ttk.LabelFrame(
            self.overview_tab,
            text="Solar Automate Links"
        )
        solar_links.place(x=10, y=190, width=300, height=120)

        tk.Button(
            solar_links,
            text="Join Solar Automate Discord",
            command=lambda: open_link(
                "https://discord.com/invite/aMZY8yrF8r"
            )
        ).place(x=20, y=25, width=240)

        tk.Button(
            solar_links,
            text="Upcoming Features",
            command=lambda: open_link(
                "https://docs.google.com/document/d/1WwWWMR-eN-R-GO42IioToHpWTgiXkLoiNE_4NeE-GsU/"
            )
        ).place(x=20, y=60, width=240)

        # AutoHotKey Links
        ahk_links = ttk.LabelFrame(
            self.overview_tab,
            text="AutoHotKey Links"
        )
        ahk_links.place(x=320, y=190, width=300, height=120)

        tk.Button(
            ahk_links,
            text="Using the Program",
            command=lambda: open_link(
                "https://www.autohotkey.com/docs/v2/Program.htm"
            )
        ).place(x=20, y=25, width=240)

        tk.Button(
            ahk_links,
            text="How to Write Hotkeys",
            command=lambda: open_link(
                "https://www.autohotkey.com/docs/v2/howto/WriteHotkeys.htm"
            )
        ).place(x=20, y=60, width=240)

        # More AHK Documentation
        ahk_docs = ttk.LabelFrame(
            self.overview_tab,
            text="AutoHotKey Documentation"
        )
        ahk_docs.place(x=10, y=320, width=610, height=150)

        tk.Button(
            ahk_docs,
            text="How to Send Keystrokes",
            command=lambda: open_link(
                "https://www.autohotkey.com/docs/v2/howto/SendKeys.htm"
            )
        ).place(x=20, y=25, width=240)

        tk.Button(
            ahk_docs,
            text="How to Run Programs",
            command=lambda: open_link(
                "https://www.autohotkey.com/docs/v2/howto/RunPrograms.htm"
            )
        ).place(x=320, y=25, width=240)

        tk.Button(
            ahk_docs,
            text="How to Manage Windows",
            command=lambda: open_link(
                "https://www.autohotkey.com/docs/v2/howto/ManageWindows.htm"
            )
        ).place(x=20, y=60, width=240)

        tk.Button(
            ahk_docs,
            text="Quick Reference",
            command=lambda: open_link(
                "https://www.autohotkey.com/docs/v2/"
            )
        ).place(x=320, y=60, width=240)

        # Help Files
        help_files = ttk.LabelFrame(
            self.overview_tab,
            text="Help"
        )
        help_files.place(x=10, y=480, width=610, height=55)

        tk.Button(
            help_files,
            text="Help Files",
            command=lambda: open_link("https://www.autohotkey.com/docs/v1/")
        ).place(x=20, y=10, width=240)
class Playback:
    def __init__(self):
        pass
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
        for line, current_line in enumerate(_script):
            if self.flow:
                break

            if line <= start or line <= skip_until:
                continue

            if line >= end:
                break

            processed_line = current_line.lower().replace("    ", "")
            if current_line.startswith(";") or current_line.strip() == "":
                continue

            flow = self._flow_command(processed_line)
            if flow:
                self.flow = flow
                break

            if debug == True:
                print("Processing: ", _script[line])
            # Hashtag commands
            if processed_line.startswith("#"):
                self._cmd_directives(current_line)
            # if (Condition)
            # Keep function-call parentheses. Stripping every "(" / ")"
            # turned InStr(a, b) into InStr a, b and skipped handle_variable.
            if_pattern = r'(?mi)^\s*if\s+(.+?)\s*$'
            is_if = re.match(if_pattern, current_line)
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
            is_loop_files = re.match(loop_files_pattern, current_line)
            if is_loop_files:
                file_pattern = is_loop_files.group(1).strip()
                mode = is_loop_files.group(2)
                skip_until = self.cmd_loop_files(line, file_pattern, mode, _script)
                continue

            # Loop, Amount
            # Loop { ... } is infinite. Loop, N { ... } runs N times.
            # N may be a literal or a %Var% / identifier resolved at runtime.
            loop_pattern = r'(?mi)^\s*Loop(?:\s*,\s*(.+?))?\s*\{'
            is_loop = re.match(loop_pattern, current_line)
            if is_loop:
                raw_count = is_loop.group(1)
                if raw_count is None or str(raw_count).strip() == "":
                    loop_count = None
                else:
                    resolved = self.handle_variable(str(raw_count).strip(), line)
                    try:
                        loop_count = int(float(str(resolved).strip() or 0))
                    except (TypeError, ValueError):
                        loop_count = 0
                # cmd_loop already runs the body loop_count times (or until Break).
                # Jump past the matching } so the body is not run an extra time.
                skip_until = self.cmd_loop(line, loop_count, _script)
                continue

            # GoSub, LabelName
            if processed_line.startswith("gosub"):
                gosub = self.cmd_gosub(current_line)
                if gosub != 0:
                    messagebox.showerror(f"Error at line {line + 1}", f"Error at line {line + 1}\nMissing Label: {gosub}")
            # FunctionName(Parameters)
            function_pattern = r'(?mi)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*'
            is_function_call = re.match(function_pattern, current_line)
            if is_function_call:
                function_name = is_function_call.group(1)
                parameters = is_function_call.group(2)
                # print("Function:", function_name)
                # print("Parameters:", parameters)
                try:
                    start_line2 = self.functions_start[function_name]
                    end_line2 = self.functions_end[function_name]
                    self.execute_script(start_line2, end_line2)
                    if self.flow == "return":
                        self.flow = None
                except Exception as e:
                    if function_name in self.builtin_functions:
                        args = self.split_args(parameters)
                        result = self.builtin_functions[function_name](*args)
                    else:
                        print(traceback.format_exc())
                        messagebox.showerror(f"Error at line {line + 1}", f"Error at line {line + 1}\nMissing Function: {e}")
            # VariableName := Value
            variable_assignment_pattern = r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*(.*?)\s*$'
            match = re.match(variable_assignment_pattern, current_line)
            if match:
                variable_name = match.group(1)
                # Resolve functions / %Var% / bare identifiers.
                variable_value = self.handle_variable(match.group(2))
                # Keep an empty string as an empty string.
                # Do not pass it through the math handler.
                if variable_value != "":
                    try:
                        int(variable_value)
                    except (TypeError, ValueError):
                        variable_value = self.handle_math(variable_value)
                self.local_variables[variable_name] = variable_value
                # print(f"Variable Subsitution: {variable_name} := {variable_value} ({match.group(2)})")
            # VariableName .= Value
            # AHK v1: same as Var := Var . Value (expression).
            # FileName "|"  ->  FileName . "|"
            variable_append_pattern = r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*\.\=\s*(.*?)\s*$'
            match = re.match(variable_append_pattern, current_line)
            if match:
                variable_name = match.group(1)
                variable_value = self.handle_concat(match.group(2))
                current_value = self.local_variables.get(variable_name, "")
                self.local_variables[variable_name] = (
                    str(current_value) + str(variable_value)
                )
            # SplitPath, InputVar, OutFileName, OutDir, OutExtension, OutNameNoExt, OutDrive
            if processed_line.startswith("splitpath"):
                self.cmd_splitpath(current_line)

            # MsgBox, Options, Title, Text
            if processed_line.startswith("msgbox"):
                arguments = [p.strip() for p in current_line.split(",", 3)]

                # Default values
                msgbox_options = ""
                msgbox_title = "MsgBox"
                msgbox_text = ""

                if len(arguments) > 1:
                    msgbox_options = arguments[1]

                if len(arguments) > 2:
                    msgbox_title = arguments[2]

                if len(arguments) > 3:
                    msgbox_text = arguments[3]

                # Handle Variable
                msgbox_text = self.handle_string_variables(msgbox_text)

                # Handle Math
                try:
                    int(float(msgbox_text))
                except (ValueError, TypeError):
                    msgbox_text = self.handle_math(msgbox_text)

                # Handle AHK newline escape
                msgbox_text = str(msgbox_text)
                msgbox_text = msgbox_text.replace("`n", "\n")

                # Display the message
                try:
                    options_int = int(msgbox_options) if msgbox_options else 0
                except (ValueError, TypeError):
                    options_int = 0
                # Low 4 bits are the button type: 4 = Yes/No (also 36 = Yes/No + question icon)
                if (options_int & 0xF) == 4:
                    self.builtin_variables["msgbox_result"] = messagebox.askyesno(msgbox_title, msgbox_text)
                else:
                    messagebox.showerror(msgbox_title, msgbox_text)

            # IfMsgBox, Yes / IfMsgBox, No
            if processed_line.startswith("ifmsgbox"):
                arguments = [p.strip() for p in current_line.split(",")]
                expected_button = arguments[1].strip().lower() if len(arguments) > 1 else ""
                msgbox_result = self.builtin_variables.get("msgbox_result", False)
                # messagebox.askyesno returns True for Yes, False for No
                if isinstance(msgbox_result, bool):
                    actual_button = "yes" if msgbox_result else "no"
                else:
                    actual_button = str(msgbox_result).lower()
                result = (actual_button == expected_button)
                skip_until = self.cmd_if(line, result, _script)
                continue
            if processed_line.startswith("pixelsearch"):
                self.cmd_pixelsearch(current_line)
            if processed_line.startswith("pixelgetcolor"):
                self._cmd_pixelgetcolor(current_line)
            if processed_line.startswith("send"):
                self._cmd_send(current_line)
            if processed_line.startswith("click"):
                self._cmd_click(current_line)
            if processed_line.startswith("sleep"):
                self._cmd_sleep(current_line)
            if processed_line.startswith("mousemove"):
                self._cmd_mousemove(current_line)
            if processed_line.startswith("mousegetpos"):
                error = self._cmd_mousegetpos(current_line)
                if error != 0:
                    messagebox.showerror(f"Error at line {line + 1}", f"Error at line {line + 1}\nError in MouseGetPos: {e}")
            # Hotkey, Hotkey, Label, Status
            if processed_line.startswith("hotkey"):
                self.cmd_hotkey(current_line)
            # IniRead, OutputVar, Filename, Section, Key, Default=ERROR
            # IniWrite, Value, Filename, Section, Key
            if processed_line.startswith("ini"):
                self.cmd_ini(current_line)
            # GuiControl, Subcommand, Control, Value
            if processed_line.startswith("guicontrol"):
                self.cmd_guicontrol(current_line)
            # WinActivate, Window
            if processed_line.startswith("winactivate"):
                self.cmd_winactivate(current_line)
            # WinGetPos, OutX, OutY, OutWidth, OutHeight [, WinTitle]
            if processed_line.startswith("wingetpos"):
                self.cmd_wingetpos(current_line)
            # Gui, Action
            if processed_line.startswith("gui") and not processed_line.startswith("guicontrol"):
                self.cmd_gui(current_line)
            # SetKeyDelay, Delay
            if processed_line.startswith("setkeydelay"):
                parts = [x.strip() for x in current_line.split(",")]
                self.key_delay = int(parts[1])
            # Reload
            if processed_line.startswith("reload"):
                args = [sys.executable, f'"{sys.argv[0]}"'] + sys.argv[1:]
                os.execv(sys.executable, args)
            # ExitApp
            if processed_line.startswith("exitapp"):
                self.destroy()
if __name__ == "__main__":
    app = MainGUI()