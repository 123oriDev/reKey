import keyboard # pyright: ignore[reportMissingModuleSource]
import socket
import util

SERVER_IP = ''
SERVER_PORT = 849  # ascii sum keyboard

def welcome():
    print(r"""
               _                               _                      _  __          
 __      _____| | ___ ___  _ __ ___   ___     | |_ ___       _ __ ___| |/ /___ _   _ 
 \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \    | __/ _ \     | '__/ _ \ ' // _ \ | | |
  \ V  V /  __/ | (_| (_) | | | | | |  __/    | || (_) |    | | |  __/ . \  __/ |_| |
   \_/\_/ \___|_|\___\___/|_| |_| |_|\___|     \__\___/     |_|  \___|_|\_\___|\__, |
                                                                               |___/                                                                                                                                             
    """)

def menu():
    print("[0] Quit")
    print("[1] Record keys")
    print("[2] Enter a key")
    print("[3] Delete")


def record_input():
    print("Recording. Press Esc to stop.")
    events = keyboard.record("esc")

    typed_string = list(keyboard.get_typed_strings(events))[0]

    return typed_string

def deleteKey():


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
                    client_message = util.generate_message(150, record_input())
                elif choice == '2':
                    client_message = util.generate_message(100, input("Enter a key"))
                elif choice == '3':
                    client_message = util.generate_message(100, 'delete')
                else:
                    print("No match found")
                    continue

                server_soc.sendall(client_message.encode())
                server_message = server_soc.recv(512).decode()
                server_message = util.decode_message(server_message)
                print(server_message[1])
    

if __name__ == "__main__":
    main()
