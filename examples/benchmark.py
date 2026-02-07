# SPDX-FileCopyrightText: Copyright (c) 2026 Przemyslaw Patrick Socha
#
# SPDX-License-Identifier: Unlicense

"""
DisplayIO Performance Benchmark
================================

Benchmarks displayio.Bitmap operations on RM690B0 display.

Measurements:
    1. Full-screen fill + refresh
    2. Partial region update (100x100)
    3. Many small rectangles (100x 40x40)

Dependencies:
    - bitmaptools (built-in firmware module)
"""

import time
import gc
import board
import displayio
import bitmaptools
from rm690b0 import RM690B0, create_qspi_bus


def average(values):
    """Calculate average of list."""
    return sum(values) / len(values) if values else 0.0


def main():  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    print("=" * 70)
    print("DISPLAYIO PERFORMANCE BENCHMARK - RM690B0")
    print("=" * 70)
    print()

    bus = None
    try:
        # Initialize display
        print("Initializing display...")
        displayio.release_displays()
        bus = create_qspi_bus(board, frequency=40_000_000)
        display = RM690B0(bus, width=600, height=450)

        # Create bitmap
        print("Creating 600x450 displayio.Bitmap (65536 colors)...")
        gc.collect()
        mem_before = gc.mem_free()  # pylint: disable=no-member

        bitmap = displayio.Bitmap(600, 450, 65536)
        converter = displayio.ColorConverter(input_colorspace=displayio.Colorspace.RGB565)
        tilegrid = displayio.TileGrid(bitmap, pixel_shader=converter)
        group = displayio.Group()
        group.append(tilegrid)
        display.root_group = group

        gc.collect()
        mem_after = gc.mem_free()  # pylint: disable=no-member
        mem_used = mem_before - mem_after

        print(f"  Memory used: {mem_used} bytes ({mem_used/1024:.1f} KB)")
        print(f"  Free memory: {mem_after} bytes ({mem_after/1024:.1f} KB)")
        print()

        # Test 1: Full-screen fill + refresh
        print("-" * 70)
        print("TEST 1: Full-screen fill + refresh")
        print("-" * 70)

        colors = [0xF800, 0x07E0, 0x001F]  # Red, Green, Blue
        full_times = []

        for i in range(6):
            color = colors[i % len(colors)]
            t0 = time.monotonic()
            bitmap.fill(color)
            display.refresh()
            elapsed = (time.monotonic() - t0) * 1000.0
            full_times.append(elapsed)
            print(f"  Run {i+1}: {elapsed:.2f} ms")

        full_avg = average(full_times)
        print(f"\nAverage: {full_avg:.2f} ms")

        if full_avg < 100:
            print("  [OK] EXCELLENT - Very fast C implementation!")
        elif full_avg < 500:
            print("  [OK] Good - Acceptable performance")
        else:
            print("  [WARN] Slower than expected")

        # Test 2: Partial region update
        print()
        print("-" * 70)
        print("TEST 2: Partial region update (100x100)")
        print("-" * 70)

        bitmap.fill(0x0000)
        display.refresh()

        partial_times = []
        for i in range(12):
            x = (i * 43) % 500
            y = (i * 29) % 350
            color = (i * 997) & 0xFFFF

            t0 = time.monotonic()
            bitmaptools.fill_region(bitmap, x, y, x + 100, y + 100, color)
            bitmap.dirty(x1=x, y1=y, x2=x + 100, y2=y + 100)
            display.refresh()
            elapsed = (time.monotonic() - t0) * 1000.0
            partial_times.append(elapsed)

        partial_avg = average(partial_times)
        print(f"Average: {partial_avg:.2f} ms")

        if partial_avg < 50:
            print("  [OK] EXCELLENT - True partial refresh!")
        elif partial_avg < 200:
            print("  [OK] Good - Partial refresh working")
        else:
            print("  [WARN] May be doing full-screen refresh")

        # Test 3: Many small rectangles
        print()
        print("-" * 70)
        print("TEST 3: 100x fill_rect(40x40) + refresh")
        print("-" * 70)
        print()

        bitmap.fill(0x0000)
        t0 = time.monotonic()

        for i in range(100):
            x = (i * 37) % 560
            y = (i * 23) % 410
            color = (i * 613) & 0xFFFF
            bitmaptools.fill_region(bitmap, x, y, x + 40, y + 40, color)

        display.refresh()
        rect_time = (time.monotonic() - t0) * 1000.0

        print(f"100x fill_rect time: {rect_time:.2f} ms")
        print(f"Per rect: {rect_time/100:.2f} ms")
        print()

        if rect_time < 500:
            print("\n  [OK] SUCCESS!")
        elif rect_time < 5000:
            print("\n  [OK] Good")
        else:
            print("\n  [WARN] Slower than expected")

        # Summary
        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Full-screen fill + refresh:  {full_avg:.2f} ms")
        print(f"Partial update (100x100):    {partial_avg:.2f} ms")
        print(f"100x fill_rect + refresh:    {rect_time:.2f} ms")
        print()

        ratio = partial_avg / full_avg if full_avg > 0 else 0
        print(f"Partial vs Full ratio: {ratio:.2f}x")

        if ratio < 0.3:
            print("[OK] Partial refresh properly optimized")
        elif ratio < 0.8:
            print("[WARN] Partial refresh could be better")
        else:
            print("[FAIL] Partial refresh doing full-screen flush")

        print()
        print("=" * 70)
        print("Benchmark complete!")
        print("=" * 70)
    finally:
        # Cleanup
        if bus:
            bus.deinit()
        displayio.release_displays()


if __name__ == "__main__":
    try:
        main()
        print("\nPress Ctrl+C to exit")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Benchmark stopped by user")
    finally:
        displayio.release_displays()
        print("[OK] Cleanup complete")
