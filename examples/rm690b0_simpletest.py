# SPDX-FileCopyrightText: Copyright (c) 2026 Przemyslaw Patrick Socha
#
# SPDX-License-Identifier: Unlicense

"""Simple test for RM690B0 AMOLED display - fills the screen with red."""

import board
import displayio
from rm690b0 import RM690B0, create_qspi_bus

# Release any existing displays
displayio.release_displays()

# Create QSPI bus (automatic pin detection)
bus = create_qspi_bus(board, frequency=40_000_000)

# Create RM690B0 display
display = RM690B0(bus, width=600, height=450)

# Create a red screen
splash = displayio.Group()

bitmap = displayio.Bitmap(600, 450, 1)
palette = displayio.Palette(1)
palette[0] = 0xFF0000  # Red

sprite = displayio.TileGrid(bitmap, pixel_shader=palette)
splash.append(sprite)

# Show on display
display.root_group = splash
display.refresh()

while True:
    pass
