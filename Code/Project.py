### RFID tags:
### 5300C80323 is is the clear card and is not valid
### 5300C8121A is is the card with a sticker and is not valid
### 010FB3B47B is is the disk shaped tag and is valid
### 5400653D3D is from scooter group and is valid
### 5300C82FB3 is from home security group and is valid
### 46003B3CD0 is from fire alarm group and is valid

# Imports
import RPi.GPIO as GPIO
import time
import LCD1602 as LCD
import keypadfunc as KP
import RFID
import PCF8591 as ADC
import dht as DHT
import urllib.request as URL
import requests
import myFuzzy
import os
from flask import Flask, render_template, send_file
from picamera import PiCamera
from datetime import datetime


# Global variables
END_BUTTON = 17 # Yellow button
SCROLL_BUTTON = 4 # Red button
LED_INLET = 5 # Green LED
LED_OUTLET = 6 # Red LED
BUZZER = 16
TRIG = 12
ECHO = 13
DHT_SENSOR = 10
PH_POT_CHANNEL = 0 # Red ADC wire
TDS_POT_CHANNEL = 1 # White ADC wire
TUR_POT_CHANNEL = 2 # Brown ADC wire
ORP_POT_CHANNEL = 3 # Yellow ADC wire
prompt = ""
mode = ""
tagRFID = ""
API_KEY = "Y0XB7TFU6Q637EPL"
CH_ID = 2324161
NumberOfReadings = 1000
tankIDs = ["123", "155", "139", "111"]
system = True
validRFIDs = [("010FB3B47B", "Ahmad Mansour"), ("5400653D3D", "Salman Siddiqui"), ("5300C82FB3", "Snapping Turtle"), ("46003B3CD0", "Goofy Stuff")]
endTest = False
# Order: pH, TDS, Turbidity, ORP (Fuzzy last one in reading and names)
readings = [0.0,0.0,0.0,0.0,0.0] 
channels = [PH_POT_CHANNEL, TDS_POT_CHANNEL, TUR_POT_CHANNEL, ORP_POT_CHANNEL]
thresholds = [14, 2000, 5, 3000]
names = ["pH", "TDS", "Turbidity", "ORP", "Drinkability"]
LCDIndex = 4

# ADC initialization
ADC.setup(0x48)

# LCD initialization
LCD.init(0x27, 1)

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# I/O pin setup
GPIO.setup([END_BUTTON, SCROLL_BUTTON], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup([ECHO], GPIO.IN)
GPIO.setup([LED_INLET, LED_OUTLET, BUZZER, TRIG], GPIO.OUT)

# Buzzer setup
buzz = GPIO.PWM(BUZZER, 0.1)
buzz.start(50)

# Flask configuration code with camera
mycamera = PiCamera()
mycamera.resolution = (640, 480) # Switching resolution to not fill the screen
myapp = Flask(__name__)

# Function to flush inputs
def flushInputs():
    global tagRFID, modeKB, mode, prompt, endTest, LCDIndex
    tagRFID = ""
    modeKB = ""
    mode = ""
    prompt = ""
    endTest = False
    LCDIndex = 4

# Distance method definition and implementation
def distance():
    GPIO.output(TRIG, GPIO.LOW) 
    time.sleep(0.000002)
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)
    while GPIO.input(ECHO) == 0:
        dummy = 0                                          
    time1 = time.time()                        
    while GPIO.input(ECHO) == 1:
        dummy = 0                                                  
    time2 = time.time()                       
    duration = time2 - time1
    return duration*1000000/58

# Function to display readings on LCD
def displayReading():
    global readings, names, LCDIndex
    LCD.clear()
    LCD.write(0,0,names[LCDIndex])
    LCD.write(0,1,"{:0.2f}".format(readings[LCDIndex]))

# Interrupt 1: Check if end button was pressed to end water sample testing
def stopTesting(self):
    global mode, endTest
    if (mode == "test"):
        endTest = True

