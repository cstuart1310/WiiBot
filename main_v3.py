#V3 has wiimote support

import RPi.GPIO as GPIO
import sys, tty, termios
import time
import cwiid

#Vars

webcam_enabled=False
auto_enabled=False
autoTurtle_enabled=False
wiiCatch=False
wiiAcc=False

wallDist=15 #Closest the sensor can be before warning the

deadzoneXmin=110
deadzoneXmax=140

deadzoneYmin=120
deadzoneYmax=130

deadzoneZmin=150
deadzoneZmax=160

def help():
    print("""
    ---Controls---
    W - Forward
    A - Left
    S - Back
    D - Right
    SPACE - Stop
    Q - Beep

    C - Test all pins
    R - Stop and shutdown 
    T - Toggle Webcam
    F - Toggle auto-mode
    G - Toggle auto-mode with turtle
    V - Read Ultrasonic Sensor
    B - Swap control to wiimote (Buttons)

    ------------------------------------------------
    """)
def toggle_webcam():
    global webcam_enabled

    if webcam_enabled==False:
        #Do some code stuff
        webcam_enabled=True
        print("Webcam is ENabled")
    else:
        #do more code stuff
        webcam_enabled=False
        print("Webcam is DISabled")

def toggle_auto():
    global auto_enabled
    if auto_enabled==False:
        #Do some code stuff
        auto_enabled=True
        autoTurtle_enabled=False
        print("Auto is ENabled")
        auto()
    else:
        #do more code stuff
        auto_enabled=False
        print("Auto is DISabled")

def toggle_autoTurtle():
    global autoTurtle_enabled
    if autoTurtle_enabled==False:
        #Do some code stuff
        autoTurtle_enabled=True
        auto_enabled=False
        print("Auto Turtle is ENabled")
        autoTurtle()
    else:
        #do more code stuff
        autoTurtle_enabled=False
        print("Auto Turtle is DISabled")

def toggle_wiiAcc():
    global wiiAcc

    if wiiAcc==False:
        wiiAcc=True
    else:
        wiiAcc=False

#Control funcs
def fwd():
    print("Forward")
    brake()
    GPIO.output(rf, GPIO.HIGH)
    GPIO.output(lf, GPIO.HIGH)
def back():
    print("Back")
    brake()
    GPIO.output(rb, GPIO.HIGH)
    GPIO.output(lb, GPIO.HIGH)

def left():
    print("Left")
    brake()
    GPIO.output(rf, GPIO.HIGH)
    GPIO.output(lb, GPIO.HIGH)
def right():
    print("Right")
    brake()
    GPIO.output(lf, GPIO.HIGH)
    GPIO.output(rb, GPIO.HIGH)

def brake():
    #print("Braking") #commented out so it doesnt say braking every single time
    GPIO.output(lf, GPIO.LOW)
    GPIO.output(rf, GPIO.LOW)
    GPIO.output(lb, GPIO.LOW)
    GPIO.output(rb, GPIO.LOW)
    #sys.exit()

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def test_movement():
    global pins
    print("---Testing pins---")
    for pin in pins:
        print(pin)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(3)
        GPIO.output(pin, GPIO.LOW)
    print("---Finished testing---\n")

def auto():
    brake()
    global wallDist
    obsticle=False
    global auto_enabled
    auto_enabled=True
    
    print("---Enabling Auto Mode ---")
    while auto_enabled==True:
        ultraVal=readUltra()
        try:      
            if ultraVal<10:#Checks if needs to reverse first so it will reverse then turn
                back()
                time.sleep(1)#Delay so it reverses for 1.5 secs total
            

            if ultraVal<=wallDist:
                print("Too close! Turning left")                
                left()
                time.sleep(1)
            elif ultraVal>wallDist:
                fwd()

            time.sleep(0.5)
        except KeyboardInterrupt:
            print("---Resuming User Control ---")
            auto_enabled=False
            brake()

def autoTurtle():
    brake()
    global wallDist
    obsticle=False
    global auto_enabled

    autoTurtle_enabled=True
    t = turtle.Turtle()
    print("---Enabling Auto Turtle Mode ---")
    while auto_enabled==True:
        try:
            if readUltra()<=wallDist:
                print("Too close! Turning left")
                left()
                t.left(90)
                time.sleep(1)
            elif readUltra()>wallDist:
                fwd()
                t.fwd(5)
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("---Resuming User Control ---")
            autoTurtle_enabled=False
            brake()
            canvas=t.getcanvas()
            canvas.postscript(file="room.ps", colormode='color')


