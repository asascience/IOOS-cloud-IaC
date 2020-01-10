#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
import sys
import os
from Cluster.AWSCluster import AWSCluster
import pprint
import subprocess
import romsUtil as util

from prefect import Flow, task

pp = pprint.PrettyPrinter()


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
  return 'STARTED'

#######################################################################



# Reuse if parameterized
# Customize
#######################################################################
# TODO - paramaterize this forecast run
@task
def forecast_run(cluster):

  jobDesc = "jobs/liveocean.job"

  PPN = cluster.getCoresPN()
  NPROCS = cluster.nodeCount*PPN

  with open(jobDesc, 'r') as cf:
    jobDict = json.load(cf)

  print(json.dumps(jobDict, indent=4))
  print(str(jobDict))

  CDATE = jobDict['CDATE']
  HH = jobDict['HH']
  OFS = jobDict['OFS']

  runscript="fcst_launcher.sh"

  # Make ocean in for ROMS
  if cluster.OFS == 'liveocean':

    # Using f-strings
 
    # Add stuff to the replacement dictionary 
    fdate = f"f{CDATE[0:3]}.{CDATE[4:5]}.{CDATE[6:7]}"
    template = f"templates/{OFS}.ocean.in"
    outfile = f"/com/liveocean/{fdate}/liveocean.in"

    TIME_REF = "19700101"
    DSTART = util.ndays(CDATE,TIME_REF)

    replace = {
      "__NTIMES__"   : jobDict['NTIMES'],
      "__TIME_REF__" : jobDict['TIME_REF'],
      "__DSTART__"   : DSTART,
      "__FDATE__"    : fdate,
      "__ININAME__"  : "/com/liveocean/f2019.11.05/ocean_his_0025.nc"
    }

  elif cluster.OFS == 'cbofs':
    template = f"TODO-cbofstemplate"
    outfile = f"TODO-template"
  else
    print("unsupported model")
 
  # FVCOM 

  makeOceanin(cluster,replace,template,outfile)

  try:
    HOSTS=cluster.getHostsCSV()
  except Exception as e:
    print('In driver: execption retrieving list of hostnames:' + str(e))
    # TODO - check this error handling and refactor if needed

  try:
    subprocess.run([runscript,CDATE,HH,str(NPROCS),str(PPN),HOSTS,OFS], \
      stderr=subprocess.STDOUT)
  except Exception as e:
    print('In driver: Exception during subprocess.run :' + str(e))

  print('Forecast finished')
  return 'DONE'

#######################################################################



# Reuse if parameterized
# Customize
#######################################################################
# TODO add a job config to parameterize these templated variables
def makeOceanin(cluster,template,outfile) :

  # TODO - setup for NOSOFS
  #template=""
  #outfile=""

  # Can remove cluster dependency if nodeCount and corePN are parameterized
  # cluster dependency can remain above and this can be added to romsUtil module
  nodeCount = cluster.nodeCount
  coresPN = cluster.getCoresPN()
  totalCores = nodeCount * coresPN
  tiles = util.getTiling( totalCores )

  # TODO - separate settings for nosofs and liveocean
  # TODO - fix variables for liveocean, hardcoded for specific test case currently
  # Just a dictionary
  # Could also read this in from a json file 
  settings = {
    "__NTILEI__"   : tiles["NtileI"],
    "__NTILEJ__"   : tiles["NtileJ"],
    "__NTIMES__"   : 60,
    "__TIME_REF__" : "20191212.00",     # adnoc
    "__DSTART__"   : "18206.0d0",       # liveocean - calculate
    "__FDATE__"    : "f2019.11.06",     # liveocean - 
    "__ININAME__"  : "/com/liveocean/f2019.11.05/ocean_his_0025.nc"
  }

  #       DSTART =  18206.0d0
  # ! days from TIME_REF to start of forecast day

  util.sedoceanin ( template, outfile, settings )

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
  started = start_cluster(cluster)

  # Run the forecast
  fcst_status = forecast_run(cluster).set_upstream(started)

  # Terminate the cluster nodes
  terminate_cluster(cluster).set_upstream(fcst_status)
 
  # fcstflowrunner = fcstflow.run()
  fcstflow.run()

  # postflowrunner = postflow.run(executor=daskexecutor)
  # if (fcstflowrunner.state() =
