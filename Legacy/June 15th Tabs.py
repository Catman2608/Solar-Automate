import tkinter as tk
from tkinter import messagebox
import sys
import os
try:
    playback_path = sys.argv[1]
    open_mode = "Playback"
except:
    open_mode = "Editor"
    folder_path = os.getcwd()
open_mode = "Playback"
playback_path = os.path.join(folder_path, "recording.ahk")
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
        self.geometry("300x300")
        delete_string = str(os.getcwd())
        title = playback_path.replace(f"{delete_string}/", "")
        self.title(title)
        with open(playback_path, "r", encoding="utf-8") as f:
            self.script_text = f.read()
        self.script = self.script_text.splitlines()
        self.after(0, self.withdraw)
        self.build_main_content()
        self.mainloop()
    def build_main_content(self):
        current_tab = None

        for line in self.script:
            line = line.strip()

            if line.lower() == "return":
                break

            if line.startswith("Gui"):
                self.execute_gui(line)
    def execute_gui(self, line):
        # Split the input into multiple lines (if it contains newlines)
        lines = line.splitlines()
        
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
            if command3.startswith("x"):
                options = {}
                for token in command3.split():
                    key = token[0]
                    value = token[1:]
                    options[key] = value
            # if command.startswith("Add"):
            #     print("Command (2): ", command2, "| Command (3): ", command3)
            # else:
            #     print("Command: ", command)
            if command2 == "Text":
                tk.Label(self, text=command4).place(x=options["x"], y=options["y"]) 
            if command2 == "Edit":
                tk.Entry(self, width=30).place(x=int(options["x"]), y=int(options["y"]), width=int(options["w"]))
            if command == "Show":
                self.after(0, self.deiconify)
            if command == "Hide":
                self.after(0, self.withdraw)
        
if __name__ == "__main__":
    if open_mode == "Editor":
        app = MainGUI()
        app.mainloop()
    elif open_mode == "Playback":
        playback = Playback(playback_path)