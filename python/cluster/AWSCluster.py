import time
import json
import logging

import boto3
from botocore.exceptions import ClientError

import cluster.nodeInfo as nodeInfo

from cluster import Cluster

debug = False

#logging.basicConfig(format='%(asctime)s %(levelname)s - %(funcName)s %(message)s', level=logging.DEBUG)

log = logging.getLogger('workflow')
log.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter(' %(asctime)s  %(levelname)s - %(module)s.%(funcName)s | %(message)s')
#ch.setFormatter(formatter)
#log.addHandler(ch)

class AWSCluster(Cluster.Cluster) :

  def __init__(self, configfile) :

    # Call the parent constructor??
    # Cluster.__init__(self)
    self.daskscheduler = None
    
    self.configfile = configfile
    self.__state = "none"   # This could be an enumeration of none, running, stopped, error
    self.__instances = []
    self.platform  = 'AWS'
    self.nodeType  = ''
    self.nodeCount = 0
    self.NPROCS    = 0
    self.tags      = []
    self.image_id  = ''
    self.key_name  = ''
    self.sg_id1    = ''
    self.sg_id2    = ''
    self.sg_id3    = ''
    self.subnet_id = ''
    self.placement_group = ''

    #cfDict = self.readConfig(configfile)
    #self.__parseConfig(cfDict)
    self.readConfig(configfile)

    self.PPN = nodeInfo.getPPN(self.nodeType)
    self.NPROCS = self.nodeCount * self.PPN

    log.info(f"nodeCount: {self.nodeCount}  PPN: {self.PPN}")

    # Can do it this way also - nested functions
    #self.__parseConfig(self.readConfig(configfile))
    

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

# Moved to job config
#    self.OFS       = cfDict['OFS']
#    self.CDATE     = cfDict['CDATE']
#    self.HH        = cfDict['HH']
   
    self.platform  = cfDict['platform']
    self.region    = cfDict['region']
    self.nodeType  = cfDict['nodeType']
    self.nodeCount = cfDict['nodeCount'] 
    self.tags      = cfDict['tags']
    self.image_id  = cfDict['image_id']
    self.key_name  = cfDict['key_name']
    self.sg_id1    = cfDict['sg_id1']
    self.sg_id2    = cfDict['sg_id2']
    self.sg_id3    = cfDict['sg_id3']
    self.subnet_id = cfDict['subnet_id']
    self.placement_group = cfDict['placement_group']

    return
  ########################################################################


  # TODO: make this consistent
  # TODO: add nprocs field
  def getCoresPN(self) :
    return self.PPN

  def start(self) :
    return self.__AWScreateCluster()

  def terminate(self) :
    self.terminateDaskScheduler()
    return self.__AWSterminateCluster()

  def getHosts(self) :
    return self.__AWSgetHosts()

  def getHostsCSV(self) :
    return self.__AWSgetHostsCSV()

#  def getState(self) :
#    return self.__state


  ########################################################################
  def __AWSgetHosts(self) :
    hosts = []

    for instance in self.__instances :
      hosts.append(instance.private_dns_name)
    return hosts
  ########################################################################


  
  ########################################################################
  def __AWSgetHostsCSV(self) :
    hosts = ''

    instcnt=len(self.__instances)
    cnt=0
    for instance in self.__instances :
      cnt += 1
      hostname=instance.private_dns_name
      # no comma on last host
      if cnt == instcnt :
        hosts += hostname
      else :
        hosts += hostname + ','
    return hosts
  ########################################################################



  ########################################################################
  # This is a bit of a hack to satisfy AWS
  def __AWSplacementGroup(self) :
    group = {} 
    if self.nodeType.startswith('c5') :
      group = { 'GroupName': self.placement_group }
  
    return group
  ########################################################################
  
  
  
  
  ########################################################################
  # Specify an efa enabled network interface if supported by node type
  # Also attaches security groups
  #
  # TODO: refactor Groups
  def __AWSnetInterface(self) :
  
    interface = {
          'AssociatePublicIpAddress': True,
          'DeleteOnTermination': True,
          'Description': 'Network adaptor via boto3 api',
          'DeviceIndex': 0,
          'Groups': [ self.sg_id1, self.sg_id2, self.sg_id3 ],
          'SubnetId': self.subnet_id
    }
  
    if self.nodeType == 'c5n.18xlarge' :
      interface['InterfaceType'] = 'efa'

    return interface
  ########################################################################
  
  
  
  
  
  ########################################################################
  def __AWScreateCluster(self) :
  
    ec2 = boto3.resource('ec2',region_name=self.region)
  
    try: 
      self.__instances = ec2.create_instances(
        ImageId=self.image_id,
        InstanceType=self.nodeType,
        KeyName=self.key_name,
        MinCount=self.nodeCount,    
        MaxCount=self.nodeCount,
        TagSpecifications=[
          {
            'ResourceType': 'instance',
            'Tags': self.tags
          }
        ],
        Placement= self.__AWSplacementGroup(),
        NetworkInterfaces = [ self.__AWSnetInterface() ],
        CpuOptions={
          'CoreCount': self.PPN,
          'ThreadsPerCore': 1
        }
        
      )
    except ClientError as e:
      log.exception('ClientError exception in createCluster' + str(e))
      raise Exception() from e
  
 
    print('Waiting for nodes to enter running state ...') 
    # Make sure the nodes are running before returning
  
    client = boto3.client('ec2', self.region)
    waiter = client.get_waiter('instance_running')
  
    for instance in self.__instances:
      waiter.wait(
        InstanceIds=[instance.instance_id],
        WaiterConfig={
          'Delay': 5,
          'MaxAttempts': 12
        }
      )
  
    # Wait a little more. sshd is sometimes slow to come up
    time.sleep(60) 
    # Assume the nodes are ready, set to False if not
    ready=True
  
    # if any instance is not running, ready=False
    inum=1
    for instance in self.__instances :
      state=ec2.Instance(instance.instance_id).state['Name']
      print ('instance ' + str(inum) + ' : ' + state)
      if state != 'running':
        ready=False
      inum+=1
  
    if not(ready) :
      self.__AWSterminateCluster()
      raise Exception('Nodes did not start within time limit... terminating them...')    
  
    return self.__instances
   
  ########################################################################
  
  
  
  
  ''' Function: terminate_nodes '''
  ########################################################################
  def __AWSterminateCluster(self) :

    # Terminate any running dask scheduler 
    self.terminateDaskScheduler()

    log.info(f"Terminating instances: {self.__instances}")
    
    ec2 = boto3.resource('ec2',region_name=self.region)
  
    responses = []
  
    for instance in self.__instances :
      response = instance.terminate()['TerminatingInstances']
      responses.append(response)
  
    return responses
  ########################################################################
