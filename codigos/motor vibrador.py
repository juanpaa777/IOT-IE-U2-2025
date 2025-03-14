from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del motor de vibración
motor = Pin(26, Pin.OUT)  # GPIO26 controla el motor (IN)

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_motor_vibracion"
MQTT_BROKER = "192.168.221.135"  # Cambia por la IP de tu servidor Mosquitto
MQTT_PORT = 1883
MQTT_TOPIC_MOTOR = "actuator/vibracion"

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

        # Activar el motor de vibración
        motor.value(1)
        mensaje = "Motor activado"
        client.publish(MQTT_TOPIC_MOTOR, mensaje.encode())
        print(f"[INFO] Publicado en {MQTT_TOPIC_MOTOR}: {mensaje}")

        time.sleep(3)  # Vibrar durante 3 segundos

        # Apagar el motor de vibración
        motor.value(0)
        mensaje = "Motor desactivado"
        client.publish(MQTT_TOPIC_MOTOR, mensaje.encode())
        print(f"[INFO] Publicado en {MQTT_TOPIC_MOTOR}: {mensaje}")

        time.sleep(3)  # Esperar antes de repetir el ciclo

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
