'''
# Alexa Personal Assitant for Raspberry Pi
# Coded by Simon Beal and Matthew Timmons-Brown for "The Raspberry Pi Guy" YouTube channel
# Built upon the work of Sam Machin, (c)2016
# Feel free to look through the code, try to understand it & modify as you wish!
# The installer MUST be run before this code.

#!/usr/bin/python
import sys
import time
from grovepi import *
import os
import alsaaudio
import wave
import numpy
import copy
from evdev import InputDevice, list_devices, ecodes

import alexa_helper # Import the web functions of Alexa, held in a separate program in this directory

print "Welcome to Alexa. I will help you in anyway I can.\n  Press Ctrl-C to quit"
'''
'''
#sense = SenseHat() # Initialise the SenseHAT
#sense.clear()  # Blank the LED matrix

# Search for the SenseHAT joystick
found = False
devices = [InputDevice(fn) for fn in list_devices()]
for dev in devices:
    if dev.name == 'Raspberry Pi Sense HAT Joystick':
        found = True
        break

# Exit if SenseHAT not found
if not(found):
    print('Raspberry Pi Sense HAT Joystick not found. Aborting ...')
    sys.exit()
'''
'''
# Initialise audio buffer
audio = ""
inp = None

# We're British and we spell "colour" correctly :) Colour code for RAINBOWZ!!
colours = [[255, 0, 0], [255, 0, 0], [255, 105, 0], [255, 223, 0], [170, 255, 0], [52, 255, 0], [0, 255, 66], [0, 255, 183]]

# Loudness for highest bar of RGB display
max_loud = 1024
'''
'''
# Given a "loudness" of speech, convert into RGB LED bars and display - equaliser style
def set_display(loudness):
    mini = [[0,0,0]]*8
    brightness = max(1, min(loudness, max_loud) / (max_loud/8))
    mini[8-brightness:] = colours[8-brightness:]
    display = sum([[col]*8 for col in mini], [])
    sense.set_pixels(display)
'''
'''
# When button is released, audio recording finishes and sent to Amazon's Alexa service
def release_button():
    global audio, inp
    #sense.set_pixels([[0,0,0]]*64)
    w = wave.open(path+'recording.wav', 'w') # This and following lines saves voice to .wav file
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(16000)
    w.writeframes(audio)
    w.close()
    #sense.show_letter("?") # Convert to question mark on display
    alexa_helper.alexa(sense) # Call upon alexa_helper program (in this directory)
    #sense.clear() # Clear display
    inp = None
    audio = ""

# When button is pressed, start recording
def press_button():
    global audio, inp
    try:
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, alexa_helper.device)
    except alsaaudio.ALSAAudioError:
        print('Audio device not found - is your microphone connected? Please rerun program')
        sys.exit()
    inp.setchannels(1)
    inp.setrate(16000)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(1024)
    audio = ""
    l, data = inp.read()
    if l:
        audio += data

# Whilst button is being pressed, continue recording and set "loudness"
def continue_pressed():
    global audio, inp
    l, data = inp.read()
    if l:
        audio += data
        a = numpy.fromstring(data, dtype='int16') # Converts audio data to a list of integers
        loudness = int(numpy.abs(a).mean()) # Loudness is mean of amplitude of sound wave - average "loudness"
        #set_display(loudness) # Set the display to show this "loudness"

# Event handler for button
def handle_enter(pressed):
    handlers = [release_button, press_button, continue_pressed] # 0=released, 1=pressed, 2=held
    handlers[pressed]()

# Continually loops for events, if event detected and is the middle joystick button, call upon event handler above
def event_loop():
    try:
        handle_enter(1)
      
        
        for event in dev.read_loop(): # for each event
            if event.type == ecodes.EV_KEY and event.code == ecodes.KEY_ENTER: # if event is a key and is the enter key (middle joystick)
                handle_enter(event.value) # handle event
     
    except KeyboardInterrupt: # If Ctrl+C pressed, pass back to main body - which then finishes and alerts the user the program has ended
        pass

if __name__ == "__main__": # Run when program is called (won't run if you decide to import this program)
    while alexa_helper.internet_on() == False:
        print "."
    token = alexa_helper.gettoken()
    path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
    os.system('mpg123 -q {}hello.mp3'.format(path, path)) # Say hello!
    event_loop()
    print "\nYou have exited Alexa. I hope that I was useful. To talk to me again just type: python main.py"
'''
        
        
        
import os
import random
import time
import RPi.GPIO as GPIO
import alsaaudio
import wave
import random
#from creds import *
import requests
import json
import re
import cwiid
from memcache import Client

#Settings
button = 18 #GPIO Pin with button connected
lights = [24, 25] # GPIO Pins with LED's conneted
device = "sysdefault:CARD=Snowball" # Name of your microphone/soundcard in arecord -L

#Setup
recorded = False
servers = ["127.0.0.1:11211"]
mc = Client(servers, debug=1)
path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))



