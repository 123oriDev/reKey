from collections.abc import Callable
from typing import Optional

import flet as ft


class TextEditor(ft.Row):
    def __init__(
        self,
        initial_text: str = "None",
        on_change_text=None,
        text_color: str = "white",
        text_tooltip: str = "",
        filter_func: Optional[Callable[[str], bool]] = None,
    ):
        super().__init__()

        self.current_text = initial_text
        self.on_change_text_callback = on_change_text
        self.filter_func = filter_func

        self.vertical_alignment = ft.CrossAxisAlignment.CENTER

        # Text displayed when not editing
        self.text_control = ft.Text(
            value=self.current_text,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=text_color,
            tooltip=text_tooltip,
        )

        self.text_display = ft.Container(
            content=self.text_control,
            on_click=self._start_editing_text,
            padding=6,
            border_radius=6,
            ink=True,
        )

        # Text field displayed while editing
        self.text_input = ft.TextField(
            value=self.current_text,
            width=115,
            height=45,
            text_size=24,
            text_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD
            ),
            color=text_color,
            content_padding=ft.Padding(8, 0, 8, 0),
            border_radius=6,
            border=ft.InputBorder.OUTLINE,
            focused_border_color="#38BDF8",

            on_change=self._update_text_input_width,
            on_submit=self._finish_editing_text,
            on_blur=self._finish_editing_text,

            visible=False,
        )

        self.controls = [
            self.text_display,
            self.text_input,
        ]

    def _update_text_input_width(self, e=None):
        char_count = max(len(self.text_input.value), 1)

        self.text_input.width = max(
            115,
            char_count * 15,
        )

        self.text_input.update()

    def _start_editing_text(self, e):
        self.text_input.value = self.current_text

        self._update_text_input_width()

        self.text_display.visible = False
        self.text_input.visible = True

        self.text_input.focus()

        if self.page:
            self.page.update()

    def _finish_editing_text(self, e):
        new_val = self.text_input.value.strip()

        # Only proceed if the value is not empty and actually changed
        if new_val and new_val != self.current_text:
            
            # Check the filter; if no filter exists, default to True
            is_valid = self.filter_func(new_val) if self.filter_func else True
            
            if is_valid:
                self.current_text = new_val
                self.text_control.value = self.current_text

                if self.on_change_text_callback:
                    self.on_change_text_callback(self.current_text)

        self.text_input.visible = False
        self.text_display.visible = True

        if self.page:
            self.page.update()

    @property
    def text(self) -> str:
        return self.current_text