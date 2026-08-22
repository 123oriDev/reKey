import flet as ft
from components.text_editor import TextEditor
from components.virtual_keyboard import BaseKeyHandler, VirtualKeyboard


class AppKeyHandler(BaseKeyHandler):
    """Custom handler to manage keyboard presses, releases, and status messages."""
    def __init__(self, status_text_ui, page: ft.Page):
        self.status_text_ui = status_text_ui
        self.page = page

    def on_press(self, key: str) -> None:
        print(f"DOWN: {key}")

    def on_release(self, key: str) -> None:
        print(f"UP: {key}")

    def on_status_change(self, msg: str) -> None:
        self.status_text_ui.value = msg
        self.status_text_ui.update()


def is_valid_ip(text: str) -> bool:
    # Split the string by the dot character
    parts = text.split('.')
    
    # A standard IPv4 address has exactly 4 parts (meaning 3 dots)
    if len(parts) != 4:
        return False
        
    for part in parts:
        # Check if the part is empty or contains non-numbers
        if not part.isdigit():
            return False
            
        # Optional but recommended: Check if it's a valid IP range (0 to 255)
        if not (0 <= int(part) <= 255):
            return False
            
    return True


def main(page: ft.Page):
    page.title = "ReKey Full Virtual Keyboard"
    page.bgcolor = "#0F172A"
    page.padding = 20

    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    status_text = ft.Text(
        "Press any key...",
        size=44,
        weight="bold",
        color="#38BDF8",
        text_align="center",
    )

    # 1. Instantiate your custom handler
    keyboard_handler = AppKeyHandler(status_text, page)

    ip_control = TextEditor(
        initial_text="127.0.0.1",
        on_change_text=lambda new_ip: print(f"Server IP set to: {new_ip}"),
        filter_func= is_valid_ip
    )

    # 2. Pass the handler object to VirtualKeyboard
    keyboard = VirtualKeyboard(handler=keyboard_handler)

    top_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.SETTINGS,
                        on_click=lambda e: print("Settings opened!"),
                    ),
                    ip_control,
                ]
            ),
            ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.SEARCH,
                        on_click=lambda e: print("Search opened!"),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.LANGUAGE,
                        on_click=keyboard.toggle_caps_lock,
                        tooltip="Toggle Caps Lock",
                    ),
                ]
            ),
        ],
    )

    main_screen = ft.Container(
        content=ft.Column(
            [status_text, ft.Container(height=15), keyboard],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        expand=True,
        alignment=ft.Alignment(0, 0),
    )

    page.add(top_bar, main_screen)


if __name__ == "__main__":
    ft.app(main)