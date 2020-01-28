import sys
import json
import os

if os.path.abspath('..') not in sys.path:
    sys.path.append(os.path.abspath('..'))

from job.Job import Job

import romsUtil as util


class Plotting(Job):


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
    self.BUCKET = jobDict['BUCKET']
    self.BCKTFLDR = jobDict['BCKTFLDR']

    # TODO: use a read config and parse config subroutine as in AWSCluster

if __name__ == '__main__':
  pass
