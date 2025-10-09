import time
import machine
import time
import neopixel

class TIG01:
    def __init__(self):
        """Inizializza l'hardware e le configurazioni del gioco"""
        self.buzzer = machine.PWM(machine.Pin(9))
        self.button_blue = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
        self.button_yellow = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
        self.led_blue = machine.Pin(11, machine.Pin.OUT)
        self.led_yellow = machine.Pin(10, machine.Pin.OUT)
        self.NUM_LEDS = 8

        self.np = neopixel.NeoPixel(machine.Pin(8), self.NUM_LEDS)

        self.button_blue_pressed = False
        self.button_yellow_pressed = False

    def play_tone(self, frequency, duration):
        self.buzzer.freq(frequency)
        self.buzzer.duty_u16(32768)  
        time.sleep(duration)
        self.buzzer.duty_u16(0)

    def set_color(self, r, g, b):
        for i in range(self.NUM_LEDS):
            self.np[i] = (r, g, b)  
        self.np.write()  

    def button_handler(self, pin):

        if pin == self.button_blue:
            self.button_blue_pressed = True
        elif pin == self.button_yellow:
            self.button_yellow_pressed = True


    def start(self):
        """Avvia il gioco principale"""        
        self.set_color(0,0,0)

        self.button_blue.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.button_handler)
        self.button_yellow.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.button_handler)

        while True:
            if self.button_blue_pressed:
                self.led_blue.on()
                self.set_color(0, 0, 255)
                self.play_tone(300, 0.5)
                self.button_blue_pressed = False
                time.sleep(0.5)
                self.set_color(0,0,0)
                self.led_blue.off()
                
            if self.button_yellow_pressed:
                self.led_yellow.on()
                self.set_color(255, 255, 0)
                self.play_tone(600, 0.5)
                self.button_yellow_pressed = False
                time.sleep(0.5)
                self.set_color(0, 0, 0)
                self.led_yellow.off()
            
            time.sleep(0.1)


def start():
    game = TIG01()
    game.start()





