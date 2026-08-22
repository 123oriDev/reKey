import flet as ft


def main(page: ft.Page):
    page.title = "ReKey Full Virtual Keyboard"
    page.bgcolor = "#0F172A"
    page.padding = 20

    # Start adding items from the top of the page instead of the center
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    # --- STATE & REFERENCES ---
    server_ip = "127.0.0.1"

    page.session.store.set("caps_lock", False)
    page.session.store.set("shift", False)
    page.session.store.set("fn", False)

    key_blacklist = ['Fn']
    dynamic_keys = []
    caps_container_ref = [None]
    shift_container_refs = []
    fn_container_ref = [None]

    # Map of standard keys to their Shifted counterparts
    SHIFT_MAP = {
        "`": "~",
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

    # Map of number row keys to their Function counterparts
    FN_MAP = {
        "`": "esc",
        "1": "f1",
        "2": "f2",
        "3": "f3",
        "4": "f4",
        "5": "f5",
        "6": "f6",
        "7": "f7",
        "8": "f8",
        "9": "f9",
        "0": "f10",
        "-": "f11",
        "=": "f12",
    }

    # 1. On-Screen Display
    status_text = ft.Text(
        "Press any key...",
        size=44,
        weight="bold",
        color="#38BDF8",
        text_align="center",
    )

    # --- UI UPDATE HELPER ---
    def update_keyboard_labels():
        is_caps = page.session.store.get("caps_lock")
        is_shift = page.session.store.get("shift")
        is_fn = page.session.store.get("fn")

        for key_data in dynamic_keys:
            txt_ctrl = key_data["text"]
            base_label = key_data["base_label"]

            if key_data["is_letter"]:
                should_be_upper = is_caps != is_shift
                txt_ctrl.value = (
                    base_label.upper() if should_be_upper else base_label.lower()
                )
            else:
                if is_fn and base_label in FN_MAP:
                    txt_ctrl.value = FN_MAP[base_label]
                else:
                    txt_ctrl.value = (
                        SHIFT_MAP.get(base_label, base_label)
                        if is_shift
                        else base_label
                    )

        page.update()

    # --- CAPS LOCK TOGGLE HELPER ---
    def toggle_caps_lock(e=None):
        is_caps = not page.session.store.get("caps_lock")
        page.session.store.set("caps_lock", is_caps)
        if caps_container_ref[0]:
            caps_container_ref[0].bgcolor = (
                ACTION_COLOR if is_caps else ACCENT_COLOR
            )
        update_keyboard_labels()
        msg = f"Caps Lock: {'ON' if is_caps else 'OFF'}"
        status_text.value = msg
        page.update()
        print(msg)

    # 2. Event Handlers
    def button_down(e):
        key = e.control.data

        if key == "capslock":
            toggle_caps_lock()
            return

        elif key == "shift":
            page.session.store.set("shift", True)
            for ref in shift_container_refs:
                ref.bgcolor = ACTION_COLOR
            update_keyboard_labels()

        elif key == "Fn":
            page.session.store.set("fn", True)
            if fn_container_ref[0]:
                fn_container_ref[0].bgcolor = ACTION_COLOR
            update_keyboard_labels()

        if key not in key_blacklist:
            is_fn = page.session.store.get("fn")
            active_key = FN_MAP[key] if (is_fn and key in FN_MAP) else key

            msg = f"Key PRESSED:  {active_key}"
            status_text.value = msg
            print(msg)

        page.update()

    def button_up(e):
        key = e.control.data

        is_fn = page.session.store.get("fn")
        active_key = FN_MAP[key] if (is_fn and key in FN_MAP) else key

        if key == "shift":
            page.session.store.set("shift", False)
            for ref in shift_container_refs:
                ref.bgcolor = ACCENT_COLOR
            update_keyboard_labels()

        elif key == "Fn":
            page.session.store.set("fn", False)
            if fn_container_ref[0]:
                fn_container_ref[0].bgcolor = ACCENT_COLOR
            update_keyboard_labels()

        if key not in key_blacklist:
            msg = f"Key RELEASED: {active_key}"
            status_text.value = msg
            print(msg)

        page.update()

    # 3. Key Builder Function
    def create_key(label, key_data, width=50, height=50, bg_color="#1E293B"):
        is_letter = len(key_data) == 1 and key_data.isalpha()
        display_label = label.lower() if is_letter else label

        key_text = ft.Text(display_label, size=15, weight="bold", color="white")

        if is_letter or label in SHIFT_MAP or label in FN_MAP:
            dynamic_keys.append(
                {"text": key_text, "base_label": label, "is_letter": is_letter}
            )

        key_container = ft.Container(
            content=key_text,
            alignment=ft.Alignment(0, 0),
            width=width,
            height=height,
            bgcolor=bg_color,
            border_radius=8,
        )

        if key_data == "capslock":
            caps_container_ref[0] = key_container
        elif key_data == "shift":
            shift_container_refs.append(key_container)
        elif key_data == "Fn":
            fn_container_ref[0] = key_container

        return ft.GestureDetector(
            on_tap_down=button_down,
            on_tap_up=button_up,
            on_tap_cancel=button_up,
            data=key_data,
            content=key_container,
        )

    # 4. Keyboard Layout Data
    PRIMARY_COLOR = "#1E293B"
    ACCENT_COLOR = "#334155"
    ACTION_COLOR = "#2563EB"

    keyboard_rows = [
        [
            ("`", "`"),
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
            ("Caps", "caps lock", 75, ACCENT_COLOR),
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
            ("win", "left windows", 65, ACCENT_COLOR),
            ("alt", "alt", 65, ACCENT_COLOR),
            ("Space", "space", 209, ACTION_COLOR),
            ("alt", "right alt", 65, ACCENT_COLOR),
            ("Fn", "Fn", 65, ACCENT_COLOR),
            ("←", "left", 50, ACCENT_COLOR),
            ("↑", "up", 50, ACCENT_COLOR),
            ("↓", "down", 50, ACCENT_COLOR),
            ("→", "right", 50, ACCENT_COLOR),
        ],
    ]

    # 5. Build UI Rows
    gui_rows = []
    for row_data in keyboard_rows:
        row_widgets = []
        for key_info in row_data:
            label = key_info[0]
            key_data = key_info[1]
            width = key_info[2] if len(key_info) > 2 else 50
            bg_color = key_info[3] if len(key_info) > 3 else PRIMARY_COLOR

            key_widget = create_key(label, key_data, width=width, bg_color=bg_color)
            row_widgets.append(key_widget)

        gui_rows.append(
            ft.Row(row_widgets, alignment=ft.MainAxisAlignment.CENTER, spacing=6)
        )

    # --- INLINE IP EDITING ---
    ip_text = ft.Text(
        value=server_ip,
        size=24,
        weight=ft.FontWeight.BOLD,
        color="white",
        tooltip="Click to edit IP",
    )

    def start_editing_ip(e):
        ip_input.value = server_ip
        update_ip_input_width()  # Adjust width to match the text before showing
        ip_display.visible = False
        ip_input.visible = True
        ip_input.focus()
        page.update()

    def finish_editing_ip(e):
        nonlocal server_ip
        new_val = ip_input.value.strip()
        if new_val:
            server_ip = new_val
            ip_text.value = server_ip

        ip_input.visible = False
        ip_display.visible = True
        page.update()

    ip_display = ft.Container(
        content=ip_text,
        on_click=start_editing_ip,
        padding=6,
        border_radius=6,
        ink=True,
    )
    # Helper to calculate dynamic width based on text length
    def update_ip_input_width(e=None):
        char_count = max(len(ip_input.value), 1)
        ip_input.width = max(115, char_count * 15)
        page.update()

    ip_input = ft.TextField(
        value=server_ip,
        width=115,
        height=45,
        text_size=24,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        content_padding=ft.Padding(8, 0, 8, 0),  # Corrected Flet Padding syntax
        border_radius=6,
        border=ft.InputBorder.OUTLINE,
        focused_border_color="#38BDF8",
        on_change=update_ip_input_width,
        on_submit=finish_editing_ip,
        on_blur=finish_editing_ip,
        visible=False,
    )

    ip_control = ft.Row(
        controls=[ip_display, ip_input],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # 6. Add to Screen
    topBar = ft.Row(
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
                        icon=ft.Icons.SEARCH, on_click=lambda e: print("Search opened!")
                    ),
                    ft.IconButton(
                        icon=ft.Icons.LANGUAGE,
                        on_click=toggle_caps_lock,
                        tooltip="Toggle Caps Lock",
                    ),
                ]
            ),
        ],
    )

    main_screen = ft.Container(
        content=ft.Column(
            [status_text, ft.Container(height=15), *gui_rows],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        expand=True,
        alignment=ft.Alignment(0, 0),
    )

    page.add(topBar, main_screen)


ft.app(main)