import flet as ft
from file_system import FileDB


class FileList(ft.ReorderableListView):

    def __init__(
        self,
        db: FileDB,
        on_delete,
        get_extra_buttons,
    ):
        super().__init__(
            expand=True,
            spacing=8,
            show_default_drag_handles=False,
        )

        self.db = db
        self.on_delete = on_delete
        self.get_extra_buttons = get_extra_buttons

        self.on_reorder = self._reorder

        self.refresh()

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh(self):

        self.controls.clear()

        files = self.db.get_all()

        for file in files:

            self.controls.append(
                self.build_item(file)
            )

        if not files:

            self.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No files added yet.",
                        color=ft.Colors.GREY,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=30,
                )
            )

    # ========================================================
    # BUILD FILE ITEM
    # ========================================================

    def build_item(self, file):

        return ft.Card(
            data=file["id"],

            content=ft.Container(
                padding=10,

                content=ft.Row(
                    controls=[
                        self.build_drag_handle(),
                        self.build_file_info(file),
                        self.build_actions(file),
                        self.build_delete_button(file),
                    ],

                    vertical_alignment=(
                        ft.CrossAxisAlignment.CENTER
                    ),
                ),
            ),
        )

    # ========================================================
    # DRAG HANDLE
    # ========================================================

    def build_drag_handle(self):

        return ft.ReorderableDragHandle(
            content=ft.Icon(
                ft.Icons.DRAG_INDICATOR,
                color=ft.Colors.GREY,
            ),
        )

    # ========================================================
    # FILE INFO
    # ========================================================

    def build_file_info(self, file):

        return ft.Column(
            controls=[
                ft.Text(
                    file["name"],
                    weight=ft.FontWeight.BOLD,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),

                ft.Text(
                    file["path"],
                    size=12,
                    color=ft.Colors.GREY,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],

            expand=True,

            spacing=3,
        )

    # ========================================================
    # EXTRA BUTTONS
    # ========================================================

    def build_actions(self, file):

        buttons = self.get_extra_buttons(file)

        return ft.Row(
            controls=buttons,
            spacing=0,
        )

    # ========================================================
    # DELETE BUTTON
    # ========================================================

    def build_delete_button(self, file):

        return ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED,
            tooltip="Delete",

            on_click=lambda e, file_id=file["id"]:
                self.on_delete(file_id),
        )

    # ========================================================
    # REORDER
    # ========================================================

    def _reorder(self, e: ft.OnReorderEvent):

        item = self.controls.pop(e.old_index)

        self.controls.insert(
            e.new_index,
            item,
        )

        ids = [
            control.data
            for control in self.controls
            if control.data is not None
        ]

        self.db.save_order(ids)

        self.update()