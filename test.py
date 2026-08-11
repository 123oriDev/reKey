import sys
import tkinter as tk
from tkinter import filedialog


def enable_high_dpi():
    """Configures system High-DPI scaling for crisp text on all operating systems."""
    if sys.platform == "win32":
        # Windows: Explicitly request per-monitor DPI awareness via ctypes
        try:
            import ctypes

            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass
    elif sys.platform == "darwin":
        # macOS: Retina display scaling is handled natively by Cocoa / macOS
        pass
    elif sys.platform.startswith("linux"):
        # Linux: X11/Wayland DEs handle DPI scaling automatically in Tk 8.6+
        pass


def get_file_path(title="Select a File", filetypes=None):
    """Opens a native, high-res file picker dialog and returns the selected path."""
    enable_high_dpi()

    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window

    # Cross-platform fix: Ensure the dialog pops up on top of other windows
    root.attributes("-topmost", True)

    if filetypes is None:
        filetypes = [("All files", "*.*")]

    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)

    # Clean up the Tk instance after selection
    root.destroy()

    return file_path


# --- Usage Example ---
if __name__ == "__main__":
    selected_file = get_file_path(
        title="Select Script or Document",
        filetypes=[("Python & Text Files", "*.py *.txt"), ("All Files", "*.*")],
    )

    if selected_file:
        print(f"Selected file: {selected_file}")
    else:
        print("No file selected.")