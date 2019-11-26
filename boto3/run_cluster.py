#!/usr/bin/env python3

# would like to keep things cloud platform agnostic at this layer
import sys
import time
import cluster
import pprint


pp = pprint.PrettyPrinter()

#nodeType='c5n.large'
#nodeType='c5.large'
nodeType='t3.micro'
nodes=1

tags = [ { 'Key': 'Name', 'Value': 'IOOS-cloud-sandbox' },
         { 'Key': 'NAME', 'Value': 'T3Micro-BOTO3-created-instance' }
       ]

# Should create my own client class also, I need some experience with Azure for comparison
client = cluster.getClient()

print('Starting %d instances ...' % (nodes))
print('Waiting for all instances to enter running state ...')

try:
  instances = cluster.createNodes(nodes,nodeType,tags)
except Exception as e:
  print('In driver: Exception while creating nodes :' + str(e))
  sys.exit()

print('All instances are running... cluster ready')

for instance in instances:
  print('Instance started: ' + str(instance))


print()
print('##################')
print('Run something here')
print('##################')
print()


# Terminate the cluster nodes
print('About to terminate: ', instances)
responses = cluster.terminateNodes(instances)

# Just check the state
print('Responses from terminate: ')
for response in responses :
  pp.pprint(response)

