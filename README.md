                                                   # Data-Collector-RPI0
                                                            
This application is built using Python to store observations from the sensor like temperature, humidity, thermal, brightness, and images into firebase as well as the local database tables via APIs hosted on webserver. RPI0 does not support firebase module hence we created an API to store these information.

---

### Necessary configuration to be set on the RPI before starting to use it
- Issue the command ifconfig on cmd to get the IP address of the RPI
- To SSH into the RPI enable the SSH config: Preferences -> Raspberry Pi Configuration -> Interfaces -> SSH: enable
- To setup camera module in RPI: 1) Refer to installation instruction from https://elinux.org/RPi-Cam-Web-Interface to setup the camera. 2) To check if Camera is working fine, browse the IPAddress of the server. 3) To be able to use the camera in python script disable the http option by a) sudo nano /etc/rc.local b) o	remove #START RASPIMJPEG SECTION c) restart RPI.

### Firebase and Local Database preparation
- Add the entry of the rpidescription in the Firebase Database -> RPI-details -> add new instance of the RPI and add field parameters with required information. Example: IPAddress: 172.21.123.141
         collection: blackbox
         location: growth room #1 (Middle)
         password: gafst1234
         type: rpi0
         username: wendy-king
- Create another entry of the RPI in the Firebase Database -> CollectionName(same as used in the above data)
- Create another entry of the RPI in the Storage to store images
- Create a database table in Data-Store.db on webserver for the respective RPI on webserver@128.192.158.63 path: /var/www/aspendb/probesearch/SensorsData
- Firebase account can be accessed using https://console.firebase.google.com/u/1/project/rpi-dataset/firestore/data/~2FRPI-details

---

### Flow of the application:
<img src="https://github.com/sakshi-seth-17/Data-Collector-RPI0/blob/main/ApplicationFlow.jpg" alt="Alt text" title="Optional title">

### Instructions
1. Clone this repository. \
`git clone https://github.com/sakshi-seth-17/Data-Collector-RPI3.git`

2. Make neccessary changes required in the app.py wrt specific RPI. \

3. Travel to the parent project directory and install the required python packages. \
`Create virtual environment – python3 -m venv venv` \
`source venv/bin/activate` \
`pip3 install -r requirement.txt` \
`To check if application is working fine run – python3 app.py` \

### Create service file to make the app run indefinitely
`sudo nano /lib/systemd/system/datacollector.service` \
Paste below lines inside the file by making necessary changes \
[Unit] \
Description=rpi0 \
After=multi-user.target 


[Service] \
WorkingDirectory=/home/sonya-cummings \
User=sonya-cummings \
Type=idle \
ExecStart=/home/sonya-cummings/DataCollector/venv/bin/python3 /home/sonya-cummings/DataCollector/app.py \
Restart=on-failure \
KillMode=process \
LimitMEMLOCK=infinity \
LimitNOFILE=65535 \
Type=simple 


[Install] \
WantedBy=multi-user.target 

`sudo chmod 644 /lib/systemd/system/datacollector.service` \
`sudo systemctl enable datacollector.service` \
`sudo systemctl daemon-reload` \
`sudo systemctl start datacollector.service` \
`sudo systemctl status datacollector.service` \

---
Folder Structure
	- venv/
	- app.py
	- config.json (Not on github, need to ask for this file from lab members)
	- error.log
	- humidity.py
	- sendEmail.py
	- userdefined.py
	- db-key.json (Not on github, need to ask for this file from lab members)
	- requirement.txt
	
---
### Application Code Flow - app.py
1. Import all the necessary packages.
2. Initialize varibales and load data/key required in the code.
3. There are 5 functions each used to fulfill a particular functionality.
  - raspberryIP() -> Gets current IPAddress of the RPI server
  - storeImage() -> Captures image by initializing camera object and captures image
  - brightness() -> Uses the image clicked by the camera and gets the brightness. It is done to check if lights are turned on or off in a particular location.
  - storeSensorReadings() -> This function uses another function from module humidity.py called getSensorReadings() to get the temperature and humidity of the           sensor. It checks if the temperature is in a particular range(18-30) if not it sends out an email notification informing about the abnormalities using another function called sendStaus from module sendEmail.py. After we get all the required information this information is stored sent to 2 apis one handles the firebase storage and another one handles local database storage. To send data on webserver, storeOnWebserver() function is used to transfer the data using an API.
  - storeOnWebserver() -> sends data to the webserver using an API.
4. A while loop makes sure that the application never stops, storeImage() and storeSensorReadings() functions are called every 30 mins to record information
