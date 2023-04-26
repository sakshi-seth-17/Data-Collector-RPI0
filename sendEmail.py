import smtplib
from email.message import EmailMessage

def sendStaus(rpidescription, location, IPAddress, temperature):
    email = "TsaiLab.status@gmail.com"
    password = "pmildtcgqwdlqbau"
    
    try:
        # starting the smtplib server 
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        server.login(email, password)
        
        #Create an object to fill in information to be used to send and email
        msg = EmailMessage()
        text = "Temperature: {} \nLocation: {} \nIPAddress: {}".format(temperature,location,IPAddress)
        
        msg.set_content(text)
        
        msg['Subject'] = "({}-pi3-{})Abnormalities in temperature".format(rpidescription,location)
        msg['From'] = email
        msg['To'] = ["TsaiLab.status@gmail.com","ch29576@uga.edu","ss29714@uga.edu"]
        
        # send email
        server.send_message(msg)
        
        #closing the connection
        server.quit()
    except Exception as e:
        print("Error: {}".format(e))