# Interrupt 2: Scrolls variables displayed on LCD screen when scroll button is pressed
def scrollLCD(self):
    global LCDIndex
    LCDIndex = (LCDIndex + 1)%5

# Interrupt events
GPIO.add_event_detect(END_BUTTON, GPIO.RISING, callback=stopTesting, bouncetime=500)
GPIO.add_event_detect(SCROLL_BUTTON, GPIO.RISING, callback=scrollLCD, bouncetime=500)

# ThingSpeak upload function
def sendToThing(tankID, pH, TDS, tur, ORP, fuzzyOut):
    dummy = URL.urlopen("https://api.thingspeak.com/update?api_key={}&field1={}&field2={}&field3={}&field4={}&field5={}&field6={}".format(API_KEY, tankID, pH, TDS, tur, ORP, fuzzyOut))

# Function to get data from Thingspeak based on the amount of days and tank ID specified. Returns the data as a JSON object to be used in an HTML file
def getThingData(numOfdays, tankID):
    global CH_ID
    global API_KEY
    global NumberOfReadings
    URL = "https://api.thingspeak.com/channels/{}/feeds.json?days={}&results={}".format(CH_ID, numOfdays, NumberOfReadings)
    headers = {
        'User-Agent': 'PostmanRuntime/7.34.0',
        'Connection': 'keep-alive'
    }
    response = requests.get(URL, headers=headers)
    data = response.json().get("feeds", [])
    data = [entry for entry in data if entry['field1'] == str(tankID)]
    return data

# Function to take photo
def takePhoto(ID, name):
    timestamp = datetime.now().isoformat()
    mycamera.start_preview()
    mycamera.annotate_text = "User {} with ID {} logged in at {}".format(name, ID, timestamp)
    time.sleep(2)
    mycamera.capture("/home/pi/Desktop/F23/Project/image.jpg")
    mycamera.stop_preview()

# Function to take short video
def takeVideo():
    timestamp = datetime.now().isoformat()
    mycamera.annotate_text = "Security breach - Time: {}".format(timestamp)
    mycamera.start_recording("/home/pi/Desktop/F23/Project/video.h264")
    time.sleep(5)
    mycamera.stop_recording()

# Function to sound buzzer alarm
def runAlarm():
    global buzz
    for i in range(10):
        buzz.ChangeFrequency(2800)
        time.sleep(0.5)
        buzz.ChangeFrequency(2500)
        time.sleep(0.5)
    buzz.ChangeFrequency(0.1)

# Function to authorize user before allowing them to test water sample
def authorizeUser():
    global tagRFID, validRFIDs, RFID
    count = 0
    while (count < 3):
        print("Scan your authorized user tag on the RFID scanner")
        time.sleep(2)
        while (not RFID.readRFID()): dummy = 0
        tagRFID = RFID.readRFID()
        for ID, name in validRFIDs:
            if ID == tagRFID:
                print("User {} authorized. Welcome {}".format(ID, name))
                takePhoto(ID, name) # Triggered when someone successfully logs in. Takes photo of authorized user for record
                return True
        count += 1
        print("Invalid tag... You have {} tries left.".format(3-count))
    # Triggered when someone attempts accessing system unsuccessfully 3 times in a row. Takes short video then sounds buzzer alarm
    takeVideo()
    runAlarm()
    return False

# Function used to choose a valid tank ID using keypad, returns chosen tank ID 
def chooseTank():
    global tankIDs
    key, keyS = ("","")
    while True:
        inputID = ""
        print("Enter the tank ID to be sampled (press # to confirm): ", end = "")
        key, keyS = KP.keypad()
        key = str(key)
        while (key != "#"):
            inputID = inputID + key
            print(key, end = "")
            time.sleep(0.25)
            key, keyS = KP.keypad()
            key = str(key)
        time.sleep(0.2)
        print("")
        if inputID in tankIDs:
            print("Tank {} chosen successfully".format(inputID))
            return inputID
        else:
            print("Invalid tank ID...")

