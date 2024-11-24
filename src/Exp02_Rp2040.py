import machine
import ustruct
from utime import sleep_us
from i2cslave import I2CSlave
from machine import Pin
import rp2


i2c = I2CSlave(address=0x0A)


zxpin = Pin(4, Pin.IN)  
trpin = Pin(5, Pin.OUT)  

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def dimmer():
    set(pin, 0)
    pull()
    mov(x, osr)

    label('waitzx')
    wrap_target()
    wait(0, pin, 0)
    pull(noblock)
    mov(x, osr)
    mov(y, x)
    wait(1, pin, 0)
    nop() [4]

    label('delay')
    jmp(y_dec, 'delay')
    set(pins, 1)
    set(pins, 0)
    jmp('waitzx')
    wrap()


sm = rp2.StateMachine(0, dimmer, freq=5_000, in_base=zxpin, set_base=trpin)
sm.active(1)

def adjust_brightness(power):
    power = round(power)  
    if power < 1:
        sm.active(0)  
        print(f'Potencia: {power}% | Foco APAGADO')
    else:
        delay = 21 - int(21 * power / 100)  
        sm.put(delay)
        sm.active(1)  
        print(f'Potencia: {power}% | Retraso: {delay}')

while True:
    while i2c.rxBufferCount() < 4:
        sleep_us(10)
    data = i2c.read()
    power = round(ustruct.unpack("<f", data)[0])  
    power = max(0, min(100, power))  
    adjust_brightness(power)
