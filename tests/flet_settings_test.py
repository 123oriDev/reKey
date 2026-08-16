import flet as ft

def main(page: ft.Page):
    page.title = "Settings Panel Example"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # 1. State / Data
    current_title = "Welcome to the App!"
    settings_open = False  # Track settings drawer state

    # 2. Main Page UI Elements
    main_title = ft.Text(
        value=current_title,
        size=32,
        weight=ft.FontWeight.BOLD,
    )

    # Text input inside the settings panel
    title_input = ft.TextField(
        label="Main Page Title",
        value=current_title,
        on_change=lambda e: update_title(e.control.value),
    )

    def update_title(new_value):
        """Updates the main text dynamically as you type."""
        main_title.value = new_value if new_value.strip() else "Welcome to the App!"
        main_title.update()

    def toggle_settings(e):
        """Slides the panel in or out by toggling its X-axis offset."""
        nonlocal settings_open
        settings_open = not settings_open
        
        # Offset(0, 0) is visible, Offset(-1, 0) pushes it 100% of its width off-screen to the left
        settings_panel.offset = ft.Offset(0, 0) if settings_open else ft.Offset(-1, 0)
        settings_panel.update()

    # 3. Settings Side Panel (Fixed Width + Offset Animation)
    settings_panel = ft.Container(
        width=280,  # Constant fixed width (prevents text wrapping/squishing)
        top=0,
        bottom=0,
        left=0,
        bgcolor="surfaceContainerHighest",
        shadow=ft.BoxShadow(blur_radius=15, color="black54"),
        offset=ft.Offset(-1, 0),  # Starts completely off-screen to the left
        animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT),  # Smooth slide transition
        padding=20,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            on_click=toggle_settings,
                            tooltip="Close Settings",
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(),
                ft.Text("Appearance & Content", size=14, color="grey400"),
                title_input,
            ],
            spacing=15,
        ),
    )

    # 4. Main Content Area
    main_content = ft.Container(
        expand=True,
        padding=30,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS,
                            on_click=toggle_settings,
                            tooltip="Open Settings",
                        ),
                        ft.Text("Dashboard", size=16, color="grey400"),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                ),
                ft.Divider(),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    content=main_title,
                ),
            ],
        ),
    )

    # 5. Root Layout (Stack lets the panel slide over top cleanly)
    page.add(
        ft.Stack(
            controls=[
                main_content,
                settings_panel,
            ],
            expand=True,
        )
    )

ft.app(target=main)