# Function used to read ADC of passed channel and convert to meaningful reading
def readADC(chn, thresh):
    global ORP_POT_CHANNEL
    temp = ADC.read(chn)
    temp = (temp/256.0) * float(thresh)
    # ORP can vary between -1500 to 1500 so if we are reading from ORP we set threshold as 3000 and then subtract 1500
    if chn == ORP_POT_CHANNEL: temp -= 1500
    return temp

# Function used to write to ADC using passed value and threshold to be converted to ADC code
def writeADC(val, thresh):
    if val > thresh: val = thresh
    temp = float(val)/float(thresh) * 255
    ADC.write(temp)

# Function used to test water sample after authorization and a tank was chosen
def testWater(tankID):
    global endTest, readings, channels, thresholds, names, LCDIndex
    # Step 1: Check if humidity and temperature of test tank is suitable
    abort = False
    humidity, temperature = DHT.getValues(DHT_SENSOR)
    if humidity > 80: # humidity limits are subject to change
        print("Humidity of the test tank is not suitable.")
        abort = True
    if temperature > 25 or temperature < 20:
        print("Temperature of the test tank is not suitable.")
        abort = True
    if abort:
        print("Aborting test session...")
        return
    print("Test tank conditions | Humidity:{}%,  Temperature: {}C".format(humidity, temperature))
    # Step 2: Open test tank inlet (inlet LED) and wait until test tank full (ultrasonic detects < 20cm)
    print("Opening test tank inlet...")
    GPIO.output(LED_INLET, GPIO.HIGH)
    time.sleep(1)
    dis = distance()
    if dis > 100: dis = 100
    while dis > 20:
        print("Water level: {:0.2f} cm".format(100-dis))
        time.sleep(2)
        dis = distance()
        if dis > 100: dis = 100
    # Step 3: Close inlet
    print("Test tank reached adequate water level. Closing test tank inlet...")
    GPIO.output(LED_INLET, GPIO.LOW)
    time.sleep(1)
    ## Until end button is pressed...
    while not endTest:
        # Step 4: Read ADC and store in variables
        for i in range (4):
            readings[i] = readADC(channels[i], thresholds[i])
        # Step 5: Run fuzzy logic and get output
        readings[4] = myFuzzy.runFuzzy(readings[0], readings[1], readings[2], readings[3])
        # Step 6: Adjust brightness of analog out LED
        writeADC(readings[4] + 15, 100)
        # Step 7: Display readings/fuzzy on LCD
        displayReading()
        # Step 8: Send tank ID, sensor readings and fuzzy output to thingspeak
        sendToThing(tankID, readings[0], readings[1], readings[2], readings[3], readings[4])
        time.sleep(0.1)
    print("End button pressed. Testing session terminated.")
    LCD.clear()
    writeADC(0,1)
    # Step 9: Open outlet (outlet LED) and wait until test tank empty (ultrasonic detects around 100cm) 
    print("Opening test tank outlet...")
    GPIO.output(LED_OUTLET, GPIO.HIGH)
    time.sleep(1)
    dis = distance()
    if dis > 100: dis = 100
    while dis < 100:
        print("Water level: {:0.2f} cm".format(100-dis))
        time.sleep(2)
        dis = distance()
        if dis > 100: dis = 100
    # Step 10: Close outlet
    print("Test tank drained. Closing test tank outlet...")
    GPIO.output(LED_OUTLET, GPIO.LOW)
    time.sleep(1)

@myapp.route("/") # index page
def index():
    return render_template("index.html", validRFIDs=validRFIDs, tankIDs=tankIDs)

@myapp.route("/lastLoggedIn") # Static page to show picture and name of last login
def lastLogin():
    return send_file("/home/pi/Desktop/F23/Project/image.jpg", mimetype = "image/jpeg")

@myapp.route("/blockDiagram") # Static page to show block diagram ;)
def blockDiagram():
    return render_template("block_diagram.html")

@myapp.route("/ph") # Static page to show picture the pH input graph
def ph():
    return send_file("/home/pi/Desktop/F23/Project/templates/FuzzyHTML_files/lvtemporary_394949.jpg", mimetype = "image/jpeg")

