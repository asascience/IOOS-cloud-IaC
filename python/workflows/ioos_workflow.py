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
  runscript="/save/nosofs-NCO/jobs/launcher.sh"

  # Make ocean in
  # TODO - setup for NOSOFS
  #makeOceanin(cluster)

  try:
    HOSTS=cluster.getHostsCSV()
  except Exception as e:
    print('In driver: execption retrieving list of hostnames:' + str(e))
  # TODO - check this error handling and refactor if needed

  try:
    subprocess.run([runscript,CDATE,HH,str(NPROCS),str(PPN),hosts,OFS], \
      stderr=subprocess.STDOUT)
  except Exception as e:
    print('In driver: Exception during subprocess.run :' + str(e))

  print('Forecast finished')
  return 'DONE'

#######################################################################




#######################################################################
# TODO add a job config
#@task
def makeOceanin(cluster) :

  # TODO - setup for NOSOFS
  template=""
  outfile=""

  nodeCount = cluster.nodeCount
  coresPN = cluster.getCoresPN()
  totalCores = nodeCount * coresPN
  tiles = util.getTiling( totalCores )

  # Just a dictionary
  # Could also read this in from a json file 
  settings = {
    "__NTILEI__": tiles["NtileI"],
    "__NTILEJ__": tiles["NtileJ"],
    "__NTIMES__": 60,
    "__TIME_REF__": "20191212.00"
  }

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
  config='./configs/ioos.config'

  # Forecast
  cluster = init_cluster(config)

  cluster = start_cluster(cluster)

  status = forecast_run(cluster)

  # Terminate the cluster nodes
  terminate_cluster(cluster).set_upstream(status)

  # Post process example
  #config = 'post.config'
  #postscript = 'poststub'

  #post_machine = init_cluster(config)
  #start_cluster(post_machine)
  #post_run(post_machine,postscript)

  # fcstflowrunner = fcstflow.run()



  # postflowrunner = postflow.run(executor=daskexecutor)

  # if (fcstflowrunner.state() =
