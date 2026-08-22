import keyboard

def on_key_event(event):
    # Only trigger when the key is pressed down (not released)
    if event.event_type == keyboard.KEY_DOWN:
        print(f"Key '{event.name}' pressed")

print("Press any key to print the name. Press 'esc' to exit...")
keyboard.hook(on_key_event)

keyboard.wait('esc')