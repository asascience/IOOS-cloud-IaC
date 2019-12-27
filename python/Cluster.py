
from abc import ABC, abstractmethod
import nodeInfo

class Cluster(ABC) :

#  __configFile = ''
#  __instances = []
#cluster = AWSCluster(platform,nodeType,nodes,tags)

  def __init__(self, platform, nodeType, nodeCount) :


    # We can use a Factory pattern here, can either have a type parameter, or infer it from the nodeType
    #self.__configFile = configFile
    # Or, self.platform = getPlatform(nodeType)
    self.platform = platform   # only AWS is valid currently
    self.nodeCount = nodeCount
    self.nodeType = nodeType
    self.__state = "none"      # This should be an enumeration of none, running, stopped, error
    self.__instances = []

    # dependency here on nodeInfo - nodeType must be defined there
    self.PPN = nodeInfo.getPPN(nodeType)


  ## getPPN - get the number of processors per node 
  #@abstractmethod
  def getCoresPN(self) :
    return self.PPN
    #pass
  
  ''' 
  Abstract Function Definitions
  ==============================
  '''
  
  # We want these to be polymorphic

  ## start
  @abstractmethod
  def start() :
    pass

  ## terminate  
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
  

  @abstractmethod
  def getState() :
    pass
