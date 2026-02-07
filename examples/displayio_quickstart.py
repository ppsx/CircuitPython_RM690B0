# SPDX-FileCopyrightText: Copyright (c) 2026 Przemyslaw Patrick Socha
#
# SPDX-License-Identifier: Unlicense

"""
DisplayIO Quickstart for RM690B0
=================================

Minimal example showing how to use RM690B0 with standard displayio.

This example fills the screen with a solid color to verify the display works.
"""

import time
import board
import displayio
from rm690b0 import RM690B0, create_qspi_bus

# Release any existing displays
displayio.release_displays()

# Start timing
t_start = time.monotonic()

# Create QSPI bus (automatic pin detection)
bus = create_qspi_bus(board, frequency=40_000_000)

# Create RM690B0 display
display = RM690B0(bus, width=600, height=450)

# Create a red screen
splash = displayio.Group()

# Create bitmap (600x450 pixels, 1 color)
bitmap = displayio.Bitmap(600, 450, 1)
palette = displayio.Palette(1)
palette[0] = 0xFF0000  # Red

# Create sprite and add to group
sprite = displayio.TileGrid(bitmap, pixel_shader=palette)
splash.append(sprite)

# Show on display
display.root_group = splash
display.refresh()  # IMPORTANT: Must refresh to display!

# Calculate total time
t_elapsed = (time.monotonic() - t_start) * 1000.0

print("[OK] Display initialized - screen should be RED")
print(f"[OK] Total time (init + render + display): {t_elapsed:.2f} ms")
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
