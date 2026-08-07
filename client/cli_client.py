import socket

import cli_client_util
import keyboard  # pyright: ignore[reportMissingModuleSource]
import util

SERVER_IP = ""
SERVER_PORT = 849  # ascii sum keyboard

class SocketHandler(cli_client_util.BaseKeyHandler):
    """An handler to send messages to the server"""
    
    def __init__(self, socket: socket.socket):
        self._sock = socket

    def on_press(self, key: str) -> None:
        client_message = util.generate_message(200, record_input())
        print(client_message)
        send_message(client_message, self._sock)

    def on_release(self, key: str) -> None:
        client_message = util.generate_message(250, record_input())
        print(client_message)
        send_message(client_message, self._sock)

def welcome():
    """
    prints a welcome text to the user
    return: None
    rtype: None
    """
    print(r"""
               _                               _                      _  __          
 __      _____| | ___ ___  _ __ ___   ___     | |_ ___       _ __ ___| |/ /___ _   _ 
 \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \    | __/ _ \     | '__/ _ \ ' // _ \ | | |
  \ V  V /  __/ | (_| (_) | | | | | |  __/    | || (_) |    | | |  __/ . \  __/ |_| |
   \_/\_/ \___|_|\___\___/|_| |_| |_|\___|     \__\___/     |_|  \___|_|\_\___|\__, |
                                                                               |___/                                                                                                                                             
    """)


def menu():
    """
    prints the menu to the user
    return: None
    rtype: None
    """
    print("[0] Quit")
    print("[1] Record keys")
    print("[2] Record input")
    print("[3] Delete")


def send_message(client_message, server_soc):
    """
    sends a message to the server (send and receive)
    :param client_message: the message to send
    :param server_soc: the socket to the server
    :type code: string
    :type server_soc: socket
    :return: None
    :rtype: None
    """
    server_soc.sendall(client_message.encode())
    server_message = server_soc.recv(512).decode()
    server_message = util.decode_message(server_message)
    print(server_message[1])


def record_input():
    """
    prints a welcome text to the user
    return: a string of what the user entered
    rtype: string
    """
    print("Recording. Press Esc to stop.")
    events = keyboard.record("esc")

    typed_string = list(keyboard.get_typed_strings(events))[0]

    return typed_string

def record_Keys(server_soc):
    """Listens for keys and sends each key individually or hotkey to the server.

    :param server_soc: the socket to the server
    :type server_soc: socket
    :return: None
    :rtype: None
    """
    my_handler = SocketHandler(
        socket = server_soc
    )

    # 2. Pass the handler and a custom exit shortcut to the interceptor
    interceptor = cli_client_util.KeyboardInterceptor(
        handler=my_handler,
        exit_combo={"ctrl", "shift", "alt", "q"}
    )

    interceptor.start()
    


def main():
    cli_client_util.check_privileges()

    welcome()

    SERVER_IP = input("Enter machine ip: ")

    

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_soc:
        server_soc.connect((SERVER_IP, SERVER_PORT))
        choice = "-1"

        while choice != "0":
            menu()
            choice = input("Enter your choice: ")

            if choice == "0":
                client_message = util.generate_message(900)

            elif choice == "1":
                record_Keys(server_soc)
            elif choice == "2":
                client_message = util.generate_message(150, record_input())
            elif choice == "3":
                client_message = util.generate_message(100, "backspace")
                send_message(client_message, server_soc)
            else:
                print("No match found")
                continue


if __name__ == "__main__":
    main()
