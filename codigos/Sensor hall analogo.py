from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor de efecto Hall
sensor_hall = ADC(Pin(34))  # GPIO34 como entrada analógica
sensor_hall.atten(ADC.ATTN_11DB)  # Configura el rango de voltaje (hasta 3.3V)

# Umbral para detección de imán (ajústalo según pruebas)
UMBRAL = 2000  

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_hall"
MQTT_BROKER = "192.168.221.135"  # Cambia por la IP de tu servidor Mosquitto
MQTT_PORT = 1883
MQTT_TOPIC_SENSOR = "sensor/hallAnalogo"

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

        # Leer el sensor de efecto Hall
        hall_value = sensor_hall.read()

        # Determinar si hay un imán cerca (1) o no (0)
        deteccion = 1 if hall_value < UMBRAL else 0
        print(f"[INFO] Imán detectado: {deteccion}")

        # Publicar el estado en MQTT
        client.publish(MQTT_TOPIC_SENSOR, str(deteccion).encode())

        time.sleep(2)  # Esperar antes de la siguiente lectura

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
