from machine import Pin, reset
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# 📡 Configuración MQTT
MQTT_CLIENT_ID = "esp32"
MQTT_BROKER = "192.168.31.135"
MQTT_PORT = 1883
MQTT_TOPIC = "actuator/laser"

# Actuador KY-008 (Láser) conectado al GPIO 14
laser = Pin(14, Pin.OUT)

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
        print("\n WiFi Conectada!")
    else:
        print("\n No se pudo conectar a WiFi. Reiniciando...")
        reset()  # Reiniciar el ESP32 si no se conecta a WiFi

# 📌 Función para manejar mensajes MQTT
def llegada_mensaje(topic, msg):
    pass

# 📌 Función para conectarse a MQTT
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    client.set_callback(llegada_mensaje)  # Asignar la función para recibir mensajes
    try:
        client.connect()
        client.subscribe(MQTT_TOPIC)  # Suscribirse al tópico del láser
        print(f"Conectado a MQTT {MQTT_BROKER} y suscrito a {MQTT_TOPIC}")
        return client
    except Exception as e:
        print(f"Error al conectar a MQTT: {e}")
        reset()  # Reiniciar el ESP32 si no se conecta a MQTT

# 📡 Conectar a WiFi
conectar_wifi()

# 📡 Conectar a MQTT
client = conectar_mqtt()

while True:
    try:
        # Invertir el estado actual del láser
        valor = not laser.value()
        laser.value(valor)  # Aplicar el nuevo estado

        # Publicar el nuevo estado en MQTT
        mensaje = str(int(valor))  # Convertir el valor booleano a "1" o "0"
        print(f"Publicando: {mensaje}")
        client.publish(MQTT_TOPIC, mensaje)

        # Mostrar en consola el estado del láser
        if valor == 0:
            print("Láser APAGADO")
        else:
            print("Láser ENCENDIDO")

        # Revisar si hay mensajes MQTT entrantes
        client.check_msg()

    except Exception as e:
        print(f"Error en el bucle principal: {e}")

    time.sleep(3)  # Leer cada 3 segundos
