#!/usr/bin/env python
# Released under MIT license.
# Based on code written by Uwe Hermann <uwe@hermann-uwe.de>, released as public domain.

from array import array
import usb
from time import sleep
import queue
import threading
import sys
from PIL import Image

class PyOsziButtons:
    BTN_F0                               = [0x00, 0x01]
    BTN_F1                               = [0x01, 0x01]
    BTN_F2                               = [0x02, 0x01]
    BTN_F3                               = [0x03, 0x01]
    BTN_F4                               = [0x04, 0x01]
    BTN_F5                               = [0x05, 0x01]
    BTN_F6                               = [0x06, 0x01]
    BTN_F7                               = [0x07, 0x01]
    BTN_V0_LEFT_TURN                     = [0x08, 0x01]
    BTN_V0_RIGHT_TURN                    = [0x09, 0x01]
    BTN_V0_PRESS                         = [0x0A, 0x01]
    BTN_SAVE_RECALL                      = [0x0B, 0x01]
    BTN_MEASURE                          = [0x0C, 0x01]
    BTN_ACQUIRE                          = [0x0D, 0x01]
    BTN_UTILITY                          = [0x0E, 0x01]
    BTN_CURSOR                           = [0x0F, 0x01]
    BTN_DISPLAY                          = [0x10, 0x01]
    BTN_AUTOSET                          = [0x11, 0x01]
    BTN_SINGLE_SEQ                       = [0x12, 0x01]
    BTN_RUN_STOP                         = [0x13, 0x01]
    BTN_HELP                             = [0x14, 0x01]
    BTN_DEFAULT_SETUP                    = [0x15, 0x01]
    BTN_SAVE_TO_USB                      = [0x16, 0x01]
    BTN_MATH_MENU                        = [0x17, 0x01]
    BTN_CH1_MENU                         = [0x18, 0x01]
    BTN_CH1_POSITION_LEFT_TURN           = [0x19, 0x01]
    BTN_CH1_POSITION_RIGHT_TURN          = [0x1A, 0x01]
    BTN_CH1_POSITION_PRESS               = [0x1B, 0x01]
    BTN_CH1_VOLTS_DIV_LEFT_TURN          = [0x1C, 0x01]
    BTN_CH1_VOLTS_DIV_RIGHT_TURN         = [0x1D, 0x01]
    BTN_CH2_MENU                         = [0x1E, 0x01]
    BTN_CH2_POSITION_LEFT_TURN           = [0x1F, 0x01]
    BTN_CH2_POSITION_RIGHT_TURN          = [0x20, 0x01]
    BTN_CH2_POSITION_PRESS               = [0x21, 0x01]
    BTN_CH2_VOLTS_DIV_LEFT_TURN          = [0x22, 0x01]
    BTN_CH2_VOLTS_DIV_RIGHT_TURN         = [0x23, 0x01]
    BTN_HORZ_MENU                        = [0x24, 0x01]
    BTN_HORIZONTAL_POSITION_RIGHT_TURN   = [0x25, 0x01]
    BTN_HORIZONTAL_POSITION_LEFT_TURN    = [0x26, 0x01]
    BTN_HORIZONTAL_POSITION_PRESS        = [0x27, 0x01]
    BTN_HORIZONTAL_SEC_DIV_LEFT_TURN     = [0x28, 0x01]
    BTN_HORIZONTAL_SEC_DIV_RIGHT_TURN    = [0x29, 0x01]
    BTN_TRIG_MENU                        = [0x2A, 0x01]
    BTN_TRIGGER_LEVEL_LEFT_TURN          = [0x2B, 0x01]
    BTN_TRIGGER_LEVEL_RIGHT_TURN         = [0x2C, 0x01]
    BTN_TRIGGER_LEVEL_PRESS              = [0x2D, 0x01]
    BTN_SET_TO_50_PCT                    = [0x2E, 0x01]
    BTN_FORCE_TRIG                       = [0x2F, 0x01]
    BTN_PROBE_CHECK                      = [0x30, 0x01]

