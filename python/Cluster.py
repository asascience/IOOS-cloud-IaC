#!/usr/bin/env python3

import nodeInfo



class Cluster:

#  __configFile = ''
#  __instances = []

  def __init__(self, nodes, nodeType, tags)
    #self.__configFile = configFile
    self.nodes = nodes
    self.nodeType = nodeType
    self.tags = tags
    self.image_id = 'ami-04a10608958c0c138'   # HDF5 1.10.5, NetCDF 4.5
    self.key_name = 'patrick-ioos-cloud-sandbox'
    self.sg_id1 = 'sg-006041073bfa7b072'
    self.sg_id2 = 'sg-0a48755f7b926b051'
    self.sg_id3 = 'sg-04a6bcecaec589f64'
    self.subnet_id = 'subnet-09dae53e246bd68e4'
    self.placement_group = 'IOOS-cloud-sandbox-cluster-placement-group'
    self.__instances = []
    self.PPN = nodeInfo.getPPN(nodeType)



''' 
Function  Definitions
=====================
'''


def start()
   return __AWScreateCluster()


def terminate()
   return __AWSterminateCluster()


def getPPN()
  return self.PPN


def getHostsCSV() :
  return __AWSgetHostsCSV()


  
########################################################################
def __AWSgetHostsCSV() :
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
def __AWSplacementGroup(nodeType) :
  group = {} 
  if nodeType.startswith('c5') :
    group = { 'GroupName': placement_group }

  return group
########################################################################




########################################################################
# Specify an efa enabled network interface if supported by node type
# Also attaches security groups
#
# TODO: refactor Groups
def __AWSnetInterface(nodeType) :

  interface = {
        'AssociatePublicIpAddress': True,
        'DeleteOnTermination': True,
        'Description': 'Network adaptor via boto3 api',
        'DeviceIndex': 0,
        'Groups': [ sg_id1,  sg_id2, sg_id3 ],
        'SubnetId': subnet_id
  }

  if nodeType == 'c5n.18xlarge' :
    interface['InterfaceType'] = 'efa'

  return interface
########################################################################





########################################################################
def __AWScreateCluster() :

  ec2 = boto3.resource('ec2')

  try: 
    self.__instances = ec2.create_instances(
      ImageId=self.image_id,
      InstanceType=self.nodeType,
      KeyName=self.key_name,
      MinCount=self.count,    
      MaxCount=self.count,
      TagSpecifications=[
        {
          'ResourceType': 'instance',
          'Tags': self.tags
        }
      ],
      Placement= __AWSplacementGroup(self.nodeType),
      NetworkInterfaces = [ __AWSnetInterface(self.nodeType) ],
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
def __AWSterminateCluster() :

  print('Terminating instances: ',self.__instances)

  ec2 = boto3.resource('ec2')

  responses = []

  for instance in self.__instances :
    response = instance.terminate()['TerminatingInstances']
    responses.append(response)

  return responses
########################################################################
