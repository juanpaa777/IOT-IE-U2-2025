from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración de pines
sensor_inclinacion = Pin(15, Pin.IN)  # Sensor SW-520D en GPIO15
led_alerta = Pin(14, Pin.OUT)  # LED de alerta en GPIO14

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_inclinacion"
MQTT_BROKER = "192.168.31.135"
MQTT_PORT = 1883
MQTT_TOPIC_ACTUATOR = "sensor/inclinacion2"

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

# Estado inicial del sensor
estado_anterior = sensor_inclinacion.value()

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

        # Leer el estado del sensor
        estado_actual = sensor_inclinacion.value()

        if estado_actual != estado_anterior:  # Solo enviar si cambia el estado
            if estado_actual == 1:
                print("Sensor detecta inclinación!")
                led_alerta.value(1)
                mensaje = "Inclinación detectada"
            else:
                print("Sensor estable")
                led_alerta.value(0)
                mensaje = "Sin inclinación"

            # Publicar estado en MQTT
            client.publish(MQTT_TOPIC_ACTUATOR, mensaje.encode())
            print(f"[INFO] Publicado en {MQTT_TOPIC_ACTUATOR}: {mensaje}")
            estado_anterior = estado_actual  # Actualizar estado

        time.sleep(0.2)  # Pequeña pausa para evitar envíos rápidos

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None

    time.sleep(1)  # Esperar antes de la siguiente iteración
