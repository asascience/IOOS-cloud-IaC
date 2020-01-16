#!/usr/bin/env python3

# keep things cloud platform agnostic at this layer
# Python dependencies
import sys
import os
import json
import pprint
import subprocess
import traceback
import glob

# 3rd party dependencies
from prefect import Flow, task, unmapped
from prefect.triggers import all_successful, all_finished
#from prefect.engine.executors import DaskExecutor
from prefect.engine.task_runner import TaskRunner

# Local dependencies
from Cluster.AWSCluster import AWSCluster
import romsUtil as util

from plotting.plot import plot_roms

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
  return
#######################################################################

# Reuse
#######################################################################
@task(trigger=all_finished)
def terminate_cluster(cluster):

  responses = cluster.terminate()
  # Just check the state
  print('Responses from terminate: ')
  for response in responses :
    pp.pprint(response)

  return
#######################################################################



# Reuse ? Only if parameterize hard coded paths/filenames
# NPROCS in JOB or NPROCS=totalCores in cluster? Who decides?
#######################################################################
# @ task : need to parameterize/objectify Job if to be made a task
# TODO: jobDesc file - paramter
def job_init(cluster) :

  # TODO: Move this into it's own routine, make it a function param
  jobDesc = "jobs/liveocean.job"

  PPN = cluster.getCoresPN()
  totalCores = cluster.nodeCount*PPN

  with open(jobDesc, 'r') as cf:
    jobDict = json.load(cf)

  if (debug) :
    print(json.dumps(jobDict, indent=4))
    print(str(jobDict))

  CDATE = jobDict['CDATE']
  HH = jobDict['HH']
  OFS = jobDict['OFS']
  TIME_REF = jobDict['TIME_REF']

  # TODO: Make ocean in for NOSOFS
  if OFS == 'liveocean':

    # TODO: NO HARDCODED PATHS!
    # LiveOcean requires a significant amount of available RAM to run > 16GB
    # NTIMES 90 is 1 hour for liveocean 
    # Using f-strings
    # Add stuff to the replacement dictionary 
    fdate = f"f{CDATE[0:4]}.{CDATE[4:6]}.{CDATE[6:8]}"
    template = f"templates/{OFS}.ocean.in"
    outfile = f"/com/liveocean/{fdate}/liveocean.in"

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

  makeOceanin(totalCores,settings,template,outfile)

  return jobDict
#######################################################################



# Reuse if parameterized
# Customize
#######################################################################
# TODO - paramaterize this forecast run, add Job object
@task
def forecast_run(cluster):

  print("PT TESTING, skipping forecast run")
  return

  # Setup the job
  PPN = cluster.getCoresPN()
  NPROCS = cluster.nodeCount*PPN

  try:
    jobDict = job_init(cluster)
  except Exception as e:
    print('In forecast_run: execption from job_init: '+ str(e))
    traceback.print_stack()
    return False
    
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
  return

#######################################################################



# Reuse
# TODO: Move this into romsUtils
#######################################################################
def makeOceanin(totalCores,settings,template,outfile) :

  # TODO - setup for NOSOFS

  tiles = util.getTiling( totalCores )

  reptiles = {
    "__NTILEI__"   : str(tiles["NtileI"]),
    "__NTILEJ__"   : str(tiles["NtileJ"]),
  }

  settings.update(reptiles)
  util.sedoceanin(template,outfile,settings)
  return
#######################################################################



#####################################################################

@task
def nc_files(SOURCE):
    FILES = sorted(glob.glob(f'{SOURCE}/*.nc'))
    for f in FILES:
      print(f)
    return FILES
#####################################################################



#####################################################################
@task
def make_plots(filename,target,varname):

  print(f"{filename} {target} {varname}")

  if not os.path.exists(target):
      os.mkdir(target)

  plot_roms(filename,target,varname)
  return
#####################################################################




#####################################################################
@task
def start_dask(cluster) -> str:

  # For now assuming post will only run on one node

  # get first host
  host = cluster.getHostsCSV()[0]

  # Should this be specified in the Job? Possibly?
  #nppost = cluster.nodeCount * cluster.PPN
  nppost = cluster.PPN

  # Start a dask scheduler on the host
  port = "8786"
  tcphost = f"tcp://{host}:{port}" 

  print("DEBUG: tcphost : ",tcphost)

  try:
    subprocess.run(["ssh", host, "dask-scheduler", "&"], stderr=subprocess.STDOUT)
    for i in range(0,nppost):
      subprocess.run(["ssh", host, "dask-worker", tcphost, "&"], stderr=subprocess.STDOUT)
  except Exception as e:
    print("In start_dask during subprocess.run :" + str(e))
    traceback.print_stack()

  return tcphost
#####################################################################



 # Customize
with Flow('ofs workflow') as flow:

  #####################################################################
  # FORECAST
  #####################################################################

  # TODO: make this a runtime argument?
  #config='./configs/liveocean.config'
  config='./configs/test.config'

  # Create the cluster object
  cluster = init_cluster(config)

  # Start the cluster
  #PT fcStarted = start_cluster(cluster)

  # Run the forecast
  fcstStatus = forecast_run(cluster)

  # Terminate the cluster nodes
  fcTerminated = terminate_cluster(cluster)

  #PT flow.add_edge(fcStarted,fcstStatus)
  flow.add_edge(fcstStatus,fcTerminated)


  #####################################################################
  # POST Processing
  #####################################################################
  # Spin up a new machine?
  # or launch a container?
  # or run concurrently on above?
  # or run on local machine?
 
  SOURCE = os.path.abspath('/com/liveocean/current')
  TARGET = os.path.abspath('/com/liveocean/current/plots')
  FILES = nc_files(SOURCE, upstream_tasks=[fcstStatus])

  # Start a machine
  postconfig = './configs/post.config'
  postmach = init_cluster(postconfig)
  pmStarted = start_cluster(postmach, upstream_tasks=[fcstStatus])

  # Start a dask scheduler on the host
  # dasksched = start_dask(postmach,upstream_tasks=[isStarted])
  # This is overly complicated!!!!! Might be easier to just run with MPIRUN - MPMD script

  plots = make_plots.map(filename=FILES, target=unmapped(TARGET), varname=unmapped('temp'))
  plots.set_upstream([fcstStatus])
  pmTerminated = terminate_cluster(postmach,upstream_tasks=[plots])


#####################################################################

def main():

  print(flow.tasks)
  flow.run()

#####################################################################

 
if __name__ == '__main__':
  main()
