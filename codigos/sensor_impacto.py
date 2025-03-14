from machine import Pin, reset
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# 📡 Configuración MQTT
MQTT_CLIENT_ID = "esp32_impact_sensor"
MQTT_BROKER = "192.168.221.135"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/obstaculos"

# 🔧 Configuración del sensor KY-031 (Sensor de impacto/vibración)
sensor_impacto = Pin(15, Pin.IN)  # Conectado al pin 15 del ESP32

# 📡 Función para conectar a WiFi
def conectar_wifi():
    print("[INFO] Conectando a WiFi...")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    tiempo_max_espera = 10  # Tiempo máximo de espera (10 segundos)
    while not sta_if.isconnected() and tiempo_max_espera > 0:
        print(".", end="")
        time.sleep(1)
        tiempo_max_espera -= 1

    if sta_if.isconnected():
        print("\n✅ WiFi Conectada!")
        print(f"[INFO] Dirección IP: {sta_if.ifconfig()[0]}")
    else:
        print("\n❌ No se pudo conectar a WiFi, reiniciando ESP32...")
        reset()  # Reinicia el ESP32 si no hay WiFi

# 📡 Función para conectar a MQTT con manejo de errores
def conectar_mqtt():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"✅ Conectado a MQTT {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"❌ Error al conectar a MQTT: {e}, reintentando en 5 segundos...")
        time.sleep(5)
        return None  # Devolver None si falla la conexión

# 🔄 Función para leer el sensor de impacto (con filtrado)
def leer_sensor():
    valor = sensor_impacto.value()  # Lee el valor digital del sensor
    return valor  # Retorna 0 si hay impacto, 1 si no

# 📡 Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_mqtt()

ultimo_valor = None

# 🔥 Loop principal: Monitoreo y envío de datos a MQTT
while True:
    try:
        if not client:
            client = conectar_mqtt()
            if not client:
                time.sleep(5)
                continue
        
        # 🔍 Leer el estado del sensor de impacto
        impacto_detectado = leer_sensor()

        # 📡 Solo enviar mensaje si el estado cambia
        if impacto_detectado != ultimo_valor:
            mensaje = str(impacto_detectado)
            
            if impacto_detectado == 1:
                print("⚡ ¡Obstactulo Detectado!")
            else:
                print("✅ No hay obstaculo")
            
            print(f"📡 Enviando MQTT: {mensaje}")
            client.publish(MQTT_TOPIC, mensaje)
            
            ultimo_valor = impacto_detectado  # Actualizar el último estado

        client.check_msg()  # Revisión de mensajes entrantes de MQTT
        
    except Exception as e:
        print(f"❌ Error en el loop principal: {e}")
        client = None  # Resetear conexión si hay error
        time.sleep(5)  # Esperar antes de reintentar

    time.sleep(0.5)  # Espera entre lecturas
