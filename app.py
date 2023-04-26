'''
    Import necessary packages
'''
from picamera import PiCamera
from datetime import datetime, timedelta
import os
from humidity import *
from userdefined import *
import time
import urllib.request
from sendEmail import *
from PIL import Image
import json
import requests
import base64
import logging

'''
    Load/initialize information about path
'''
path = "/home/sonya-cummings/DataCollector/storage/"
configData = readJson("/home/sonya-cummings/DataCollector/config.json")
rpidescription = "sonya_cummings"
rpidescriptionLocation = "sonya_cummings"

'''
    Logger to record error
'''
logging.basicConfig(filename='/home/sonya-cummings/DataCollector/error.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
logging.info(f"Error log for [{rpidescription}")

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
    
'''
    Takes image as an input and calculates the brightness, it is done to check if lights are turned on or off in a particular room.
'''
def brightness(image):
    # Open image using PIL
    img = Image.open(image).convert('L')
    # Calculate brightness
    hist = img.histogram()
    brightness = sum(i * hist[i] for i in range(256)) / (img.size[0] * img.size[1])
    return brightness

'''
    sends data to the webserver using an API
'''
def storeOnWebserver(data,url):
    data_str = json.dumps(data)

    # Send the JSON string to the API endpoint
    response = requests.post(url, json=data_str)

    # return the response
    return response.text


'''
    capture the image which will be converted into base64 form and sent to api on webserver which will save it into firebase and local database
'''
def storeImage():
    try:
        #initialize camera object
        camera = PiCamera()
        #use now datetime as name of the Image
        now = datetime.now()
        dt = now.strftime("%d-%m-%Y %H:%M:%S")
        name = dt+".jpg"
        #capture image using the name
        camera.capture(name)
        #send the image to brightness() to get the brightness value
        brightness_value = brightness(name)
        
        configData["current_brightness"] = brightness_value
        flag = writeJson("/home/sonya-cummings/DataCollector/config.json",configData)
        
        #convert the image to base64 form to be able to save in the structured database i.e database on webserver
        with open(name, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            
        encoded_string = encoded_string.decode("utf-8")
        #delete the image saved in the local directory
        os.remove(name)
        #close camera object
        camera.close()
        print("Image stored")
        return name.replace(".jpg",""),encoded_string
    except Exception as err:
        logging.error('storeImage: {}'.format(err))
        return "", ""
    
    
    
'''
    Store Humidity, Temperature, IP Address data
'''
    
def storeSensorReadings(docName,motion,encoded_string):
    #get humidity and temperature from humidity.py module
    data = getSensorReadings()  #Humidity and Temperature   
    #get location of where the RPI is installed from the API
    location = ""
    try:
        response = storeOnWebserver({"rpidescription":rpidescriptionLocation},'http://aspendb.uga.edu/rpi0/getlocation')
        response = json.loads(response)
        location = response["location"]
    except:
        logging.error('storeSensorReadings: {}'.format(err))
        location = ""
        
    '''  if temperature is in abnormal range, check again and if still abnormal send an email '''
    if data["Temperature"] < 18 or  data["Temperature"] > 30: 
        data = getSensorReadings()
        logging.info("Temperature {}".format(data["Temperature"]))
        if data["Temperature"] < 18 or  data["Temperature"] > 30: 
            sendStaus(rpidescriptionLocation,location, raspberryIP(), data["Temperature"]) 
    
    #store all the data into a dictionary 
    data["Motion"] = motion   #Currently set to None
    data["IPAddress"] = raspberryIP()   #IP address of the RPI
    data["ImgRef"] = docName #ImgRef
    data["brightness"] = configData["current_brightness"]   #store brightness
    data["rpi"] = rpidescription
    data["image"] = encoded_string
    data["location"]= location
    
    try:
        #send this data to webserver to store it in into local database using storeOnWebserver()
        storeOnWebserver(data,'http://aspendb.uga.edu/database/storedata')
        #send this data to webserver to store it in into firebase database using storeOnWebserver()
        storeOnWebserver(data,'http://aspendb.uga.edu/rpi0/storedata')
        print("KPI stored")
    except Exception as err:
        logging.error('storeSensorReadings: {}'.format(err))
    
        

motion = 0
#Infinite loop to keep this app running
while True:
    try:
        #Call storeImage() to get imageRef and encoded Image
        docName,encoded_string = storeImage()
        #Call storeSensorReadings() to save all info into firebase and database
        storeSensorReadings(docName.replace(path,""),motion,encoded_string)
        time.sleep(1800)
    except Exception as err:
        logging.error('{}'.format(err))
        pass
    

