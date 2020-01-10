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




#######################################################################
@task
def start_cluster(cluster):

  print('Starting ' + str(cluster.nodeCount) + ' instances ...')
  try:
    cluster.start()
  except Exception as e:
    print('In driver: Exception while creating nodes :' + str(e))
    sys.exit()
  return cluster

#######################################################################




#######################################################################
# TODO - paramaterize this forecast run
@task
def forecast_run(cluster):

  # Shared libraries must be available to the executable!!! shell env is not preserved
  #runscript='/save/nosofs-NCO/jobs/launcher.sh'
  PPN = cluster.getCoresPN()
  NPROCS = cluster.nodeCount*PPN

  print('In forecast_run. PPN = ', str(PPN), ' NPROCS = ', str(NPROCS))

  # TODO: Read these from a job config file
  CDATE = cluster.CDATE
  HH = cluster.HH
  OFS = cluster.OFS

  # TODO parameterize this
  runscript="fcst_launcher.sh"

  # Make ocean in
  # TODO - setup for NOSOFS and LiveOcean
  template = f"templates/{OFS}.ocean.in"
  outfile = "/com/liveocean/f2019.11.06/liveocean.in"
  makeOceanin(cluster,template,outfile)

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




#######################################################################
# TODO add a job config to parameterize these templated variables
def makeOceanin(cluster,template,outfile) :

  # TODO - setup for NOSOFS
  #template=""
  #outfile=""

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
    "__DSTART__"   : "18206.0d0",       # liveocean
    "__FDATE__"    : "f2019.11.06",     # liveocean
    "__ININAME__"  : "/com/liveocean/f2019.11.05/ocean_his_0025.nc"
  }

  #       DSTART =  18206.0d0
  # ! days from TIME_REF to start of forecast day

  util.sedoceanin ( template, outfile, settings )

#######################################################################




#######################################################################
@task 
def terminate_cluster(cluster):

  
  responses = cluster.terminate()
  # Just check the state
  print('Responses from terminate: ')
  for response in responses :
    pp.pprint(response)
#######################################################################



with Flow('ofs workflow') as fcstflow:

  # Pre process tasks here


  # TODO: refactor the DAG instead of relying on the cluster object 
  # TODO: separate the cluster infrastructure config from the forecast job config
  # TODO: make this a runtime argument
  config='./configs/liveocean.config'

  # Forecast
  cluster = init_cluster(config)

  cluster = start_cluster(cluster)

  status = forecast_run(cluster)

  # Terminate the cluster nodes
  terminate_cluster(cluster).set_upstream(status)
 
  # fcstflowrunner = fcstflow.run()
  fcstflow.run()

  # postflowrunner = postflow.run(executor=daskexecutor)
  # if (fcstflowrunner.state() =
