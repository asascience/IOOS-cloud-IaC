#!/usr/bin/env python3

# would like to keep things cloud platform agnostic at this layer
import sys
import time
import cluster
import pprint


#pp = pprint.PrettyPrinter(indent=2)
#pp = pprint.PrettyPrinter(compact=True)
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

try:
  print('Starting %d instances ...' % (nodes))
  print('Waiting for all instances to enter running state ...')
  instances = cluster.createNodes(nodes,nodeType,tags)
  print('All instances are running... cluster ready')
  for instance in instances:
    print('Created InstanceId: ' + instance.instance_id)

except Exception as e:
  print('In driver: Exception while creating nodes :' + str(e))
  cluster.terminateNodes(instances)
  sys.exit()


# Need something smaller - just the state
# This contains out-of-date instance metadata from the initial api call
#for instance in instances :
#  print('describe_instances')
#  response = cluster.describeInstance(instance) 
#  pp.pprint(response)


print()
print('Run something here')
print()

########################################################################
########################################################################
# Launch the run script
########################################################################
########################################################################


# Terminate the cluster nodes
print('About to terminate: ', instances)
responses = cluster.terminateNodes(instances)

# Just check the state
print('Responses from terminate: ')
for response in responses :
  pp.pprint(response)

