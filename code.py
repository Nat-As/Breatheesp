import time, gc, os
import adafruit_dotstar
import board
import feathers2


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
configsRoute = "http://localhost:3000/api/config"
readingsRoute = "http://localhost:3000/api/reading"




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
def OffLoad(wifi,temp,humid):
    try:
        # Set up network sockets
        pool = socketpool.SocketPool(wifi.radio)
        requests = adafruit_requests.Session(pool, ssl.create_default_context())

        ### Send JSON Data ###
        header = {
            'User-Agent': 'Mesh Sensor',
            'Content-Type': 'application/json;charset=UTF-8'}

        payload = { 
                'sensor_ID': sensorId,
                'timestamp': time.time(), 
                'temperature': temp,
                'humidity': humid}
        r = requests.post(readingsRoute, headers=header, data=payload)
        print(header,payload)
    except Exception as e:
        OFLERR(e)

# Generate Fake Data
def DataGen(wifi):
    temp = time.time()%22 + 60
    humid  = time.time()%30 + 50
    # Upload Fake Data to server
    OffLoad(wifi,temp,humid)
DataGen(wifi)

# Main Loop
while True:
    dotstar[0] = (0, 255, 0, 0.1) # Green
    feathers2.led_blink()#Blink Blue LED
    # Sleep for 1s reduces console traffic
    time.sleep(1.3)


#Main questions are:
#1) How to allow the webserver to send configurations and have sensor receive it
#2) How to set an ID that is consistent with a specific sensor and their IP
#3) How to deal with the problem of an IP changing with the sensor (PUT requests)