import time
import keyboard


def my_function():
    print("Ctrl + V was pressed!")


# Listens for Ctrl + V and triggers the function
keyboard.add_hotkey("ctrl+v", my_function)

print("Listening for Ctrl+V... Press ESC to exit.")
keyboard.wait("esc")