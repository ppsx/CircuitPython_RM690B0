# SPDX-FileCopyrightText: Copyright (c) 2026 Przemyslaw Patrick Socha
#
# SPDX-License-Identifier: Unlicense

"""
Text Demo - DisplayIO Version
==============================

Demonstrates text rendering using adafruit_display_text library.
"""

import time
import board
import displayio
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

# Background (black)
bg_bitmap = displayio.Bitmap(600, 450, 1)
bg_palette = displayio.Palette(1)
bg_palette[0] = 0x000000
bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
splash.append(bg_sprite)

print("Rendering text...")

# Start timing
t_start = time.monotonic()

# Title
text1 = label.Label(
    terminalio.FONT, text="RM690B0 DISPLAYIO TEXT", color=0xFFFFFF, x=40, y=40
)
splash.append(text1)

# Numbers
text2 = label.Label(
    terminalio.FONT, text="0123456789", color=0xFFFF00, x=40, y=72  # Yellow
)
splash.append(text2)

# Status message
text3 = label.Label(
    terminalio.FONT, text="DISPLAY READY", color=0x00FFFF, x=40, y=104  # Cyan
)
splash.append(text3)

# Multiline text
# Note: Label supports \n for line breaks
text4 = label.Label(
    terminalio.FONT, text="LINE 1\nLINE 2\nLINE 3", color=0x00FF00, x=40, y=150  # Green
)
splash.append(text4)

# Multiple colors demo
colors = [
    0xFF0000,  # Red
    0xFF7F00,  # Orange
    0xFFFF00,  # Yellow
    0x00FF00,  # Green
    0x0000FF,  # Blue
    0x4B0082,  # Indigo
]

for i in range(6):
    text = label.Label(
        terminalio.FONT, text=f"COUNT {i}", color=colors[i], x=360, y=40 + i * 18
    )
    splash.append(text)

# Show on display
display.root_group = splash
display.refresh()  # IMPORTANT: Must refresh to display!

# Calculate render time
t_elapsed = (time.monotonic() - t_start) * 1000.0

print("[OK] Text rendered successfully!")
print("")
print(f"Render + display time: {t_elapsed:.2f} ms")
print("")
print("Note: terminalio.FONT is built-in (no external files needed)")
print("      For custom fonts, use adafruit_bitmap_font library")
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
