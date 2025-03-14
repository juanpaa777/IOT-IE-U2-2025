from machine import Pin, reset
import time
import network
from umqtt.simple import MQTTClient

# 📡 Configuración WiFi
WIFI_SSID = "Galaxy S22 Ultra"
WIFI_PASSWORD = "Jp159000"

# 📡 Configuración MQTT
MQTT_CLIENT_ID = "esp32"
MQTT_BROKER = "192.168.41.135"
MQTT_PORT = 1883
MQTT_TOPIC = "sensor/flama"

# 🔥 Configuración del sensor de flama
sensor_flama = Pin(15, Pin.IN)  # Asegurar que el sensor está realmente en este GPIO

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

# 🔄 Función para leer el sensor de flama con filtrado (reduce ruido)
def leer_sensor():
    muestras = 5  # Se toman 5 muestras
    detecciones = sum(sensor_flama.value() for _ in range(muestras))
    return 1 if detecciones > (muestras // 2) else 0  # Se usa la mayoría de votos

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
        
        # 🔍 Leer el estado del sensor con filtrado
        flama_detectada = leer_sensor()

        # 📡 Solo enviar mensaje si el estado cambia
        if flama_detectada != ultimo_valor:
            mensaje = str(flama_detectada)
            
            if flama_detectada == 1:
                print("🔥 ¡Fuego Detectado!")
            else:
                print("✅ No hay fuego")
            
            print(f"📡 Enviando MQTT: {mensaje}")
            client.publish(MQTT_TOPIC, mensaje)
            
            ultimo_valor = flama_detectada  # Actualizar el último estado

        client.check_msg()  # Revisión de mensajes entrantes de MQTT
        
    except Exception as e:
        print(f"❌ Error en el loop principal: {e}")
        client = None  # Resetear conexión si hay error
        time.sleep(5)  # Esperar antes de reintentar

    time.sleep(2)  # Espera entre lecturas
