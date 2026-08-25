class MessageSyntaxError(Exception):
    def __init__(self, arg):
        self._arg = arg

    def __str__(self):
        return f"Provided message '{self._arg}' is invalid"

    def get_arg(self):
        return self._arg


def generate_message(code, data):
    """
    creates a message in the protocol
    :param code: the code of the message
    :param data: the data of the message
    :type code: int
    :type data: str
    :return: a message string
    :rtype: string
    """
    return f'code:"{code}",data:"{data}"'

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
    server_message = decode_message(server_message)
    print(server_message[1])


def decode_message(message):
    """
    give you the code and data from a message
    :param message: a message in the protocol
    :type message: str
    :return: the code and the data
    :rtype: list
    """
    try:
        message_parts = message.split(",")

        code_data = [part.split(":")[1][1:-1] for part in message_parts]

        return code_data

    except Exception:
        raise MessageSyntaxError(message) from None


def main():
    message = generate_message(200, "hello")
    # message = 'dad'
    print(message)
    print(decode_message(message))


if __name__ == "__main__":
    main()
