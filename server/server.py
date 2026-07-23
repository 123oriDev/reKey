import socket
import process

PORT = 849  # ascii sum keyboard


def main():
    print("Code here")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("", PORT))
        sock.listen(1)

        client_soc, addr = sock.accept()

        with client_soc:
            server_message = ""

            while server_message != 'code:"300",data:""':
                client_message = client_soc.recv(512).decode()
                server_message = process.process_message(client_message)
                client_soc.sendall(server_message.encode())


if __name__ == "__main__":
    main()
