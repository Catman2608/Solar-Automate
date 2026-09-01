import tkinter as tk
from tkinter import ttk
class AhkEditor:
    def __init__(self, master):
        self.master = master

        self.window = tk.Toplevel(self.master)
        self.window.title("AutoHotKey Script Editor")
        self.window.geometry("800x600")
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        self.build_main_content()

        self.build_menu()
        self.hide()

    def show(self):
        self.window.deiconify()

    def hide(self):
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

        recording_button = tk.Button(self.top_bar, text="Start Recording", command=self.start_recording)  # Specify master as self.top_bar
        recording_button.grid(row=0, column=2, sticky="ew")  # Only east-west

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

    def start_recording(self):
        recording_button = tk.Button(self.top_bar, text="Stop Recording", command=self.stop_recording)  # Specify master as self.top_bar

    def stop_recording(self):
        pass

    def new_file(self):
        self.text_editor.delete("1.0", tk.END)


    def open_file(self):
        pass


    def save_file(self):
        pass


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
        
    def add_content(self):
        selected = self.current_command.get()

        if not selected:
            return

        last_line = self.text_editor.get("end-1c linestart", "end-1c")

        if last_line.strip():
            self.text_editor.insert(tk.END, "\n" + selected)
        else:
            self.text_editor.insert("end-1c", selected)

        self.text_editor.focus_set()
