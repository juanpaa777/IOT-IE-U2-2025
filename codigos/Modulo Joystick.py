from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Pines del joystick
VRX = ADC(Pin(34))  # Eje X
VRY = ADC(Pin(35))  # Eje Y

VRX.atten(ADC.ATTN_11DB)  # Rango 0 - 3.3V
VRY.atten(ADC.ATTN_11DB)  # Rango 0 - 3.3V

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_joystick"
MQTT_BROKER = "192.168.41.135"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/joystick"

# Umbrales para detección de movimiento
UMBRAL_MIN = 1500  # Límite para Izquierda/Abajo
UMBRAL_MAX = 2500  # Límite para Derecha/Arriba
UMBRAL_CENTRO = 2048  # Valor medio del joystick en reposo

def conectar_wifi():
    """Conecta el ESP32 a WiFi."""
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

# Estado previo para evitar publicaciones repetitivas
ultimo_movimiento = ""

# Bucle principal
while True:
    try:
        # Verificar conexión WiFi y MQTT
        if not network.WLAN(network.STA_IF).isconnected():
            print("[ERROR] WiFi desconectado, reconectando...")
            conectar_wifi()
            client = conectar_mqtt()

        if client is None:
            print("[ERROR] MQTT desconectado, reconectando...")
            client = conectar_mqtt()
            time.sleep(5)
            continue

        # Leer valores del joystick
        x = VRX.read()
        y = VRY.read()

        # Determinar dirección del movimiento
        if x < UMBRAL_MIN:
            movimiento = "Izquierda"
        elif x > UMBRAL_MAX:
            movimiento = "Derecha"
        elif y < UMBRAL_MIN:
            movimiento = "Abajo"
        elif y > UMBRAL_MAX:
            movimiento = "Arriba"
        else:
            movimiento = "Centrado"

        # Publicar solo si hay un cambio de movimiento
        if movimiento != ultimo_movimiento:
            client.publish(MQTT_TOPIC, movimiento.encode())
            print(f"[INFO] Publicado en {MQTT_TOPIC}: {movimiento}")
            ultimo_movimiento = movimiento  # Actualizar estado

        time.sleep(0.5)  # Pequeña pausa

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None
