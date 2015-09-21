#!/usr/bin/env python

import os
import xively
import subprocess
import time
import datetime
import requests

import time
import RPi.GPIO as GPIO
import Adafruit_DHT as DHT
GPIO.setmode(GPIO.BCM)
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)

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


# function to read 1 minute load average from system uptime command
def read_loadavg():
  if DEBUG:
    print ("Reading load average")
  return subprocess.check_output(["awk '{print $1}' /proc/loadavg"], shell=True)

# function to return a datastream object. This either creates a new datastream,
# or returns an existing one
def get_datastream(feed):
  try:
    datastream = feed.datastreams.get("load_avg")
    if DEBUG:
      print ("Found existing datastream")
    return datastream
  except:
    if DEBUG:
      print ("Creating new datastream")
    datastream = feed.datastreams.create("load_avg", tags="load_01")
    return datastream

def get_device_status(feed):
  try:
    datastream = feed.datastreams.get("device_status")
    if DEBUG:
      print ("Found existing device status datastream")
    return datastream
  except:
    if DEBUG:
      print ("Creating new device status datastream")
    datastream = feed.datastreams.create("device_status", tags="device_status_01")
    return datastream	
	
def get_temperature_stream(feed):
  try:
    datastream = feed.datastreams.get("field_temperature")
    if DEBUG:
      print ("Field Temprature Stream Found")
    return datastream
  except:
    if DEBUG:
      print( "Creating field_temperature datastream")
    datastream = feed.datastreams.create("field_temperature",tags="temperature")
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
    datastream = feed.datastreams.create("field_humidity",tags="humidity")
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
    datastream = feed.datastreams.create("field_humidity_controller",tags="humidity_controller")
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
    datastream = feed.datastreams.create("field_temperature_controller",tags="temperature_controller")
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
    datastream = feed.datastreams.create("field_temperature_threshold",tags="temperature_threshold")
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
    datastream = feed.datastreams.create("field_humidity_threshold",tags="humidity_threshold")
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
    datastream = feed.datastreams.create("operating_mode",tags="device_operating_mode")
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
  print "Starting TeGro Controller "

  feed = api.feeds.get(FEED_ID)

  temperature_stream = get_temperature_stream(feed)
  humidity_stream = get_humidity_stream(feed)
  temperature_controller_stream = get_temperature_controller_stream(feed)
  humidity_controller_stream = get_humidity_controller_stream(feed)
  temperature_threshold_stream = get_temperature_threshold_stream(feed)
  humidity_threshold_stream = get_humidity_threshold_stream(feed)
  operating_mode_stream = get_mode_stream(feed)


  
  while True:

    #temperature_stream = get_temperature_stream(feed)
    #humidity_stream = get_humidity_stream(feed)
    #temperature_controller_stream = get_temperature_controller_stream(feed)
    #humidity_controller_stream = get_humidity_controller_stream(feed)
    #temperature_threshold_stream = get_temperature_threshold_stream(feed)
    #humidity_threshold_stream = get_humidity_threshold_stream(feed)
    operating_mode_stream = get_mode_stream(feed)

     
    reading_h,reading_t = DHT.read_retry(11,4)
    update_stream(temperature_stream,reading_t)
    update_stream(humidity_stream,reading_h)


    if MODE_AUTO == operating_mode_stream.current_value:
      print("TeGro Auto Mode Enabled : " + str(operating_mode_stream.current_value)) 
      execute_auto_mode(reading_t, reading_h,feed) 
     
    else:
      print("TeGro Manual Mode Enabled : " + str(operating_mode_stream.current_value))
      execute_manual_mode(reading_t,reading_h,feed)



    time.sleep(10)

run()
