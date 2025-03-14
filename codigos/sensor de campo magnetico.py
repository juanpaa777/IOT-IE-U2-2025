from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor de campo magnético
sensor_magnetico = ADC(Pin(34))  
sensor_magnetico.atten(ADC.ATTN_11DB)  

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_magnetico"
MQTT_BROKER = "192.168.36.135"
MQTT_PORT = 1883
MQTT_TOPIC_MAGNETIC = "sensor/campoMagnetico"

# Umbral de detección
UMBRAL_CAMPO_MAGNETICO = 2000

def conectar_wifi():
    """Conecta el ESP32 a la red WiFi."""
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    while not sta_if.isconnected():
        time.sleep(0.5)
    
    print("\n[INFO] WiFi Conectada!")

def conectar_mqtt():
    """Conecta a MQTT y maneja reconexiones."""
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        return client
    except Exception:
        print("[ERROR] No se pudo conectar a MQTT")
        return None

# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_mqtt()

estado_anterior = None  

while True:
    try:
        if not network.WLAN(network.STA_IF).isconnected():
            conectar_wifi()
            client = conectar_mqtt()

        if client is None:
            client = conectar_mqtt()
            time.sleep(5)
            continue

        estado_actual = sensor_magnetico.read() >= UMBRAL_CAMPO_MAGNETICO

        if estado_actual != estado_anterior:
            mensaje = "Ausente" if estado_actual else "Detectado"
            client.publish(MQTT_TOPIC_MAGNETIC, mensaje.encode())
            print(f"[INFO] Publicado: {mensaje}")

        estado_anterior = estado_actual  
        time.sleep(1)  

    except Exception:
        print("[ERROR] Error en el loop principal")
        client = None
