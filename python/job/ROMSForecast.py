import sys
import json
import os

if os.path.abspath('..') not in sys.path:
    sys.path.append(os.path.abspath('..'))

curdir = os.path.dirname(os.path.abspath(__file__))

from job.Job import Job

import romsUtil as util

debug = False

class ROMSForecast(Job):


  def __init__(self, configfile, NPROCS):

    TEMPLPATH = f"{curdir}/templates"

    self.__jobtype = 'roms'
    self.configfile = configfile
    self.NPROCS = NPROCS

    jobDict = self.readConfig(configfile)

    # TODO: Implement in parseConfig

    self.OFS = jobDict['OFS']
    self.CDATE = jobDict['CDATE']
    self.HH = jobDict['HH']
    self.COMROT = jobDict['COMROT']
    self.EXEC = jobDict['EXEC']
    TIME_REF = jobDict['TIME_REF']

    self.BUCKET = jobDict['BUCKET']
    self.BCKTFLDR = jobDict['BCKTFLDR']

    # Easier to use 
    CDATE = self.CDATE
    HH = self.HH
    OFS = self.OFS
    COMROT = self.COMROT
    
    # Create the ocean.in file from a template 
    # TODO: Make ocean in for NOSOFS
    if OFS == 'liveocean':
  
      # LiveOcean requires a significant amount of available RAM to run > 16GB
      # NTIMES 90 is 1 hour for liveocean 
      # Using f-strings
      # Add stuff to the replacement dictionary 
      fdate = f"f{CDATE[0:4]}.{CDATE[4:6]}.{CDATE[6:8]}"
      template = f"{TEMPLPATH}/{OFS}.ocean.in"
  
      self.OUTDIR = f"{COMROT}/{OFS}/{fdate}"
      outfile = f"{self.OUTDIR}/liveocean.in"

      if not os.path.exists(self.OUTDIR):
        os.makedirs(self.OUTDIR)
  
      DSTART = util.ndays(CDATE,TIME_REF)
      # DSTART = days from TIME_REF to start of forecast day larger minus smaller date
  
      settings = {
        "__NTIMES__"   : jobDict['NTIMES'],
        "__TIME_REF__" : jobDict['TIME_REF'],
        "__DSTART__"   : DSTART,
        "__FDATE__"    : fdate,
        "__ININAME__"  : jobDict['ININAME']
      }
      
      # TODO: Template this in npzd2o_Banas.in or copy the rivers.nc file over
      # SSFNAME == /com/liveocean/forcing/f2019.11.06/riv2/rivers.nc
  
    elif OFS == 'adnoc':

      self.OUTDIR = f"{COMROT}/{OFS}/{CDATE}"

      # TODO: fix this - don't need two variables for the same thing do we?
      jobDict['OUTDIR'] = self.OUTDIR
      self.OUTDIR = self.OUTDIR


      if not os.path.exists(self.OUTDIR):
        os.makedirs(self.OUTDIR)

      settings = {
        "__NTIMES__"   : jobDict['NTIMES'],
        "__TIME_REF__" : jobDict['TIME_REF'],
      }

      outfile = f"{self.OUTDIR}/ocean.in"
      template = f"{TEMPLPATH}/{OFS}.ocean.in"

    elif OFS == 'cbofs':
      template = f"TODO-cbofstemplate"
      outfile = f"TODO-template"
    else :
      raise Exception("unsupported model")

    # Create the ocean.in
    util.makeOceanin(self.NPROCS,settings,template,outfile)


  ########################################################################
  def __parseConfig(self, cfDict) : 
    print("parseConfig stub")
    return
  
