from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor de línea
sensor_linea = Pin(34, Pin.IN)  # GPIO34 como entrada digital

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_linea"
MQTT_BROKER = "192.168.41.135"  # Cambia por la IP de tu servidor Mosquitto
MQTT_PORT = 1883
MQTT_TOPIC_LINEA = "sensor/linea"

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

# Variables para evitar publicaciones repetidas
detectado = False  # Indica si la línea fue detectada anteriormente

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

        # Leer el valor del sensor de línea
        estado_actual = sensor_linea.value()  # 1 = No línea (blanco), 0 = Línea (negro)

        if estado_actual == 0 and not detectado:
            # Detectó línea negra por primera vez
            mensaje = "Línea detectada"
            client.publish(MQTT_TOPIC_LINEA, mensaje.encode())
            print(f"[INFO] Publicado en {MQTT_TOPIC_LINEA}: {mensaje}")
            detectado = True  # Marcar como detectado

        elif estado_actual == 1 and detectado:
            # Salió de la línea negra, publica "Sin línea"
            mensaje = "Sin línea"
            client.publish(MQTT_TOPIC_LINEA, mensaje.encode())
            print(f"[INFO] Publicado en {MQTT_TOPIC_LINEA}: {mensaje}")
            detectado = False  # Reiniciar estado

        # Mantener MQTT activo
        client.check_msg()

        time.sleep(0.1)  # Pequeña pausa

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
