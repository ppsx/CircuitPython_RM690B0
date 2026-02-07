# SPDX-FileCopyrightText: Copyright (c) 2026 Przemyslaw Patrick Socha
#
# SPDX-License-Identifier: Unlicense

"""
Basic Shapes Demo - DisplayIO Version
======================================

Demonstrates rectangle, circle, line, and text drawing using standard
displayio and community libraries.

Dependencies:
    - adafruit_display_shapes (Community Bundle)
    - adafruit_display_text (Community Bundle)
"""

import time
import board
import displayio

# Graphics libraries
from adafruit_display_shapes.circle import Circle
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.rect import Rect

# Text library
from adafruit_display_text import label
import terminalio
from rm690b0 import RM690B0, create_qspi_bus

print("Initializing RM690B0 display...")

# Release any existing displays
displayio.release_displays()

# Create QSPI bus
bus = create_qspi_bus(board, frequency=40_000_000)

# Create RM690B0 display
display = RM690B0(bus, width=600, height=450)

# Create main group
splash = displayio.Group()

print("Drawing basic shapes...")

# Start timing
t_start = time.monotonic()

# Background (black)
bg_bitmap = displayio.Bitmap(600, 450, 1)
bg_palette = displayio.Palette(1)
bg_palette[0] = 0x000000  # Black
bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
splash.append(bg_sprite)

# Rectangles (filled)
rect1 = Rect(20, 20, 160, 80, fill=0xFF0000)  # Red
splash.append(rect1)

rect2 = Rect(220, 20, 160, 80, fill=0x00FF00)  # Green
splash.append(rect2)

rect3 = Rect(420, 20, 160, 80, fill=0x0000FF)  # Blue
splash.append(rect3)

# Circles
# Filled yellow circle
circle1 = Circle(140, 240, 70, fill=0xFFFF00)
splash.append(circle1)

# Outline cyan circle
circle2 = Circle(340, 240, 70, outline=0x00FFFF, stroke=2)
splash.append(circle2)

# Lines (diagonal cross)
line1 = Line(0, 0, 599, 449, color=0xFFFFFF)
splash.append(line1)

line2 = Line(0, 449, 599, 0, color=0xFFFFFF)
splash.append(line2)

# Text labels
text1 = label.Label(
    terminalio.FONT,
    text="RM690B0 DISPLAYIO",
    color=0xFFFFFF,
    x=410,
    y=220
)
splash.append(text1)

text2 = label.Label(
    terminalio.FONT,
    text="BASIC SHAPES",
    color=0xFFA500,  # Orange
    x=410,
    y=236
)
splash.append(text2)

# Show on display
display.root_group = splash
display.refresh()  # IMPORTANT: Must refresh to display!

# Calculate render time
t_elapsed = (time.monotonic() - t_start) * 1000.0

print("[OK] Shapes rendered successfully!")
print("")
print(f"Render + display time: {t_elapsed:.2f} ms")
print("")
print("Press Ctrl+C to exit")

try:
    while True:
        pass
except KeyboardInterrupt:
    print("\n[INFO] Stopping...")
finally:
    displayio.release_displays()
    if bus:
        bus.deinit()
    print("[OK] Cleanup complete")
