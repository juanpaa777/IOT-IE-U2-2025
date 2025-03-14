from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración del sensor MQ-2
sensor_ao = ADC(Pin(34))  # MQ-2 salida analógica en GPIO34
sensor_ao.atten(ADC.ATTN_11DB)  # Lectura hasta 3.3V
sensor_do = Pin(26, Pin.IN)  # MQ-2 salida digital en GPIO26
led_alerta = Pin(14, Pin.OUT)  # LED en GPIO14

# Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_sensor_mq2"
MQTT_BROKER = "192.168.153.135"  # Cambia por la IP de tu Mosquitto
MQTT_PORT = 1883
MQTT_TOPIC_AO = "sensor/mq2Q"


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

        # Leer el valor analógico del sensor MQ-2 (AO)
        valor_analogico = sensor_ao.read()
        # Leer la salida digital del sensor MQ-2 (DO)
        valor_digital = sensor_do.value()

        print(f"Valor AO (analógico): {valor_analogico}")


        # Definir umbral de alerta
        umbral_alerta = 2000  # Aumentamos el umbral a 2000 para evitar falsos positivos

        if valor_digital == 1:
            print("")
            led_alerta.value(1)
            mensaje_do = ""
        else:
            mensaje_do = ""
            led_alerta.value(0)

        if valor_analogico > umbral_alerta:
            print("[ALERTA] AO superó el umbral")
            mensaje_ao = f"¡ALERTA! Nivel alto de gas: {valor_analogico}"
        else:
            mensaje_ao = f"Nivel de gas normal: {valor_analogico}"

        # Publicar valores en MQTT
        client.publish(MQTT_TOPIC_AO, mensaje_ao.encode())
       

        print(f"[INFO] Publicado en {MQTT_TOPIC_AO}: {mensaje_ao}")
        

        time.sleep(1)  # Esperar antes de la siguiente lectura

    except Exception as e:
        print(f"[ERROR] Error en el loop principal: {e}")
        client = None

    time.sleep(1)
