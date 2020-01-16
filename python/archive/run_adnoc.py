#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
import sys
#from AWSCluster import AWSCluster
from Cluster.AWSCluster import AWSCluster
import pprint
import subprocess

pp = pprint.PrettyPrinter()

config='configs/adnoc.config'

## Task cluster instantiate()
try:
  print('creating cluster')
  cluster = AWSCluster(config)
  print('cluster initialized')

except Exception as e:
  print('Could not create cluster: ' + str(e))
  sys.exit()

PPN = cluster.getCoresPN()
NP = cluster.nodeCount*PPN

print('Starting ' + str(cluster.nodeCount) + ' instances ...')


## Task cluster.start()
try:
  cluster.start()
except Exception as e:
  print('In driver: Exception while creating nodes :' + str(e))
  sys.exit()

## Task getHosts
try:
  hosts=cluster.getHostsCSV()
except Exception as e:
  print('In driver: execption retrieving list of hostnames:' + str(e))

print('hostnames : ' + hosts)

# Task setup ROMS forecast
# read config
# create template

## Task forecast run
##################################################
####  Cluster job script here
##################################################

## Shared libraries must be available to the executable!!! shell env is not preserved
#runscript='/save/nosofs-NCO/jobs/launcher.sh'
#try:
#  # cluster.run(task)
#  subprocess.run([runscript,CDATE,HH,str(NP),str(PPN),hosts,cluster.OFS], \
#    stderr=subprocess.STDOUT)
#except Exception as e:
#  print('In driver: Exception during subprocess.run :' + str(e))

print('Task finished')

# Terminate the cluster nodes
print('About to terminate cluster ')
responses = cluster.terminate()

# Just check the state
print('Responses from terminate: ')
for response in responses :
  pp.pprint(response)

