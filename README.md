# Breatheesp
This is the uploaded Circuit Python Firmware for an IOT air quality sensor with the UM Feather S2 development board. Currently this project is using Circuit Python V6.3.0 with the ESP32-S2 as a proof-of-concept (POC). This code can eventually be ported to Circuit Python 7.X.X, but plans are currently being made to port this to a C code instead.
<BR>
  <BR>
    
This Project is designed to create an air-quality sensor using the Feather S2 platform as a prototype. A later version will be created in C with custom hardware and software. This code currently connects to the wifi in the secrets file (change it to yours before using) and gets an IP address from the router. All setup is done in order to use the requests module and immedietly begin making API requests.
  
# Libraries
Cool Adafruit Libraries [here](https://github.com/adafruit/Adafruit_CircuitPython_Bundle/releases/tag/20211003)
# Examples
Some great [examples](https://learn.adafruit.com/adafruit-metro-esp32-s2/circuitpython-internet-test)
