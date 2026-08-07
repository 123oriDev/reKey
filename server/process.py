import keyboard  # pyright: ignore[reportMissingModuleSource]
import util

CLIENT_KEY = "100"
CLIENT_WRITE = "150"
CLIENT_PRESS = "200"
CLIENT_RELEASE = "250"
CLIENT_LOGOUT = "900"

def process_message(message):
    """
    process the message(Enter the key) and generate a response
    :param message: a client message in the protocol
    :type message: str
    :return: the response message
    :rtype: string
    """
    try:
        code_data = util.decode_message(message)

    except Exception as e:
        return util.generate_message(900, e)

    print(code_data)

    try:
        if code_data[0] == CLIENT_KEY:
            keyboard.press_and_release(code_data[1])

        elif code_data[0] == CLIENT_WRITE:
            keyboard.write(code_data[1])
        
        elif code_data[0] == CLIENT_PRESS:
            keyboard.press(code_data[1])

        elif code_data[0] == CLIENT_RELEASE:
            keyboard.release(code_data[1])

        elif code_data[0] == CLIENT_LOGOUT:
            pass
        else:
            print("No match found")

    except Exception:
        return util.generate_message(900, "Invalid data input")
    else:
        return util.generate_message(100, "Success")


def main():
    message = 'code:"150",data:"hello"'

    print(process_message(message))


if __name__ == "__main__":
    main()
