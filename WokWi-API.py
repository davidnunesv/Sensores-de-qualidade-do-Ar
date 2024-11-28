import network
import urequests
import time
from umqtt.simple import MQTTClient

# Configuração Wi-Fi (rede do Wokwi)
SSID = "Wokwi-GUEST"
PASSWORD = ""

# API Keys e URLs
OPEN_WEATHER_MAP_API_KEY = "API KEY"
cidadeURL = "Sao%20Paulo"
cidadePrint = "São Paulo"
estado = "Sao%20Paulo"
paisOpenW = "BR"
paisAirQ = "Brazil"
IQAIR_API_KEY = "API KEY"
AIR_QUALITY_URL = f"https://api.airvisual.com/v2/city?city={cidadeURL}&state={estado}&country={paisAirQ}&key={IQAIR_API_KEY}"

#Variaveis globais
current_temp = None
current_air_quality = None
current_humidity = None

# Configurações do MQTT
BROKER = "broker.hivemq.com"  # Broker público
PORT = 1883
CLIENT_ID = "WokwiSensorClient"
TOPIC_TEMP = "home/sensor/temperature"
TOPIC_HUM = "home/sensor/humidity"
TOPIC_AIR_QUALITY = "home/sensor/air_quality"

def send_data_mqtt(client):
    if current_temp is not None:
        client.publish(TOPIC_TEMP, str(current_temp))
        print(f"Temperatura enviada: {current_temp}")
    if current_humidity is not None:
        client.publish(TOPIC_HUM, str(current_humidity))
        print(f"Umidade enviada: {current_humidity}")
    if current_air_quality is not None:
        client.publish(TOPIC_AIR_QUALITY, current_air_quality)
        print(f"Qualidade do ar enviada: {current_air_quality}")


# Função para conectar ao Wi-Fi do Wokwi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Conectando ao Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(1)
    print("Conectado ao Wi-Fi:", wlan.ifconfig())

# Função para obter a temperatura da API OpenWeatherMap
def get_temperatura_e_umidade():
    global current_temp, current_humidity
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={cidadeURL},{paisOpenW}&APPID={OPEN_WEATHER_MAP_API_KEY}&units=metric"
        response = urequests.get(url)
        if response.status_code == 200:
            data = response.json()
            current_temp = data['main']['temp']
            current_humidity = data['main']['humidity']
            print(f"Temperatura em {cidadePrint}: {current_temp}°C \nUmidade: {current_humidity}")
        else:
            print(f"Erro ao acessar a API OpenWeatherMap, código de status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao obter dados de temperatura: {e}")

# Função para obter a qualidade do ar da API IQAir
def get_qualidade_ar():
    global current_air_quality
    try:
        response = urequests.get(AIR_QUALITY_URL)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'current' in data['data'] and 'pollution' in data['data']['current']:
                aqi_us = data['data']['current']['pollution']['aqius']
                print(f"AQI para os EUA: {aqi_us}")
                if aqi_us <= 50:
                    current_air_quality = "Boa"
                elif aqi_us <= 100:
                    current_air_quality = "Moderada"
                elif aqi_us <= 150:
                    current_air_quality = "Não saudável para grupos sensíveis"
                elif aqi_us <= 200:
                    current_air_quality = "Não saudável"
                elif aqi_us <= 300:
                    current_air_quality = "Muito não saudável"
                else:
                    current_air_quality = "Perigoso"
                print(f"Qualidade do Ar: {current_air_quality}")
            else:
                print("Dados de poluição não encontrados na resposta da API.")
        else:
            print(f"Erro ao acessar a API IQAir, código de status: {response.status_code}")
    except Exception as e:
        print(f"Erro ao obter dados de qualidade do ar: {e}")


def send_data_mqtt(client):
    if current_temp is not None:
        client.publish(TOPIC_TEMP, str(current_temp))
        print(f"Temperatura enviada: {current_temp}")
    if current_humidity is not None:
        client.publish(TOPIC_HUM, str(current_humidity))
        print(f"Umidade enviada: {current_humidity}")
    if current_air_quality is not None:
        client.publish(TOPIC_AIR_QUALITY, current_air_quality)
        print(f"Qualidade do ar enviada: {current_air_quality}")
        


# Função principal
def main():
    connect_wifi()

    # Configurar o cliente MQTT
    client = MQTTClient(CLIENT_ID, BROKER, port=PORT)
    client.connect()
    print("Conectado ao Broker MQTT!")

    while True:
        print("\nConsultando dados...")
        print("Dados métricos:")
        get_temperatura_e_umidade()  # Obter temperatura
        get_qualidade_ar()  # Obter qualidade do ar

        send_data_mqtt(client)
        time.sleep(10)  # Aguarda 10 segundos antes de nova consulta


# Inicia a função principal
main()
