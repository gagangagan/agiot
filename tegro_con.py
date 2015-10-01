#!/usr/bin/env python


import os
import xively
import subprocess
import time
import datetime
import requests

import time
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.IN)

# extract feed_id and api_key from environment variables
FEED_ID = os.environ["FEED_ID"]
API_KEY = os.environ["API_KEY"]
DEBUG = os.environ["DEBUG"] or false
TEMP_THRESHOLD = "20"
MODE_AUTO = "0"
MODE_MAMNUAL = "1"
CONTROLLER_ENABLED = "1"
CONTROLLER_DISABLED = "0"



# initialize api client
api = xively.XivelyAPIClient(API_KEY)



	
def get_temperature_stream(feed):
  try:
    datastream = feed.datastreams.get("field_temperature")
    if DEBUG:
      print ("Field Temprature Stream Found")
    return datastream
  except:
    if DEBUG:
      print( "Creating field_temperature datastream")
    datastream = feed.datastreams.create("field_temperature",tags="Temperature")
    return datastream

def get_humidity_stream(feed):
  try:
    datastream = feed.datastreams.get("field_humidity")
    if DEBUG:
      print ("Field Humidity Stream Found")
    return datastream
  except:
    if DEBUG:
      print( "Creating field_humidity datastream")
    datastream = feed.datastreams.create("field_humidity",tags="Humidity")
    return datastream

def get_humidity_controller_stream(feed):
  try:
    datastream = feed.datastreams.get("field_humidity_controller")
    if DEBUG:
      print ("Field Humidity Controller  Stream Found")
    return datastream
  except:
    if DEBUG:
      print( "Creating field_humidity_controller datastream")
    datastream = feed.datastreams.create("field_humidity_controller",tags="Humidity Controller")
    return datastream

def get_temperature_controller_stream(feed):
  try:
    datastream = feed.datastreams.get("field_temperature_controller")
    if DEBUG:
      print ("Field Temperature Controller  Stream Found")
    return datastream
  except:
    if DEBUG:
      print( "Creating field_temperature_controller datastream")
    datastream = feed.datastreams.create("field_temperature_controller",tags="Temperature Controller")
    return datastream
     
def get_temperature_threshold_stream(feed):
  try:
    datastream = feed.datastreams.get("field_temperature_threshold")
    if DEBUG:
      print (" Temperature Threshold  Stream Found")
    return datastream
  except:
    if DEBUG:
      print( "Creating temperature_threshold datastream")
    datastream = feed.datastreams.create("field_temperature_threshold",tags="Temperature Threshold")
    return datastream


def get_humidity_threshold_stream(feed):
  try:
    datastream = feed.datastreams.get("field_humidity_threshold")
    if DEBUG:
      print ("Humidity Threshold  Stream Found")
    return datastream
  except:
    if DEBUG:
      print( "Creating humidity_threshold datastream")
    datastream = feed.datastreams.create("field_humidity_threshold",tags="Humidity Threshold")
    return datastream


def get_mode_stream(feed):
  try:
    datastream = feed.datastreams.get("operating_mode")
    if DEBUG:
      print ("Operating Mode  Stream Found")
    return datastream
  except:
    if DEBUG:
      print( "Creating operating_mode datastream")
    datastream = feed.datastreams.create("operating_mode",tags="Operating Mode")
    return datastream
 
def update_stream(stream,value):
  print("Stream = " + stream.id )
  print("Value = " + str(value))
  stream.current_value = value 
  stream.at = datetime.datetime.utcnow() 

  try:
     stream.update()
  except requests.HTTPError as e:
     print ("HTTPError({0}): {1}".format(e.errno, e.strerror))

def execute_auto_mode(temp,humidity, feed):

  temp_threshold_stream = get_temperature_threshold_stream(feed) 
  if int(temp)  >= int(temp_threshold_stream.current_value):
    GPIO.output(17,GPIO.HIGH)
  else:
    GPIO.output(17,GPIO.LOW) 


     
  humidity_threshold_stream = get_humidity_threshold_stream(feed) 

  if int(humidity) >= int(humidity_threshold_stream.current_value):
    GPIO.output(27,GPIO.HIGH)
  else:
    GPIO.output(27,GPIO.LOW) 


def execute_manual_mode(temp,humidity, feed):
  print("Executing Manual Mode")

  temp_controller_stream = get_temperature_controller_stream(feed) 
  print("Temperatur Controller = " + str(temp_controller_stream.current_value))
  if CONTROLLER_ENABLED == temp_controller_stream.current_value:
    print("Temp Controller Enabled")
    GPIO.output(17,GPIO.HIGH)
  else:
    print("Temp Controller disabled")
    GPIO.output(17,GPIO.LOW) 

  humidity_controller_stream = get_humidity_controller_stream(feed) 

  if CONTROLLER_ENABLED == humidity_controller_stream.current_value:
    GPIO.output(27,GPIO.HIGH)
  else:
    GPIO.output(27,GPIO.LOW) 


# main program entry point - runs continuously updating our datastream with the
# current 1 minute temperature & humidity readings 

def run():
  print ("Starting TeGro Controller") 
  current_switch_state = 0

  feed = api.feeds.get(FEED_ID)

  temperature_controller_stream = get_temperature_controller_stream(feed)
  switch_init_state = temperature_controller_stream.current_value
  switch_current_state = switch_init_state
  print("Controller State : " + str(temperature_controller_stream.current_value))


  
  while True:

    #temperature_controller_stream = get_temperature_controller_stream(feed)

     
    controller_state_switch = GPIO.input(17)
    #print("Controller : " + str(controller_state_switch))
    print(controller_state_switch)
    if controller_state_switch == 0 :
      #temperature_controller_stream = get_temperature_controller_stream(feed)
      if temperature_controller_stream.current_value == CONTROLLER_ENABLED:
        print("Enabling Temperature Controller")
        #update_stream(temperature_controller_stream,CONTROLLER_DISABLED)
      else:
        print("Disabling Temperature Controller")
        #update_stream(temperature_controller_stream,CONTROLLER_ENABLED)
         

    #time.sleep(10)

run()
