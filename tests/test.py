# Source - https://stackoverflow.com/a/78799842
# Posted by VonDerHase, modified by community. See post 'Timeline' for change history
# Retrieved 2026-08-21, License - CC BY-SA 4.0

import keyboard

def test(callback):
    print(callback.name)

keyboard.hook(test)
keyboard.wait()
