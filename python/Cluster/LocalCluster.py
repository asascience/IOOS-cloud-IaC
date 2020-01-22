import time
import json
import os

import boto3
from botocore.exceptions import ClientError

import Cluster.nodeInfo as nodeInfo

from Cluster import Cluster

debug = False

class LocalCluster(Cluster.Cluster) :

  def __init__(self, configfile) :

    self.configfile = configfile

    self.__state = "none"   # This could be an enumeration of none, running, stopped, error
    self.platform  = 'Local'
    self.nodeType  = os.uname().sysname
    self.nodeCount = 1

    self.readConfig(configfile)
    #self.PPN = os.cpu_count()
    self.PPN = len(os.sched_getaffinity(0))

  ''' 
  Function  Definitions
  =====================
  '''

  # Implement these interfaces

  ## getState
  def getState(this) :
    return this.__state


  ## setState
  def setState(this, state) :
    this.__state = state
    return this.__state


  ########################################################################
  ########################################################################
  def readConfig(self, configfile) :

    with open(configfile, 'r') as cf:
      cfDict = json.load(cf)

    if (debug) :
      print(json.dumps(cfDict, indent=4))
      print(str(cfDict))

    # Could do the parse here instead also, more than one way to do it
    #return cfDict
    self.__parseConfig(cfDict)

    return
  ########################################################################



  ########################################################################
  def __parseConfig(self, cfDict) :
    self.platform  = cfDict['platform']
    return
  ########################################################################


  def getCoresPN(self) :
    return self.PPN

  def start(self) :
     return

  def terminate(self) :
     return

  def getHosts(self) :
    return [os.uname().nodename]

  def getHostsCSV(self) :
    return os.uname().nodename

