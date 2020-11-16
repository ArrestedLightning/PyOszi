from PyOszi import *
from time import sleep
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
import math

def callback(data, channel):
    if (data):
        print("Received data of length {}".format(len(data)))
        print("RMS of data is: {}".format(calc_rms(data)))
        plt.plot(data)
        plt.grid()
        plt.show()
    else:
        print("Error receiving data on channel {} (Is scope in run mode?)".format(channel))

def calc_rms(data):
    sum_squares = 0
    for d in data:
        sum_squares += (d * d)
    return math.sqrt(sum_squares / len(data))

if __name__ == "__main__":
    b = PyOsziButtons
    scope = PyOszi(debug=False)
    scope.request_raw_data(0, callback)
    #Scope communication is asynchronous, give it time to  finish
    sleep(2)
    scope.close()
