from abc import ABC, abstractmethod
from subprocess import Popen
import time


class Cluster(ABC) :
  ''' This is an abstract base class for cloud clusters.
      It defines a generic interface to implement
  '''

  def __init__(self):

    self.daskscheduler = None
    self.daskworker = None

  #  __configFile = ''
  #  __instances = []
  #cluster = AWSCluster(platform,nodeType,nodes,tags)

  # Idea: We can use a Factory pattern here, can either have a type parameter, or infer it from the nodeType
  # self.__configFile = configFile
  # Or, self.platform = getPlatform(nodeType)

  #self.nodeCount = nodeCount
  #self.nodeType = nodeType
  #self.__state = "none"   # This should be an enumeration of none, running, stopped, error
  #self.__instances = []

  # This assumes scheduler is on only one node ... 
  # TODO: Make this scalable to multiple nodes
  # If the daskScheduler will be this closely coupled to the architecture it could be here
  def setDaskScheduler(self,  proc: Popen ):
    self.daskscheduler = proc
    return proc


  def terminateDaskScheduler(self):
    if self.daskscheduler != None: 
      poll = self.daskscheduler.poll()

      if poll == None:
        # Process hasn't terminated yet, terminate it
        print("In Cluster.terminateDaskScheduler")
        self.daskscheduler.kill()
        time.sleep(3)
    return

  def setDaskWorker(self,  proc: Popen ):
    print('............................................  In setDaskScheduler')
    self.daskworker = proc
    return proc


  def terminateDaskWorker(self):
    print('............................................  In terminateDaskScheduler')

    if self.daskworker != None: 
      poll = self.daskworker.poll()

      if poll == None:
        # Process hasn't terminated yet, terminate it
        print("In Cluster.terminateDaskScheduler")
        self.daskworker.kill()
        time.sleep(3)
    return

  ## getPPN - get the number of processors per node 
  @abstractmethod
  def getCoresPN(self) :
    return self.PPN

  ## getState
  @abstractmethod
  def getState(this) :
    return this.__state


  ## setState
  @abstractmethod
  def setState(this, state) :
    this.__state = state
    return this.__state

  
  ''' 
  Abstract Function Definitions
  ==============================
  '''
  
  # We want these to be polymorphic

  ## start
  @abstractmethod
  def readConfig() :
    pass

  ## start
  @abstractmethod
  def start() :
    pass


  ## terminate  
  @abstractmethod
  def terminate() :
    pass



  ## getHosts 
  ## get the list of hostnames or IPs in this cluster 
  @abstractmethod
  def getHosts() :
    pass

 
  ## getHostsCSV
  ## get a comma separated list of hosts in this cluster
  @abstractmethod
  def getHostsCSV() :
    pass

