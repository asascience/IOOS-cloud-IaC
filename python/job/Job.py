from abc import ABC, abstractmethod
import json

debug = False

class Job(ABC) :
  ''' This is an abstract base class for cloud clusters.
      It defines a generic interface to implement
  '''
  
  @abstractmethod
  def __init__(self) :
    self.configfile = ''
    self.jobtype = ''
    self.CDATE = ''
    self.HH = ''
    self.OFS = ''
    self.OUTDIR = ''
    self.INDIR = ''
    self.NPROCS = 0
    self.settings = {}
 
  ########################################################################


  def readConfig(self, configfile) :

    # TODO call the regular function in this module
    with open(configfile, 'r') as cf:
      cfDict = json.load(cf)

    if (debug) :
      print(json.dumps(cfDict, indent=4))
      print(str(cfDict))

    # Could do the parse here instead also, more than one way to do it
    return cfDict

  ######################################################################## 


  #@abstractmethod
  #def __parseConfig(self, cfDict) : 
  #pass



