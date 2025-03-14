from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# 📡 Configuración MQTT
MQTT_CLIENT_ID = "esp32_boton"
MQTT_BROKER = "192.168.31.135"
MQTT_PORT = 1883
MQTT_TOPIC_BOTON = "actuator/button"

# 📌 Configuración del botón
boton = Pin(4, Pin.IN, Pin.PULL_UP)  # Botón en GPIO 15 con pull-up interno

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

# 🔄 Bucle principal para leer el botón
while True:
    if boton.value() == 0:  # Si el botón se presiona
        print("🔘 Botón presionado (1)")
        client.publish(MQTT_TOPIC_BOTON, "1")  # Enviar estado 1
        time.sleep(0.2)  # Anti-rebote
    
        # Esperar a que el botón se suelte
        while boton.value() == 0:
            time.sleep(0.1)
        
        print("🔘 Botón soltado (0)")
        client.publish(MQTT_TOPIC_BOTON, "0")  # Enviar estado 0
        time.sleep(0.2)  # Pequeña espera para evitar múltiples lecturas
