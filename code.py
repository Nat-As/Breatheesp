import time, gc, os
import adafruit_dotstar
import board
import feathers2
import adafruit_scd4x
import busio
from adafruit_pm25.i2c import PM25_I2C


try:
    import ipaddress
    import ssl
    import wifi
    import socketpool
    import adafruit_requests
except ImportError:
    print("Unable to locate WiFi Modules")
    raise

# Configuration
sensorId = "001"
configsRoute = "http://192.168.8.4:3000/api/config"
readingsRoute = "http://192.168.8.4:3000/api/reading"




# Housekeeping items
############################################################
# Make sure the 2nd LDO is turned on
feathers2.enable_LDO2(True)
dotstar = adafruit_dotstar.DotStar(
    board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.5, auto_write=True
)
dotstar[0] = (255, 0, 127, 0.1) # Purple - Boot up
# Turn on the internal blue LED
feathers2.led_set(True)
# For Sensors
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
scd = adafruit_scd4x.SCD4X(i2c)
scd.start_periodic_measurement()
reset_pin = None
pm25 = PM25_I2C(i2c, reset_pin)

# Import Secret Wifi info from secrets.py
try:
    from secrets import secrets
except ImportError:
    print("Secrets file not found!")
    raise
# Error codes
def CONERR(e):
    while True:
        print(e) # Log Error to console
        dotstar[0] = (255,0,0, 0.5) # RED
        time.sleep(0.9)
        # Retry Problematic function

def OFLERR(e):
    while True:
        print(e) # Log Error to console
        dotstar[0] = (255,140,0, 0.5) # ORANGE
        time.sleep(0.9)
        # Retry Problematic function
############################################################

# Function Definitions

def GetMemSize():
    # Show available memory
    print("Memory Info - gc.mem_free()")
    print("---------------------------")
    print("{} Bytes\n".format(gc.mem_free()))

    flash = os.statvfs("/")
    flash_size = flash[0] * flash[2]
    flash_free = flash[0] * flash[3]
    # Show flash size
    print("Flash - os.statvfs('/')")
    print("---------------------------")
    print("Size: {} Bytes\nFree: {} Bytes\n".format(flash_size, flash_free))


# Main Code


#Find WiFi
def WiFiEnum(wifi):
    print("Searching for WiFi Networks")
    for network in wifi.radio.start_scanning_networks():
        print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
                network.rssi, network.channel))
    wifi.radio.stop_scanning_networks()
WiFiEnum(wifi)

# Connect to WiFi
def WiFiCon(wifi):
    try:
        wifi.radio.connect(secrets["ssid"], secrets["password"])
        print("Connected to %s!"%secrets["ssid"])
        print("My IP address is", wifi.radio.ipv4_address)
    except Exception as e:
        CONERR(e)
WiFiCon(wifi)

# Send Data
def OffLoad(wifi,temp,humid,PM):
    try:
        # Set up network sockets
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())

        ### Send JSON Data ###
        header = {
            'User-Agent': 'Mesh Sensor',
            'Content-Type': 'application/json'}

        payload = { 
                'sensor_ID': str(sensorId), #make sure that it's all strings. 
                'temperature': str(temp),
                'humidity': str(humid),
                'PM_03': str(PM)}
        response = requests.post(readingsRoute, headers=header, json=payload) #sends a post request
        print('request sent')
    except Exception as e:
        OFLERR(e)

# Gather AQ Data
def DataGen(wifi):
    aqdata = pm25.read()
    if scd.data_ready:
        temp = (scd.temperature * 9/5) + 32
        humid  = scd.relative_humidity
        PM3UM = aqdata["particles 03um"] #0.3 micron particles
        PM5UM = aqdata["particles 05um"] #0.5 micron particles
        PM50M = aqdata["particles 50um"] # 5 micron particles
        # Upload Data to server
        OffLoad(wifi,temp,humid,PM3UM)
DataGen(wifi)

# Main Loop
while True:
    dotstar[0] = (0, 255, 0, 0.1) # Green
    feathers2.led_blink()#Blink Blue LED
    # Sleep for 1s reduces console traffic
    time.sleep(1.3)

#circuitpython for vs code: F1 menu -> select board -> select serial port -> open serial monitor. 
#A question is:
#1) How do we allow the webserver to send configuration HTTP requests and have the sensor receive it? 
# We may do this if we can set an ID that is or makes itself consistent with a specific sensor and their IP
