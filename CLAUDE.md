# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TIG-01-BARI is a MicroPython-based implementation of the classic **ZAP! Coleco** game for embedded hardware (TIG01 board). ZAP! was originally a handheld electronic game by Coleco, featuring a two-player reaction-based gameplay where a light travels back and forth between players who must press their button at the right moment to send it back.

The game features:
- Two-player competitive gameplay with button controls
- NeoPixel LED strip (8 LEDs) for light/ball visualization
- Audio feedback via PWM buzzer
- Dynamic difficulty with speed increases per level
- Victory music sequences

## Hardware Configuration

The TIG01 class is configured for specific GPIO pins on the target microcontroller:
- **Buzzer**: GPIO 9 (PWM)
- **Blue button**: GPIO 4 (input, pull-up, active low)
- **Yellow button**: GPIO 5 (input, pull-up, active low)
- **Blue LED**: GPIO 11 (output)
- **Yellow LED**: GPIO 10 (output)
- **NeoPixel strip**: GPIO 8 (8 LEDs, WS2812/similar)

Buttons are active LOW due to PULL_UP configuration.

## Code Architecture

### Core Structure
- **`tig_01_bari.py`**: Main game logic in the `TIG01` class
- **`main.py`**: Entry point that calls `tig_01_bari.start()`

### TIG01 Class Design

All constants are defined as class attributes:
- Musical notes (NOTE_C4, NOTE_E4, etc.)
- Game states (IDLE, KICK_0_1, KICK_1_0)
- Game parameters (MAX_DELAY_VEL, MAX_LEVEL)

Access constants via `self.CONSTANT_NAME` within instance methods.

### Game States
1. **IDLE**: Waiting for first button press, rotating LED animation
2. **KICK_0_1**: Light moving from player 0 (blue) to player 1 (yellow)
3. **KICK_1_0**: Light moving from player 1 (yellow) to player 0 (blue)

### Key Game Mechanics
- **Light position**: Travels along the LED strip (0-7 index), encoded differently based on direction
- **Speed calculation**: Decreases based on timing of button press and current level
- **Mid-light position**: Position 4 (center) - displayed in green, others in red
- **Win condition**: Light reaches opponent's end (position >= NUM_LEDS)
- **Early press penalty**: Pressing before mid_light_position results in opponent win
- **Perfect timing reward**: Pressing closer to your end increases speed/difficulty for opponent
- **Level progression**: 1-15, affects speed and LED brightness

### Color Encoding (RGB for NeoPixels)
- **Blue** (Player 0): (0, 0, 255)
- **Yellow** (Player 1): (255, 255, 0)
- **Red** (traveling light): (r, 0, 0) - intensity varies with level
- **Green** (mid-point): (0, g, 0) - intensity varies with level

## Running the Game

Deploy to MicroPython-capable board (e.g., ESP32, RP2040):
```python
import main
main.main()
```

Or call directly:
```python
import tig_01_bari
tig_01_bari.start()
```

The game runs in an infinite loop until KeyboardInterrupt (Ctrl+C).

## Development Notes

- This is MicroPython code targeting embedded hardware - standard Python features like type hints or modern syntax may not be available
- Button debouncing uses bitwise operations on `button_press_states` and `button_ready_states`
- Time tracking uses `time.ticks_ms()` and `time.ticks_diff()` for millisecond precision
- The `map_value()` method provides Arduino-style value mapping between ranges
- Sound can be toggled via `self.sound` flag
- Exception handling in `start()` function uses MicroPython's `sys.print_exception()`
- Variable names in the code still reference "ball" (e.g., `ball_position`, `ball_speed`) as this was originally modeled after Pong, but conceptually represents the traveling light in the ZAP! Coleco game
- This implementation recreates the classic Coleco handheld electronic game experience using modern embedded hardware

## License

Apache License 2.0
