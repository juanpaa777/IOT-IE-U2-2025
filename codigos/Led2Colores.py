from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# 📡 Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_bicolor"
MQTT_BROKER = "192.168.31.135"
MQTT_PORT = 1883
MQTT_TOPIC_SENSOR = "actuator/led2"

# 📌 Configuración del sensor
sensor = Pin(15, Pin.IN)  # Sensor en GPIO 15

# 📌 Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    tiempo_max_espera = 10
    while not sta_if.isconnected() and tiempo_max_espera > 0:
        print(".", end="")
        time.sleep(1)
        tiempo_max_espera -= 1

    if sta_if.isconnected():
        print("\n✅ WiFi Conectada!")
    else:
        print("\n⚠️ No se pudo conectar a WiFi")
        machine.reset()

# 📌 Función para conectarse a MQTT
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    try:
        client.connect()
        print(f"✅ Conectado a MQTT")
        return client
    except Exception as e:
        print(f"⚠️ Error al conectar a MQTT: {e}")
        machine.reset()

# 🔗 Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_mqtt()

# 🔄 Bucle principal
estado_anterior = sensor.value()  # Guardamos el primer estado
while True:
    estado_actual = sensor.value()  # Leer el estado del sensor
    if estado_actual != estado_anterior:  # Solo enviar si cambia el estado
        print(f"🔘 Sensor: {estado_actual}")  # Mostrar en consola
        client.publish(MQTT_TOPIC_SENSOR, str(estado_actual))  # Enviar estado a MQTT
        estado_anterior = estado_actual  # Actualizar el estado anterior
    time.sleep(0.2)  # Pequeña pausa para evitar spam de datos
