import asyncio

import flet as ft
import text_editor


class SubPanel(ft.Container):
    """Individual panel layer inside PopContinue."""

    def __init__(
        self,
        panel_color,
        animation_duration,
        animation_curve,
        on_anim_end,
        on_close,
    ):
        self.title_text = ft.Text(
            "",
            size=20,
            weight=ft.FontWeight.BOLD,
        )

        self.header_row = ft.Row(
            controls=[
                self.title_text,
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    on_click=lambda e: on_close(),
                    tooltip="Close Panel",
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self.header_section = ft.Column(
            controls=[
                self.header_row,
                ft.Divider(),
            ],
            spacing=5,
        )

        self.body_section = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        super().__init__(
            top=0,
            bottom=0,
            left=0,
            right=0,
            bgcolor=panel_color,
            padding=20,
            offset=ft.Offset(1, 0),
            animate_offset=ft.Animation(
                animation_duration,
                animation_curve,
            ),
            on_animation_end=on_anim_end,
            content=ft.Column(
                controls=[
                    self.header_section,
                    self.body_section,
                ],
                expand=True,
                spacing=10,
            ),
        )

    def build_content(
        self,
        top_text,
        components,
        main_alignment,
        cross_alignment,
    ):
        """Populate panel title, components and alignment."""

        self.title_text.value = top_text or "Details"

        self.body_section.alignment = (
            main_alignment
            if main_alignment is not None
            else ft.MainAxisAlignment.START
        )

        self.body_section.horizontal_alignment = (
            cross_alignment
            if cross_alignment is not None
            else ft.CrossAxisAlignment.START
        )

        self.body_section.controls = components or []


class PopContinue(ft.Container):
    """Secondary detail panel using two alternating overlay layers."""

    def __init__(
        self,
        top_text: str = "Details",
        components: list = None,
        panel_color="surfaceContainerHigh",
        left_offset=280,
        animation_duration=300,
        animation_curve=ft.AnimationCurve.EASE_OUT,
        main_alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START,
        cross_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.START,
    ):
        self.is_open = False

        # ---------------------------------------------------------
        # Create the two reusable panel layers
        # ---------------------------------------------------------

        self.p1 = SubPanel(
            panel_color=panel_color,
            animation_duration=animation_duration,
            animation_curve=animation_curve,
            on_anim_end=self._on_p1_anim_end,
            on_close=self.close_panel,
        )

        self.p2 = SubPanel(
            panel_color=panel_color,
            animation_duration=animation_duration,
            animation_curve=animation_curve,
            on_anim_end=self._on_p2_anim_end,
            on_close=self.close_panel,
        )

        # Initial content goes into p1
        self.p1.build_content(
            top_text,
            components,
            main_alignment,
            cross_alignment,
        )

        # p1 starts as the active panel
        self.active_panel = self.p1
        self.hidden_panel = self.p2

        # Both panels exist in the Stack
        self.stack = ft.Stack(
            controls=[
                self.p1,
                self.p2,
            ],
            expand=True,
        )

        super().__init__(
            top=0,
            bottom=0,
            left=left_offset,
            right=0,
            content=self.stack,
        )

    async def open_panel(
        self,
        top_text: str = None,
        components: list = None,
        main_alignment: ft.MainAxisAlignment = None,
        cross_alignment: ft.CrossAxisAlignment = None,
    ):
        """
        Open the panel.

        If the panel is already open, the second panel slides
        over the current panel.
        """

        # =========================================================
        # FIRST OPEN
        # =========================================================

        if not self.is_open:
            self.active_panel.build_content(
                top_text,
                components,
                main_alignment,
                cross_alignment,
            )

            # Start off-screen
            self.active_panel.offset = ft.Offset(1, 0)
            self.active_panel.update()

            # Give Flet time to render the starting position
            await asyncio.sleep(0.01)

            # Animate onto the screen
            self.active_panel.offset = ft.Offset(0, 0)
            self.active_panel.update()

            self.is_open = True
            return

        # =========================================================
        # PANEL IS ALREADY OPEN
        # =========================================================

        target_panel = self.hidden_panel

        # ---------------------------------------------------------
        # Put the hidden panel on top of the current panel
        # ---------------------------------------------------------

        if target_panel in self.stack.controls:
            self.stack.controls.remove(target_panel)

        self.stack.controls.append(target_panel)

        # ---------------------------------------------------------
        # Set its new content
        # ---------------------------------------------------------

        target_panel.build_content(
            top_text,
            components,
            main_alignment,
            cross_alignment,
        )

        # ---------------------------------------------------------
        # IMPORTANT:
        #
        # First position the new panel off-screen.
        # Then update Flet so it actually renders that position.
        # ---------------------------------------------------------

        target_panel.offset = ft.Offset(1, 0)
        target_panel.update()

        await asyncio.sleep(0.01)

        # ---------------------------------------------------------
        # Now move it onto the screen.
        #
        # animate_offset detects the change from:
        #
        #     Offset(1, 0)
        #
        # to:
        #
        #     Offset(0, 0)
        #
        # and creates the animation.
        # ---------------------------------------------------------

        target_panel.offset = ft.Offset(0, 0)
        target_panel.update()

        # ---------------------------------------------------------
        # Swap the active/hidden panels
        # ---------------------------------------------------------

        self.hidden_panel = self.active_panel
        self.active_panel = target_panel

    def _on_p1_anim_end(self, e):
        """Reset p2 after p1 finishes sliding in."""

        if self.active_panel == self.p1:
            self.p2.offset = ft.Offset(1, 0)
            self.p2.update()

    def _on_p2_anim_end(self, e):
        """Reset p1 after p2 finishes sliding in."""

        if self.active_panel == self.p2:
            self.p1.offset = ft.Offset(1, 0)
            self.p1.update()

    def close_panel(self):
        """Close both panel layers."""

        self.is_open = False

        self.p1.offset = ft.Offset(1, 0)
        self.p2.offset = ft.Offset(1, 0)

        self.p1.update()
        self.p2.update()


class PopMenu(ft.Container):
    def __init__(
        self,
        components: list,
        icon_name_open: ft.IconData,
        icon_name_exit: ft.IconData,
        top_text: str,
        pop_continue: PopContinue = None,
        panel_color="surfaceContainerHighest",
        animation_duration=300,
        animation_curve=ft.AnimationCurve.EASE_OUT,
    ):
        self.components = components
        self.pop_continue = pop_continue
        self.pop_menu_open = False

        # ---------------------------------------------------------
        # Open button
        # ---------------------------------------------------------

        self.button = ft.IconButton(
            icon=icon_name_open,
            on_click=self.toggle_pop_menu,
            tooltip="Open Menu",
        )

        # ---------------------------------------------------------
        # Panel header
        # ---------------------------------------------------------

        panel_controls = [
            ft.Row(
                controls=[
                    ft.Text(
                        top_text,
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.IconButton(
                        icon=icon_name_exit,
                        on_click=self.toggle_pop_menu,
                        tooltip="Close Menu",
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Divider(),
        ]

        panel_controls.extend(components)

        # ---------------------------------------------------------
        # Main menu panel
        # ---------------------------------------------------------

        self.pop_menu_panel = ft.Container(
            width=280,
            top=0,
            bottom=0,
            left=0,
            bgcolor=panel_color,
            shadow=ft.BoxShadow(
                blur_radius=15,
                color="black54",
            ),
            offset=ft.Offset(-1, 0),
            animate_offset=ft.Animation(
                animation_duration,
                animation_curve,
            ),
            padding=20,
            content=ft.Column(
                controls=panel_controls,
                spacing=15,
            ),
        )

        super().__init__(
            content=self.button,
        )

    def did_mount(self):
        """Add the menu panels to the page overlay."""

        if (
            self.pop_continue
            and self.pop_continue not in self.page.overlay
        ):
            self.page.overlay.append(self.pop_continue)

        if self.pop_menu_panel not in self.page.overlay:
            self.page.overlay.append(self.pop_menu_panel)

        self.page.update()

    def toggle_pop_menu(self, e=None):
        """Open/close the main settings menu."""

        self.pop_menu_open = not self.pop_menu_open

        self.pop_menu_panel.offset = (
            ft.Offset(0, 0)
            if self.pop_menu_open
            else ft.Offset(-1, 0)
        )

        self.pop_menu_panel.update()

        # Closing the main menu also closes the detail panel
        if not self.pop_menu_open and self.pop_continue:
            self.pop_continue.close_panel()


def main(page: ft.Page):
    page.title = "Settings Menu"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # =============================================================
    # DETAIL PANEL
    # =============================================================

    pop_continue = PopContinue(
        top_text="Advanced Details",
        components=[
            ft.Text(
                "Select an option from the menu to view details."
            ),
        ],
    )

    # =============================================================
    # IP EDITOR
    # =============================================================

    ip_control = text_editor.TextEditor(
        initial_text="127.0.0.1",
        on_change_text=lambda ip: print(
            f"Server IP set to: {ip}"
        ),
        text_color="white",
    )

    # =============================================================
    # NETWORK SETTINGS BUTTON
    # =============================================================

    network_details_btn = ft.ElevatedButton(
        "Network Options (Top-Left) >",
        on_click=lambda e: e.page.run_task(
            pop_continue.open_panel,
            top_text="Network Settings",
            components=[
                ft.Text(
                    "Configure Port and Subnet:"
                ),
                ft.TextField(
                    label="Port",
                    value="8080",
                ),
                ft.TextField(
                    label="Subnet Mask",
                    value="255.255.255.0",
                ),
                ft.Switch(
                    label="Enable DHCP"
                ),
            ],
            main_alignment=ft.MainAxisAlignment.START,
            cross_alignment=ft.CrossAxisAlignment.START,
        ),
    )

    # =============================================================
    # APPEARANCE SETTINGS BUTTON
    # =============================================================

    theme_details_btn = ft.ElevatedButton(
        "Appearance Options (Centered Body) >",
        on_click=lambda e: e.page.run_task(
            pop_continue.open_panel,
            top_text="Appearance Settings",
            components=[
                ft.Text(
                    "Customize UI Theme:",
                    size=18,
                ),
                ft.Row(
                    controls=[
                        ft.RadioGroup(
                            content=ft.Column(
                                controls=[
                                    ft.Radio(
                                        value="dark",
                                        label="Dark Mode",
                                    ),
                                    ft.Radio(
                                        value="light",
                                        label="Light Mode",
                                    ),
                                ]
                            ),
                            value="dark",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ],
            main_alignment=ft.MainAxisAlignment.CENTER,
            cross_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    # =============================================================
    # SETTINGS MENU
    # =============================================================

    settings = PopMenu(
        components=[
            ip_control,
            ft.Divider(),
            network_details_btn,
            theme_details_btn,
        ],
        icon_name_open=ft.Icons.SETTINGS,
        icon_name_exit=ft.Icons.CLOSE,
        top_text="Settings",
        pop_continue=pop_continue,
    )

    # =============================================================
    # TOP BAR
    # =============================================================

    top_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            settings,
            ft.IconButton(
                icon=ft.Icons.MENU,
                on_click=lambda e: print("hello"),
                tooltip="hello",
            ),
        ],
        spacing=10,
    )

    # =============================================================
    # MAIN CONTENT
    # =============================================================

    main_content = ft.Container(
        expand=True,
        alignment=ft.Alignment(0, 0),
        content=ft.Text(
            "Welcome to the App!",
            size=32,
            weight=ft.FontWeight.BOLD,
        ),
    )

    # =============================================================
    # PAGE
    # =============================================================

    page.add(
        ft.Column(
            controls=[
                top_bar,
                ft.Divider(),
                main_content,
            ],
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)