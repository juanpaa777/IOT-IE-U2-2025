from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# 📡 Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_temp"
MQTT_BROKER = "192.168.31.135"
MQTT_PORT = 1883
MQTT_TOPIC_TEMP = "sensor/temperaturadi"  # Tema para la temperatura

# 📌 Configuración del sensor de temperatura
pin_analog = ADC(Pin(34))  # Pin analógico AO
pin_digital = Pin(23, Pin.IN)  # Pin digital DO

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

# 📌 Función para leer el sensor de temperatura
def leer_sensor():
    # Leer el valor analógico
    valor_analogico = pin_analog.read()
    # Convertir el valor a temperatura (ajusta según la especificación del sensor)
    temperatura = (valor_analogico / 4095) * 100  # Ejemplo de conversión
    print(f"🌡️ Temperatura: {temperatura:.2f}°C")
    client.publish(MQTT_TOPIC_TEMP, f"{temperatura:.2f}")  # Publicar datos en MQTT

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
while True:
    try:
        leer_sensor()  # Leer el sensor de temperatura
        time.sleep(5)  # Esperar 5 segundos antes de la siguiente lectura
    except Exception as e:
        print(f"⚠️ Error en la lectura del sensor: {e}")
        time.sleep(2)  # Esperar antes de reintentar