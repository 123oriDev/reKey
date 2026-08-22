import os
import platform
import sys
from threading import Event

import keyboard


def check_privileges() -> None:
    """Ensure the process has root/admin access required for OS-level input hooks."""
    is_win = platform.system() == "Windows"
    if is_win:
        import ctypes
        has_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    else:
        has_admin = os.geteuid() == 0

    if not has_admin:
        hint = "Run terminal as Administrator" if is_win else "sudo python3 script.py"
        sys.exit(f"Error: Elevated privileges required.\nHint: {hint}")


# --- 1. NEW: The Handler Interface ---
class BaseKeyHandler:
    """Base class for keyboard event handlers. Inherit from this to create your own."""
    def on_press(self, key: str) -> None:
        pass

    def on_release(self, key: str) -> None:
        pass


# --- 2. MODULAR: The Interceptor ---
class KeyboardInterceptor:
    """Hooks global keyboard events, delegating actions to a Handler object with optional local suppression."""

    def __init__(self, handler: BaseKeyHandler, exit_combo: set[str], suppress: bool = True):
        self.handler = handler
        self.exit_combo = {k.lower() for k in exit_combo}
        self.suppress = suppress  # Controls whether keys type on the local machine
        self._pressed_keys = set()
        self._stop_signal = Event()

    def _on_key_event(self, event: keyboard.KeyboardEvent) -> None:
        key_name = str(event.name).lower()

        if event.event_type == keyboard.KEY_DOWN:
            if key_name not in self._pressed_keys:
                self._pressed_keys.add(key_name)
                self.handler.on_press(key_name)

            if self.exit_combo.issubset(self._pressed_keys):
                self._stop_signal.set()
                return

        elif event.event_type == keyboard.KEY_UP:
            if key_name in self._pressed_keys:
                self._pressed_keys.discard(key_name)
                self.handler.on_release(key_name)

    def _flush_remaining_releases(self) -> None:
        """Trigger release callbacks for held keys on shutdown."""
        for key_name in list(self._pressed_keys):
            self.handler.on_release(key_name)
        self._pressed_keys.clear()

    def start(self) -> None:
        """Start global hook and block execution until exit combination is pressed."""
        # Dynamic suppression: True = block local typing, False = allow local typing
        keyboard.hook(self._on_key_event, suppress=self.suppress)

        combo_str = " + ".join(k.upper() for k in self.exit_combo)
        print(f"Platform: {platform.system()}")
        
        if self.suppress:
            print("UNIVERSAL BLOCKER ACTIVE: All local keyboard inputs suppressed.")
        else:
            print("PASSTHROUGH MODE ACTIVE: Keystrokes will type locally and be transmitted.")
            
        print(f"Press '{combo_str}' to exit and restore control.\n")

        try:
            self._stop_signal.wait()
        finally:
            self._flush_remaining_releases()
            keyboard.unhook_all()
            print(f"\n[EXIT] '{combo_str}' detected. Keyboard hook removed.")

# --- 3. IMPLEMENTATION: Your Custom Logic ---
class MyCustomHandler(BaseKeyHandler):
    """Your specific implementation that stores its own state and parameters."""
    
    def __init__(self, app_name: str, logger_id: int, mode: str):
        # Save custom parameters as instance variables
        self.app_name = app_name
        self.logger_id = logger_id
        self.mode = mode
        
        # You can even track state, like counting total keystrokes!
        self.keystroke_count = 0 

    def on_press(self, key: str) -> None:
        self.keystroke_count += 1
        print(f"[{self.app_name} | ID:{self.logger_id} | {self.mode}] -> Pressed: {key} (Total: {self.keystroke_count})")

    def on_release(self, key: str) -> None:
        print(f"[{self.app_name} | ID:{self.logger_id}] <- Released: {key}")


def main() -> None:
    check_privileges()

    # 1. Instantiate your custom handler with all the parameters it needs
    my_handler = MyCustomHandler(
        app_name="reKey App", 
        logger_id=101, 
        mode="DEBUG"
    )

    # 2. Pass the handler and a custom exit shortcut to the interceptor
    interceptor = KeyboardInterceptor(
        handler=my_handler,
        exit_combo={"ctrl", "shift", "alt", "q"},
        suppress= False
    )

    interceptor.start()


if __name__ == "__main__":
    main()