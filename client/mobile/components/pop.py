import flet as ft
import text_editor


class PopContinue(ft.Container):
    """Secondary detail/settings panel template.

    Header stays pinned at the top, while body content alignment can be customized.
    """

    def __init__(
        self,
        top_text: str = "Details",
        components: list = [],
        icon_name_exit: ft.IconData = ft.Icons.CLOSE,
        panel_color="surfaceContainerHigh",
        left_offset=280,
        animation_duration=300,
        animation_curve=ft.AnimationCurve.EASE_OUT,
        main_alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START,
        cross_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.START,
        spacing: int = 15,
        padding: int = 20,
    ):
        self.components = components or []
        self.top_text = top_text
        self.icon_name_exit = icon_name_exit
        self.is_open = False

        # --------------------------------
        # Header (Pinned at Top)
        # --------------------------------
        self.title_text = ft.Text(
            self.top_text,
            size=20,
            weight=ft.FontWeight.BOLD,
        )

        self.header_row = ft.Row(
            controls=[
                self.title_text,
                ft.IconButton(
                    icon=self.icon_name_exit,
                    on_click=lambda e: self.close_panel(),
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

        # --------------------------------
        # Body (Customizable Alignment)
        # --------------------------------
        self.body_section = ft.Column(
            controls=self.components,
            spacing=spacing,
            alignment=main_alignment,
            horizontal_alignment=cross_alignment,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        # Main Layout
        super().__init__(
            top=0,
            bottom=0,
            left=left_offset,
            right=0,
            bgcolor=panel_color,
            padding=padding,
            offset=ft.Offset(1, 0),
            animate_offset=ft.Animation(
                animation_duration,
                animation_curve,
            ),
            content=ft.Column(
                controls=[
                    self.header_section,
                    self.body_section,
                ],
                expand=True,
                spacing=10,
            ),
        )

    def open_panel(
        self,
        top_text: str = "",
        components: list = [],
        main_alignment: ft.MainAxisAlignment = None,
        cross_alignment: ft.CrossAxisAlignment = None,
    ):
        """Open panel and update title, body controls, or body alignment dynamically."""
        if top_text is not None:
            self.title_text.value = top_text

        # Update body alignment without affecting header
        if main_alignment is not None:
            self.body_section.alignment = main_alignment

        if cross_alignment is not None:
            self.body_section.horizontal_alignment = cross_alignment

        # Update body components
        if components is not None:
            self.components = components
            self.body_section.controls = self.components

        self.is_open = True
        self.offset = ft.Offset(0, 0)
        self.update()

    def close_panel(self):
        self.is_open = False
        self.offset = ft.Offset(1, 0)
        self.update()


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

        self.button = ft.IconButton(
            icon=icon_name_open,
            on_click=self.toggle_pop_menu,
            tooltip="Open Menu",
        )

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
        if self.pop_continue and self.pop_continue not in self.page.overlay:
            self.page.overlay.append(self.pop_continue)

        if self.pop_menu_panel not in self.page.overlay:
            self.page.overlay.append(self.pop_menu_panel)

        self.page.update()

    def toggle_pop_menu(self, e=None):
        self.pop_menu_open = not self.pop_menu_open
        self.pop_menu_panel.offset = (
            ft.Offset(0, 0) if self.pop_menu_open else ft.Offset(-1, 0)
        )
        self.pop_menu_panel.update()

        if not self.pop_menu_open and self.pop_continue:
            self.pop_continue.close_panel()


def main(page: ft.Page):
    page.title = "Settings Menu"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    pop_continue = PopContinue(
        top_text="Advanced Details",
        components=[
            ft.Text("Select an option from the menu to view details."),
        ],
    )

    ip_control = text_editor.TextEditor(
        initial_text="127.0.0.1",
        on_change_text=lambda ip: print(f"Server IP set to: {ip}"),
        text_color="white",
    )

    # Option 1: Body aligned Left/Top
    network_details_btn = ft.ElevatedButton(
        "Network Options (Top-Left) >",
        on_click=lambda e: pop_continue.open_panel(
            top_text="Network Settings",
            components=[
                ft.Text("Configure Port and Subnet:"),
                ft.TextField(label="Port", value="8080"),
                ft.TextField(label="Subnet Mask", value="255.255.255.0"),
                ft.Switch(label="Enable DHCP"),
            ],
            main_alignment=ft.MainAxisAlignment.START,
            cross_alignment=ft.CrossAxisAlignment.START,
        ),
    )

    # Option 2: Body aligned Center/Center (Title stays at the top!)
    # Option 2: Body aligned Center/Center (Title stays at the top!)
    theme_details_btn = ft.ElevatedButton(
        "Appearance Options (Centered Body) >",
        on_click=lambda e: pop_continue.open_panel(
            top_text="Appearance Settings",
            components=[
                ft.Text("Customize UI Theme:", size=18),
                
                # Wrap the RadioGroup in a Centered Row to stop it from stretching to the left
                ft.Row(
                    controls=[
                        ft.RadioGroup(
                            content=ft.Column(
                                controls=[
                                    ft.Radio(value="dark", label="Dark Mode"),
                                    ft.Radio(value="light", label="Light Mode"),
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

    main_content = ft.Container(
        expand=True,
        alignment=ft.Alignment(0, 0),
        content=ft.Text(
            "Welcome to the App!",
            size=32,
            weight=ft.FontWeight.BOLD,
        ),
    )

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