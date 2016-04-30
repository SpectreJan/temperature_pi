# -*- coding: utf8 -*-
#  Copyright (C) {2016}  {Jan Kraemer}
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
import re, os, urllib2
import time
import RPi.GPIO as gpio
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("debug_mode")
parser.add_argument("sensor_mode", type=int)
args = parser.parse_args()

url_base = ""

sensor_path = ""

led_error_pin = 11
led_success_pin = 10

def check_log_dir():
  return os.path.isdir("log/")

def create_log_dir():
  try:
    os.makedirs("log/")
  except:
    if not check_log_dir():
      raise

def get_temp(path):
  temp = None
  
  try:

    gpio.output(led_error_pin, gpio.LOW)
    sensor = open(path, 'r')
    line = sensor.readline()

    if re.match(r"([0-9a-f]{2} ){9}: crc=[0-9a-f]{2} YES", line):

      line = sensor.readline()
      match = re.match(r"([0-9a-f]{2} ){9}t=([+-]?[0-9]+)", line)
      if(match):
        temp = float(match.group(2))/1000
        flash_led(led_success_pin, 1.0)
        
      else:
        error_str = "Temperature could not be read correctly!"
        log_errors(error_str)
        flash_led(led_error_pin, 1.0)

    else:
      error_str = "Wrong CRC for reading"
      log_errors(error_str)
      flash_led(led_error_pin, 1.0)

    sensor.close()

  except IOError:
    error_str = "Could not read sensor!"
    log_errors(error_str)
    flash_led(led_error_pin, 1.0)

  return temp

def create_url(temp, mode):
  temp_url = url_base + repr(temp)
  temp_url = temp_url % mode

  print "Temperature = " + repr(temp) + " °C"
  return temp_url

def send_url(url):
  ret = 0
  st = "http://google.de" 
  try:
    result = urllib2.urlopen(st)
    flash_led(led_success_pin, 0.25)

  except urllib2.HTTPError as error:
    err_str = error.code + " " + error.reason
    log_errors(err_str)
    flash_led(led_error_pin, 0.25)

 
def flash_led(led, interval):

  for x in xrange(0,4):
    gpio.output(led, gpio.HIGH)
    time.sleep(interval)
    gpio.output(led, gpio.LOW)
    time.sleep(interval)

def log_result(temp, mode, url):
  curr_date = time.strftime("%d_%m_%Y")
  curr_time = time.strftime(" %H:%M:%S")
  time_str = curr_date + curr_time
  log_str = "Log: "
  log_str += time_str + ": <debug_mode>" + repr(mode) + "<\debug_mode>"
  log_str += "<token><\\token>"
  log_str += "<type>sbc<\\type>"
  log_str += "\n"

  temp_url = url + "\n"

  print log_str + temp_url

  logfilename = "log/temperature_pi_" + curr_date + ".log"

  logfile = open(logfilename, 'a')
  logfile.write(log_str)
  logfile.write(temp_url)
  logfile.close()

def log_errors(error_msg):
  curr_time = time.strftime("%d/%m/%Y %H:%M:%S")
  err_str = curr_time + " Error:"
  err_str += error_msg + "\n"

  print err_str

  logfile = open("temperature_pi.log", 'a')
  logfile.write(err_str)
  logfile.close()

if __name__ == '__main__':
  
  dbg_mode = args.debug_mode
  if(args.sensor_mode == 1):
    used_sens_path = "Blad"
  else:
    used_sens_path = sensor_path

  create_log_dir()

  # Set GPIOs for the LEDs
  gpio.setwarnings(False)
  gpio.setmode(gpio.BOARD)
  gpio.setup(led_error_pin, gpio.OUT)
  gpio.setup(led_success_pin, gpio.OUT)
  gpio.output(led_error_pin, gpio.HIGH)
  gpio.output(led_success_pin, gpio.HIGH)
  time.sleep(1)
  gpio.output(led_error_pin, gpio.LOW)
  gpio.output(led_success_pin, gpio.LOW)

  url = ""
  temp = get_temp(used_sens_path)
  if temp != None:
    url = create_url(temp, dbg_mode)
    send_url(url)
    log_result(temp, dbg_mode, url)

  gpio.output(led_success_pin, gpio.LOW)
  gpio.output(led_error_pin, gpio.LOW)
  
