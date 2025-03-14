from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del Reed Switch (KY-025)
reed_switch = Pin(25, Pin.IN, Pin.PULL_UP)  # GPIO25 como entrada con pull-up

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_reed_switch"
MQTT_BROKER = "192.168.221.135"  # Cambia por la IP de tu servidor Mosquitto
MQTT_PORT = 1883
MQTT_TOPIC_REED = "sensor/redswitch"

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

# Variable para almacenar el estado anterior del reed switch
estado_anterior = reed_switch.value()

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

        # Leer el estado actual del Reed Switch
        estado_actual = reed_switch.value()

        # Solo enviar mensaje si el estado cambió
        if estado_actual != estado_anterior:
            mensaje = "Abierto" if estado_actual == 1 else "Cerrado"
            client.publish(MQTT_TOPIC_REED, mensaje.encode())
            print(f"[INFO] Publicado en {MQTT_TOPIC_REED}: {mensaje}")

            # Actualizar el estado anterior
            estado_anterior = estado_actual

        time.sleep(0.1)  # Pequeña pausa para evitar rebotes

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
