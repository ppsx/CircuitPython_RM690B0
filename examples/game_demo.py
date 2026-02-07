# SPDX-FileCopyrightText: Copyright (c) 2026 Przemyslaw Patrick Socha
#
# SPDX-License-Identifier: Unlicense

"""
Simple Game Demo - DisplayIO Version
=====================================

Bouncing ball game demo using displayio bitmap-based rendering.

Dependencies:
    - bitmaptools (built-in firmware module)
    - adafruit_display_text (Community Bundle)
"""

import time
import board
import displayio
import bitmaptools
from adafruit_display_text import label
import terminalio
from rm690b0 import RM690B0, create_qspi_bus

DISPLAY_WIDTH = 600
DISPLAY_HEIGHT = 450

print("Initializing RM690B0 display...")

# Release any existing displays
displayio.release_displays()

# Create QSPI bus
bus = create_qspi_bus(board, frequency=40_000_000)

# Create RM690B0 display
display = RM690B0(bus, width=DISPLAY_WIDTH, height=DISPLAY_HEIGHT)

# Game state
ball_x = 300
ball_y = 226
# Time-based velocity (pixels/second). This keeps motion speed stable
# when refresh cost varies with dirty area size.
ball_vx = 240.0
ball_vy = 144.0
ball_r = 14
ball_fx = float(ball_x)
ball_fy = float(ball_y)

paddle_x = 270
paddle_y = 420
paddle_w = 60
paddle_h = 10

score = 0
frame_count = 0

print("Setting up game canvas...")

# Create main group
game = displayio.Group()

# Create canvas bitmap (we'll draw everything here)
canvas = displayio.Bitmap(DISPLAY_WIDTH, DISPLAY_HEIGHT, 65536)
palette = displayio.ColorConverter(input_colorspace=displayio.Colorspace.RGB565)
canvas_sprite = displayio.TileGrid(canvas, pixel_shader=palette)
game.append(canvas_sprite)

# Text labels (overlaid on canvas)
score_label = label.Label(
    terminalio.FONT, text="SCORE 0000", color=0x00FFFF, x=16, y=16
)
game.append(score_label)

fps_label = label.Label(terminalio.FONT, text="FPS: --", color=0xFFFF00, x=16, y=32)
game.append(fps_label)

# Show initial state
display.root_group = game

print("Pre-rendering sprites...")

# Pre-render ball sprite (WHITE circle)
ball_size = ball_r * 2 + 4
ball_sprite = displayio.Bitmap(ball_size, ball_size, 65536)
ball_sprite.fill(0x0000)

# Pre-render clear sprite (BLACK circle - for erasing)
clear_sprite = displayio.Bitmap(ball_size, ball_size, 65536)
clear_sprite.fill(0x0000)

# Draw filled circles
ball_center = ball_r + 2
r_squared = ball_r * ball_r
for dy in range(-ball_r, ball_r + 1):
    y_pos = ball_center + dy
    dx_max = int((r_squared - dy * dy) ** 0.5)
    for dx in range(-dx_max, dx_max + 1):
        x_pos = ball_center + dx
        ball_sprite[x_pos, y_pos] = 0xFFFF  # White
        clear_sprite[x_pos, y_pos] = 0x0000  # Black (for clearing)

# Pre-render paddle sprite (GREEN rectangle with 2px padding)
paddle_sprite_w = paddle_w + 4
paddle_sprite_h = paddle_h + 4
paddle_sprite = displayio.Bitmap(paddle_sprite_w, paddle_sprite_h, 65536)
paddle_sprite.fill(0x0000)
bitmaptools.fill_region(paddle_sprite, 2, 2, 2 + paddle_w, 2 + paddle_h, 0x07E0)

# Pre-render paddle clear sprite (BLACK - for erasing)
paddle_clear = displayio.Bitmap(paddle_sprite_w, paddle_sprite_h, 65536)
paddle_clear.fill(0x0000)

print("Sprites created!")
print(f"Ball sprite size: {ball_sprite.width}x{ball_sprite.height}")
print(f"Paddle sprite size: {paddle_sprite.width}x{paddle_sprite.height}")


# Initial clear (full screen once)
canvas.fill(0x0000)
display.refresh()

# Draw initial objects
ball_sprite_x = int(ball_x - ball_r - 2)
ball_sprite_y = int(ball_y - ball_r - 2)
bitmaptools.blit(
    canvas, ball_sprite, ball_sprite_x, ball_sprite_y, skip_source_index=0x0000
)
bitmaptools.blit(
    canvas, paddle_sprite, paddle_x - 2, paddle_y - 2, skip_source_index=0x0000
)
display.refresh()

print("Game started!")
print("No input; paddle follows ball automatically")
print("Press Ctrl+C to stop")
print()

fps_samples = []
last_fps_update = time.monotonic()
last_motion_update = time.monotonic()


def _mark_ball_dirty(bitmap, prev_bx, prev_by, bx, by):
    x1 = min(prev_bx, bx) - ball_r - 2
    y1 = min(prev_by, by) - ball_r - 2
    x2 = max(prev_bx, bx) + ball_r + 2
    y2 = max(prev_by, by) + ball_r + 2
    x1 = max(0, x1) & ~1
    y1 = max(0, y1)
    x2 = min(DISPLAY_WIDTH, (x2 + 1) & ~1)
    y2 = min(DISPLAY_HEIGHT, y2)
    if x2 <= x1:
        x2 = min(DISPLAY_WIDTH, x1 + 2)
    if y2 <= y1:
        y2 = min(DISPLAY_HEIGHT, y1 + 1)
    bitmap.dirty(x1=x1, y1=y1, x2=x2, y2=y2)


