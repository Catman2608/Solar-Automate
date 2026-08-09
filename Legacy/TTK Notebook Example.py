import tkinter as tk
from tkinter import ttk

def on_tab_change(event):
    # Retrieve the widget that triggered the event
    notebook = event.widget
    # Get the text of the selected tab
    selected_tab_text = notebook.tab(notebook.select(), "text")
    print(f"Switched to: {selected_tab_text}")

# 1. Initialize the main window
root = tk.Tk()
root.title("Tkinter ttk.Notebook Example")
root.geometry("450x300")

# 2. Create the Notebook container
notebook = ttk.Notebook(root)
notebook.pack(pady=15, fill="both", expand=True)

# 3. Build Content for Tab 1
tab1 = ttk.Frame(notebook)
label1 = ttk.Label(tab1, text="Welcome to the Home Screen!", font=("Arial", 12))
label1.pack(pady=20)
btn1 = ttk.Button(tab1, text="Action Button")
btn1.pack(pady=10)

# 4. Build Content for Tab 2
tab2 = ttk.Frame(notebook)
label2 = ttk.Label(tab2, text="Adjust your application configurations here:")
label2.pack(pady=15)
chk1 = ttk.Checkbutton(tab2, text="Enable Notifications")
chk1.pack(pady=5)
chk2 = ttk.Checkbutton(tab2, text="Dark Mode")
chk2.pack(pady=5)

# 5. Add the frames as tabs to the notebook
notebook.add(tab1, text="Home")
notebook.add(tab2, text="Settings")

# 6. Optional: Bind a virtual event to detect tab switches
notebook.bind("<<NotebookTabChanged>>", on_tab_change)

# Start the application loop
root.mainloop()
