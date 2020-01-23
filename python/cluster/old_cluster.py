#!/usr/bin/env python3

import boto3
import time
from botocore.exceptions import ClientError
import nodeInfo

# Can use dependency injection / service dependency for interface layer, platform agnostic
# One pattern on a service constructor, e.g. this.cluster = new clusterService(aws | azure | gcp)
# where aws | azure | gcp have the implemented methods 


# Should create a class to initialize and hold this instance data
# eg class Cluster:
# REGION us-east-1
# ami-01d859635d7625db5 - CentOS7updated-GCC6.5-IMPI2002-EFA-EFS
# image_id='ami-01d859635d7625db5'  # netcdf 4.2

#image_id='ami-099cf72623c9aa846'  # NetCDF 4.5 HDF5 parallel
#image_id='ami-00114486c1dc4ec09'  # NetCDF 4.5 HDF5 serial
image_id='ami-04a10608958c0c138'   # HDF5 1.10.5, NetCDF 4.5
key_name='patrick-ioos-cloud-sandbox'
sg_id1='sg-006041073bfa7b072'
sg_id2='sg-0a48755f7b926b051'
sg_id3='sg-04a6bcecaec589f64'
subnet_id='subnet-09dae53e246bd68e4'
placement_group='IOOS-cloud-sandbox-cluster-placement-group'

'''
CpuOptions={
        'CoreCount': 123,
        'ThreadsPerCore': 123
    },
'''


''' 
Function  Definitions
=====================
'''

########################################################################
def getHosts(instances) :
  hosts = []

  for instance in instances :
    hostname=instance.private_dns_name
    hosts.append(hostname)

  return hosts
########################################################################



########################################################################
def getHostsCSV(instances) :
  hosts = ''

  instcnt=len(instances)
  cnt=0
  for instance in instances :
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
def describeInstance(instance) :
  client = boto3.client('ec2')
  return client.describe_instances(InstanceIds=[instance.instance_id]) 
  
########################################################################




########################################################################
def getClient() :
  client = boto3.client('ec2')
  return client
########################################################################




########################################################################
def placementGroup(nodeType) :
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
def netInterface(nodeType) :

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
def createNodes(count, nodeType, tags) :

  # Add error checking
  # REGION us-east-1
  # ami-01d859635d7625db5 - CentOS7updated-GCC6.5-IMPI2002-EFA-EFS
  min_count=count
  max_count=count
  instance_type=nodeType
  

  ec2 = boto3.resource('ec2')

  instances = []

  try: 
    instances = ec2.create_instances(
      ImageId=image_id,
      InstanceType=instance_type,
      KeyName=key_name,
      MinCount=min_count,    
      MaxCount=max_count,
      TagSpecifications=[
        {
          'ResourceType': 'instance',
          'Tags': tags
        }
      ],
      Placement= placementGroup(nodeType),
      NetworkInterfaces = [ netInterface(nodeType) ],
      CpuOptions={
        'CoreCount': nodeInfo.getPPN(instance_type),
        'ThreadsPerCore': 1
      }
      
    )
  except ClientError as e:
    print('ClientError exception in createNodes' + str(e))
    raise Exception() from e


  # Make sure the nodes are running before returning

  client = boto3.client('ec2')
  waiter = client.get_waiter('instance_running')

  # print('Waiting for instances to enter running state ...')
  for instance in instances:
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
  for instance in instances :
    state=ec2.Instance(instance.instance_id).state['Name']
    print ('instance ' + str(inum) + ' : ' + state)
    if state != 'running':
      ready=False
    inum+=1

  if not(ready) :
    terminateNodes(instances)
    raise Exception('Nodes did not start within time limit... terminating them...')    


  return instances
########################################################################




''' Function: terminate_nodes '''
########################################################################
def terminateNodes(instances) :

  print('Terminating instances: ',instances)

  ec2 = boto3.resource('ec2')

  responses = []

  for instance in instances :
    response = instance.terminate()['TerminatingInstances']
    responses.append(response)

  return responses
########################################################################
