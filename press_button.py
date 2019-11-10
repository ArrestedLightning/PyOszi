from PyOszi import *
from time import sleep

if __name__ == "__main__":
    b = PyOsziButtons
    scope = PyOszi(debug=False)
    scope.press_button(b.BTN_RUN_STOP)
    sleep(1)
    scope.close()
