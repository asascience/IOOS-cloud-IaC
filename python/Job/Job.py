from abc import ABC, abstractmethod

''' This is an abstract base class for cloud clusters.
    It defines a generic interface to implement
'''
class Job(ABC) :

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
  
