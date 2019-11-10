from PyOszi import *
from time import sleep

if __name__ == "__main__":
    b = PyOsziButtons
    scope = PyOszi(debug=True)
    sleep(2)
    scope.beep(1)
    sleep(2)
    scope.beep(0.5)
    sleep(.6)
    scope.beep(0.2)
    sleep(2)
    scope.close()
