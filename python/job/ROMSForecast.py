import sys
import json
import os
import datetime

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
    self.make_oceanin()



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

    if self.CDATE == "today":
      today = datetime.date.today().strftime("%Y%m%d")
      self.CDATE = today

    if self.OCNINTMPL == "auto":
      self.OCNINTMPL = f"{self.TEMPLPATH}/{OFS}.ocean.in"

    return
  ########################################################################




  def make_oceanin(self) :
    
    OFS = self.OFS
    
    # Create the ocean.in file from a template 
    # TODO: Make ocean in for NOSOFS
    if OFS == 'liveocean':
      self.__make_oceanin_lo()
    elif OFS == 'adnoc':
      self.__make_oceanin_adnoc()
    elif OFS == 'cbofs':
      template = f"TODO-cbofstemplate"
      outfile = f"TODO-template"
    else :
      raise Exception(f"{OFS} is not a supported forecast")

    return
  ########################################################################




  def __make_oceanin_lo(self):

    CDATE = self.CDATE
    HH = self.HH
    OFS = self.OFS
    COMROT = self.COMROT

    template = self.OCNINTMPL

    #fdate = f"f{CDATE[0:4]}.{CDATE[4:6]}.{CDATE[6:8]}"
    fdate = util.lo_date(CDATE)
    prevdate = util.ndate(CDATE, -1)
    fprevdate = util.lo_date(prevdate)

    if self.OUTDIR == "auto":
      self.OUTDIR = f"{COMROT}/{OFS}/{fdate}"
      outfile = f"{self.OUTDIR}/liveocean.in"

    if not os.path.exists(self.OUTDIR):
      os.makedirs(self.OUTDIR)

    if self.ININAME == "auto":
      self.ININAME = f"/com/liveocean/{fprevdate}/ocean_his_0025.nc"

    DSTART = util.ndays(CDATE,self.TIME_REF)
    # DSTART = days from TIME_REF to start of forecast day larger minus smaller date

    settings = {
      "__NTIMES__"   : self.NTIMES,
      "__TIME_REF__" : self.TIME_REF,
      "__DSTART__"   : DSTART,
      "__FDATE__"    : fdate,
      "__ININAME__"  : self.ININAME
    }

    # Create the ocean.in
    if self.OCEANIN == "auto":
      util.makeOceanin(self.NPROCS,settings,template,outfile)

    return
  ########################################################################





  def __make_oceanin_adnoc(self):
    
    CDATE = self.CDATE
    HH = self.HH
    OFS = self.OFS
    COMROT = self.COMROT

    if self.OUTDIR == "auto":
      self.OUTDIR = f"{COMROT}/{OFS}/{CDATE}"

    if not os.path.exists(self.OUTDIR):
      os.makedirs(self.OUTDIR)

    settings = {
      "__NTIMES__"   : cfDict['NTIMES'],
      "__TIME_REF__" : cfDict['TIME_REF'],
    }

    template = self.OCNINTMPL

    outfile = f"{self.OUTDIR}/ocean.in"

    # Create the ocean.in
    if self.OCEANIN == "auto":
      util.makeOceanin(self.NPROCS,settings,template,outfile)

    return
  ########################################################################


if __name__ == '__main__':
  pass 
