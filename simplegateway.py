#!/usr/bin/env python
""" 
kode for å lese data fra Ciseco radio og skrive til Firebase
koden er basert på kode fra Ciseco - takk til dem!

last ned LLAPSerial.py fra https://github.com/CisecoPlc/LLAPtoCOSM
installer firebase fra https://pypi.python.org/pypi/python-firebase/1.2
"""

import sys, time, Queue
import LLAPSerial
from firebase import firebase
import urllib3
import requests

def ts():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

class LLAPFB:
    def __init__(self):
        self._running = True
        self.devid = "PI"
        self.port = "/dev/ttyAMA0"
        
        #Firebase details
        self.FBApp = "https://yourapphere.firebaseio.com"
        self.FBAPIKey ="YOUR API KEY HERE"    #<<<YOUR FEED API KEY HERE
        self.FBPath = "/readings/xxyeto23"                  #<<<YOUR FEED NUMBER HERE
        self.FBConn = firebase.FirebaseApplication(self.FBApp, None)
        
        #self.COSMUrl = '/v2/feeds/{feednum}.xml' .format(feednum = self.COSMFeed)
        
        #setup serial bits
        self.queue = Queue.Queue()
        self.serial = LLAPSerial.LLAPSerial(self.queue)
    
    def __del__(self):
       pass
    
    def on_init(self):
        # connect serial on start
        self.serial.connect(self.port)
        print("Serial Connected")
        self._running = True
        print("Running")
    
    def main(self):
        if self.on_init() == False:
            self._running = False
        
        # loop
        while ( self._running ):
            try:
                self.on_loop()
            except KeyboardInterrupt:
                print("Keybord Quit")
                self._running = False
        self.disconnect_all()
            
    def disconnect_all(self):
        # disconnet serial
        self.serial.disconnect()
    
    def on_loop(self):
        if not self.queue.empty():
            llapMsg = self.queue.get()

            devID = llapMsg[1:3]
            payload = llapMsg[3:]
            print(llapMsg+" devID "+devID+" payload ", payload)
            
            #main state machine to handle llapMsg's
            if payload.startswith('TMP'):
                # remove trailing -
                temp = payload[3:].replace("-","")    
                data = {'value':temp, 'ts':ts()}
                try:
                    self.FBConn.post(self.FBPath+"/Temp/",data )
                except:
                    print "Shit happens"

            elif payload.startswith('HUM'):
                temp = payload[3:].replace("-","")
                data = {'value':temp, 'ts':ts()}
                try:
                    self.FBConn.post(self.FBPath+"/Humid/",data )
                except:
                    print "Shit happens"

            elif payload.startswith('DST'):
                temp = payload[3:].replace("-","")
                data = {'value':temp, 'ts':ts()}
                try:
                    self.FBConn.post(self.FBPath+"/Dust/",data )
                except:
                    print "Shit happens"                
        
if __name__ == "__main__":
    application = LLAPFB()
    application.main()

