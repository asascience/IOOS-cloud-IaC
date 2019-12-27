import boto3
import time
from botocore.exceptions import ClientError

from Cluster import Cluster
import nodeInfo

class AWSCluster(Cluster) :

#  __configFile = ''
#  __instances = []

  def __init__(self, platform, nodeType, nodeCount, tags) :

    # Call the parent constructor
    Cluster.__init__(self, platform, nodeType, nodeCount)
    #self.platform = platform   # only AWS is valid currently
    #self.nodeCount = nodeCount
    #self.nodeType = nodeType
    #self.__state = "none"
    #self.__instances = []
    #self.PPN = nodeInfo.getPPN(self.nodeType)

    self.tags = tags
    self.image_id = 'ami-04a10608958c0c138'   # HDF5 1.10.5, NetCDF 4.5
    self.key_name = 'patrick-ioos-cloud-sandbox'
    self.sg_id1 = 'sg-006041073bfa7b072'
    self.sg_id2 = 'sg-0a48755f7b926b051'
    self.sg_id3 = 'sg-04a6bcecaec589f64'
    self.subnet_id = 'subnet-09dae53e246bd68e4'
    self.placement_group = 'IOOS-cloud-sandbox-cluster-placement-group'


  ''' 
  Function  Definitions
  =====================
  '''


  def start(self) :
     return self.__AWScreateCluster()

  def terminate(self) :
     return self.__AWSterminateCluster()

  def getHosts(self) :
    return self.__AWSgetHosts()

  def getHostsCSV(self) :
    return self.__AWSgetHostsCSV()

  def getState(self) :
    return self.__state

  #def getPPN(self) :
  #return self.PPN

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
  
    ec2 = boto3.resource('ec2')
  
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

        # TODO : Do not need function parameter with this class instance
        Placement= self.__AWSplacementGroup(),
        NetworkInterfaces = [ self.__AWSnetInterface() ],
        CpuOptions={
          'CoreCount': self.PPN,
          'ThreadsPerCore': 1
        }
        
      )
    except ClientError as e:
      print('ClientError exception in createCluster' + str(e))
      raise Exception() from e
  
  
    # Make sure the nodes are running before returning
  
    client = boto3.client('ec2')
    waiter = client.get_waiter('instance_running')
  
    for instance in self.__instances:
      waiter.wait(
        InstanceIds=[instance.instance_id],
        WaiterConfig={
          'Delay': 5,
          'MaxAttempts': 12
        }
      )
  
    # Wait another 30 seconds, sshd is sometimes slow to come up
    time.sleep(30) 
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
      __AWSterminateCluster()
      raise Exception('Nodes did not start within time limit... terminating them...')    
  
    return self.__instances
   
  ########################################################################
  
  
  
  
  ''' Function: terminate_nodes '''
  ########################################################################
  def __AWSterminateCluster(self) :
  
    print('Terminating instances: ',self.__instances)
  
    ec2 = boto3.resource('ec2')
  
    responses = []
  
    for instance in self.__instances :
      response = instance.terminate()['TerminatingInstances']
      responses.append(response)
  
    return responses
  ########################################################################
