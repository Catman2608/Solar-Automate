from pynput import mouse

def on_click(x, y, button, pressed):
    if pressed:
        print(f"Mouse button {button} is PRESSED at ({x}, {y})")
    else:
        print(f"Mouse button {button} is RELEASED at ({x}, {y})")

# Start listening (this blocks until you stop it)
with mouse.Listener(on_click=on_click) as listener:
    listener.join()