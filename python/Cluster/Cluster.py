from abc import ABC, abstractmethod
from subprocess import Popen

''' This is an abstract base class for cloud clusters.
    It defines a generic interface to implement
'''
class Cluster(ABC) :

  __daskscheduler: Popen

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
    print('............................................  In setDaskScheduler')
    self.__daskscheduler = proc
    return proc


  def terminateDaskScheduler(self):
    print('............................................  In terminateDaskScheduler')

    poll = self.__daskscheduler.poll()

    if poll == None:
      # Process hasn't terminated yet, terminate it
      self.__daskscheduler.terminate()

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

