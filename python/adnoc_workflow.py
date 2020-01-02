#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
import sys
from AWSCluster import AWSCluster
import pprint
import subprocess

from prefect import Flow, task

pp = pprint.PrettyPrinter()


@task
def init_cluster(config):
  try:
    cluster = AWSCluster(config)
  except Exception as e:
    print('Could not create cluster: ' + str(e))
    sys.exit()

  return cluster



@task
def start_cluster(cluster):

  print('Starting ' + str(cluster.nodeCount) + ' instances ...')
  try:
    cluster.start()
  except Exception as e:
    print('In driver: Exception while creating nodes :' + str(e))
    sys.exit()



@task
def setup_run(cluster):
  try:
    hosts=cluster.getHostsCSV()
  except Exception as e:
    print('In driver: execption retrieving list of hostnames:' + str(e))

  print('hostnames : ' + hosts)
  return hosts


# TODO - paramaterize this forecast run
@task
def forecast_run(cluster, runscript):

  # Shared libraries must be available to the executable!!! shell env is not preserved
  #runscript='/save/nosofs-NCO/jobs/launcher.sh'
  PPN = cluster.getCoresPN()
  NP = cluster.nodeCount*PPN
  CDATE=cluster.CDATE
  HH=cluster.HH
  OFS=cluster.OFS
  hosts=setup_run(cluster)

  try:
    subprocess.run([runscript,CDATE,HH,str(NP),str(PPN),hosts,OFS], \
      stderr=subprocess.STDOUT)
  except Exception as e:
    print('In driver: Exception during subprocess.run :' + str(e))

  print('Forecast finished')


@task 
def terminate_cluster(cluster):

  responses = cluster.terminate()
  # Just check the state
  print('Responses from terminate: ')
  for response in responses :
    pp.pprint(response)





with Flow('ofs workflow') as flow:

  # Pre process

  # TODO: separate the cluster infrastructure config from the forecast job config
  config='adnoc.config'

  # Forecast
  cluster = init_cluster(config)
  start_cluster(cluster)

  runscript='stub'
  forecast_run(cluster, runscript)
  print('Forecast finished')

  # Terminate the cluster nodes
  print('About to terminate cluster ')
  terminate_cluster(cluster)

  # Post process
  config = 'post.config'
  postscript = 'poststub'

  post_machine = init_cluster(config)
  start_cluster(post_machine)
  post_run(post_machine,postscript)
  
flow.run()



