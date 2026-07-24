import keyboard # pyright: ignore[reportMissingModuleSource]
import socket
import util

SERVER_IP = ''
SERVER_PORT = 849  # ascii sum keyboard

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

def on_key(event, server_soc):
    """
    listens to a key and sends it to the server
    :param event: the key that was pressed
    :param server_soc: the socket to the server
    :type code: KeyboardEvent
    :type server_soc: socket
    :return: None
    :rtype: None
    """
    client_message = util.generate_message(100, event.name)
    print(f"Key pressed: {event.name}")

    send_message(client_message, server_soc)

def record_Keys(server_soc):
    """
    listens for keys and send each key individually to the sever
    :param server_soc: the socket to the server
    :type server_soc: socket
    :return: None
    :rtype: None
    """
    # The lambda receives `e` (event) from keyboard and passes both `e` and `my_custom_value`
    keyboard.on_press(lambda e: on_key(e, server_soc))

    print("Listening for key presses... Press ESC to quit.")
    keyboard.wait("esc")

    

def main():
    welcome()

    SERVER_IP = input("Enter machine ip: ")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_soc:
            server_soc.connect((SERVER_IP, SERVER_PORT))
            choice = '-1'
            

            while choice != '0':
                menu()
                choice = input("Enter your choice: ")

                if choice == '0':
                    client_message = util.generate_message(900)

                elif choice == '1':
                    record_Keys(server_soc)
                elif choice == '2':
                    client_message = util.generate_message(150, record_input())
                elif choice == '3':
                    client_message = util.generate_message(100, 'backspace')
                    send_message(client_message, server_soc)
                else:
                    print("No match found")
                    continue
    

if __name__ == "__main__":
    main()
