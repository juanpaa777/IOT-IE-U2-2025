from machine import Pin
import time
import network
from umqtt.simple import MQTTClient
import onewire, ds18x20

# Configuración de pines
PIN_DS18B20 = 4  # GPIO donde está conectado el sensor
sensor = ds18x20.DS18X20(onewire.OneWire(Pin(PIN_DS18B20)))

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_temp"
MQTT_BROKER = "192.168.36.135"
MQTT_PORT = 1883
MQTT_TOPIC_TEMP = "sensor/temp18b20"

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

# Detectar el sensor DS18B20
roms = sensor.scan()
if not roms:
    print("[ERROR] No se detectó el sensor DS18B20.")
    while True:
        time.sleep(1)

print("[INFO] Sensor DS18B20 detectado.")

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

        # Leer temperatura del DS18B20
        sensor.convert_temp()
        time.sleep(1)  # Esperar conversión
        temperatura = sensor.read_temp(roms[0])
        print(f"Temperatura: {temperatura:.2f}°C")

        # Publicar en MQTT
        mensaje = f"Temperatura: {temperatura:.2f}°C"
        client.publish(MQTT_TOPIC_TEMP, mensaje.encode())
        print(f"[INFO] Publicado en {MQTT_TOPIC_TEMP}: {mensaje}")

        time.sleep(2)  # Esperar antes de la siguiente lectura

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None

    time.sleep(1)
