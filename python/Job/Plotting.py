import sys
import json

from Job import Job

sys.path.insert(0, '..')      
import romsUtil as util


class Plotting(Job.Job):


  def __init__(self, configfile, NPROCS):

    debug = True

    self.__jobtype = 'plotting'
    self.configfile = configfile
    self.NPROCS = NPROCS

    with open(configfile, 'r') as cf:
      jobDict = json.load(cf)
    
    if (debug) :
      print(json.dumps(jobDict, indent=4))
      print(str(jobDict))

    self.OFS = jobDict['OFS']
    self.CDATE = jobDict['CDATE']
    self.HH = jobDict['HH']
    self.INDIR = jobDict['INDIR']
    self.OUTDIR = jobDict['OUTDIR']
    self.VARS = jobDict['VARS']

    # TODO: use a read config and parse config subroutine as in AWSCluster
