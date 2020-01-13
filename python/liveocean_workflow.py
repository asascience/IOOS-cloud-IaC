#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
# Python dependencies
import sys
import os
import json
import pprint
import subprocess

# 3rd party dependencies
from prefect import Flow, task

# Local dependencies
from Cluster.AWSCluster import AWSCluster
import romsUtil as util

pp = pprint.PrettyPrinter()
debug = False

# Reuse
#######################################################################
@task
def init_cluster(config) -> AWSCluster :
  try:
    cluster = AWSCluster(config)
  except Exception as e:
    print('Could not create cluster: ' + str(e))
    sys.exit()
  return cluster
#######################################################################




# Reuse
#######################################################################
@task
def start_cluster(cluster):

  print('Starting ' + str(cluster.nodeCount) + ' instances ...')
  try:
    cluster.start()
  except Exception as e:
    print('In driver: Exception while creating nodes :' + str(e))
    sys.exit()
  return True
#######################################################################




# Reuse ? Only if parameterize hard coded paths/filenames
#######################################################################
# @ task : need to parameterize/objectify Job if to be made a task
def job_init(cluster) :

  # TODO: Move this into it's own routine, make it a function param
  jobDesc = "jobs/liveocean.job"

  PPN = cluster.getCoresPN()
  NPROCS = cluster.nodeCount*PPN

  with open(jobDesc, 'r') as cf:
    jobDict = json.load(cf)

  if (debug) :
    print(json.dumps(jobDict, indent=4))
    print(str(jobDict))

  CDATE = jobDict['CDATE']
  HH = jobDict['HH']
  OFS = jobDict['OFS']
  TIME_REF = jobDict['TIME_REF']

  # TODO: Make ocean in for ROMS
  if OFS == 'liveocean':

    # LiveOcean requires a significant amount of available RAM to run > 16GB
    # NTIMES 90 is 1 hour for liveocean 
    # Using f-strings
    # Add stuff to the replacement dictionary 
    fdate = f"f{CDATE[0:4]}.{CDATE[4:6]}.{CDATE[6:8]}"
    template = f"templates/{OFS}.ocean.in"
    outfile = f"/com/liveocean/{fdate}/liveocean.in"

    print('PT DEBUG: str error')

    DSTART = util.ndays(CDATE,TIME_REF)
    # DSTART = days from TIME_REF to start of forecast day larger minus smaller date

    settings = {
      "__NTIMES__"   : jobDict['NTIMES'],
      "__TIME_REF__" : jobDict['TIME_REF'],
      "__DSTART__"   : DSTART,
      "__FDATE__"    : fdate,
      "__ININAME__"  : "/com/liveocean/f2019.11.05/ocean_his_0025.nc"
    }

  elif cluster.OFS == 'cbofs':
    template = f"TODO-cbofstemplate"
    outfile = f"TODO-template"
  else :
    print("unsupported model")
    # TODO: Throw exception

  print('PT DEBUG: about to call makeOceanin')
  makeOceanin(cluster,settings,template,outfile)
  print('PT DEBUG: after makeOceanin')

  return jobDict
#######################################################################



# Reuse if parameterized
# Customize
#######################################################################
# TODO - paramaterize this forecast run, add Job object
@task
def forecast_run(cluster):

  # Setup the job
  # TODO: make it a function param? own task?

  PPN = cluster.getCoresPN()
  NPROCS = cluster.nodeCount*PPN

  jobDict = job_init(cluster)
  #try:
  #  jobDict = job_init(cluster)
  #except Exception as e:
  #  print('In forecast_run: execption from job_init: '+ str(e))
  #  return False
    

  CDATE = jobDict['CDATE']
  HH = jobDict['HH']
  OFS = jobDict['OFS']

  runscript="fcst_launcher.sh"

  try:
    HOSTS=cluster.getHostsCSV()
  except Exception as e:
    print('In driver: execption retrieving list of hostnames:' + str(e))
    return False
    # TODO - check this error handling and refactor if needed

  try:
    subprocess.run([runscript,CDATE,HH,str(NPROCS),str(PPN),HOSTS,OFS], \
      stderr=subprocess.STDOUT)
  except Exception as e:
    print('In driver: Exception during subprocess.run :' + str(e))
    return False

  print('Forecast finished')
  return True

#######################################################################



# Reuse if parameterized
# Customize
#######################################################################
# TODO add a job config to parameterize these templated variables
def makeOceanin(cluster,settings,template,outfile) :

  # TODO - setup for NOSOFS

  # Can remove cluster dependency if nodeCount and corePN are parameterized
  # cluster dependency can remain above and this can be added to romsUtil module
  nodeCount = cluster.nodeCount
  coresPN = cluster.getCoresPN()
  totalCores = nodeCount * coresPN
  tiles = util.getTiling( totalCores )

  reptiles = {
    "__NTILEI__"   : str(tiles["NtileI"]),
    "__NTILEJ__"   : str(tiles["NtileJ"]),
  }

  settings.update(reptiles)

  util.sedoceanin(template,outfile,settings)

#######################################################################



# Reuse
#######################################################################
@task 
def terminate_cluster(cluster):
  
  responses = cluster.terminate()
  # Just check the state
  print('Responses from terminate: ')
  for response in responses :
    pp.pprint(response)
#######################################################################


# Customize
with Flow('ofs workflow') as fcstflow:

  # Pre process tasks here


  # TODO: refactor the DAG instead of relying on the cluster object 
  # TODO: separate the cluster infrastructure config from the forecast job config
  # TODO: make this a runtime argument
  config='./configs/liveocean.config'

  # Create the cluster object
  cluster = init_cluster(config)

  # Start the cluster
  isStarted = start_cluster(cluster)

  # Run the forecast
  runStatus = forecast_run(cluster)

  # Terminate the cluster nodes
  terminated = terminate_cluster(cluster)

  # fcstflow.add_edge(cluster,isStarted)  # implicit
  fcstflow.add_edge(isStarted,runStatus)
  fcstflow.add_edge(runStatus,terminated)
 
  # fcstflowrunner = fcstflow.run()
  fcstflow.run()

  # postflowrunner = postflow.run(executor=daskexecutor)
  # if (fcstflowrunner.state() =
