from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración de pines
led_rojo_pin = Pin(14, Pin.OUT)  # GPIO14 para el LED rojo
led_verde_pin = Pin(12, Pin.OUT)  # GPIO12 para el LED verde

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_bicolor"
MQTT_BROKER = "192.168.31.135"
MQTT_PORT = 1883
MQTT_TOPIC_ACTUATOR = "actuator/led2"

# Variables de control
errores_conexion = 0

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
    global errores_conexion
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"[INFO] Conectado a MQTT en {MQTT_BROKER}")
        errores_conexion = 0
        return client
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a MQTT: {e}")
        errores_conexion += 1
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

        # Ejemplo: Encender el LED rojo y apagar el verde
        led_rojo_pin.value(1)  # Enciende el LED rojo
        led_verde_pin.value(0)  # Apaga el LED verde
        mensaje = "Rojo"  # Enviar mensaje "Rojo" al MQTT

        # Publicar en MQTT
        client.publish(MQTT_TOPIC_ACTUATOR, mensaje)
        print(f"[INFO] Publicado en {MQTT_TOPIC_ACTUATOR}: {mensaje}")

        # Esperar 2 segundos
        time.sleep(2)

        # Ejemplo: Encender el LED verde y apagar el rojo
        led_rojo_pin.value(0)  # Apaga el LED rojo
        led_verde_pin.value(1)  # Enciende el LED verde
        mensaje = "Verde"  # Enviar mensaje "Verde" al MQTT

        # Publicar en MQTT
        client.publish(MQTT_TOPIC_ACTUATOR, mensaje)
        print(f"[INFO] Publicado en {MQTT_TOPIC_ACTUATOR}: {mensaje}")

        # Esperar 2 segundos
        time.sleep(2)

        # Si hay demasiados errores, reiniciar conexiones
        if errores_conexion >= 10:
            print("[ERROR] Demasiados errores, reiniciando conexiones...")
            conectar_wifi()
            client = conectar_mqtt()
            errores_conexion = 0

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None

    time.sleep(1)  # Esperar 1 segundo antes de la siguiente iteración