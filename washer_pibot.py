try:
    # Import necessary libraries
    import RPi.GPIO as GPIO
    import time
    import json, requests
    import logging             # for debugging
except RuntimeError:
    print("Error loading RPi.GPIO")

DELAYINSECS = 120 # Time in seconds before declaring end of cycle

# Define RPi input/output pins
BUTTON = 10
# LED = 37
VIBRATION = 14

# Function to send push notification with pushbullet
def pushdone():
    url = "https://api.pushbullet.com/v2/pushes"
    payload = {"type":"note","title":"Your Washing is Complete!", "body":"Courtesy PiBot","email":"josiahmaharaj.ee@gmail.com"}
    headers = {"Access-Token":"o.cjYYyyL4TOyuiS9UoXmteGLqXHwKz3Za","content-type": "application/json"}
    requests.post(url, data=json.dumps(payload), headers=headers)
    print "Sent Message"

def main():
    try:
        # Configure GPIO pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(VIBRATION, GPIO.IN)
        # GPIO.setup(LED, GPIO.OUT)

        # "Pull-down" resistor must be added to input 
        # push-button to avoid floating value at 
        # RPi input when button not in closed circuit.
        GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Start of sensing of upwards or downwards front on
        # pin connected to vibration detector. 
        # "Bouncetime" argument ignores effect of bouncing caused by
        # sudden state changes.
        GPIO.add_event_detect(VIBRATION, GPIO.BOTH, bouncetime=200)

        # Configure debugging journal file on RPi
        logging.basicConfig(filename='/home/pi/washer.log', 
                            level=logging.INFO, 
                            format='%(asctime)s %(levelname)s:%(message)s')
        logging.info("****************************")
        stop = False
        logging.info("Entering main loop")

        # Main loop, waits for push-button to be 
        # pressed to indicate beginning of cycle, then 
        # periodically checks vibration.
        while not stop:
            logging.info("Main loop iteration")
            print "Waiting for Press"
            # GPIO.output(LED, True) # LED off
            GPIO.wait_for_edge(BUTTON, GPIO.RISING) # wait for signal 
                                                    # from push-button
            logging.info(" Started")
            print "Started"
            going = True
            # GPIO.output(LED, False) # LED on

            # Secondary program circuit, checks every 3 
            # minutes for vibrations during this time. 
            # If no vibration for the last 3 
            # minutes, cycle considered done.
            while going:
                logging.info("  Inner loop iteration")
                print "Inner Loop"
                print "Maching Active"
                time.sleep(DELAYINSECS)
                logging.info("  Just slept %ds", DELAYINSECS)
                
                # Manual override to stop the current cycle; 
                # keep push-button
                # pressed during check.
                if GPIO.input(BUTTON):
                    stop = True
                    going = False
                    print "Button End"

                # End of cycle if no vibration detected.
                if not GPIO.event_detected(VIBRATION):
                    logging.info("  Stopped vibrating")
                    print "Machine Inactive"
                    pushdone()
                    going = False
            logging.debug(" End of iteration")
    except:
        logging.warning("Quit on exception")
    finally:
        logging.info("Cleaning up")
        GPIO.remove_event_detect(VIBRATION)
        GPIO.cleanup()

if __name__ == '__main__': main()