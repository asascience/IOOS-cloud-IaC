import sys
import json
import os
import

if os.path.abspath('..') not in sys.path:
    sys.path.append(os.path.abspath('..'))

curdir = os.path.dirname(os.path.abspath(__file__))

from job.Job import Job

import romsUtil as util

debug = False

class ROMSForecast(Job):


  # TODO: make self and cfDict consistent
  def __init__(self, configfile, NPROCS):

    self.TEMPLPATH = f"{curdir}/templates"

    self.jobtype = 'roms'
    self.configfile = configfile
    self.NPROCS = NPROCS

    if debug:
      print(f"DEBUG: in ROMSForecast init")
      print(f"DEBUG: job file is: {configfile}")

    cfDict = self.readConfig(configfile)
    self.__parseConfig(cfDict)
    self.make_oceanin(cfDict)



  ########################################################################
  def __parseConfig(self, cfDict) : 

    self.OFS = cfDict['OFS']
    self.CDATE = cfDict['CDATE']
    self.HH = cfDict['HH']
    self.COMROT = cfDict['COMROT']
    self.EXEC = cfDict['EXEC']
    self.TIME_REF = cfDict['TIME_REF']
    self.BUCKET = cfDict['BUCKET']
    self.BCKTFLDR = cfDict['BCKTFLDR']
    self.NTIMES = cfDict['NTIMES']
    self.ININAME = cfDict['ININAME']
    self.OUTDIR = cfDict['OUTDIR']
    self.OCEANIN = cfDict['OCEANIN']
    self.OCNINTMPL = cfDict['OCNINTMPL']

    return


  def make_oceanin(self, cfDict) :
    
    # Easier to use 
    CDATE = self.CDATE

    if CDATE == "today":
      self.CDATE = "20200203"
    
    HH = self.HH
    OFS = self.OFS
    COMROT = self.COMROT
    
    # Create the ocean.in file from a template 
    # TODO: Make ocean in for NOSOFS
    if OFS == 'liveocean':
      self.__make_oceanin_lo(cfDict)
    elif OFS == 'adnoc':
      self.__make_oceanin_adnoc(cfDict)
    elif OFS == 'cbofs':
      template = f"TODO-cbofstemplate"
      outfile = f"TODO-template"
    else :
      raise Exception(f"{OFS} is not a supported forecast")

    return




  def __make_oceanin_lo(self, cfDict):

    CDATE = self.CDATE
    HH = self.HH
    OFS = self.OFS
    COMROT = self.COMROT
    TEMPLPATH = self.TEMPLPATH

    # LiveOcean requires a significant amount of available RAM to run > 16GB
    # NTIMES 90 is 1 hour for liveocean 
    # Using f-strings
    # Add stuff to the replacement dictionary 
    if self.OCNINTMPL == "auto":
      template = f"{TEMPLPATH}/{OFS}.ocean.in"
    else:
      template = self.OCNINTMPL

    fdate = f"f{CDATE[0:4]}.{CDATE[4:6]}.{CDATE[6:8]}"

    self.OUTDIR = f"{COMROT}/{OFS}/{fdate}"
    outfile = f"{self.OUTDIR}/liveocean.in"

    if not os.path.exists(self.OUTDIR):
      os.makedirs(self.OUTDIR)

    DSTART = util.ndays(CDATE,self.TIME_REF)
    # DSTART = days from TIME_REF to start of forecast day larger minus smaller date

    settings = {
      "__NTIMES__"   : cfDict['NTIMES'],
      "__TIME_REF__" : cfDict['TIME_REF'],
      "__DSTART__"   : DSTART,
      "__FDATE__"    : fdate,
      "__ININAME__"  : cfDict['ININAME']
    }

    # Create the ocean.in
    util.makeOceanin(self.NPROCS,settings,template,outfile)





  def __make_oceanin_adnoc(self, cfDict):
    
    CDATE = self.CDATE
    HH = self.HH
    OFS = self.OFS
    COMROT = self.COMROT
    TEMPLPATH = self.TEMPLPATH

    if self.OUTDIR == "auto":
      self.OUTDIR = f"{COMROT}/{OFS}/{CDATE}"

    # TODO: fix this - don't need two variables for the same thing do we?
    cfDict['OUTDIR'] = self.OUTDIR
    self.OUTDIR = self.OUTDIR

    if not os.path.exists(self.OUTDIR):
      os.makedirs(self.OUTDIR)

    settings = {
      "__NTIMES__"   : cfDict['NTIMES'],
      "__TIME_REF__" : cfDict['TIME_REF'],
    }

    if self.OCNINTMPL == "auto":
      template = f"{TEMPLPATH}/{OFS}.ocean.in"
    else:
      template = self.OCNINTMPL

    outfile = f"{self.OUTDIR}/ocean.in"

    # Create the ocean.in
    if self.OCEANIN == "auto":
      util.makeOceanin(self.NPROCS,settings,template,outfile)

    return


if __name__ == '__main__':
  pass 
