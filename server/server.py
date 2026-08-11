import socket

import process

PORT = 849  # ascii sum keyboard


def main():
    print("Server is running")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("", PORT))
        sock.listen(1)

        while True:
            try:
                client_soc, addr = sock.accept()
                print(f"{addr} Connected")

                with client_soc:
                    server_message = ""

                    while server_message != 'code:"300",data:""':
                        client_message = client_soc.recv(512).decode()
                        server_message = process.process_message(client_message)
                        client_soc.sendall(server_message.encode())
            except Exception as e:  # noqa: BLE001
                print(f"{addr} Disconnected")
                print(e)


if __name__ == "__main__":
    main()
