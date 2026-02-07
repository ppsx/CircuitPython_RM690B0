# SPDX-FileCopyrightText: Copyright (c) 2026 Przemyslaw Patrick Socha
#
# SPDX-License-Identifier: MIT

"""
`rm690b0`
====================================================

CircuitPython displayio driver for RM690B0 AMOLED displays

* Author(s): Przemyslaw Patrick Socha

Implementation Notes
--------------------

**Hardware:**

* `Waveshare ESP32-S3-Touch-AMOLED-2.41 <https://www.waveshare.com/esp32-s3-touch-amoled-2.41.htm>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

from busdisplay import BusDisplay

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/ppsx/CircuitPython_RM690B0.git"

# RM690B0 initialization sequence
# This sequence is based on vendor recommendations and has been tested
# to work reliably with RM690B0 AMOLED panels.
_INIT_SEQUENCE = (
    # Page select and configuration
    b"\xFE\x01\x20"  # Enter user command mode
    b"\x26\x01\x0A"  # Bias setting
    b"\x24\x01\x80"  # Source output control
    b"\xFE\x01\x13"  # Page 13
    b"\xEB\x01\x0E"  # Unknown vendor command
    b"\xFE\x01\x00"  # Return to page 0
    # Display configuration
    b"\x3A\x01\x55"  # COLMOD: 16-bit RGB565
    b"\xC2\x81\x00\x0A"  # Unknown vendor command with delay
    b"\x35\x00"  # Tearing effect line on
    b"\x51\x81\x00\x0A"  # Brightness control with delay
    # Power on sequence
    b"\x11\x80\x50"  # Sleep out, wait 80ms
    # Set display window (600x450 with 16-pixel Y offset)
    b"\x2A\x04\x00\x10\x01\xD1"  # CASET: column 16 to 465
    b"\x2B\x04\x00\x00\x02\x57"  # RASET: row 0 to 599
    # Enable display
    b"\x29\x80\x0A"  # Display on, wait 10ms
    # Memory access control (rotation)
    b"\x36\x81\x30\x0A"  # MADCTL: default orientation
    # Brightness
    b"\x51\x01\xFF"  # Set brightness to maximum
)


class RM690B0(BusDisplay):  # pylint: disable=too-few-public-methods
    """
    RM690B0 AMOLED display driver.

    This class provides a displayio-compatible interface to RM690B0 panels.
    It inherits from BusDisplay and handles all initialization and
    communication with the display controller.

    :param bus: The QSPI bus interface (qspibus.QSPIBus)
    :param int width: Display width in pixels (default: 600)
    :param int height: Display height in pixels (default: 450)
    :param int colstart: Column start offset (default: 0)
    :param int rowstart: Row start offset (default: 16)
    :param int rotation: Display rotation in degrees (0, 90, 180, 270)
    :param bool auto_refresh: Enable automatic refresh (default: False)

    Example:

        bus = qspibus.QSPIBus(...)
        display = RM690B0(bus, width=600, height=450)
        display.root_group = my_group
        display.refresh()
    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        bus,
        *,
        width=600,
        height=450,
        colstart=0,
        rowstart=16,
        rotation=0,
        auto_refresh=False,
    ):
        """Initialize RM690B0 display driver."""
        super().__init__(
            bus,
            _INIT_SEQUENCE,
            width=width,
            height=height,
            colstart=colstart,
            rowstart=rowstart,
            rotation=rotation,
            color_depth=16,
            auto_refresh=auto_refresh,
        )


# Convenience function for pin resolution
def _first_pin(board_module, *pin_names):
    """
    Find first available pin from a list of names.

    :param board_module: The board module (typically `board`)
    :param pin_names: Pin name candidates (e.g., "LCD_CLK", "QSPI_CLK")
    :return: Pin object
    :raises AttributeError: If no pin found
    """
    for name in pin_names:
        if hasattr(board_module, name):
            return getattr(board_module, name)
    raise AttributeError(f"Missing board pin: {', '.join(pin_names)}")


def create_qspi_bus(board_module, frequency=40_000_000):
    """
    Helper function to create QSPI bus with automatic pin detection.

    This function tries common pin naming conventions and creates a QSPIBus
    instance with the first available pins.

    :param board_module: The board module (typically `board`)
    :param int frequency: QSPI bus frequency in Hz (default: 40MHz)
    :return: QSPIBus instance
    :raises AttributeError: If required pins are not found

    Example:

        import board
        from rm690b0 import create_qspi_bus, RM690B0

        bus = create_qspi_bus(board)
        display = RM690B0(bus)
    """
    import qspibus  # pylint: disable=import-outside-toplevel

    clock = _first_pin(board_module, "LCD_CLK", "QSPI_CLK", "DISPLAY_SCK")
    data0 = _first_pin(board_module, "LCD_D0", "QSPI_D0", "DISPLAY_D0")
    data1 = _first_pin(board_module, "LCD_D1", "QSPI_D1", "DISPLAY_D1")
    data2 = _first_pin(board_module, "LCD_D2", "QSPI_D2", "DISPLAY_D2")
    data3 = _first_pin(board_module, "LCD_D3", "QSPI_D3", "DISPLAY_D3")
    chip_select = _first_pin(board_module, "LCD_CS", "QSPI_CS", "DISPLAY_CS")

    # Optional pins
    reset = None
    for name in ("LCD_RESET", "AMOLED_RESET", "DISPLAY_RST"):
        if hasattr(board_module, name):
            reset = getattr(board_module, name)
            break

    return qspibus.QSPIBus(
        clock=clock,
        data0=data0,
        data1=data1,
        data2=data2,
        data3=data3,
        cs=chip_select,
        reset=reset,
        frequency=frequency,
    )
