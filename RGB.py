# Default Firmware
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

# Make sure the 2nd LDO is turned on
# feathers2.enable_LDO2(True)

# Create a DotStar instance
dotstar = adafruit_dotstar.DotStar(
    board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.5, auto_write=True
)

# Turn on the internal blue LED
feathers2.led_set(True)
color_index = 0

# Import Secret Wifi info from secrets.py
try:
    from secrets import secrets
except ImportError:
    print("Secrets file not found!")
    raise


# Main Loop
while True:
    # Get the R,G,B values of the next colour
    r, g, b = feathers2.dotstar_color_wheel(color_index)
    # Set the colour on the dotstar
    dotstar[0] = (r, g, b, 0.1)
    # Increase the wheel index
    color_index += 1

    # If the index == 255, loop it
    if color_index == 255:
        color_index = 0
    # Blink Blue LED
    feathers2.led_blink()

    # Sleep for 1s reduces console traffic
    time.sleep(0.1)
