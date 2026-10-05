import tkinter as tk
from tkinter import ttk

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
if __name__ == "__main__":
    app = MainGUI()