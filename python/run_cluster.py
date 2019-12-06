#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
import sys
import time
import cluster
import pprint
import subprocess

pp = pprint.PrettyPrinter()

#nodeType='c5n.large'
#nodeType='c5.large'
nodeType='c5n.xlarge'
#nodeType='c5n.4xlarge'
#nodeType='t3.micro'
nodes=2

tags = [ { 'Key': 'Name', 'Value': 'IOOS-cloud-sandbox' },
         # { 'Key': 'NAME', 'Value': nodeType + '-BOTO3-created-instance' }
         { 'Key': 'NAME', 'Value': nodeType + '-BOTO3-ngofs-run' }
       ]

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


# compute the number of processors available
# Feed that data to run script 

# 
# NODES
# NPP
# PPN
# Do a lookup, embed in a class

'''
               VCPUS CPUS
c5n.large	2    1
c5n.xlarge	4    2
c5n.2xlarge	8    4
c5n.4xlarge	16   8
c5n.9xlarge	36   18
c5n.18xlarge	72   36
c5n.metal	72   36

PPN=VCPUS/2
'''
# 
# cluster.create() or ctor
# cluster.start()
# cluster.stop()
# cluster.terminate()
# Need to generate hostsfile or hosts string

CDATE='20191206'
HH='03'

# TODO -- look up this number by machine type
PPN=2

NP=nodes*PPN
# set export I_MPI_OFI_LIBRARY_INTERNAL=1 or 0
# export FI_PROVIDER=efa or tcp
# setup tiling for ROMS models
# setup fcst length 

# Shared libraries must be available to the executable!!! 
runscript='/save/nosofs-NCO/jobs/launcher.sh'

try:
  hosts=cluster.getHostsCSV(instances)
except Exception as e:
  print('In driver: execption retrieving list of hostnames:' + str(e))

print('hostnames : ' + hosts)

#runcmd='/home/centos/nosofs-NCO/jobs/fcstrun.sh ' + CDATE + ' ' + NODES + ' ' +
#os.system(runcmd)
#subprocess.run(args, *, stdin=None, input=None, stdout=None, stderr=None, shell=False, cwd=None, timeout=None, check=False, encoding=None, errors=None, env=None)
#subprocess.run(["ls", "-l", "/dev/null"], stdout=subprocess.PIPE)
#subprocess.run([runscript,CDATE,HH,nodes,NP], stdout=subprocess.PIPE)
try:
  # TODO - make this a method of cluster
  subprocess.run([runscript,CDATE,HH,str(nodes),str(NP),hosts], stderr=subprocess.STDOUT)
except Exception as e:
  print('In driver: Exception during subprocess.run :' + str(e))


# Terminate the cluster nodes
print('About to terminate: ', instances)
responses = cluster.terminateNodes(instances)

# Just check the state
print('Responses from terminate: ')
for response in responses :
  pp.pprint(response)


