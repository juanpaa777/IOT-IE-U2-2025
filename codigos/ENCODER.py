from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Pines del Encoder KY-040
clk = Pin(18, Pin.IN, Pin.PULL_UP)
dt = Pin(19, Pin.IN, Pin.PULL_UP)
sw = Pin(21, Pin.IN, Pin.PULL_UP)  # Botón del encoder

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_encoder"
MQTT_BROKER = "192.168.153.135"  # Cambia por la IP de tu servidor Mosquitto
MQTT_PORT = 1883
MQTT_TOPIC_ENCODER = "sensor/encoder"
MQTT_TOPIC_BUTTON = "sensor/button"

# Variables de estado
contador = 0
ultimo_estado_clk = clk.value()

def conectar_wifi():
    """Conecta el ESP32 a la red WiFi."""
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.5)
    
    print("\n[INFO] WiFi Conectada!")
    print(f"[INFO] Dirección IP: {sta_if.ifconfig()[0]}")

def conectar_mqtt():
    """Conecta a MQTT y maneja reconexiones."""
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        return None

# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_mqtt()

# Bucle principal
while True:
    try:
        # Verificar conexión WiFi
        if not network.WLAN(network.STA_IF).isconnected():
            print("[ERROR] WiFi desconectado, reconectando...")
            conectar_wifi()
            client = conectar_mqtt()

        # Verificar conexión MQTT
        if client is None:
            print("[ERROR] MQTT desconectado, reconectando...")
            client = conectar_mqtt()
            time.sleep(5)
            continue

        # Leer el estado actual del CLK
        estado_actual_clk = clk.value()

        # Detectar cambio en CLK (Giro)
        if estado_actual_clk != ultimo_estado_clk:
            if dt.value() != estado_actual_clk:  # Gira a la derecha
                contador += 1
            else:  # Gira a la izquierda
                contador -= 1

            print(f"[INFO] Contador: {contador}")
            client.publish(MQTT_TOPIC_ENCODER, str(contador).encode())

        # Guardar el estado actual de CLK
        ultimo_estado_clk = estado_actual_clk

        # Detectar botón presionado
        if sw.value() == 0:  
            print("[INFO] Botón presionado")
            client.publish(MQTT_TOPIC_BUTTON, "CLICK".encode())

            # Esperar a que se suelte para evitar repeticiones
            while sw.value() == 0:
                time.sleep(0.1)

        time.sleep(0.01)  # Pequeña pausa para estabilidad

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
