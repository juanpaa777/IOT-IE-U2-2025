from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# 📡 Configuración MQTT
MQTT_CLIENT_ID = "esp32_led_rgb"
MQTT_BROKER = "192.168.124.135"
MQTT_PORT = 1883
MQTT_TOPIC_RGB = "actuator/rgb"

# 🎨 Configuración del módulo LED RGB
pin_red = Pin(25, Pin.OUT)
pin_green = Pin(26, Pin.OUT)
pin_blue = Pin(27, Pin.OUT)

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

# 📌 Función para controlar el LED RGB
def controlar_led_rgb(color):
    """Enciende solo el color indicado: 'rojo', 'verde' o 'azul'"""
    pin_red.value(1 if color == "rojo" else 0)
    pin_green.value(1 if color == "verde" else 0)
    pin_blue.value(1 if color == "azul" else 0)
    print(f"🎨 LED encendido: {color}")
    client.publish(MQTT_TOPIC_RGB)  # Enviar confirmación a MQTT

# 📌 Función para manejar mensajes MQTT
def llegada_mensaje(topic, msg):
    color = msg.decode().strip().lower()  # Convertir mensaje a minúsculas sin espacios
    print(f"📩 Mensaje MQTT recibido: {color}")

    if color in ["rojo", "verde", "azul"]:
        controlar_led_rgb(color)
    else:
        print("⚠️ Color no válido, usa: rojo, verde o azul.")

# 📌 Función para conectarse a MQTT
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(llegada_mensaje)
    try:
        client.connect()
        client.subscribe(MQTT_TOPIC_RGB)
        print(f"✅ Conectado a MQTT y suscrito a {MQTT_TOPIC_RGB}")
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
        client.check_msg()  # Revisar mensajes MQTT
    except Exception as e:
        print(f"⚠️ Error en la recepción MQTT: {e}")
        time.sleep(2)  # Esperar antes de reintentar
