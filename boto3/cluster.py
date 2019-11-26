#!/usr/bin/env python3

import boto3
import time

# class Cluster:

# Should create a class to initialize and hold this instance data
image_id='ami-01d859635d7625db5'
key_name='patrick-ioos-cloud-sandbox'
sg_id1='sg-006041073bfa7b072'
sg_id2='sg-0a48755f7b926b051'
sg_id3='sg-04a6bcecaec589f64'
subnet_id='subnet-09dae53e246bd68e4'
placement_group='IOOS-cloud-sandbox-cluster-placement-group'



''' Function  Definitions '''
'''-----------------------'''

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
  if nodeType.startswith('c5') :
    group = { 'GroupName': placement_group }
    return group
########################################################################




########################################################################
def netInterface(nodeType) :

  interfaceDict = {
        'AssociatePublicIpAddress': True,
        'DeleteOnTermination': True,
        'Description': 'Network adaptor via boto3 api',
        'DeviceIndex': 0,
        'Groups': [ sg_id1,  sg_id2, sg_id3 ],
        'SubnetId': subnet_id
  }

  if nodeType == 'c5n.18xlarge' :
    interfaceDict['InterfaceType'] = 'efa'

  return interfaceDict
########################################################################





########################################################################
def createNodes(count, nodeType, tags) :

  # Add error checking
  # If interface is efa, node must by c5n.18xlarge
  # Can only add some types to placement group: C3, C4, C5, C5d, C5n
  # REGION us-east-1
  # ami-01d859635d7625db5 - CentOS7updated-GCC6.5-IMPI2002-EFA-EFS
  min_count=count
  max_count=count
  instance_type=nodeType

  ec2 = boto3.resource('ec2')

  instances = ec2.create_instances(
    ImageId=image_id,
    InstanceType=instance_type,
    KeyName=key_name,
    MinCount=min_count,    
    MaxCount=max_count,
    #Placement={
    #  'GroupName': placement_group
    #},
    NetworkInterfaces=[
      {
        'AssociatePublicIpAddress': True,
        'DeleteOnTermination': True,
        'Description': 'EFA Network adaptor via BOTO create_instances',
        'DeviceIndex': 0,
        'Groups': [ sg_id1,  sg_id2, sg_id3 ],
        'SubnetId': subnet_id,
        #'InterfaceType': interface
      }
    ],
    TagSpecifications=[
      {
        'ResourceType': 'instance',
        'Tags': tags
      }
    ]

#    Placement={
#      placementGroup
#    },
#    NetworkInterfaces = [ netInterface(nodeType) ]
#    
  )

  return instances
########################################################################




''' Function: terminate_nodes '''
''' ------------------------- '''
########################################################################
def terminateNodes(instances) :

  import time

  print('Terminating instances: ',instances)

  ec2 = boto3.resource('ec2')

  responses = []

  for instance in instances :
    response = instance.terminate()
    responses.append(response)

  return responses
########################################################################
'''
{
    'TerminatingInstances': [
        {
            'CurrentState': {
                'Code': 123,
                'Name': 'pending'|'running'|'shutting-down'|'terminated'|'stopping'|'stopped'
            },
            'InstanceId': 'string',
            'PreviousState': {
                'Code': 123,
                'Name': 'pending'|'running'|'shutting-down'|'terminated'|'stopping'|'stopped'
            }
        },
    ]
}
'''
