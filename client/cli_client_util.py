import os
import platform
import sys
from collections.abc import Callable
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


class KeyboardInterceptor:
    """Hooks, suppresses, and routes global keyboard events to custom press/release callbacks."""

    def __init__(
        self,
        on_press: Callable[[str], None] | None = None,
        on_release: Callable[[str], None] | None = None,
    ):
        self.on_press_callback = on_press
        self.on_release_callback = on_release
        self._pressed_keys = set()
        self._stop_signal = Event()

    def _on_key_event(self, event: keyboard.KeyboardEvent) -> None:
        key_name = str(event.name).lower()

        if event.event_type == keyboard.KEY_DOWN:
            # 1. Deduplicate OS key-repeats and trigger press callback
            if key_name not in self._pressed_keys:
                self._pressed_keys.add(key_name)
                if self.on_press_callback:
                    self.on_press_callback(key_name)

            # 2. Check for emergency exit shortcut: Ctrl + Shift + Alt + Q
            has_ctrl = any("ctrl" in k for k in self._pressed_keys)
            has_shift = any("shift" in k for k in self._pressed_keys)
            has_alt = any("alt" in k for k in self._pressed_keys)
            has_q = "q" in self._pressed_keys

            if has_ctrl and has_shift and has_alt and has_q:
                self._stop_signal.set()
                return

        elif event.event_type == keyboard.KEY_UP:
            # Remove key from active set and trigger release callback
            if key_name in self._pressed_keys:
                self._pressed_keys.discard(key_name)
                if self.on_release_callback:
                    self.on_release_callback(key_name)

    def _flush_remaining_releases(self) -> None:
        """Trigger release callbacks for any keys that are still held when shutting down."""
        for key_name in list(self._pressed_keys):
            if self.on_release_callback:
                self.on_release_callback(key_name)
        self._pressed_keys.clear()

    def start(self) -> None:
        """Start global hook and block execution until exit combination is pressed."""
        keyboard.hook(self._on_key_event, suppress=True)

        print(f"Platform: {platform.system()}")
        print("UNIVERSAL BLOCKER ACTIVE: All keyboard inputs suppressed.")
        print("Press 'CTRL + SHIFT + ALT + Q' to exit and restore control.\n")

        try:
            self._stop_signal.wait()
        finally:
            # Fire release callbacks for held keys (ctrl, shift, alt, q, etc.) before unhooking
            self._flush_remaining_releases()
            keyboard.unhook_all()
            print("\n[EXIT] 'CTRL + SHIFT + ALT + Q' detected. Keyboard restored.")


def handle_press(key: str) -> None:
    """Callback function executed on a key press."""
    print(f"-> Pressed key: {key}")


def handle_release(key: str) -> None:
    """Callback function executed on a key release."""
    print(f"<- Released key: {key}")


def main() -> None:
    """Main application entry point."""
    check_privileges()

    interceptor = KeyboardInterceptor(on_press=handle_press, on_release=handle_release)

    interceptor.start()


if __name__ == "__main__":
    main()