def internet_on():
    print "Checking Internet Connection"
    try:
        r =requests.get('https://api.amazon.com/auth/o2/token')
	print "Connection OK"
        return True
    except:
	print "Connection Failed"
    	return False

	
def gettoken():
	token = mc.get("access_token")
	refresh = refresh_token
	if token:
		return token
	elif refresh:
		payload = {"client_id" : Client_ID, "client_secret" : Client_Secret, "refresh_token" : refresh, "grant_type" : "refresh_token", }
		url = "https://api.amazon.com/auth/o2/token"
		r = requests.post(url, data = payload)
		resp = json.loads(r.text)
		mc.set("access_token", resp['access_token'], 3570)
		return resp['access_token']
	else:
		return False

def connect_wiimote():
	connected = False
	while connected == False:
		try:
			wii=cwiid.Wiimote()
			wii.led = 1
			connected = True
		except RuntimeError:
			print "Error opening wiimote connection"
			time.sleep(10)
			connected=False
	wii.rpt_mode = cwiid.RPT_BTN
	return wii

def rumble(wii, kind='once'):
	if kind == 'once':
		wii.rumble = 1
		time.sleep(0.5)
		wii.rumble = 0
	if kind =='twice':
		wii.rumble = 1
		time.sleep(0.2)
		wii.rumble = 0
		time.sleep(0.2)
		wii.rumble = 1
		time.sleep(0.2)
		wii.rumble = 0	

def alexa():
	GPIO.output(24, GPIO.HIGH)
	url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
	headers = {'Authorization' : 'Bearer %s' % gettoken()}
	d = {
   		"messageHeader": {
       		"deviceContext": [
           		{
               		"name": "playbackState",
               		"namespace": "AudioPlayer",
               		"payload": {
                   		"streamId": "",
        			   	"offsetInMilliseconds": "0",
                   		"playerActivity": "IDLE"
               		}
           		}
       		]
		},
   		"messageBody": {
       		"profile": "alexa-close-talk",
       		"locale": "en-us",
       		"format": "audio/L16; rate=16000; channels=1"
   		}
	}
	with open(path+'recording.wav') as inf:
		files = [
				('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
				('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
				]	
		r = requests.post(url, headers=headers, files=files)
	if r.status_code == 200:
		for v in r.headers['content-type'].split(";"):
			if re.match('.*boundary.*', v):
				boundary =  v.split("=")[1]
		data = r.content.split(boundary)
		for d in data:
			if (len(d) >= 1024):
				audio = d.split('\r\n\r\n')[1].rstrip('--')
		with open(path+"response.mp3", 'wb') as f:
			f.write(audio)
		GPIO.output(25, GPIO.LOW)
		os.system('mpg123 -q {}1sec.mp3 {}response.mp3'.format(path, path))
		GPIO.output(24, GPIO.LOW)
	else:
		GPIO.output(lights, GPIO.LOW)
		for x in range(0, 3):
			time.sleep(.2)
			GPIO.output(25, GPIO.HIGH)
			time.sleep(.2)
			GPIO.output(lights, GPIO.LOW)
		



def start(wii):
	#last = GPIO.input(button)
	buttons = wii.state['buttons']
    	if (buttons & cwiid.BTN_A):
        	last = 0
    	else:
        	last = 1
	while True:
		buttons = wii.state['buttons']
		if (buttons & cwiid.BTN_A):
            		val = 0
        	else:
            		val = 1
		#val = GPIO.input(button)
		if val != last:
			last = val
			if val == 1 and recorded == True:
				rf = open(path+'recording.wav', 'w') 
				rf.write(audio)
				rf.close()
				inp = None
				alexa()
			elif val == 0:
				GPIO.output(25, GPIO.HIGH)
				inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, device)
				inp.setchannels(1)
				inp.setrate(16000)
				inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
				inp.setperiodsize(500)
				audio = ""
				l, data = inp.read()
				if l:
					audio += data
				recorded = True
		elif val == 0:
			l, data = inp.read()
			if l:
				audio += data
		# ----------------------------------------
        	# If Plus and Minus buttons pressed
        	# together then rumble and quit.
        	if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):  
            		print '\nClosing connection ...'
            		rumble(wii,'twice')
            		wii.close()
            		# Wait for reconnect
            		wii = connect_wiimote()	

if __name__ == "__main__":
	GPIO.setwarnings(False)
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.setup(lights, GPIO.OUT)
	GPIO.output(lights, GPIO.LOW)
	while internet_on() == False:
		print "."
	token = gettoken()
	os.system('mpg123 -q {}1sec.mp3 {}hello.mp3'.format(path, path))
	for x in range(0, 3):
		time.sleep(.1)
		GPIO.output(24, GPIO.HIGH)
		time.sleep(.1)
		GPIO.output(24, GPIO.LOW)
	wii = connect_wiimote()
	start(wii)
