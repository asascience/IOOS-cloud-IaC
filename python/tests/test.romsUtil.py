#!/usr/bin/python3
import os
import romsUtil as util
import datetime

def templatetest() :
  template="../adnoc/ocean.in.template"
  outfile="ocean.in"
  
  
  nodeCount=1
  coresPN=36
  
  tiles = util.getTiling( nodeCount * coresPN )
  
  # Just a dictionary
  # Could also read this in from a json file 
  settings = {
    "__NTILEI__": tiles["NtileI"],
    "__NTILEJ__": tiles["NtileJ"],
    "__NTIMES__": 60,
    "__TIME_REF__": "20191212.00"
  }
  
  util.sedoceanin ( template, outfile, settings )


def todaytest():
  CDATE = "today"

  if CDATE == "today":
    today = datetime.date.today().strftime("%Y%m%d")
    #print(f"today is: {today.year}{today.month}{today.day}")
    print(f"today is: {today}")

def pathsize():
  path = '/mnt/efs/com/liveocean/forcing/f2020.01.28'
  size = os.path.getsize(path)
  print(f"size is : {size}")

def ndaystest() :
            
  refdate = "19700101"
  cdate = "20191106"
  # cdate - refdate
  days = util.ndays(cdate, refdate)
  print ("ndays is", days)


#ndaystest()
#todaytest()
pathsize()

