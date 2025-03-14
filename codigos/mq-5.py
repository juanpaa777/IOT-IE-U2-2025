from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración de pines
sensor_mq5 = ADC(Pin(34))  # Sensor MQ-5 en GPIO34 (entrada analógica)
sensor_mq5.atten(ADC.ATTN_11DB)  # Ajusta la atenuación para leer hasta 3.3V
led_alerta = Pin(14, Pin.OUT)  # LED de alerta en GPIO14

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_gas"
MQTT_BROKER = "192.168.36.135"
MQTT_PORT = 1883
MQTT_TOPIC_GAS = "sensor/mq5"

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

        # Leer el valor del sensor MQ-5
        valor_gas = sensor_mq5.read()
        print(f"Valor del sensor MQ-5: {valor_gas}")

        # Activar LED si el valor supera un umbral (ajustable según necesidad)
        umbral_alerta = 1900  # Ajusta según la calibración del sensor
        if valor_gas > umbral_alerta:
            led_alerta.value(1)
            mensaje = f"Alerta! Nivel de gas alto: {valor_gas}"
        else:
            led_alerta.value(0)
            mensaje = f"Nivel de gas normal: {valor_gas}"

        # Publicar el valor del sensor en MQTT
        client.publish(MQTT_TOPIC_GAS, mensaje.encode())
        print(f"[INFO] Publicado en {MQTT_TOPIC_GAS}: {mensaje}")

        time.sleep(2)  # Esperar antes de la siguiente lectura

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None

    time.sleep(1)
