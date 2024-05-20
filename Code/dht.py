import RPi.GPIO as GPIO
import time
import DHT11



GPIO.setmode(GPIO.BCM)



def getValues(pin):
        result=""
        while (not result):
            result = DHT11.readDht11(pin)
            if result:
                humidity, temperature = result
                return (humidity, temperature)


