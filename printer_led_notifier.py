import RPi.GPIO as GPIO
import time
import requests
import json
import configparser
from os.path import exists
import first_start
import datetime


blue = 26
green = 19
red = 13
white = 6
leds = [blue, green, red, white]


def start_up():
    # Setup the GPIO Pins
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    for led in leds:
        GPIO.setup(led, GPIO.OUT)

    # Flash all LED's
    for led in leds:
        GPIO.output(led, GPIO.HIGH)
    time.sleep(1)

    for led in leds:
        GPIO.output(led, GPIO.LOW)

    GPIO.output(red, GPIO.HIGH)
    GPIO.output(green, GPIO.HIGH)
    time.sleep(1)
    GPIO.output(red, GPIO.LOW)
    GPIO.output(green, GPIO.LOW)


def led_on(led):
    GPIO.output(led, GPIO.HIGH)


def led_off(led):
    GPIO.output(led, GPIO.LOW)


def led_blink(led, last_blink):
    if last_blink + datetime.timedelta(seconds=1) < datetime.datetime.now():
        last_blink = datetime.datetime.now()
        #GPIO.setup(led, GPIO.IN)
        if GPIO.input(led) == True:
            #GPIO.setup(led, GPIO.OUT)
            led_off(led)
        elif GPIO.input(led) == False:
            #GPIO.setup(led, GPIO.OUT)
            led_on(led)
    return last_blink


def all_led_on():
    for led in leds:
        led_on(led)


def all_led_off():
    for led in leds:
        led_off(led)


def http_fail():
    x = 0
    while x < 5:
        for led in leds:
            led_on(led)
        time.sleep(.5)
        for led in leds:
            led_off(led)
        time.sleep(.5)
        x += 1


def get_data(ip_address):
    try:
        data = requests.get("http://{}:7070/info".format(ip_address), timeout=2).text
        print(data)
        led_off(white)
        data = json.loads(data)
        stalled = False
        printing = False
        idle = False

        for thing in data:
            printer_status = thing[0]
            stalled_flag = thing[7]
            #print(stalled)
            if printer_status.lower() == 'operational':
                idle = True
            if printer_status.lower() == 'printing':
                printing = True
            if stalled_flag:
                stalled = True


        if stalled:
            led_on(red)
        else:
            led_off(red)

        if printing:
            led_on(green)
        else:
            led_off(green)

        if idle:
            led_on(blue)
        else:
            led_off(blue)

    except requests.exceptions.ConnectionError:
        print("HTTP Fail")
        all_led_off()
        led_on(white)
    except requests.exceptions.ReadTimeout:
        print("Timeout")
        all_led_off()
        led_on(white)


def get_config():
    if not exists('config.ini'):
        first_start.the_hunter()

    config = configparser.ConfigParser()
    config.read('config.ini')

    ip_address = config['op_monitor']['ipaddress']

    return ip_address


if __name__ == '__main__':
    last_blink = datetime.datetime.now()
    last_run = datetime.datetime.now() - datetime.timedelta(seconds=10)
    start_up()
    ip_address = get_config()

    while(True):
        #print("Running Loop")
        if last_run + datetime.timedelta(seconds=5) <= datetime.datetime.now():
            print("Running Update")
            get_data(ip_address)
            last_run = datetime.datetime.now()
        time.sleep(.25)
        #last_blink = led_blink(green, last_blink)

