import threading
import time

import keyboard
import util

CLIENT_KEY = "100"
CLIENT_WRITE = "150"
CLIENT_PRESS = "200"
CLIENT_RELEASE = "250"
CLIENT_LOGOUT = "900"

# --- NEW: Global set to track which keys are currently being held ---
active_keys = set()

def simulate_physical_hold(key):
    """
    Runs in the background. Simulates physical auto-repeat 
    as long as the key remains in the active_keys set.
    """
    try:
        keyboard.press(key) # Initial press
        
        # 1. Hardware pause (Wait 0.5s, but check constantly if it was released early)
        start = time.time()
        while time.time() - start < 0.5:
            if key not in active_keys:
                return # Key was released before auto-repeat started, stop thread
            time.sleep(0.01)
            
        # 2. Auto-repeat spam loop
        while key in active_keys:
            keyboard.press(key)
            time.sleep(0.03) # Standard physical keyboard repeat rate
            
    finally:
        # 3. Always let go when the thread finishes or crashes
        keyboard.release(key)


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
        
    except Exception as e:  # noqa: BLE001
        return util.generate_message(900, e)

    print(code_data)

    try:
        if code_data[0] == CLIENT_KEY:
            keyboard.press_and_release(code_data[1])

        elif code_data[0] == CLIENT_WRITE:
            keyboard.write(code_data[1])
        
        elif code_data[0] == CLIENT_PRESS:
            key = code_data[1]
            if key not in active_keys:
                active_keys.add(key) # Mark as active
                # Start the background thread so we don't block the server
                threading.Thread(target=simulate_physical_hold, args=(key,), daemon=True).start()

        elif code_data[0] == CLIENT_RELEASE:
            key = code_data[1]
            active_keys.discard(key) # This tells the background thread to stop
            keyboard.release(key)       # Failsafe release just in case

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