def readUltra():
    #print("Reading ultra")
    global trig
    global echo
    #Pings sensor
    distance=0
    #while distance==0: #Loops until it finds a result
    #print("Pinging sensor")
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)
    #print("Getting result")
    while GPIO.input(echo)==0:#Starts the timer when sensor has no input
        pulse_start = time.time()
    #print("Getting result 2")
    while GPIO.input(echo)==1:#Stops the timer when the sensor has recieved an input
        pulse_end = time.time()
    #print("Got results")
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance+1.15, 2)
    print(distance,"cm")
    if distance>1000:
        distance=distance/100
    return distance
 
def beep():
    global horn
    print("Beep")
    GPIO.output(horn, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(horn, GPIO.LOW)

def wiiConnect():       
    global wii
    global wiiCatch 
    global keyCatch
    print ('Please press buttons 1 + 2 on your Wiimote now ...')
    time.sleep(1)
    # This code attempts to connect to your Wiimote and if it fails the program quits
    try:
        wii=cwiid.Wiimote()
        print("Connected!")
        wii.rumble = 1
        time.sleep(1)
        wii.rumble = 0
        wii.rpt_mode = cwiid.RPT_BTN
        wiiCatch=True
        keyCatch=False
        print("---Wiimote Control---")
    except RuntimeError:
        print ("Cannot connect to your Wiimote. Run again and make sure you are holding buttons 1 + 2!")
def wiiDisconnect():
    global keyCatch
    print("Disconnecting wiimote")
    wii.rumble = 1
    time.sleep(1)
    wii.rumble = 0
    keyCatch=True
    print("---Keyboard Control---")

#Main
print("\n"*30)
#Setup
print("Setting up")
# Pin Definitons:
rb = 21
rf = 20
lb = 13
lf = 19
trig = 8#24
horn= 6
echo = 7#26
pins=[rb,rf,lb,lf,trig,horn] #Array of pins used for testing
inpins=[echo]
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
print("Setting up output pins")
for pin in pins:
    GPIO.setup(pin, GPIO.OUT) # LED pin set as output
    print("Setup pinmode for ",pin)

for pin in inpins:
    GPIO.setup(pin, GPIO.IN)#Set pin as input
    print("Setup pinmode for",pin)
brake() #Stops all motors from previous programs


GPIO.output(trig,False)#Makes sure the sensor is off for a clean reset
print("Giving time for setup to complete")
time.sleep(1)
print("Setup successful. Robot is ready")
print("Press H for a list of controls")
print("----------------------------------------------------------")

keyCatch=True

while True: # Main loop
    while keyCatch== True:
        key=getch()
        #print("\n",key)
        if key=="w":
            fwd()
        elif key=="a":
            left()
        elif key=="s":
            back()
        elif key=="d":
            right()
        elif key=="r":
            print("---Exiting---")
            brake()
            print("Braked")
            GPIO.cleanup()
            print("Cleaned up GPIO")
            keyCatch==False
            print("Stopped catching keys")
            sys.exit()
        elif key==" ":
            print("Braking")
            brake()
        elif key=="t":
            toggle_webcam()
        elif key=="f":
            toggle_auto()
        elif key=="g":
            print("Auto turtle is broke u poo")
            #toggle_autoTurtle()
        elif key=="h":
            help()
        elif key=="c":
            test_movement()
        elif key=="v":
            readUltra()
        elif key=="q":
            beep()
        elif key=="b":
            wiiConnect()

    while wiiCatch == True:
        time.sleep(0.1)
        wii.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
        buttons = wii.state['buttons']

        if wiiAcc==True:
            wiiPos=wii.state['acc']
            wiimoteX, wiimoteY, wiimoteZ =wiiPos
            # print(wiimoteX)
            # print(wiimoteY)
            # print(wiimoteZ)
            time.sleep(1)

        if (buttons & cwiid.BTN_UP) or (wiiAcc==True and wiimoteX>deadzoneXmax):
            fwd()
        if (buttons & cwiid.BTN_LEFT) or (wiiAcc==True and wiimoteY>deadzoneYmax):
            left()
        if (buttons & cwiid.BTN_DOWN) or (wiiAcc==True and wiimoteX>deadzoneXmin):
            back()
        if(buttons & cwiid.BTN_RIGHT) or (wiiAcc==True and wiimoteY>deadzoneYmin):
            right()
        if (buttons & cwiid.BTN_HOME):
            wiiCatch = False        
            wiiDisconnect()
            keyCatch=True
        if (buttons & cwiid.BTN_A):
            print("Braking")
            brake()
        if (buttons & cwiid.BTN_1):
            toggle_auto()
        if (buttons & cwiid.BTN_2):
            beep()
        if (buttons & cwiid.BTN_PLUS):
            toggle_wiiAcc()