#!/usr/bin/env python3

# Need a JSON formatter for pretty print

import boto3
import time
import cluster
import json

interface='efa' 
#nodeType='c5n.large'
#interface='interface' # does not accept interface
#nodeType='c5.large'
nodeType='t3.micro'
nodes=1

client = boto3.client('ec2')

instances = cluster.create_nodes(nodes,nodeType,interface)
print('create_nodes created : ', instances);

for instance in instances :
  print('describe_instances')
  response = client.describe_instances(InstanceIds=[instance.instance_id])
  print(response)

# wait for node to startup
print('Sleeping for 30 seconds')
time.sleep(20)

print('About to terminate: ', instances)
# launch run script

responses = cluster.terminate_nodes(instances)

print('Responses from terminate: ')
for response in responses :
  print(response)

print('describe_instances')
for instance in instances :
  response = client.describe_instances(InstanceIds=[instance.instance_id])
  print(response)

