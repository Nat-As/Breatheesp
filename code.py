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

# Housekeeping items
############################################################
# Make sure the 2nd LDO is turned on
feathers2.enable_LDO2(True)

# Create a DotStar instance
dotstar = adafruit_dotstar.DotStar(
    board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.5, auto_write=True
)

# Turn on the internal blue LED
feathers2.led_set(True)
# Create a colour wheel index int
color_index = 0

# Import Secret Wifi info from secrets.py
try:
    from secrets import secrets
except ImportError:
    print("Secrets file not found!")
    raise

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
print("Searching for WiFi Networks")
for network in wifi.radio.start_scanning_networks():
    print("\t%s\t\tRSSI: %d\tChannel: %d" % (str(network.ssid, "utf-8"),
            network.rssi, network.channel))
wifi.radio.stop_scanning_networks()
# Connect to WiFi
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!"%secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

try:
    # Set up network sockets
    pool = socketpool.SocketPool(wifi.radio)
    requests = adafruit_requests.Session(pool, ssl.create_default_context())

    ### Send JSON Data ###
    header = {
        'User-Agent': 'Mesh Sensor',
        'Content-Type': 'application/json;charset=UTF-8'}

    payload = {
            'DeviceID': 'Sensor001',
            'Timestamp': time.time(),
            'Temp': '72',
            'Humid': '36'}

    r = requests.post("http://192.168.10.116:6060", headers=header, data=payload)
    print(r.text)
except Exception as e:
    print("Failed to send data")
    print(e)

# Main Loop
while True:
    # Get the R,G,B values of the next colour
    r, g, b = feathers2.dotstar_color_wheel(color_index)
    # Set the colour on the dotstar
    dotstar[0] = (r, g, b, 0.5)
    # Increase the wheel index
    color_index += 1

    # If the index == 255, loop it
    if color_index == 255:
        color_index = 0
        # Invert the internal LED state every half colour cycle
        feathers2.led_blink()

    # Sleep for 1s reduces console traffic
    time.sleep(0.1)
