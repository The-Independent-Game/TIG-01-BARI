import time
import machine
import neopixel
import random


class TIG01:
    # Musical notes (frequency in Hz)
    NOTE_C4 = 262
    NOTE_E4 = 330
    NOTE_FS4 = 370
    NOTE_G4 = 392
    NOTE_A4 = 440
    NOTE_B4 = 494
    NOTE_C5 = 523
    NOTE_D5 = 587
    NOTE_E5 = 659
    NOTE_F5 = 698
    REST = 0

    # Game states
    IDLE = 0
    KICK_0_1 = 1
    KICK_1_0 = 2

    # Constants
    MAX_DELAY_VEL = 300
    MAX_LEVEL = 15

    def __init__(self):
        """Inizializza l'hardware e le configurazioni del gioco Pong"""
        # Hardware pins - adapted to existing TIG01 hardware
        self.buzzer = machine.PWM(machine.Pin(9))
        self.button_red = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
        self.button_yellow = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
        self.led_red = machine.Pin(11, machine.Pin.OUT)
        self.led_yellow = machine.Pin(10, machine.Pin.OUT)
        self.NUM_LEDS = 8

        self.np = neopixel.NeoPixel(machine.Pin(8), self.NUM_LEDS)

        # Game state variables
        self.button_press_states = 0
        self.button_ready_states = 0
        self.game_state = self.IDLE
        self.ball_position = 0
        self.timer = 0
        self.last_time_ball_position = 0
        self.animation_time = 0
        self.kick_time = 0
        self.ball_speed = self.MAX_DELAY_VEL
        self.animation_button = 0
        self.sound = True
        self.mid_ball_position = self.NUM_LEDS // 2
        self.level = 0
        self.tone_end_time = 0

        # Musical tones for idle animation
        self.tones = [261, 277, 294, 311, 330, 349, 370, 392, 415, 440]

        # Setup
        self.buzzer.duty_u16(0)
        self.stop_button_leds()
        self.stop_ball()
        self.ball_speed = self.MAX_DELAY_VEL

        print("Pong Game Ready - TIG01")

    def millis(self):
        """Return milliseconds since start"""
        return time.ticks_ms()

    def map_value(self, x, in_min, in_max, out_min, out_max):
        """Map value from one range to another"""
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

    def is_button_pressed(self, button):
        """Check if button bit is set"""
        return (self.button_press_states >> button) & 1

    def stop_button_leds(self):
        """Turn off all button LEDs"""
        self.led_red.off()
        self.led_yellow.off()
        self.no_tone()

    def button_led_on(self, led_index):
        """Turn on specific button LED"""
        if led_index == 0:
            self.led_red.on()
            self.led_yellow.off()
        else:
            self.led_red.off()
            self.led_yellow.on()

    def all_on(self):
        """Turn on all button LEDs"""
        self.led_red.on()
        self.led_yellow.on()

    def stop_ball(self):
        """Clear all NeoPixel LEDs"""
        for i in range(self.NUM_LEDS):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def read_buttons(self):
        """Read button states with debouncing (active low - PULL_UP)"""
        buttons = [self.button_red, self.button_yellow]

        for i in range(len(buttons)):
            # Button pressed when value is 0 (PULL_UP)
            if not buttons[i].value():
                if (self.button_ready_states >> i) & 1:
                    self.button_ready_states &= ~(1 << i)
                    self.button_press_states |= (1 << i)
                else:
                    self.button_press_states &= ~(1 << i)
            else:
                self.button_ready_states |= (1 << i)
                self.button_press_states &= ~(1 << i)

    def tone(self, frequency, duration_ms):
        """Play tone on buzzer (non-blocking)"""
        if self.sound and frequency > 0:
            self.buzzer.freq(frequency)
            self.buzzer.duty_u16(32768)
            self.tone_end_time = self.timer + duration_ms

    def tone_blocking(self, frequency, duration_ms):
        """Play tone on buzzer (blocking - for victory music)"""
        if self.sound:
            if frequency > 0:
                self.buzzer.freq(frequency)
                self.buzzer.duty_u16(32768)
                time.sleep_ms(duration_ms)
            self.no_tone()
        else:
            time.sleep_ms(duration_ms)

    def no_tone(self):
        """Stop buzzer"""
        self.buzzer.duty_u16(0)

    def rotate_animation(self):
        """Rotate button LED animation"""
        self.animation_button += 1
        if self.animation_button > 1:
            self.animation_button = 0
        self.button_led_on(self.animation_button)

    def player_music_wins(self, melody):
        """Play victory melody"""
        tempo = 120
        wholenote = (60000 * 4) // tempo

        i = 0
        while i < len(melody):
            note = melody[i]
            divider = melody[i + 1]

            self.rotate_animation()

            if divider > 0:
                note_duration = wholenote // divider
            else:
                note_duration = wholenote // abs(divider)
                note_duration = int(note_duration * 1.5)

            self.tone_blocking(note, int(note_duration * 0.9))

            i += 2

        self.stop_button_leds()

    def player1_music_wins(self):
        """Player 1 (Yellow) victory music"""
        melody = [
            self.NOTE_G4, 8, self.NOTE_A4, 8, self.NOTE_B4, 4, self.NOTE_D5, 4,
            self.NOTE_D5, 4, self.NOTE_B4, 4, self.NOTE_C5, 4, self.NOTE_C5, 2
        ]
        self.player_music_wins(melody)

    def player0_music_wins(self):
        """Player 0 (Blue) victory music"""
        melody = [
            self.NOTE_C4, -8, self.NOTE_E4, 16, self.NOTE_G4, 8, self.NOTE_C5, 8,
            self.NOTE_E5, 8, self.NOTE_D5, 8, self.NOTE_C5, 8, self.NOTE_A4, 8,
            self.NOTE_FS4, 8, self.NOTE_G4, 8, self.REST, 4, self.REST, 2
        ]
        self.player_music_wins(melody)

    def end_game(self, gs):
        """End game and show winner"""
        self.stop_ball()
        self.stop_button_leds()

        # Light winner button
        self.button_led_on(0 if gs == self.KICK_0_1 else 1)

        # Set all LEDs to winner color (RGB format)
        if gs == self.KICK_1_0:
            color = (255, 0, 0)    # Red
        else:
            color = (255, 255, 0)  # Yellow
        

        for i in range(self.NUM_LEDS):
            self.np[i] = color
        self.np.write()

        # Play victory music
        if gs == self.KICK_0_1:
            self.player0_music_wins()
        else:
            self.player1_music_wins()

        self.stop_ball()

        # Reset game state
        self.ball_position = 0
        self.ball_speed = self.MAX_DELAY_VEL
        self.game_state = self.IDLE
        self.button_press_states = 0
        self.button_ready_states = 0
        self.level = 1

    def player_sound(self, direction):
        """Play kick sound (non-blocking)"""
        if direction == self.KICK_0_1:
            self.tone(400, 100)
        else:
            self.tone(700, 100)

    def ball_led_encoding(self, position, direction):
        """Encode ball LED position based on direction"""
        if direction == self.KICK_0_1:
            return position
        else:
            return self.NUM_LEDS - 1 - position

    def set_ball_led_color(self, position, direction):
        """Set ball LED color based on position"""
        led_index = self.ball_led_encoding(position, direction)

        if position == self.mid_ball_position:
            # Green at midpoint
            g = self.map_value(self.level, 1, self.MAX_LEVEL, 20, 255)
            self.np[led_index] = (0, g, 0)
        else:
            # Red elsewhere
            r = self.map_value(self.level, 1, self.MAX_LEVEL, 20, 255)
            self.np[led_index] = (r, 0, 0)

    def first_kick(self, direction):
        """Start game with first kick"""
        self.game_state = direction

        button = 0 if direction == self.KICK_0_1 else 1

        self.player_sound(direction)
        self.button_led_on(button)
        self.kick_time = self.timer

        self.ball_position = 0
        self.last_time_ball_position = self.timer
        self.level = 1

        self.set_ball_led_color(self.ball_position, direction)
        self.np.write()

    def ball_move_on(self, direction):
        """Move ball forward"""
        if self.timer - self.last_time_ball_position > self.ball_speed:
            self.ball_position += 1
            self.last_time_ball_position = self.timer

            if self.ball_position < self.NUM_LEDS:
                self.stop_ball()
                self.set_ball_led_color(self.ball_position, direction)
                self.np.write()
            else:
                self.end_game(direction)

    def opponent_responds(self, direction):
        """Handle opponent button press"""
        if self.timer - self.kick_time > 200:
            self.stop_button_leds()

        button = 1 if direction == self.KICK_0_1 else 0

        if self.is_button_pressed(button):
            self.player_sound(direction)
            self.button_led_on(button)
            self.kick_time = self.timer

            if self.ball_position <= self.mid_ball_position:
                # Too early, other wins
                self.end_game(direction)
            else:
                # Successful return
                self.level += 1
                if self.level > self.MAX_LEVEL:
                    self.level = self.MAX_LEVEL

                # Calculate new ball speed
                self.ball_speed = self.map_value(
                    self.ball_position,
                    self.mid_ball_position + 1,
                    self.NUM_LEDS - 1,
                    300, 100
                )
                self.ball_speed -= self.map_value(self.level, 1, self.MAX_LEVEL, 0, 70)

                # Switch direction
                self.game_state = self.KICK_1_0 if direction == self.KICK_0_1 else self.KICK_0_1
                self.ball_position = self.NUM_LEDS - self.ball_position - 1

    def loop(self):
        """Main game loop"""
        try:
            self.read_buttons()
            self.timer = self.millis()

            # Check if tone should stop (non-blocking tone management)
            if self.tone_end_time > 0 and self.timer >= self.tone_end_time:
                self.no_tone()
                self.tone_end_time = 0

            if self.game_state == self.IDLE:
                # Random idle animation (rare)
                if random.randint(0, 400000) == 0:
                    self.all_on()
                    self.tone(random.choice(self.tones), 500)
                    self.stop_button_leds()
                else:
                    # Regular animation
                    if time.ticks_diff(self.timer, self.animation_time) >= 500:
                        self.rotate_animation()
                        self.animation_time = self.millis()

                # Check for first kick
                if self.is_button_pressed(0):
                    self.first_kick(self.KICK_0_1)
                elif self.is_button_pressed(1):
                    self.first_kick(self.KICK_1_0)

            elif self.game_state == self.KICK_0_1:
                self.ball_move_on(self.KICK_0_1)
                self.opponent_responds(self.KICK_0_1)

            elif self.game_state == self.KICK_1_0:
                self.ball_move_on(self.KICK_1_0)
                self.opponent_responds(self.KICK_1_0)
        except Exception as e:
            print(f"ERRORE nel loop: {type(e).__name__}: {e}")
            print(f"Game state: {self.game_state}, Ball pos: {self.ball_position}")
            
    def start(self):
        """Main game entry point"""
        print("Pong Game Starting...")
        try:
            while True:
                self.loop()
                time.sleep_ms(5)  # Small delay for stability
        except KeyboardInterrupt:
            print("\nGame stopped")
            self.stop_ball()
            self.stop_button_leds()


def start():
    try:
        game = TIG01()
        game.start()
    except Exception as e:
        print(f"ERRORE: {type(e).__name__}: {e}")
        import sys
        sys.print_exception(e)





