import time
import machine
import time
import neopixel

def play_tone(frequency, duration):
    buzzer.freq(frequency)
    buzzer.duty_u16(32768)  
    time.sleep(duration)
    buzzer.duty_u16(0)

buzzer = machine.PWM(machine.Pin(9))
button_blue = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)
button_yellow = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)
led_blue = machine.Pin(11, machine.Pin.OUT)
led_yellow = machine.Pin(10, machine.Pin.OUT)
NUM_LEDS = 8

np = neopixel.NeoPixel(machine.Pin(8), NUM_LEDS)


button_blue_pressed = False
button_yellow_pressed = False

def set_color(r, g, b):
    for i in range(NUM_LEDS):
        np[i] = (r, g, b)  
    np.write()  

set_color(0,0,0)

def button_handler(pin):
    global button_blue_pressed
    global button_yellow_pressed
    global button_green_pressed
    global button_red_pressed

    if pin == button_blue:
        button_blue_pressed = True
    elif pin == button_yellow:
        button_yellow_pressed = True


button_blue.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_handler)
button_yellow.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_handler)


while True:
    if button_blue_pressed:
        led_blue.on()
        set_color(0, 0, 255)
        play_tone(300, 0.5)
        button_blue_pressed = False
        time.sleep(0.5)
        set_color(0,0,0)
        led_blue.off()
        
    if button_yellow_pressed:
        led_yellow.on()
        set_color(255, 255, 0)
        play_tone(600, 0.5)
        button_yellow_pressed = False
        time.sleep(0.5)
        set_color(0, 0, 0)
        led_yellow.off()
    
        
    
    time.sleep(0.1)



