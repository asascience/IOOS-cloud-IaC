from Job import Job

class ROMSForecast(Job.Job):

  debug = True
  TEMPLPATH = "./templates"
  COMDIR = "/com"

  def __init__(self, configfile):

    self.configfile = configfile

    self.jobtype = 'forecast'

    with open(configfile, 'r') as cf:
      jobDict = json.load(cf)
    
    if (debug) :
      print(json.dumps(jobDict, indent=4))
      print(str(jobDict))

    self.CDATE = jobDict['CDATE']
    self.HH = jobDict['HH']
    self.OFS = jobDict['OFS']
    self.TIME_REF = jobDict['TIME_REF']

    # Easier to use 
    CDATE = self.CDATE
    HH = self.HH
    OFS = self.OFS
    TIME_REF = self.TIME_REF
 
    # TODO: Make ocean in for NOSOFS
    if OFS == 'liveocean':
  
      # LiveOcean requires a significant amount of available RAM to run > 16GB
      # NTIMES 90 is 1 hour for liveocean 
      # Using f-strings
      # Add stuff to the replacement dictionary 
      dirdate = f"f{CDATE[0:4]}.{CDATE[4:6]}.{CDATE[6:8]}"
      template = f"{TEMPLPATH}/{OFS}.ocean.in"
      outfile = f"/com/{OFS}/{fdate}/liveocean.in"
  
      # Add this to dictionary
      jobDict['COMOUT'] = f"{COMDIR}/{OFS}/{fdate}"
  
      DSTART = util.ndays(CDATE,TIME_REF)
      # DSTART = days from TIME_REF to start of forecast day larger minus smaller date
  
      # TODO : parameterize this ININAME
      self.settings = {
        "__NTIMES__"   : jobDict['NTIMES'],
        "__TIME_REF__" : jobDict['TIME_REF'],
        "__DSTART__"   : DSTART,
        "__FDATE__"    : fdate,
        "__ININAME__"  : jobDict['ININAME']
      }
  
    elif cluster.OFS == 'cbofs':
      template = f"TODO-cbofstemplate"
      outfile = f"TODO-template"
    else :
      print("unsupported model")
      # TODO: Throw exception
  
  
