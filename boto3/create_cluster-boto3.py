#!/usr/bin/env python3

import boto3

image_id='ami-01d859635d7625db5'
min_count=1
max_count=1
instance_type='c5n.18xlarge'
key_name='patrick-ioos-cloud-sandbox'
sg_id1='sg-006041073bfa7b072'
sg_id2='sg-0a48755f7b926b051'
sg_id3='sg-04a6bcecaec589f64'
subnet_id='subnet-09dae53e246bd68e4'
placement_group='IOOS-cloud-sandbox-cluster-placement-group'

ec2 = boto3.resource('ec2')

instances = ec2.create_instances(
  ImageId=image_id,
  InstanceType=instance_type,
  KeyName=key_name,
  MinCount=min_count,    
  MaxCount=max_count,
  Placement={
    'GroupName': placement_group
  },
  NetworkInterfaces=[
    {
      'AssociatePublicIpAddress': True,
      'DeleteOnTermination': True,
      'Description': 'EFA Network adaptor via BOTO create_instances',
      'DeviceIndex': 0,
      'Groups': [ sg_id1,  sg_id2, sg_id3 ],
      'SubnetId': subnet_id,
      'InterfaceType': 'efa'
    }
  ],
  TagSpecifications=[
    {
      'ResourceType': 'instance',
      'Tags': [
        {
          'Key': 'Name',
          'Value': 'IOOS-cloud-sandbox'
        },
        {
          'Key': 'NAME',
          'Value': 'BOTO3-created-instance'
        }
      ]
    }
  ]
)

print(instances)

           
