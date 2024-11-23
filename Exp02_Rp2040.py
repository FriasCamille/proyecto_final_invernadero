# combined_brightness_control.py
import machine
import ustruct
from utime import sleep_ms, sleep_us
from i2cslave import I2CSlave
from machine import Pin
import rp2

# Configuración del bus I2C para recibir el nivel de brillo
i2c = I2CSlave(address=0x0A)

# Configuración del control del dimmer de CA
zxpin = Pin(2, Pin.IN)
trpin = Pin(3, Pin.OUT)

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

# Inicializa la máquina de estado
sm = rp2.StateMachine(0, dimmer, freq=5_000, in_base=zxpin, set_base=trpin)
sm.active(1)

print("Brightness control ready. Input values from 0–100.")

def adjust_brightness(brightness):
    if brightness < 1:
        sm.active(0)  # Apaga la luz completamente
        print(f'Set Brightness: {brightness}% | Light OFF')
    else:
        delay = 21 - int(21 * brightness / 100)
        sm.put(delay)
        sm.active(1)  # Asegura que la máquina de estado esté activa para el control del brillo
        print(f'Set Brightness: {brightness}% | Delay: {delay}')

while True:
    # Espera hasta que se reciban exactamente 4 bytes (1 float)
    while i2c.rxBufferCount() < 4:
        sleep_us(10)
    data = i2c.read()
    brightness = int(ustruct.unpack("<f", data)[0])
    brightness = max(0, min(100, brightness))  # Limita a 0–100
    adjust_brightness(brightness)

