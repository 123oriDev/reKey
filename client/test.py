import keyboard


def on_key(event, custom_arg):
    print(f"[{custom_arg}] Key pressed: {event.name}")


my_custom_value = "Player 1"

# The lambda receives `e` (event) from keyboard and passes both `e` and `my_custom_value`
keyboard.on_press(lambda e: on_key(e, my_custom_value))

print("Listening for key presses... Press ESC to quit.")
keyboard.wait("esc")