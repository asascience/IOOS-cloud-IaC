#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
import sys
import time
import cluster
import pprint
import subprocess
import nodeInfo

pp = pprint.PrettyPrinter()

#nodeType='c5n.large'
#nodeType='c5.large'
#nodeType='c5n.xlarge'
#nodeType='c5n.4xlarge'

nodeType='c5n.18xlarge'
nodes=5

OFS='cbofs'
CDATE='20191209'
HH='00'

tags = [ { 'Key': 'Name', 'Value': 'IOOS-cloud-sandbox' },
         { 'Key': 'NAME', 'Value': OFS + '-fcst-' + CDATE + HH }
       ]

print('Starting ' + str(nodes) + ' instances ...')
print('Waiting for all instances to enter running state ...')

# TODO: make instances a member of cluster
try:
  instances = cluster.createNodes(nodes,nodeType,tags)
except Exception as e:
  print('In driver: Exception while creating nodes :' + str(e))
  sys.exit()

print('All instances are running... cluster ready')

for instance in instances:
  print('Instance started: ' + str(instance))


# cluster.create() or ctor
# cluster.start()
# cluster.stop()
# cluster.terminate()

# look up this number by machine type
#PPN=0
try:
  coresPN=nodeInfo.getPPN(nodeType)
except:
  print('Could not determine PPN')
  cluster.terminateNodes(instances)
  sys.exit()
  # TODO: Add better failure handling routine
  # Cleanup and exit here

PPN=coresPN
NP=nodes*PPN

# Override defaults here
NP=140
PPN=28

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
  subprocess.run([runscript,CDATE,HH,str(NP),str(PPN),hosts,OFS], \
    stderr=subprocess.STDOUT)

except Exception as e:
  print('In driver: Exception during subprocess.run :' + str(e))

print('Forecast finished')

# Terminate the cluster nodes
print('About to terminate: ', instances)
responses = cluster.terminateNodes(instances)

# Just check the state
print('Responses from terminate: ')
for response in responses :
  pp.pprint(response)


