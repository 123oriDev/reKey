import os
import sqlite3
import flet as ft


# ============================================================
# DATABASE
# ============================================================

class FileDB:
    def __init__(self):
        db_path = os.path.join(
            os.getenv("FLET_APP_STORAGE_DATA", "."),
            "files.db",
        )

        self.db = sqlite3.connect(db_path)
        self.db.row_factory = sqlite3.Row

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                display_order INTEGER NOT NULL
            )
        """)

        self.db.commit()

    def get_all(self):
        return self.db.execute("""
            SELECT *
            FROM files
            ORDER BY display_order
        """).fetchall()

    def add(self, name: str, path: str):
        if self.db.execute(
            "SELECT id FROM files WHERE path = ?",
            (path,),
        ).fetchone():
            return False

        order = self.db.execute(
            """
            SELECT COALESCE(MAX(display_order), -1) + 1
            FROM files
            """
        ).fetchone()[0]

        self.db.execute(
            """
            INSERT INTO files (name, path, display_order)
            VALUES (?, ?, ?)
            """,
            (name, path, order),
        )

        self.db.commit()
        return True

    def delete(self, file_id: int):
        self.db.execute(
            "DELETE FROM files WHERE id = ?",
            (file_id,),
        )

        self.db.commit()
        self.save_order([f["id"] for f in self.get_all()])

    def save_order(self, ids):
        with self.db:
            for order, file_id in enumerate(ids):
                self.db.execute(
                    """
                    UPDATE files
                    SET display_order = ?
                    WHERE id = ?
                    """,
                    (order, file_id),
                )


# ============================================================
# FILE ITEM
# ============================================================

class FileItem(ft.Card):
    def __init__(
        self,
        file,
        on_delete,
        on_play,
        extra_buttons=None,
    ):
        self.file = file

        super().__init__(
            data=file["id"],
            content=ft.Container(
                padding=10,
                content=self._build(
                    on_delete,
                    on_play,
                    extra_buttons or [],
                ),
            ),
        )

    def _build(
        self,
        on_delete,
        on_play,
        extra_buttons,
    ):
        buttons = [
            # Play
            ft.IconButton(
                icon=ft.Icons.PLAY_ARROW,
                icon_color=ft.Colors.GREEN,
                tooltip="Print path",
                on_click=lambda e:
                    on_play(self.file["path"]),
            ),
        ]

        # Add any extra buttons here
        buttons.extend(extra_buttons)

        # Delete always stays last
        buttons.append(
            ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                icon_color=ft.Colors.RED,
                tooltip="Delete",
                on_click=lambda e:
                    on_delete(self.file["id"]),
            )
        )

        return ft.Row(
            [
                # Drag handle
                ft.ReorderableDragHandle(
                    content=ft.Icon(
                        ft.Icons.DRAG_INDICATOR,
                        color=ft.Colors.GREY,
                    ),
                ),

                # File information
                ft.Column(
                    [
                        ft.Text(
                            self.file["name"],
                            weight=ft.FontWeight.BOLD,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),

                        ft.Text(
                            self.file["path"],
                            size=12,
                            color=ft.Colors.GREY,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    expand=True,
                ),

                # Buttons
                *buttons,
            ]
        )


# ============================================================
# FILE LIST
# ============================================================

class FileList(ft.ReorderableListView):
    def __init__(
        self,
        db: FileDB,
        on_delete,
        on_play,
    ):
        super().__init__(
            expand=True,
            spacing=8,
            show_default_drag_handles=False,
        )

        self.db = db
        self.on_delete = on_delete
        self.on_play = on_play

        self.on_reorder = self._reorder

        self.refresh()

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    def refresh(self):
        self.controls.clear()

        files = self.db.get_all()

        for file in files:
            self.controls.append(
                FileItem(
                    file,
                    on_delete=self.on_delete,
                    on_play=self.on_play,
                )
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

    # --------------------------------------------------------
    # REORDER
    # --------------------------------------------------------

    def _reorder(self, e: ft.OnReorderEvent):
        item = self.controls.pop(e.old_index)

        self.controls.insert(
            e.new_index,
            item,
        )

        ids = [
            item.data
            for item in self.controls
            if item.data is not None
        ]

        self.db.save_order(ids)

        self.update()


# ============================================================
# APPLICATION
# ============================================================

class FileApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = FileDB()

        self.status = ft.Text(size=14)

        self.file_list = FileList(
            db=self.db,
            on_delete=self.delete_file,
            on_play=self.play_file,
        )

        self.picker = ft.FilePicker()

        self.build()

    # --------------------------------------------------------
    # FILE ACTIONS
    # --------------------------------------------------------

    def play_file(self, path: str):
        print(path)

        self.status.value = f"Path: {path}"
        self.page.update()

    def delete_file(self, file_id: int):
        self.db.delete(file_id)

        self.status.value = "File deleted."

        self.file_list.refresh()
        self.file_list.update()

    async def add_files(self, e):
        try:
            files = await self.picker.pick_files(
                allow_multiple=True,
                dialog_title="Select files",
            )

            if not files:
                return

            for file in files:
                if not file.path:
                    continue

                added = self.db.add(
                    file.name,
                    file.path,
                )

                self.status.value = (
                    f"Added: {file.name}"
                    if added
                    else f"Already added: {file.name}"
                )

            self.file_list.refresh()
            self.file_list.update()

        except Exception as ex:
            self.status.value = f"Error: {ex}"
            self.page.update()

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def build(self):
        self.page.title = "My Files"
        self.page.padding = 20

        header = ft.Row(
            [
                ft.Text(
                    "My Files",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Container(
                    content=ft.Button(
                        "Add files",
                        icon=ft.Icons.ADD,
                        on_click=self.add_files,
                    ),
                    alignment=ft.Alignment.CENTER_RIGHT,
                    expand=True,
                ),
            ]
        )

        self.page.add(
            ft.SafeArea(
                content=ft.Column(
                    [
                        header,
                        self.status,
                        ft.Divider(),
                        self.file_list,
                    ],
                    expand=True,
                )
            )
        )


# ============================================================
# RUN
# ============================================================

def main(page: ft.Page):
    FileApp(page)


if __name__ == "__main__":
    ft.run(main)