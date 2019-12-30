#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
import sys
from AWSCluster import AWSCluster
import pprint
import subprocess

pp = pprint.PrettyPrinter()

#nodeType='c5n.large'
#nodeType='c5n.xlarge'
#nodeType='c5n.4xlarge'
#nodeType='c5n.18xlarge'
#nodeType='c5n.18xlarge'
#nodeType='c5.18xlarge'
#nodeType='c5.9xlarge'
#nodeType='c5.4xlarge'
nodeType='c5.large'
nodes=1
OFS='ngofs'
CDATE='20191219'
HH='03'
platform='AWS'

tags = [ { 'Key': 'Name', 'Value': 'IOOS-cloud-sandbox' },
         { 'Key': 'NAME', 'Value': OFS + '-fcst-' + CDATE + HH }
       ]

# TODO - platform is probably not needed, unless using a factory pattern
cluster = AWSCluster(platform,nodeType,nodes,tags)


try:
  coresPN=cluster.getCoresPN()
except Exception as e:
  print('Could not determine PPN for '+ nodeType + ' ' + str(e))
  print('Cores='+str(coresPN))

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


try:
  hosts=cluster.getHostsCSV()
except Exception as e:
  print('In driver: execption retrieving list of hostnames:' + str(e))


print('hostnames : ' + hosts)



# Shared libraries must be available to the executable!!! shell env is not preserved
runscript='/save/nosofs-NCO/jobs/launcher.sh'
try:
  # cluster.run(task)
  subprocess.run([runscript,CDATE,HH,str(NP),str(PPN),hosts,OFS], \
    stderr=subprocess.STDOUT)
except Exception as e:
  print('In driver: Exception during subprocess.run :' + str(e))

print('Forecast finished')


# Terminate the cluster nodes
print('About to terminate cluster ')
responses = cluster.terminate()

# Just check the state
print('Responses from terminate: ')
for response in responses :
  pp.pprint(response)


