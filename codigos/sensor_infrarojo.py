from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración de pines
sensor_ir = Pin(15, Pin.IN)  # Sensor IR-08H en GPIO15
led_alerta = Pin(14, Pin.OUT)  # LED de alerta en GPIO14

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_ir"
MQTT_BROKER = "192.168.36.135"  # Cambia esto si es necesario
MQTT_PORT = 1883
MQTT_TOPIC_ACTUATOR = "sensor/infrarrojo"

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
estado_anterior = 1  # Asumimos que inicialmente no hay objeto (1)

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
        estado_actual = sensor_ir.value()

        # Comprobar si el estado del sensor ha cambiado
        if estado_actual != estado_anterior:
            if estado_actual == 0:  # Si se detecta un objeto
                print("[INFO] Objeto detectado a 40 cm o menos")
                led_alerta.value(1)  # Enciende LED
                mensaje = "Objeto detectado"
            else:  # Si no hay objeto
                print("[INFO] No hay objeto cerca")
                led_alerta.value(0)  # Apaga LED
                mensaje = "No hay objeto"

            # Publicar estado en MQTT
            client.publish(MQTT_TOPIC_ACTUATOR, mensaje.encode())
            print(f"[INFO] Publicado en {MQTT_TOPIC_ACTUATOR}: {mensaje}")

            # Actualizar el estado anterior
            estado_anterior = estado_actual

        time.sleep(0.2)  # Pequeña pausa para evitar envíos rápidos

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None

    time.sleep(1)  # Esperar antes de la siguiente iteración
