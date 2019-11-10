# PyOszi

PyOszi is a Python library for interacting with certain models of Hantek, Tekway, Voltcraft, and Protek Oscilloscopes.  These oscilloscopes are collectively referred to as "Das Oszi" in much of the reverse engineering documentation available on the web.
## Requirements
* Pillow
* PyUSB

(you should be able to install both using pip)
Tested on Python 3.6.8 under Linux Mint 19.2.  With the correct libraries installed, it should run on Windows and OS X.    It may or may not work correctly under earlier versions of Python.
So far I have only tested this library using my Hantek DSO5072P scope, but in theory it should work with any scope in the DSO5xxx family, as well as other scopes listed here: https://elinux.org/Das_Oszi#Models

## Current Features
* Press buttons on scope front panel
* Take screenshots from scope
* Beep using the scope's internal speaker

## To do
* Add checksum verification
* Implement file read/write
* Implement DSO Settings read/write

## Contributing
I am a bit limited in what I can test with only a single model of scope available to me.  Pull requests with bug features and new features are welcome!

## Acknowledgements
This library would not have been possible without the excellent documentation available here:
https://elinux.org/Das_Oszi
https://elinux.org/Das_Oszi_Protocol
