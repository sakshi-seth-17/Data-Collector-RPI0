from picamera import PiCamera
from datetime import datetime, timedelta
import os
from humidity import *
from userdefined import *
import time
#from dht import *
import urllib.request
from sendEmail import *
from PIL import Image
import json
import requests
import base64



path = "/home/sonya-cummings/DataCollector/storage/"
configData = readJson("/home/sonya-cummings/DataCollector/config.json")
rpidescription = "sonya_cummings"
rpidescriptionLocation = "sonya-cummings"


'''
    Get IP address of the Raspberry Pi
'''
def raspberryIP():
    routes = json.loads(os.popen("ip -j -4 route").read())
    for r in routes:
        if r.get("dev") == "wlan0" and r.get("prefsrc"):
            ip = r["prefsrc"]
        break
    return ip
    
def brightness(image):
    # Open image using PIL
    img = Image.open(image).convert('L')
    # Calculate brightness
    hist = img.histogram()
    brightness = sum(i * hist[i] for i in range(256)) / (img.size[0] * img.size[1])
    return brightness


def storeOnWebserver(data,url):
    data_str = json.dumps(data)

    # Send the JSON string to the API endpoint
    response = requests.post(url, json=data_str)

    # Print the response
    #print(response.text)
    return response.text


'''
    Save image to firebase storage
'''


def storeImage():
    try:
        
        camera = PiCamera()
        now = datetime.now()
        dt = now.strftime("%d-%m-%Y %H:%M:%S")
        name = dt+".jpg"
        camera.capture(name)
        
        brightness_value = brightness(name)
        configData["current_brightness"] = brightness_value
        flag = writeJson("/home/sonya-cummings/DataCollector/config.json",configData)
        
        with open(name, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            
        encoded_string = encoded_string.decode("utf-8")
        os.remove(name)
        camera.close()
        print("Image stored")
        return name.replace(".jpg",""),encoded_string
    except Exception as err:
        print("Error: ",err)
        return "", ""
    
    
    
'''
    Store Humidity, Temperature, IP Address and Motion data in firebase database
'''
    
def storeKPI(docName,motion,encoded_string):
    data = getparams()  #Humidity and Temperature   
    
    location = ""
    try:
        response = storeOnWebserver({"rpidescription":rpidescriptionLocation},'http://aspendb.uga.edu/rpi0/getlocation')
        response = json.loads(response)
        location = response["location"]
    except:
        location = ""
    '''  if temperature is in abnormal range, check again and if still abnormal send an email '''
    if data["Temperature"] < 18 or  data["Temperature"] > 30: 
        data = getparams()
        if data["Temperature"] < 18 or  data["Temperature"] > 30: 
            sendStaus(rpidescriptionLocation,location, raspberryIP(), data["Temperature"]) 
    
    data["Motion"] = motion   #Currently set to None
    data["IPAddress"] = raspberryIP()   #IP address of the RPI
    #data["Thermal"] = str(getThermal()) #Thermal matrix
    data["ImgRef"] = docName #ImgRef
    data["brightness"] = configData["current_brightness"]   #store brightness
    data["rpi"] = rpidescription
    data["image"] = encoded_string
    data["location"]= location
    
    storeOnWebserver(data,'http://aspendb.uga.edu/firebase/getdata')

    storeOnWebserver(data,'http://aspendb.uga.edu/rpi0/storedata')
    print("KPI stored")
        

motion = 0
while True:
    docName,encoded_string = storeImage()
    storeKPI(docName.replace(path,""),motion,encoded_string)
    time.sleep(1800)
    #time.sleep(10)
    

