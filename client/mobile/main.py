import socket

import flet as ft
import util
from components.pop import PopContinue, PopMenu
from components.text_editor import TextEditor
from components.virtual_keyboard import BaseKeyHandler, VirtualKeyboard
from run_files import RunFiles

SERVER_SOC = [None]

SERVER_IP = "127.0.0.1"

SERVER_PORT = 849

SERVER_CONNECTION = [False]


class AppKeyHandler(BaseKeyHandler):

    """Custom handler to manage keyboard presses, releases, and status messages."""

    def __init__(self, status_text_ui, page: ft.Page):

        self._soc = SERVER_SOC

        self._connection = SERVER_CONNECTION

        self.status_text_ui = status_text_ui

        self.page = page

        self.on_disconnect_callback = None  # Will be attached in main()



    def on_press(self, key: str) -> None:

        if self._connection[0] and self._soc[0]:

            try:

                message = util.generate_message(200, key)

                print(message)

                # Using sendall() is safer than send() to guarantee delivery

                self._soc[0].sendall(message.encode())

            except Exception as e:

                print(f"Network error on press: {e}")

                if self.on_disconnect_callback:

                    self.on_disconnect_callback()



        print(f"DOWN: {key}")



    def on_release(self, key: str) -> None:

        if self._connection[0] and self._soc[0]:

            try:

                message = util.generate_message(250, key)

                print(message)

                self._soc[0].sendall(message.encode())

            except Exception as e:

                print(f"Network error on release: {e}")

                if self.on_disconnect_callback:

                    self.on_disconnect_callback()



        print(f"UP: {key}")



    def on_status_change(self, msg: str) -> None:

        self.status_text_ui.value = msg

        self.status_text_ui.update()


def is_valid_ip(text: str) -> bool:

    parts = text.split('.')

    if len(parts) != 4:

        return False

    for part in parts:

        if not part.isdigit():

            return False

        if not (0 <= int(part) <= 255):

            return False

    return True


def main(page: ft.Page):
    page.title = "ReKey Full Virtual Keyboard"
    page.bgcolor = "#0F172A"
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO



    status_text = ft.Text(
        "Press any key...",

        size=44,
        weight="bold",
        color="#38BDF8",
        text_align="center",
    )

    keyboard_handler = AppKeyHandler(status_text, page)
    keyboard = VirtualKeyboard(handler=keyboard_handler)


    connection_switch = ft.Switch(
        value=False,
        active_color="#22C55E",        
        active_track_color="#15803D",  
        inactive_thumb_color="#EF4444",
        inactive_track_color="#991B1B",
        tooltip="Toggle Server Connection"
    )



    def disconnect_server(switch_ctrl):
        """Safely closes active socket and resets UI to disconnected (Red)."""

        if SERVER_SOC[0]:
            try:
                SERVER_SOC[0].close()

            except Exception:  # noqa: S110
                pass

            SERVER_SOC[0] = None
        SERVER_CONNECTION[0] = False

       

        if switch_ctrl:

            switch_ctrl.value = False

            switch_ctrl.update()


    # 1. Provide the handler with a way to trigger a UI disconnect
    def force_disconnect_from_handler():

        disconnect_server(connection_switch)
        keyboard_handler.on_status_change("Connection Lost!")


    keyboard_handler.on_disconnect_callback = force_disconnect_from_handler


    def toggle_connection(e):
        global SERVER_IP
        switch_ctrl = e.control


        if switch_ctrl.value:  
            try:
                if SERVER_SOC[0]:
                    SERVER_SOC[0].close()

                soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                soc.settimeout(2.0)  
                soc.connect((SERVER_IP, SERVER_PORT))

                # Reset timeout to None so standard socket operations don't unexpectedly timeout
                soc.settimeout(None)

               
                SERVER_SOC[0] = soc
                SERVER_CONNECTION[0] = True
                print(f"Connection accepted by {SERVER_IP}:{SERVER_PORT}")

               
                switch_ctrl.value = True
                switch_ctrl.update()
                keyboard_handler.on_status_change("Connected!")

               

            except Exception as ex:

                print(f"Connection refused or failed: {ex}")

                disconnect_server(switch_ctrl)  

        else:

            disconnect_server(switch_ctrl)

            keyboard_handler.on_status_change("Disconnected")


    connection_switch.on_change = toggle_connection


    def on_ip_change(new_ip):
        global SERVER_IP

        try:
            if is_valid_ip(new_ip):
                if SERVER_CONNECTION[0]:
                    print("IP changed while connected. Disconnecting automatically...")
                    disconnect_server(connection_switch)
                    keyboard_handler.on_status_change("Disconnected")

                SERVER_IP = new_ip
                print(f"Server IP set to: {SERVER_IP}")

        except Exception as err:
            print(f"Error in on_ip_change: {err}")


    ip_control = TextEditor(
        initial_text="127.0.0.1",
        on_change_text=on_ip_change,
        filter_func=is_valid_ip
    )

    pop_continue = PopContinue(
        top_text="Advanced Details",
        components=[
            ft.Text("Select an option from the menu to view details."),
        ],
    )

    run_files = RunFiles(SERVER_SOC, page)
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
    
    
    settings = PopMenu(
        components=[
            files_option,
        ],
        icon_name_open=ft.Icons.SETTINGS,
        icon_name_exit=ft.Icons.CLOSE,
        top_text="Settings",
        pop_continue=pop_continue,
    )

    top_bar = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Row(
                controls=[
                    settings,
                    ip_control,
                    connection_switch,  

                ]

            ),

            ft.Row(

                controls=[

                    ft.IconButton(

                        icon=ft.Icons.SEARCH,

                        on_click=lambda e: print("Search opened!"),

                    ),

                    ft.IconButton(

                        icon=ft.Icons.LANGUAGE,

                        on_click=keyboard.toggle_caps_lock,

                        tooltip="Toggle Caps Lock",

                    ),

                ]

            ),

        ],

    )



    main_screen = ft.Container(

        content=ft.Column(

            [status_text, ft.Container(height=15), keyboard],

            alignment=ft.MainAxisAlignment.CENTER,

            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

            spacing=8,

        ),

        expand=True,

        alignment=ft.Alignment(0, 0),

    )



    page.add(top_bar, main_screen)





if __name__ == "__main__":

    ft.app(main) 

