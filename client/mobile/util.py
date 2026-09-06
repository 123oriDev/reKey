"""Shim — canonical is common/messages.py. Keeps `import util` working."""
import os, sys
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)
try:
    from common.messages import MessageSyntaxError, generate_message, decode_message, send_message
except ImportError:
    class MessageSyntaxError(Exception):  # type: ignore[no-redef]
        def __init__(self, arg): self._arg = arg
        def __str__(self): return f"Provided message '{self._arg}' is invalid"
        def get_arg(self): return self._arg
    def generate_message(code, data):  # type: ignore[no-redef]
        return f'code:"{code}",data:"{data}"'
    def decode_message(message):  # type: ignore[no-redef]
        try:
            message_parts = message.split(",")
            code_data = [part.split(":")[1][1:-1] for part in message_parts]
            return code_data
        except Exception:
            raise MessageSyntaxError(message) from None
    def send_message(client_message, server_soc):  # type: ignore[no-redef]
        server_soc.sendall(client_message.encode())
        server_message = server_soc.recv(512).decode()
        server_message = decode_message(server_message)
        print(server_message[1])

def main():
    message = generate_message(200, "hello")
    print(message)
    print(decode_message(message))

if __name__ == "__main__":
    main()
