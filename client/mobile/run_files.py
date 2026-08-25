import time
import socket
import flet as ft
import run_key_file
import util
from file_list import FileList
from file_system import FileDB


class SocketFileKeyHandler(run_key_file.FileKeyHandler):
    def __init__(self, socket):
        self._socket = socket

    def header(self, head, key):
        if head == "press":
            client_message = util.generate_message(200, key)
            util.send_message(client_message, self._socket)

        elif head == "release":
            client_message = util.generate_message(250, key)
            util.send_message(client_message, self._socket)

        elif head == "key":
            client_message = util.generate_message(100, key)
            util.send_message(client_message, self._socket)

        elif head == "write":
            client_message = util.generate_message(150, key)
            util.send_message(client_message, self._socket)

        elif head == "sleep":
            time.sleep(float(key))

    def no_header(self, line):
        print(f"{line} - invalid")


class RunFiles:

    def __init__(self,sock: list, page: ft.Page):
        self._sock = sock
        self.page = page
        self.db = FileDB()

        self.status = ft.Text(
            size=13,
            color=ft.Colors.GREY,
        )

        self.picker = ft.FilePicker()

        self.file_list = FileList(
            db=self.db,

            on_delete=self.delete_file,

            get_extra_buttons=self.get_extra_buttons,
        )

        self.view = self.build()

    # ========================================================
    # EXTRA BUTTONS
    # ========================================================

    def get_extra_buttons(self, file):

        return [

            ft.IconButton(
                icon=ft.Icons.PLAY_ARROW,
                icon_color=ft.Colors.GREEN,

                tooltip="Print path",

                on_click=lambda e, path=file["path"]:
                    self.play_file(path),
            ),

            ft.IconButton(
                icon=ft.Icons.EDIT_OUTLINED,

                tooltip="Rename",

                on_click=lambda e, file_id=file["id"]:
                    self.rename_file(file_id),
            ),
        ]

    # ========================================================
    # PLAY
    # ========================================================

    def play_file(self, path):
        handler = SocketFileKeyHandler(self._sock[0])
        print(path)

        FileReader = run_key_file.FileKeyReader(
            handler=handler, path=path
        )
        FileReader.start()
        
        self.status.value = path

        self.page.update()

    # ========================================================
    # RENAME
    # ========================================================

    def rename_file(self, file_id):

        file = next(
            (
                file
                for file in self.db.get_all()
                if file["id"] == file_id
            ),
            None,
        )

        if not file:
            return

        name_field = ft.TextField(
            value=file["name"],
            label="File name",
            autofocus=True,
        )

        def close():

            dialog.open = False

            self.page.update()

        def rename(e):

            new_name = name_field.value.strip()

            if not new_name:
                return

            self.db.rename(
                file_id,
                new_name,
            )

            close()

            self.file_list.refresh()
            self.file_list.update()

            self.status.value = "File renamed."

            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Rename file"),

            content=name_field,

            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda e: close(),
                ),

                ft.Button(
                    "Rename",
                    on_click=rename,
                ),
            ],
        )

        self.page.show_dialog(dialog)

    # ========================================================
    # DELETE
    # ========================================================

    def delete_file(self, file_id):

        self.db.delete(file_id)

        self.status.value = "File deleted."

        self.file_list.refresh()
        self.file_list.update()

    # ========================================================
    # ADD FILES
    # ========================================================

    async def add_files(self, e):

        try:

            files = await self.picker.pick_files(
                allow_multiple=True,
                dialog_title="Select files",
            )

            if not files:
                return

            added = 0

            for file in files:

                if not file.path:
                    continue

                if self.db.add(
                    file.name,
                    file.path,
                ):
                    added += 1

            self.status.value = (
                f"{added} file(s) added."
                if added
                else "Files already added."
            )

            self.file_list.refresh()
            self.file_list.update()

        except Exception as ex:

            self.status.value = f"Error: {ex}"

            self.page.update()

    # ========================================================
    # BUILD
    # ========================================================

    def build(self):

        header = ft.Row(
            controls=[
                self.status,

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

        return ft.Column(
            controls=[
                header,


                self.file_list,
            ],

            spacing=12,

            expand=True,
        )