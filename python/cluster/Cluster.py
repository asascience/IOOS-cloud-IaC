"""

Abstract base class for a compute cluster. A cluster can also be a single machine.
This class needs to be implemented and extended for specific cloud providers.

"""
from abc import ABC, abstractmethod
from subprocess import Popen
import time

  """
  Parameters
  ----------
  var : type
    Desc

  Returns
  -------
  var : type
    Desc

  Raises
  ------
  excep
    Desc

  Notes
  -----
  
  """

class Cluster(ABC) :
  """ 
  Abstract base class for cloud clusters. It defines a generic interface to implement

  Attributes
  ----------
  daskscheduler - a reference to the Dask scheduler process started on the cluster
  daskworker    - a reference to the Dask worker process started on the cluster

  Methods
  -------
  setDaskScheduler(proc: Popen)
    Save the Popen process for dask-scheduler

  terminateDaskScheduler()
    Cleanup/kill the dask-scheduler process

  setDaskWorker(proc: Popen)
    Save the Popen process for dask-worker

  terminateDaskWorker()
    Cleanup/kill the dask-worker process

  Abstract Methods
  ----------------
  TODO: Can use class properties for some of these instead.

  getCoresPN()
    Get the number of cores per node in this cluster. Assumes a heterogenous cluster.
  getState()
    Get the cluster state.
  setState()
    Set the cluster state.
    TODO: Can use a class property instead.
  readConfig()
    Read the cluster configuration.
  start()
    Start the cluster.
  terminate()
    Terminate the cluster.
  getHosts()
    Get the list of hosts in this cluster 
  getHostsCSV() :
    Get a comma separated list of hosts in this cluster

  """

  def __init__(self):
    self.daskscheduler = None
    self.daskworker = None


  # This assumes scheduler is on only one node ... 
  # TODO: Make this scalable to multiple nodes
  # If the daskScheduler will be this closely coupled to the architecture it could be here
  def setDaskScheduler(self,  proc: Popen ):
    self.daskscheduler = proc
    return proc

  def terminateDaskScheduler(self):
    """ If process hasn't terminated yet, terminate it. """
    if self.daskscheduler != None: 
      poll = self.daskscheduler.poll()
      if poll == None:
        self.daskscheduler.kill()
    return



  def setDaskWorker(self,  proc: Popen ):
    self.daskworker = proc
    return proc

  def terminateDaskWorker(self):
    """ If process hasn't terminated yet, terminate it. """
    if self.daskworker != None: 
      poll = self.daskworker.poll()

      if poll == None:
        self.daskworker.kill()
    return


  """ 
  Abstract Function Definitions
  ==============================
  """

  @abstractmethod
  def getCoresPN() :
    pass

  @abstractmethod
  def getState() :
    pass


  @abstractmethod
  def setState() :
    pass
    
  @abstractmethod
  def readConfig() :
    pass

  @abstractmethod
  def start() :
    pass

  @abstractmethod
  def terminate() :
    pass

  ## get the list of hostnames or IPs in this cluster 
  @abstractmethod
  def getHosts() :
    pass

  ## get a comma separated list of hosts in this cluster
  @abstractmethod
  def getHostsCSV() :
    pass

