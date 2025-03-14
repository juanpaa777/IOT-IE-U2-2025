from machine import Pin, PWM
import time

# Definir los pines para los colores RGB
red_pin = Pin(21, Pin.OUT)  # Pin para el rojo
green_pin = Pin(22, Pin.OUT)  # Pin para el verde
blue_pin = Pin(23, Pin.OUT)  # Pin para el azul

# Configurar los pines como PWM (modulación por ancho de pulso) para controlar la intensidad de los colores
red = PWM(red_pin, freq=5000)
green = PWM(green_pin, freq=5000)
blue = PWM(blue_pin, freq=5000)

# Función para ajustar los colores
def set_color(r, g, b):
    red.duty(r)
    green.duty(g)
    blue.duty(b)

# Ciclo de colores
while True:
    # Rojo
    set_color(1023, 0, 0)
    time.sleep(1)
    
    # Verde
    set_color(0, 1023, 0)
    time.sleep(1)
    
    # Azul
    set_color(0, 0, 1023)
    time.sleep(1)
    
    # Amarillo (Rojo + Verde)
    set_color(1023, 1023, 0)
    time.sleep(1)
    
    # Cian (Verde + Azul)
    set_color(0, 1023, 1023)
    time.sleep(1)
    
    # Magenta (Rojo + Azul)
    set_color(1023, 0, 1023)
    time.sleep(1)
    
    # Blanco (Rojo + Verde + Azul)
    set_color(1023, 1023, 1023)
    time.sleep(1)
