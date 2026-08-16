import flet as ft

# ==========================================
# CONSTANTS & CONFIGURATION
# ==========================================
PRIMARY_COLOR = "#1E293B"
ACCENT_COLOR = "#334155"
ACTION_COLOR = "#2563EB"
BG_COLOR = "#0F172A"

SHIFT_MAP = {
    "1": "!",
    "2": "@",
    "3": "#",
    "4": "$",
    "5": "%",
    "6": "^",
    "7": "&",
    "8": "*",
    "9": "(",
    "0": ")",
    "-": "_",
    "=": "+",
    "[": "{",
    "]": "}",
    "\\": "|",
    ";": ":",
    ",": "<",
    ".": ">",
    "/": "?",
}

FN_MAP = {
    "1": "F1",
    "2": "F2",
    "3": "F3",
    "4": "F4",
    "5": "F5",
    "6": "F6",
    "7": "F7",
    "8": "F8",
    "9": "F9",
    "0": "F10",
    "-": "F11",
    "=": "F12",
}

KEYBOARD_LAYOUT = [
    [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
        ("7", "7"),
        ("8", "8"),
        ("9", "9"),
        ("0", "0"),
        ("-", "-"),
        ("=", "="),
        ("⌫", "backspace", 75, ACCENT_COLOR),
    ],
    [
        ("Tab", "tab", 65, ACCENT_COLOR),
        ("Q", "q"),
        ("W", "w"),
        ("E", "e"),
        ("R", "r"),
        ("T", "t"),
        ("Y", "y"),
        ("U", "u"),
        ("I", "i"),
        ("O", "o"),
        ("P", "p"),
        ("[", "["),
        ("]", "]"),
        ("\\", "\\"),
    ],
    [
        ("Caps", "capslock", 75, ACCENT_COLOR),
        ("A", "a"),
        ("S", "s"),
        ("D", "d"),
        ("F", "f"),
        ("G", "g"),
        ("H", "h"),
        ("J", "j"),
        ("K", "k"),
        ("L", "l"),
        (";", ";"),
        ("Enter", "enter", 85, ACTION_COLOR),
    ],
    [
        ("Shift", "shift", 95, ACCENT_COLOR),
        ("Z", "z"),
        ("X", "x"),
        ("C", "c"),
        ("V", "v"),
        ("B", "b"),
        ("N", "n"),
        ("M", "m"),
        (",", ","),
        (".", "."),
        ("/", "/"),
        ("Shift", "shift", 95, ACCENT_COLOR),
    ],
    [
        ("Ctrl", "ctrl", 65, ACCENT_COLOR),
        ("Win", "win", 65, ACCENT_COLOR),
        ("Alt", "alt", 65, ACCENT_COLOR),
        ("Space", "space", 209, ACTION_COLOR),
        ("Alt", "alt", 65, ACCENT_COLOR),
        ("Fn", "Fn", 65, ACCENT_COLOR),
        ("←", "left", 50, ACCENT_COLOR),
        ("↑", "up", 50, ACCENT_COLOR),
        ("↓", "down", 50, ACCENT_COLOR),
        ("→", "right", 50, ACCENT_COLOR),
    ],
]


