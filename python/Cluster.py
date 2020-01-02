from abc import ABC, abstractmethod

''' This is an abstract base class for cloud clusters.
    It defines a generic interface to implement
'''
class Cluster(ABC) :

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

  # dependency here on nodeInfo - nodeType must be defined there
  #self.PPN = nodeInfo.getPPN(nodeType)

  ## getPPN - get the number of processors per node 
  @abstractmethod
  def getCoresPN(self) :
    return self.PPN

  ## getState
  #@abstractmethod
  def getState(this) :
    return this.__state


  ## setState
  #@abstractmethod
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