@myapp.route("/tds") # Static page to show picture the TDS input graph
def tds():
    return send_file("/home/pi/Desktop/F23/Project/templates/FuzzyHTML_files/lvtemporary_42731.jpg", mimetype = "image/jpeg")

@myapp.route("/turbidity") # Static page to show picture the Turbidity input graph
def turbidity():
    return send_file("/home/pi/Desktop/F23/Project/templates/FuzzyHTML_files/lvtemporary_192897.jpg", mimetype = "image/jpeg")

@myapp.route("/orp") # Static page to show picture the orp input graph
def orp():
    return send_file("/home/pi/Desktop/F23/Project/templates/FuzzyHTML_files/lvtemporary_119800.jpg", mimetype = "image/jpeg")

@myapp.route("/drinkability") # Static page to show picture the drinkability output graph
def drinkability():
    return send_file("/home/pi/Desktop/F23/Project/templates/FuzzyHTML_files/lvtemporary_774252.jpg", mimetype = "image/jpeg")

@myapp.route("/securityLog") # Static page to download last taken video of security breach
def securityLog():
    return send_file("/home/pi/Desktop/F23/Project/video.h264", mimetype = "video/h.264")

@myapp.route("/tankStats/<id>/<numOfDays>") # Dynamic page to show history of water test based on tank ID
def tankStats(id, numOfDays):
    print(getThingData(numOfDays, id))
    return render_template("tank_stats.html", data=getThingData(numOfDays, id), id = id, numOfDays = numOfDays)

@myapp.route("/fuzzy/<type>") # Dynamic page to show input/output fuzzy membership function graphs
def showFuzzy(type):
    if (type.lower() == "ph"): return render_template("ph.html")
    elif (type.lower() == "tds"): return render_template("tds.html")
    elif (type.lower() == "turbidity"): return render_template("turbidity.html")
    elif (type.lower() == "orp"): return render_template("orp.html")
    elif (type.lower() == "drinkability"): return render_template("drinkability.html")
    else: return "Invalid input..." 

@myapp.route("/fuzzyTest/<ph>/<tds>/<turbidity>/<orp>") # Dynamic page to test fuzzy system by inputting values
def testFuzzy(ph, tds, turbidity, orp):
    fuzzy_output = myFuzzy.runFuzzy(float(ph), float(tds), float(turbidity), float(orp))
    if fuzzy_output < 33: drinkability = "Safe"
    elif fuzzy_output > 66: drinkability = "Dangerous"
    else: drinkability = "Semi-safe"
    return render_template("fuzzy_test_result.html", ph=ph, tds=tds, turbidity=turbidity, orp=orp, fuzzy_output=fuzzy_output, drinkability=drinkability)

# Function to run flask if chosen
def runFlask():
    if __name__ == "__main__":
        myapp.run(host = "0.0.0.0", port = 5020)

# Welcome message
print("Welcome to the smart water quality monitoring system.\n" + 
      "This system allows you to run a water quality test on any of the available water tanks.\n" +
      "The system measures pH, total dissolved solids (TDS), turbidity, and the oxidation reduction potential (ORP) of the water sampled from the chosen tank.\n" +
      "Through the use of fuzzy logic, the drinkability of the sampled water will be assessed.\n")

# "main"
while system:
    flushInputs()
    prompt = input("To run the flask server, type F.\n" +
                   "To test a water sample, type T.\n" +
                   "To quit, type Q.\n" +
                   "Type your choice: ").lower()
    if (prompt == "f"):
        mode = "flask"
        runFlask()
    elif (prompt == "t"):
        mode = "authorize"
        system = authorizeUser()
        if (system):
            mode = "tank"
            tank = chooseTank()
            mode = "test"
            testWater(tank)
    elif (prompt == "q"):
        mode = "quit"
        system = False
        print("Thank you for using the system. System shutting down...")
    else:
        print("Invalid input...")
