import flet as ft
from keyboard_data import (
    ACCENT_COLOR,
    ACTION_COLOR,
    FN_MAP,
    KEYBOARD_ROWS,
    PRIMARY_COLOR,
    SHIFT_MAP,
)


class BaseKeyHandler:
    """Base class for keyboard event handlers. Inherit from this to create your own."""

    def on_press(self, key: str) -> None:
        pass

    def on_release(self, key: str) -> None:
        pass

    def on_status_change(self, msg: str) -> None:
        pass


class VirtualKeyboard(ft.Column):
    """Virtual keyboard that delegates actions to a Handler object."""

    def __init__(self, handler: BaseKeyHandler):
        super().__init__()
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.spacing = 8

        # Replaced the individual callbacks with the handler interface
        self.handler = handler

        self.is_caps_lock = False
        self.is_shift = False
        self.is_fn = False

        self.key_blacklist = ["Fn"]
        self.dynamic_keys = []
        self.caps_container = None
        self.shift_containers = []
        self.fn_container = None

        self._build_keyboard()

    def _build_keyboard(self):
        gui_rows = []
        for row_data in KEYBOARD_ROWS:
            row_widgets = []
            for key_info in row_data:
                label = key_info[0]
                key_data = key_info[1]
                width = key_info[2] if len(key_info) > 2 else 50
                bg_color = key_info[3] if len(key_info) > 3 else PRIMARY_COLOR

                key_widget = self._create_key(
                    label, key_data, width=width, bg_color=bg_color
                )
                row_widgets.append(key_widget)

            gui_rows.append(
                ft.Row(row_widgets, alignment=ft.MainAxisAlignment.CENTER, spacing=6)
            )

        self.controls = gui_rows

    def _create_key(self, label, key_data, width=50, height=50, bg_color=PRIMARY_COLOR):
        is_letter = len(key_data) == 1 and key_data.isalpha()
        display_label = label.lower() if is_letter else label

        key_text = ft.Text(display_label, size=15, weight="bold", color="white")

        if is_letter or label in SHIFT_MAP or label in FN_MAP:
            self.dynamic_keys.append(
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

        if key_data in ["capslock", "caps lock"]:
            self.caps_container = key_container
        elif key_data == "shift":
            self.shift_containers.append(key_container)
        elif key_data == "Fn":
            self.fn_container = key_container

        return ft.GestureDetector(
            on_tap_down=self._button_down,
            on_tap_up=self._button_up,
            on_tap_cancel=self._button_up,
            data=key_data,
            content=key_container,
        )

    def update_keyboard_labels(self):
        for key_data in self.dynamic_keys:
            txt_ctrl = key_data["text"]
            base_label = key_data["base_label"]

            if key_data["is_letter"]:
                should_be_upper = self.is_caps_lock != self.is_shift
                txt_ctrl.value = (
                    base_label.upper() if should_be_upper else base_label.lower()
                )
            else:
                if self.is_fn and base_label in FN_MAP:
                    txt_ctrl.value = FN_MAP[base_label]
                else:
                    txt_ctrl.value = (
                        SHIFT_MAP.get(base_label, base_label)
                        if self.is_shift
                        else base_label
                    )

        if self.page:
            self.page.update()

    def toggle_caps_lock(self, e=None):
        self.is_caps_lock = not self.is_caps_lock
        if self.caps_container:
            self.caps_container.bgcolor = (
                ACTION_COLOR if self.is_caps_lock else ACCENT_COLOR
            )
        self.update_keyboard_labels()
        msg = f"Caps Lock: {'ON' if self.is_caps_lock else 'OFF'}"

        # Delegating to handler
        if self.handler:
            self.handler.on_status_change(msg)

    def _button_down(self, e):
        key = e.control.data

        if key in ["capslock", "caps lock"]:
            self.toggle_caps_lock()
            return

        elif key == "shift":
            self.is_shift = True
            for ref in self.shift_containers:
                ref.bgcolor = ACTION_COLOR
            self.update_keyboard_labels()

        elif key == "Fn":
            self.is_fn = True
            if self.fn_container:
                self.fn_container.bgcolor = ACTION_COLOR
            self.update_keyboard_labels()

        if key not in self.key_blacklist:
            active_key = FN_MAP[key] if (self.is_fn and key in FN_MAP) else key
            msg = f"Key PRESSED:  {active_key}"

            # Delegating to handler
            if self.handler:
                self.handler.on_status_change(msg)
                self.handler.on_press(active_key)

        if self.page:
            self.page.update()

    def _button_up(self, e):
        key = e.control.data
        active_key = FN_MAP[key] if (self.is_fn and key in FN_MAP) else key

        if key == "shift":
            self.is_shift = False
            for ref in self.shift_containers:
                ref.bgcolor = ACCENT_COLOR
            self.update_keyboard_labels()

        elif key == "Fn":
            self.is_fn = False
            if self.fn_container:
                self.fn_container.bgcolor = ACCENT_COLOR
            self.update_keyboard_labels()

        if key not in self.key_blacklist:
            msg = f"Key RELEASED: {active_key}"

            # Delegating to handler
            if self.handler:
                self.handler.on_status_change(msg)
                self.handler.on_release(active_key)

        if self.page:
            self.page.update()
