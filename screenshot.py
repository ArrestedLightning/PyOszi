from PyOszi import *
from time import sleep
from datetime import datetime

def callback(img):
    filename = "Screenshot " + datetime.now().isoformat(' ') + ".png"
    img.save(filename)
    print("Screenshot saved to " + filename)
#    img.show()

if __name__ == "__main__":
    b = PyOsziButtons
    scope = PyOszi(debug=False)
    scope.request_screenshot(callback)
    #Scope communication is asynchronous, give it time to  finish
    sleep(2)
    scope.close()