def _mark_paddle_dirty(bitmap, prev_px, px):
    x1 = min(prev_px, px) - 2
    y1 = paddle_y - 2
    x2 = max(prev_px, px) + paddle_w + 2
    y2 = paddle_y + paddle_h + 2
    x1 = max(0, x1) & ~1
    y1 = max(0, y1)
    x2 = min(DISPLAY_WIDTH, (x2 + 1) & ~1)
    y2 = min(DISPLAY_HEIGHT, y2)
    if x2 <= x1:
        x2 = min(DISPLAY_WIDTH, x1 + 2)
    if y2 <= y1:
        y2 = min(DISPLAY_HEIGHT, y1 + 1)
    bitmap.dirty(x1=x1, y1=y1, x2=x2, y2=y2)


try:
    # Track previous positions
    prev_ball_x = ball_x
    prev_ball_y = ball_y
    prev_paddle_x = paddle_x

    while True:
        frame_start = time.monotonic()
        now = time.monotonic()
        dt = now - last_motion_update
        last_motion_update = now
        if dt < 0:
            dt = 0
        elif dt > 0.05:
            dt = 0.05

        # Update ball position
        ball_fx += ball_vx * dt
        ball_fy += ball_vy * dt
        ball_x = int(ball_fx) & ~1
        ball_y = int(ball_fy) & ~1

        # Wall collisions (with position correction to prevent sprite clipping)
        # Ensure ball position allows sprite (ball_r + 2) to fit without clamping
        if ball_x - ball_r <= 0:
            ball_fx = float(ball_r + 2)
            ball_x = ball_r + 2
            ball_vx = abs(ball_vx)
            score += 1
        elif ball_x + ball_r >= DISPLAY_WIDTH - 1:
            ball_fx = float(DISPLAY_WIDTH - ball_r - 2)
            ball_x = DISPLAY_WIDTH - ball_r - 2
            ball_vx = -abs(ball_vx)
            score += 1

        if ball_y - ball_r <= 0:
            ball_fy = float(ball_r + 2)
            ball_y = ball_r + 2
            ball_vy = abs(ball_vy)
            score += 1
        elif ball_y + ball_r >= DISPLAY_HEIGHT - 1:
            ball_fy = float(DISPLAY_HEIGHT - ball_r - 2)
            ball_y = DISPLAY_HEIGHT - ball_r - 2
            ball_vy = -abs(ball_vy)
            score += 1

        # Paddle auto-follow
        paddle_x = int(ball_fx) - (paddle_w // 2)
        paddle_x &= ~1
        paddle_x = max(paddle_x, 2)
        max_px = (DISPLAY_WIDTH - paddle_w - 2) & ~1
        paddle_x = min(paddle_x, max_px)

        # Paddle collision
        if (
            ball_y + ball_r >= paddle_y
            and ball_y + ball_r <= paddle_y + paddle_h
            and paddle_x <= ball_x <= (paddle_x + paddle_w)
        ):
            ball_fy = float(paddle_y - ball_r)
            ball_y = paddle_y - ball_r
            ball_vy = -abs(ball_vy)
            score += 5

        # Bottom miss -> game over
        if ball_y - ball_r > DISPLAY_HEIGHT:
            canvas.fill(0xF800)
            display.refresh()
            time.sleep(0.5)
            ball_fx, ball_fy = 300.0, 226.0
            ball_x, ball_y = 300, 226
            ball_vx, ball_vy = 240.0, 144.0
            score = 0
            fps_samples = []
            continue

        # Update score label before refresh (visible when ball region covers it)
        score_text = f"SCORE {score:04d}"
        if score_label.text != score_text:
            score_label.text = score_text

        # --- Phase 1: Ball ---
        bitmaptools.blit(
            canvas, clear_sprite, prev_ball_x - ball_r - 2, prev_ball_y - ball_r - 2
        )
        bitmaptools.blit(
            canvas,
            ball_sprite,
            ball_x - ball_r - 2,
            ball_y - ball_r - 2,
            skip_source_index=0x0000,
        )
        _mark_ball_dirty(canvas, prev_ball_x, prev_ball_y, ball_x, ball_y)
        display.refresh()

        # --- Phase 2: Paddle ---
        bitmaptools.blit(canvas, paddle_clear, prev_paddle_x - 2, paddle_y - 2)
        bitmaptools.blit(
            canvas, paddle_sprite, paddle_x - 2, paddle_y - 2, skip_source_index=0x0000
        )
        _mark_paddle_dirty(canvas, prev_paddle_x, paddle_x)
        display.refresh()

        # Update FPS counter (every 0.5 seconds)
        now = time.monotonic()
        if now - last_fps_update >= 0.5:
            if fps_samples:
                avg_fps = sum(fps_samples) / len(fps_samples)
                fps_label.text = f"FPS: {avg_fps:.1f}"
                fps_samples = []
            last_fps_update = now

        # Save current positions for next frame
        prev_ball_x = ball_x
        prev_ball_y = ball_y
        prev_paddle_x = paddle_x

        frame_count += 1

        # Calculate FPS
        frame_time = time.monotonic() - frame_start
        if frame_time > 0:
            fps_samples.append(1.0 / frame_time)

        # Print stats every 120 frames
        if frame_count % 120 == 0:
            print(
                f"frame={frame_count}, score={score}, "
                f"frame_time={frame_time*1000:.1f}ms"
            )

except KeyboardInterrupt:
    print("\n[INFO] Game stopped by user")
    print(f"Final score: {score}")
    print(f"Total frames: {frame_count}")
finally:
    displayio.release_displays()
    print("[OK] Cleanup complete")
