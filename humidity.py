import Adafruit_DHT #pip3 install Adafruit-DHT

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4
DHT_READ_TIMEOUT = 4

def getparams():
    while True:
        result = {}
        humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
        
        if humidity is not None and temperature is not None:
            result["Temperature"] = round(temperature,1)
            result["Humidity"] = round(humidity,1)
            return result
        else:
            DHT_READ_TIMEOUT
            #result["temperature"] = 0
            #result["humidity"] = 0
            
        #return result
        