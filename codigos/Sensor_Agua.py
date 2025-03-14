from machine import Pin, reset
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# 📡 Configuración MQTT
MQTT_CLIENT_ID = "esp32_water_sensor"
MQTT_BROKER = "192.168.31.135"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/agua"

# 🌊 Sensor de agua conectado al GPIO 14 (lectura digital)
water_sensor_pin = Pin(4, Pin.IN, Pin.PULL_DOWN)

def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    tiempo_max_espera = 10  # Espera máxima de 10 segundos
    while not sta_if.isconnected() and tiempo_max_espera > 0:
        print(".", end="")
        time.sleep(1)
        tiempo_max_espera -= 1

    if sta_if.isconnected():
        print("\n✅ WiFi Conectada!")
    else:
        print("\n❌ No se pudo conectar a WiFi. Reiniciando...")
        reset()  # Reiniciar el ESP32 si no se conecta a WiFi

# 📌 Función para manejar mensajes MQTT (vacía, no imprime nada)
def llegada_mensaje(topic, msg):
    pass  # No hacer nada con los mensajes recibidos

# 📌 Función para conectarse a MQTT
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(llegada_mensaje)  # Asignar la función para recibir mensajes (sin mostrar)
    try:
        client.connect()
        client.subscribe(MQTT_TOPIC)  # Suscribirse al tópico del sensor de agua
        print(f"✅ Conectado a MQTT {MQTT_BROKER} y suscrito a {MQTT_TOPIC}")
        return client
    except Exception as e:
        print(f"❌ Error al conectar a MQTT: {e}")
        reset()  # Reiniciar el ESP32 si no se conecta a MQTT

# 📡 Conectar a WiFi
conectar_wifi()

# 📡 Conectar a MQTT
client = conectar_mqtt()

ultimo_valor = None
while True:
    try:
        # Leer el valor del sensor de agua
        valor_agua = water_sensor_pin.value()

        # Solo publica si el valor ha cambiado
        if valor_agua != ultimo_valor:
            mensaje = str(valor_agua)
            print(f"📤 Publicando valor de agua: {mensaje}")
            client.publish(MQTT_TOPIC, mensaje)
            ultimo_valor = valor_agua  # Actualizar el último valor

        # Revisar si hay mensajes en el tópico MQTT
        client.check_msg()

    except Exception as e:
        print(f"⚠️ Error en la lectura del sensor: {e}")

    time.sleep(1)  # Leer cada 1 segundo
