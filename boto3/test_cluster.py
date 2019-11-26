#!/usr/bin/env python3

# Need a JSON formatter for pretty print

# would like to keep things cloud platform agnostic at this layer
#import boto3
import time
import cluster
import json

#nodeType='c5n.large'
#nodeType='c5.large'
nodeType='t3.micro'
nodes=1

tags = [ { 'Key': 'Name', 'Value': 'IOOS-cloud-sandbox' },
         { 'Key': 'NAME', 'Value': 'T3Micro-BOTO3-created-instance' }
       ]

# Should create my own client class also, I need some experience with Azure for comparison
client = cluster.getClient()

instances = cluster.createNodes(nodes,nodeType,tags)
#instances = cluster.createNodes(nodes,nodeType)
print('create_nodes created : ', instances);

for instance in instances :
  print('describe_instances')
  response = cluster.describeInstance(instance) 
  print(response)

# wait for node to startup
secs=20
print('Sleeping for %d seconds' % (secs))  # % ('Zara', 21)
time.sleep(secs)




# Launch the run script




# Terminate the cluster nodes
print('About to terminate: ', instances)

responses = cluster.terminateNodes(instances)

print('Responses from terminate: ')
for response in responses :
  print(response)


print('describe_instances')
for instance in instances :
  response = cluster.describeInstance(instance)
  print(response)

