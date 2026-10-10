
import board
import busio
import digitalio
import displayio
import terminalio
import time

from i2cdisplaybus import I2CDisplayBus
from adafruit_displayio_sh1106 import SH1106
from adafruit_display_text import label


# ============================================================
# SETTINGS
# ============================================================

WIDTH = 128
HEIGHT = 64

FRAME_SIZE = 1024
FPS = 100

FRAME_FILE = "/frames.bin"


# ============================================================
# OLED SETUP
# ============================================================

print("Starting...")

displayio.release_displays()

i2c = busio.I2C(
    board.GP15,       # SCL
    board.GP14        # SDA
)

display_bus = I2CDisplayBus(
    i2c,
    device_address=0x3C
)

display = SH1106(
    display_bus,
    width=128,
    height=64
)

print("OLED initialized!")


# ============================================================
# BUTTON SETUP
# ============================================================

# GP18: Start button
button = digitalio.DigitalInOut(board.GP18)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# GP13: Skip animation button
skip_button = digitalio.DigitalInOut(board.GP13)
skip_button.direction = digitalio.Direction.INPUT
skip_button.pull = digitalio.Pull.UP

print("Start button on GP18 initialized!")
print("Skip button on GP13 initialized!")


# ============================================================
# HELPER: SHOW CENTERED TEXT
# ============================================================

def show_text(text, y=32):

    group = displayio.Group()

    text_label = label.Label(
        terminalio.FONT,
        text=text,
        color=0xFFFFFF
    )

    text_label.anchor_point = (0.5, 0.5)
    text_label.anchored_position = (64, y)

    group.append(text_label)
    display.root_group = group


# ============================================================
# HELPER: CHECK SKIP BUTTON
# ============================================================

def skip_pressed():

    if not skip_button.value:
        time.sleep(0.03)  # Debounce

        if not skip_button.value:
            print("SKIP BUTTON PRESSED!")
            return True

    return False


# ============================================================
# START SCREEN
# ============================================================

print("Showing start screen...")

group = displayio.Group()

title = label.Label(
    terminalio.FONT,
    text="TOP 10 TARUSH QUOTES",
    color=0xFFFFFF
)

title.anchor_point = (0.5, 0.5)
title.anchored_position = (64, 20)

subtitle = label.Label(
    terminalio.FONT,
    text="OF ALL TIME",
    color=0xFFFFFF
)

subtitle.anchor_point = (0.5, 0.5)
subtitle.anchored_position = (64, 40)

group.append(title)
group.append(subtitle)

display.root_group = group


# ============================================================
# WAIT FOR START BUTTON
# ============================================================

print("Waiting for GP18 start button...")

while button.value:
    time.sleep(0.01)

time.sleep(0.15)

while not button.value:
    time.sleep(0.01)

print("BUTTON PRESSED!")


# ============================================================
# QUOTE #1
# ============================================================

print("Showing quote #1...")

show_text("Jk you suck")

time.sleep(1.2)


# ============================================================
# CREATE ANIMATION BITMAP
# ============================================================

print("Preparing animation...")

bitmap = displayio.Bitmap(
    WIDTH,
    HEIGHT,
    2
)

palette = displayio.Palette(2)
palette[0] = 0x000000
palette[1] = 0xFFFFFF

tile_grid = displayio.TileGrid(
    bitmap,
    pixel_shader=palette
)

video_group = displayio.Group()
video_group.append(tile_grid)

display.root_group = video_group


# ============================================================
# OPEN FRAME FILE
# ============================================================

print("Opening frames.bin...")

try:
    frame_file = open(FRAME_FILE, "rb")

except Exception as error:
    print("ERROR OPENING frames.bin:")
    print(error)

    show_text("NO VIDEO FILE")

    while True:
        time.sleep(1)


# ============================================================
# PLAY ANIMATION WITH GP13 SKIP SUPPORT
# ============================================================

print("PLAYING ANIMATION!")

frame_number = 0
frame_delay = 1 / FPS

while True:

    # Check skip button before reading a new frame
    if skip_pressed():
        print("Skipping animation...")
        break

    start_time = time.monotonic()

    frame_data = frame_file.read(FRAME_SIZE)

    # End of animation file
    if len(frame_data) < FRAME_SIZE:
        break

    # Draw the frame
    byte_index = 0

    for y in range(HEIGHT):

        # Check GP13 periodically while drawing.
        # This makes skipping more responsive.
        if y % 8 == 0 and not skip_button.value:
            print("Skip requested during frame drawing!")
            break

        for x_byte in range(16):

            byte = frame_data[byte_index]
            byte_index += 1

            x = x_byte * 8

            bitmap[x, y]     = (byte >> 7) & 1
            bitmap[x + 1, y] = (byte >> 6) & 1
            bitmap[x + 2, y] = (byte >> 5) & 1
            bitmap[x + 3, y] = (byte >> 4) & 1
            bitmap[x + 4, y] = (byte >> 3) & 1
            bitmap[x + 5, y] = (byte >> 2) & 1
            bitmap[x + 6, y] = (byte >> 1) & 1
            bitmap[x + 7, y] = byte & 1

        # If pressed during drawing, stop the animation.
        if y % 8 == 0 and not skip_button.value:
            break

    # If the skip button was pressed, exit the animation loop.
    if not skip_button.value:
        time.sleep(0.05)
        break

    frame_number += 1

    # Maintain approximate target FPS
    elapsed = time.monotonic() - start_time
    remaining = frame_delay - elapsed

    if remaining > 0:
        time.sleep(remaining)


# Always close the file, even if the animation was skipped.
frame_file.close()

print("Animation ended.")
print("Frames played:", frame_number)


# ============================================================
# HAPPY BIRTHDAY SCREEN
# ============================================================

time.sleep(0.2)

group = displayio.Group()

line1 = label.Label(
    terminalio.FONT,
    text="HAPPY",
    color=0xFFFFFF
)

line1.anchor_point = (0.5, 0.5)
line1.anchored_position = (64, 18)

line2 = label.Label(
    terminalio.FONT,
    text="BIRTHDAY",
    color=0xFFFFFF
)

line2.anchor_point = (0.5, 0.5)
line2.anchored_position = (64, 34)

line3 = label.Label(
    terminalio.FONT,
    text="TARUSH!!!",
    color=0xFFFFFF
)

line3.anchor_point = (0.5, 0.5)
line3.anchored_position = (64, 52)

group.append(line1)
group.append(line2)
group.append(line3)

display.root_group = group

print("HAPPY BIRTHDAY TARUSH!!!")


# ============================================================
# DONE
# ============================================================

while True:
    time.sleep(1)