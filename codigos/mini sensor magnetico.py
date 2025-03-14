from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del mini interruptor magnético
sensor_magnetico = Pin(34, Pin.IN, Pin.PULL_UP)  # GPIO34 con pull-up interno

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_magnetico"
MQTT_BROKER = "192.168.36.135"
MQTT_PORT = 1883
MQTT_TOPIC_MAG = "sensor/MiniMagnetico"

# Variable para controlar la publicación
estado_anterior = sensor_magnetico.value()

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

def detectar_cambio(pin):
    """Manejador de interrupción cuando cambia el estado del sensor magnético."""
    global estado_anterior
    estado_actual = pin.value()

    if estado_actual != estado_anterior:  # Solo envía si hay un cambio
        mensaje = "Puerta ABIERTA" if estado_actual == 0 else "Puerta CERRADA"
        client.publish(MQTT_TOPIC_MAG, mensaje.encode())
        print(f"[INFO] Publicado en {MQTT_TOPIC_MAG}: {mensaje}")
        estado_anterior = estado_actual  # Actualizar estado

# Configurar interrupción en sensor magnético
sensor_magnetico.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=detectar_cambio)

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

        time.sleep(1)  # Pequeña pausa para evitar sobrecarga

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None