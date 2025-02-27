from machine import Pin, PWM
import time
import neopixel

NUM_LEDS = 8

np = neopixel.NeoPixel(machine.Pin(26), NUM_LEDS)
led_green = Pin(28, Pin.OUT)
led_red = Pin(22, Pin.OUT)
button_green = Pin(27, Pin.IN, Pin.PULL_UP)
button_red = Pin(21, Pin.IN, Pin.PULL_UP)
buzzer = PWM(Pin(16))  

def set_color(r, g, b):
    for i in range(NUM_LEDS):
        np[i] = (r, g, b)  # Imposta il colore RGB per ogni LED
    np.write()  # Aggiorna la striscia

#striscia led spenta
set_color(0,0,0)

def play_tone(frequency, duration):
    if frequency > 0:
        buzzer.freq(frequency)
        buzzer.duty_u16(32767)  # 50% duty cycle
    else:
        buzzer.duty_u16(0)  # Disattiva il suono
    
    time.sleep(duration)
    buzzer.duty_u16(0)  # Ferma il suono

while True:
    '''
    set_color(255, 0, 0)  # Rosso
    time.sleep(1)
    set_color(0, 255, 0)  # Verde
    time.sleep(1)
    set_color(0, 0, 255)  # Blu
    time.sleep(1)
    '''
    if button_green.value() == 0:  # pull-up -> 0 indica pressione
        led_green.value(1)
        play_tone(262,0.2)
    else:
        led_green.value(0)
        
    if button_red.value() == 0:
        led_red.value(1)
        play_tone(300,0.2)
    else:
        led_red.value(0)
        