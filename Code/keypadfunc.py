import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
GPIO.setup(20, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
GPIO.setup(21, GPIO.IN, pull_up_down = GPIO.PUD_UP) 
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP) 


GPIO.setup(23, GPIO.OUT) 
GPIO.setup(24, GPIO.OUT) 
GPIO.setup(25, GPIO.OUT) 
GPIO.setup(26, GPIO.OUT)

def keypad(): 
    while(True): 

        GPIO.output(26, GPIO.LOW)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(23, GPIO.HIGH)

        if (GPIO.input(22)==0):
            return(1,"!")
            break

        if (GPIO.input(21)==0):
            return(4,"$")
            break

        if (GPIO.input(20)==0):
            return(7,"&")
            break

        if (GPIO.input(19)==0):
            return(0xE)
            break

        GPIO.output(26, GPIO.HIGH)
        GPIO.output(25, GPIO.LOW)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(23, GPIO.HIGH)

        if (GPIO.input(22)==0):
            return(2,"@")
            break

        if (GPIO.input(21)==0):
            return(5,"%")
            break

        if (GPIO.input(20)==0):
            return(8,"*")
            break
 
        if (GPIO.input(19)==0):
            return(0,")")
            break


        GPIO.output(26, GPIO.HIGH)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(24, GPIO.LOW)
        GPIO.output(23, GPIO.HIGH)

        if (GPIO.input(22)==0):
            return(3,"#")
            break

        if (GPIO.input(21)==0):
            return(6,"^")
            break
        #Scan row 2
        if (GPIO.input(20)==0):
            return(9,"(")
            break
 
        if (GPIO.input(19)==0):
            return("#", "")
            break

        GPIO.output(26, GPIO.HIGH)
        GPIO.output(25, GPIO.HIGH)
        GPIO.output(24, GPIO.HIGH)
        GPIO.output(23, GPIO.LOW)

        if (GPIO.input(22)==0):
            return(0xA)
            break

        if (GPIO.input(21)==0):
            return(0xB)
            break

        if (GPIO.input(20)==0):
            return(0xC)
            break

        if (GPIO.input(19)==0):
            return(0xD)
            break