class PyOszi:

    echo_cmd = [0x53, 0x04, 0x00, 0x00, 0x09, 0xa7]
    run_cmd = [0x53, 0x04, 0x00, 0x12, 0x00, 0x00]
    stop_cmd = [0x53, 0x04, 0x00, 0x12, 0x00, 0x01]
    lock_cmd = [0x53, 0x04, 0x00, 0x12, 0x01, 0x01]
    unlock_cmd = [0x53, 0x04, 0x00, 0x12, 0x01, 0x00]
    beep_cmd = [0x43, 0x03, 0x00, 0x44]
    btn_cmd = [0x53, 0x04, 0x00, 0x13]
    screenshot_cmd = [0x53, 0x02, 0x00, 0x20, 0x75]
    
    image_buffer = []
    
    
    def __init__(self, debug=False):
        self.debug = debug
        # Find and open the device.
        self.dev = usb.core.find(idVendor = 0x049f, idProduct = 0x505a)
        if self.dev is None:
            raise IOError("Hantek/Voltcraft/Tekway DSO not found. Did you connect it via USB?")

        # On Linux the 'cdc_subset' driver grabs the device, unload it first.
        if self.dev.is_kernel_driver_active(0):
            self.dev.detach_kernel_driver(0)

        # Set up USB device

        # set the active configuration. With no arguments, the first
        # configuration will be the active one
        # This seems to break comms with the scope
        #self.dev.set_configuration()

        # get an endpoint instance
        self.cfg = self.dev.get_active_configuration()
        intf = self.cfg[(0,0)]

        self.ep_out = usb.util.find_descriptor(
            intf,
            # match the first OUT endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_OUT)

        assert self.ep_out is not None
        if self.debug:
            print (self.ep_out)

        self.ep_in = usb.util.find_descriptor(
            intf,
            # match the first IN endpoint
            custom_match = \
            lambda e: \
                usb.util.endpoint_direction(e.bEndpointAddress) == \
                usb.util.ENDPOINT_IN)

        assert self.ep_in is not None
        if self.debug:
            print(self.ep_in)
        self._run_threads = True
        #initialize read & write queues
        self.__rx_queue = queue.Queue()
        self.__tx_queue = queue.Queue()
        #start read and write threads
        self.__read_thread = threading.Thread(target=self.__usb_read_thread)
        self.__write_thread = threading.Thread(target=self.__usb_write_thread)
        self.__read_handler_thread = threading.Thread(target=self.__usb_read_handler)
        self.__read_thread.start()
        self.__write_thread.start()
        self.__read_handler_thread.start()
        
    def __parse_response(self, resp):
        marker = resp[0]
        length = resp[1]
        length += resp[2] * 256
        command = resp[3]
        length -= 1
        if self.debug:
            print ("Mrk: {:x}, cmd: {:x}, len: {:x}".format(marker, command, length))
        #todo: validate checksum
        if marker == 0x53:
            if command == 0x80:
                if self.debug:
                    print("Received echo")
            elif command == 0xa0:
                subcommand = resp[4]
                if subcommand == 0x01:
                    if self.debug:
                        print("Received Screenshot data")
                    self.image_buffer += resp[5:-1]
                elif subcommand == 0x02:
                    #todo: parse image checksum
                    if self.debug:
                        print("Received end of screenshot")
                    image_bytes = bytes(self.image_buffer)
                    img = Image.frombuffer("RGB", (800, 480), image_bytes, 'raw', "BGR;16", 0, 1)
                    img.show()
                    self.image_buffer = []
            
        
    
    def __usb_read_handler(self):
        if self.debug:
            print("Starting Read Handler Thread")
        while self._run_threads:
            try:
                response = self.__rx_queue.get(timeout=1)
                self.__parse_response(response)
            except queue.Empty:
                pass
        if self.debug:
            print("Exiting Read Handler Thread")

    def __usb_read_thread(self):
        if self.debug:
            print("Starting Read Thread")
        while self._run_threads:
            try:
                reply = self.ep_in.read(1000000, timeout=1000)
                if self.debug:
                    #print("Reply: {}".format(self.print_hex(reply)))
                    print("Reply Length: {}".format(len(reply)))
                self.__rx_queue.put(reply)
            except usb.core.USBError as e:
                if e.errno != 110: # 110 is a timeout.
                    sys.exit("Error reading data: %s" % str(e))
                else:
                    if self.debug:
                        print("USB Read Timeout")
                        pass
        if self.debug:
            print("Exiting Read Thread")

    def __usb_write_thread(self):
        if self.debug:
            print("Starting Write Thread")
        while self._run_threads:
            try:
                cmd = self.__tx_queue.get(timeout=1)
                self.ep_out.write(cmd)
                if self.debug:
                    print("USB Wrote command from queue")
                #must wait ~100ms between commands otherwise the scope will lose them
                sleep(0.1)
            except queue.Empty:
                pass
        if self.debug:
            print("Exiting Write Thread")
        
    def close(self):
        self._run_threads = False
        pass
        
    def print_hex(self, ls):
        return '[{}]'.format(', '.join(hex(x) for x in ls))
        
        
    def __scope_write(self, cmd):
        self.__tx_queue.put(self.build_cmd(cmd))
        self.__tx_queue.put(self.build_cmd(self.echo_cmd))
        if self.debug:
            #print("__write: {}".format(self.print_hex(cmd)))
            pass
            
    def build_cmd(self, cmd):
        checksum = sum(cmd) & 0xff
        cmd = cmd + [checksum]
        return cmd
                 
    def send_cmd(self, cmd):
        """Sends the scope the specified command string (adding the checksum)
        and returns the response.
        """
        self.__scope_write(cmd)
        
    def echo(self):
        """sends an "echo" command.  Can be used as padding to flush out the 
        scope's command buffer
        """
        if self.debug:
            print("PyOszi Echo")
        self.send_cmd(self.echo_cmd)
        
    def run(self):
        """Puts the scope into run mode.
        Buggy."""
        if self.debug:
            print("PyOszi Run")
        self.send_cmd(self.run_cmd)
        
    def stop(self):
        """Puts the scope into stop mode.
        Buggy."""
        if self.debug:
            print("PyOszi Stop")
        self.send_cmd(self.stop_cmd)
        
    def lock(self):
        """Locks the front panel of the scope"""
        if self.debug:
            print("PyOszi Lock")
        self.send_cmd(self.lock_cmd)
        
    def unlock(self):
        """Puts the scope into stop mode."""
        if self.debug:
            print("PyOszi Unlock")
        self.send_cmd(self.unlock_cmd)
        
    def beep(self, duration):
        """Causes the scope to beep
        duration of the beep should be specified in seconds"""
        duration *= 10 #duration is specified to the scope in increments of 100ms
        if duration <= 0:
            duration = 1
        elif duration > 255:
            duration = 255
        if self.debug:
            print("PyOszi Beep ({} ms)".format(duration * 100))
        duration = [int(duration)]
        cmd = self.beep_cmd + duration
        self.send_cmd(cmd)

    def press_button(self, button):
        """Presses the specified button on the scope"""
        if self.debug:
            print("PyOszi Button ({})".format(button))
        cmd = self.btn_cmd + button
        self.send_cmd(cmd)
        
    def request_screenshot(self):
        """Requests the scope to send an image of its screen."""
        if self.debug:
            print("PyOszi request screenshot")
        self.send_cmd(self.screenshot_cmd)
        
            
if __name__ == "__main__":
    b = PyOsziButtons
    scope = PyOszi(debug=True)
    scope.press_button(b.BTN_F0)
    sleep(2)
    scope.beep(1)
    sleep(2)
    scope.press_button(b.BTN_SINGLE_SEQ)
    scope.request_screenshot()
    sleep(10)
    scope.close()
