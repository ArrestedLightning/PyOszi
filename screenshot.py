from PyOszi import *
from time import sleep

if __name__ == "__main__":
    b = PyOsziButtons
    scope = PyOszi(debug=False)
    scope.request_screenshot()
    sleep(2)
    scope.close()
