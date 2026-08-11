import socket

import cli_client_util
import run_key_file
import util

SERVER_IP = ""
SERVER_PORT = 849  # ascii sum keyboard


class socket_handler(cli_client_util.BaseKeyHandler):
    """An handler to send messages to the server"""

    def __init__(self, socket: socket.socket):
        self._sock = socket

    def on_press(self, key: str) -> None:
        client_message = util.generate_message(200, key)
        send_message(client_message, self._sock)

    def on_release(self, key: str) -> None:
        client_message = util.generate_message(250, key)
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


def start_menu():
    """
    prints a menu to the user to ask if he wants to connect to a server or
    create a key presses file
    return: None
    rtype: None
    """
    print("[0] Quit")
    print("[1] Connect to a server")
    print("[2] Create a key presses file")


def menu():
    """
    prints server the menu to the user
    return: None
    rtype: None
    """
    print("[0] Quit")
    print("[1] Control the server")
    print("[2] Run a key presses file")
    print("[3] Create a key presses file")


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


def record_Keys(server_soc):
    """Listens for keys and sends each key individually or hotkey to the server.

    :param server_soc: the socket to the server
    :type server_soc: socket
    :return: None
    :rtype: None
    """
    handler = socket_handler(socket=server_soc)

    # 2. Pass the handler and a custom exit shortcut to the interceptor
    interceptor = cli_client_util.KeyboardInterceptor(
        handler=handler, 
        exit_combo={"ctrl", "shift", "alt", "q"}
    )

    interceptor.start()


class key_file_handler(cli_client_util.BaseKeyHandler):
    """An handler to send messages to the server"""

    def __init__(self, file_write):
        self._file_write = file_write

    def on_press(self, key: str) -> None:
        self._file_write.write(f'press:"{key}"\n')

    def on_release(self, key: str) -> None:
        self._file_write.write(f'release:"{key}"\n')


def create_key_file():
    path = input("Enter a path: ")

    with open(path, "w") as file_write:
        handler = key_file_handler(file_write= file_write)

        exit_combo = {"ctrl", "shift", "alt", "q"}
        exit_combo_len = len(exit_combo)
        interceptor = cli_client_util.KeyboardInterceptor(
            handler=handler, 
            exit_combo=exit_combo,
            suppress=False
        )

        interceptor.start()

    with open(path, "r") as file:
            file_read = file.readlines()[:-(exit_combo_len) * 2]
            file_read[-1] = file_read[-1].strip()
            print(file_read)

    with open(path, "w") as file_write:
        file_write.writelines(file_read)


class SocketFileKeyHandler(run_key_file.FileKeyHandler):
    def __init__(self, socket):
        self._socket = socket

    def header(self, head, key):
        if head == "press":
            client_message = util.generate_message(200, key)
            send_message(client_message, self._socket)

        if head == "release":
            client_message = util.generate_message(250, key)
            send_message(client_message, self._socket)

        if head == "key":
            client_message = util.generate_message(100, key)
            send_message(client_message, self._socket)

        if head == "write":
            client_message = util.generate_message(150, key)
            send_message(client_message, self._socket)
        

    def no_header(self, line):
        print(f"{line} - invalid")


def main():
    cli_client_util.check_privileges()


    welcome()

    
    
    choice = -1

    while choice != "1":
        start_menu()
        choice = input("Enter your choice: ")

        if choice == "0":
            return 0
        elif choice == "1":
            SERVER_IP = input("Enter machine ip: ")
        elif choice == "2":
            create_key_file()
        else:
            print("No match found")


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_soc:
        server_soc.connect((SERVER_IP, SERVER_PORT))

        while choice != "0":
            menu()
            choice = input("Enter your choice: ")

            if choice == "0":
                client_message = util.generate_message(900, "")
                send_message(client_message)

            elif choice == "1":
                record_Keys(server_soc)

            elif choice == "2":
                key_file_path = input("Enter a path to the key file: ")
                handler = SocketFileKeyHandler(
                    socket = server_soc
                )
                FileReader = run_key_file.FileKeyReader(
                    handler= handler,
                    path= key_file_path
                )

                FileReader.start()

            else:
                print("No match found")
                continue

        server_soc.close()
        print("disconnected")


if __name__ == "__main__":
    main()