# ==========================================
# MAIN APPLICATION
# ==========================================
def main(page: ft.Page):
    # Page Setup
    page.title = "ReKey Virtual Keyboard"
    page.bgcolor = BG_COLOR
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # State Management Initialization
    server_ip = "8.8.8.8"
    page.session.store.set("caps_lock", False)
    page.session.store.set("shift", False)
    page.session.store.set("fn", False)

    dynamic_keys = []
    modifiers = {"caps_lock": None, "shift": [], "fn": None}

    status_text = ft.Text(
        "Press any key...", size=24, weight=ft.FontWeight.BOLD, color="#38BDF8"
    )

    # --- Keyboard Logic & Event Handlers ---
    def update_keyboard_labels():
        is_caps = page.session.store.get("caps_lock")
        is_shift = page.session.store.get("shift")
        is_fn = page.session.store.get("fn")

        for key_data in dynamic_keys:
            txt, base = key_data["text"], key_data["base"]

            if key_data["is_letter"]:
                txt.value = (
                    base.upper() if (is_caps != is_shift) else base.lower()
                )
            else:
                if is_fn and base in FN_MAP:
                    txt.value = FN_MAP[base]
                else:
                    txt.value = (
                        SHIFT_MAP.get(base, base) if is_shift else base
                    )

        page.update()

    def handle_key_event(e, is_down):
        key = e.control.data

        if key == "capslock" and is_down:
            new_state = not page.session.store.get("caps_lock")
            page.session.store.set("caps_lock", new_state)
            modifiers["caps_lock"].bgcolor = (
                ACTION_COLOR if new_state else ACCENT_COLOR
            )
            update_keyboard_labels()

        elif key == "shift":
            page.session.store.set("shift", is_down)
            for ref in modifiers["shift"]:
                ref.bgcolor = ACTION_COLOR if is_down else ACCENT_COLOR
            update_keyboard_labels()

        elif key == "Fn":
            page.session.store.set("fn", is_down)
            modifiers["fn"].bgcolor = ACTION_COLOR if is_down else ACCENT_COLOR
            update_keyboard_labels()

        action = "PRESSED" if is_down else "RELEASED"
        status_text.value = f"Key {action}: {key}"
        page.update()

    def create_key(label, data, width=50, bg_color=PRIMARY_COLOR):
        is_letter = len(data) == 1 and data.isalpha()
        display = label.lower() if is_letter else label

        key_text = ft.Text(
            display, size=15, weight=ft.FontWeight.BOLD, color="white"
        )

        if is_letter or label in SHIFT_MAP or label in FN_MAP:
            dynamic_keys.append(
                {"text": key_text, "base": label, "is_letter": is_letter}
            )

        container = ft.Container(
            content=key_text,
            alignment=ft.Alignment(0, 0),
            width=width,
            height=50,
            bgcolor=bg_color,
            border_radius=8,
        )

        if data == "capslock":
            modifiers["caps_lock"] = container
        elif data == "shift":
            modifiers["shift"].append(container)
        elif data == "Fn":
            modifiers["fn"] = container

        return ft.GestureDetector(
            on_tap_down=lambda e: handle_key_event(e, True),
            on_tap_up=lambda e: handle_key_event(e, False),
            on_tap_cancel=lambda e: handle_key_event(e, False),
            data=data,
            content=container,
        )

    # --- Inline IP Editing ---
    ip_text = ft.Text(
        value=server_ip,
        size=24,
        weight=ft.FontWeight.BOLD,
        color="white",
        tooltip="Click to edit",
    )

    def toggle_ip_edit(e, editing=True):
        nonlocal server_ip
        if not editing:
            new_val = ip_input.value.strip()
            if new_val:
                server_ip = new_val
                ip_text.value = server_ip

        ip_display.visible = not editing
        ip_input.visible = editing
        if editing:
            ip_input.focus()
        page.update()

    ip_display = ft.Container(
        content=ip_text,
        on_click=lambda e: toggle_ip_edit(e, True),
        ink=True,
        border_radius=6,
    )

    ip_input = ft.TextField(
        value=server_ip,
        width=180,
        text_size=24,
        color="white",
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        border=ft.InputBorder.NONE,
        bgcolor="transparent",
        content_padding=0,
        cursor_color="white",
        on_submit=lambda e: toggle_ip_edit(e, False),
        on_blur=lambda e: toggle_ip_edit(e, False),
        visible=False,
    )

    ip_control = ft.Row(
        [ip_display, ip_input], vertical_alignment=ft.CrossAxisAlignment.CENTER
    )

    # --- UI Assembly ---
    keyboard_ui = [
        ft.Row(
            [create_key(*key_info) for key_info in row],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
        )
        for row in KEYBOARD_LAYOUT
    ]

    top_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Row([ft.IconButton(ft.Icons.SETTINGS), ip_control]),
            ft.Row(
                [
                    ft.IconButton(ft.Icons.SEARCH),
                    ft.IconButton(ft.Icons.LANGUAGE),
                ]
            ),
        ],
    )

    main_content = ft.Container(
        content=ft.Column(
            [status_text, ft.Container(height=15)] + keyboard_ui,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        expand=True,
        alignment=ft.Alignment(0, 0),
    )

    page.add(top_bar, main_content)


if __name__ == "__main__":
    ft.app(main)