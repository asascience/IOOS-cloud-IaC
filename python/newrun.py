#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
import sys
import time
import Cluster
import pprint
import subprocess
import nodeInfo

pp = pprint.PrettyPrinter()

#nodeType='c5n.large'
#nodeType='c5n.xlarge'
#nodeType='c5n.4xlarge'
#nodeType='c5n.18xlarge'
#nodeType='c5n.18xlarge'
#nodeType='c5.18xlarge'
#nodeType='c5.9xlarge'
nodeType='c5.4xlarge'
nodes=1
OFS='ngofs'
CDATE='20191219'
HH='03'

tags = [ { 'Key': 'Name', 'Value': 'IOOS-cloud-sandbox' },
         { 'Key': 'NAME', 'Value': OFS + '-fcst-' + CDATE + HH }
       ]

cluster = Cluster(nodeType,nodes,tags)

try:
  coresPN=cluster.getPPN()
except:
  print('Could not determine PPN for '+ nodeType)
  sys.exit()

PPN=coresPN
NP=nodes*PPN

print('Starting ' + str(nodes) + ' instances ...')
print('Waiting for all instances to enter running state ...')

try:
  cluster.start()
except Exception as e:
  print('In driver: Exception while creating nodes :' + str(e))
  sys.exit()

# CBOFS COOPS
#NP=140
#PPN=28

# Shared libraries must be available to the executable!!! shell env is not preserved
runscript='/save/nosofs-NCO/jobs/launcher.sh'

try:
  hosts=cluster.getHostsCSV()
except Exception as e:
  print('In driver: execption retrieving list of hostnames:' + str(e))

print('hostnames : ' + hosts)

try:

  # cluster.run(task)
  subprocess.run([runscript,CDATE,HH,str(NP),str(PPN),hosts,OFS], \
    stderr=subprocess.STDOUT)

except Exception as e:
  print('In driver: Exception during subprocess.run :' + str(e))

print('Forecast finished')

# Terminate the cluster nodes
print('About to terminate: ', instances)
# cluster.terminate()
responses = cluster.terminateNodes(instances)

# Just check the state
print('Responses from terminate: ')
for response in responses :
  pp.pprint(response)


