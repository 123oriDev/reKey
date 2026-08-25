import flet as ft
from pop import PopContinue, PopMenu
from run_files import RunFiles


def main(page: ft.Page):

    page.title = "My App"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    # ========================================================
    # FILES
    # ========================================================

    run_files = RunFiles(page)

    # ========================================================
    # POP CONTINUE
    # ========================================================

    pop_continue = PopContinue(
        top_text="Details",
    )

    # ========================================================
    # FILES OPTION
    # ========================================================

    files_option = ft.ListTile(
        leading=ft.Icon(
            ft.Icons.FOLDER_OUTLINED
        ),

        title=ft.Text(
            "Files",
            weight=ft.FontWeight.BOLD,
        ),

        subtitle=ft.Text(
            "Manage your files",
            size=12,
        ),

        trailing=ft.Icon(
            ft.Icons.CHEVRON_RIGHT,
        ),

        on_click=lambda e:
            pop_continue.open_panel(
                top_text="Files",

                components=[
                    run_files.view,
                ],

                main_alignment=(
                    ft.MainAxisAlignment.START
                ),

                cross_alignment=(
                    ft.CrossAxisAlignment.STRETCH
                ),
            ),
    )

    # ========================================================
    # SETTINGS
    # ========================================================

    settings = PopMenu(
        components=[
            files_option,
        ],

        icon_name_open=ft.Icons.SETTINGS_OUTLINED,

        icon_name_exit=ft.Icons.CLOSE,

        top_text="Settings",

        pop_continue=pop_continue,
    )

    # ========================================================
    # MAIN PAGE
    # ========================================================

    page.add(
        ft.Column(
            controls=[
                settings,

                ft.Container(
                    content=ft.Text(
                        "Welcome to the App!",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                    ),

                    expand=True,

                    alignment=ft.Alignment(0, 0),
                ),
            ],

            expand=True,
        )
    )


if __name__ == "__main__":
    ft.run(main)